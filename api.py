import os
import json
from typing import TypedDict
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# 🚨 Add your NEW API Key here! Do not use the compromised one.
os.environ["GOOGLE_API_KEY"] = "https://aistudio.google.com/api-keys?project=gen-lang-client-0589491357&projectFilter=gen-lang-client-0139624015"

# 🧠 THE REAL AI IS BACK ONLINE
# ⚡ SWITCHED TO THE ULTRA-FAST 1.5 FLASH 8B MODEL
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", temperature=0)
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
    """Hybrid Logic: Instant Mock + Real AI + Safety Fallback"""
    query = state['query'].lower()
    
    # 1. 🚀 STEP 1: THE "INSTANT HIT" (Mock Cases)
    # We handle common keywords locally to save API quota and increase speed.
    if "return" in query or "refund" in query:
        print("[System] ⚡ Instant Hit: Using Local Refund Policy.")
        return {"generation": "Our policy allows returns within 30 days of purchase.", "needs_human": False}
    
    if "warranty" in query:
        print("[System] ⚡ Instant Hit: Using Local Warranty Info.")
        return {"generation": "Your device has a 1-year limited hardware warranty.", "needs_human": False}

    # 2. 🧠 STEP 2: THE REAL AI INTEGRATION
    # If it's not a common case, we ask Gemini to look at the PDF context.
    print("[System] 🤖 Query unique. Consulting Real Gemini AI...")
    prompt = f"""
    Answer using ONLY the context. If not present, flag for human escalation.
    Query: {state['query']}
    Context: {state['context']}
    Output JSON: {{"answer": "...", "needs_human": true/false}}
    """
    
    try:
        response = llm.invoke(prompt)
        raw_text = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_text)
        return {"generation": data.get("answer"), "needs_human": data.get("needs_human", False)}
        
    except Exception as e:
        # 3. 🛡️ STEP 3: THE GRACEFUL FALLBACK (Rate Limit Safety)
        print(f"⚠️ API Error: {e}")
        # Instead of crashing, we trigger an automatic escalation so a human can help.
        return {
            "generation": "I'm having trouble reaching my brain right now, but I've notified a human agent to help you!", 
            "needs_human": True 
        }
def human_node(state: GraphState):
    return {"generation": f"[Agent Override]: {state['human_response']}"}

def routing_logic(state: GraphState):
    return "human_node" if state["needs_human"] else END

# Build Graph
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

# FastAPI Server Setup
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
    
    # 🛡️ THE EXTERNAL SAFETY NET (Protects against Server 500 crashes breaking the UI)
    try:
        for event in graph.stream(initial_state, config=config):
            pass
            
        state_snapshot = graph.get_state(config)
        
        if state_snapshot.next and state_snapshot.next[0] == "human_node":
            return {
                "status": "paused", 
                "bot_attempt": state_snapshot.values.get("generation"),
                "message": "Waiting for human agent."
            }
            
        return {"status": "success", "response": state_snapshot.values.get("generation")}
        
    except Exception as e:
        print(f"Backend Error Caught: {e}")
        error_message = f"⚠️ **System Alert:** The server encountered an error processing your request. Please try again in a moment. \n\n*Technical detail: {str(e)}*"
        return {"status": "success", "response": error_message}

@app.post("/human-reply")
def human_reply_endpoint(req: HumanRequest):
    config = {"configurable": {"thread_id": req.session_id}}
    graph.update_state(config, {"human_response": req.human_response})
    
    for event in graph.stream(None, config=config):
        pass
        
    final_state = graph.get_state(config)
    return {"status": "success", "response": final_state.values.get("generation")}

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
