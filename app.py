import os
import json
from typing import TypedDict
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# ==========================================
# 1. SETUP & LANGGRAPH LOGIC
# ==========================================
os.environ["GOOGLE_API_KEY"] = "AIzaSyD4Ed9JRDOpX1EhE0x5n6BgUoiyVILLLZg" # Add your key!

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

class GraphState(TypedDict):
    query: str
    context: str
    generation: str
    needs_human: bool
    human_response: str

def retrieve_node(state: GraphState):
    docs = retriever.invoke(state["query"])
    return {"context": "\n\n".join([doc.page_content for doc in docs])}

def generate_node(state: GraphState):
    prompt = f"""
    You are a customer support assistant. Answer ONLY using the context.
    If the context does not contain the answer, flag it for human escalation.
    Query: {state['query']}
    Context: {state['context']}
    Output STRICTLY as JSON: {{"answer": "...", "needs_human": true/false}}
    """
    response = llm.invoke(prompt)
    raw_text = response.content.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(raw_text)
        return {"generation": data.get("answer"), "needs_human": data.get("needs_human", False)}
    except:
        return {"generation": "Failed to parse.", "needs_human": True}

def human_node(state: GraphState):
    return {"generation": f"[Agent Override]: {state['human_response']}"}

def routing_logic(state: GraphState):
    return "human_node" if state["needs_human"] else END

workflow = StateGraph(GraphState)
workflow.add_node("retrieve_node", retrieve_node)
workflow.add_node("generate_node", generate_node)
workflow.add_node("human_node", human_node)
workflow.set_entry_point("retrieve_node")
workflow.add_edge("retrieve_node", "generate_node")
workflow.add_conditional_edges("generate_node", routing_logic)
workflow.add_edge("human_node", END)

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory, interrupt_before=["human_node"])

# ==========================================
# 2. FASTAPI SERVER SETUP
# ==========================================
app = FastAPI(title="RAG Support API")

class ChatRequest(BaseModel):
    session_id: str
    query: str

class HumanRequest(BaseModel):
    session_id: str
    human_response: str

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    config = {"configurable": {"thread_id": req.session_id}}
    initial_state = {"query": req.query, "needs_human": False, "human_response": ""}
    
    # Run the graph
    for event in graph.stream(initial_state, config=config):
        pass
        
    state_snapshot = graph.get_state(config)
    
    # Check if the graph paused for a human
    if state_snapshot.next and state_snapshot.next[0] == "human_node":
        return {
            "status": "paused", 
            "bot_attempt": state_snapshot.values.get("generation"),
            "message": "Waiting for human agent."
        }
        
    # If no human needed, return the final answer
    return {"status": "success", "response": state_snapshot.values.get("generation")}

@app.post("/human-reply")
def human_reply_endpoint(req: HumanRequest):
    config = {"configurable": {"thread_id": req.session_id}}
    
    # Update the graph state with human input
    graph.update_state(config, {"human_response": req.human_response})
    
    # Resume the graph
    for event in graph.stream(None, config=config):
        pass
        
    final_state = graph.get_state(config)
    return {"status": "success", "response": final_state.values.get("generation")}
