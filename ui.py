import streamlit as st
import requests

# API Configuration
API_URL = "http://127.0.0.1:8000"
SESSION_ID = "user_session_123"

st.set_page_config(page_title="RAG Support Bot", page_icon="🤖")
st.title("🤖 Customer Support Assistant")

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting_for_human" not in st.session_state:
    st.session_state.waiting_for_human = False
if "bot_attempt" not in st.session_state:
    st.session_state.bot_attempt = ""

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- HITL DASHBOARD UI ---
if st.session_state.waiting_for_human:
    st.error("🚨 **System Alert: Query out of bounds. Human Escalation Required.**")
    st.info(f"**Bot's Internal Thought:** {st.session_state.bot_attempt}")
    
    with st.form("human_intervention_form"):
        human_input = st.text_area("Support Agent Dashboard - Type manual response here:")
        submitted = st.form_submit_button("Send as Agent")
        
        if submitted and human_input:
            # Send the human's response to the API to resume the graph
            res = requests.post(f"{API_URL}/human-reply", json={
                "session_id": SESSION_ID,
                "human_response": human_input
            }).json()
            
            # Display the final routed message
            st.session_state.messages.append({"role": "assistant", "content": res["response"]})
            st.session_state.waiting_for_human = False
            st.rerun()

# --- NORMAL CHAT UI ---
elif prompt := st.chat_input("How can I help you today?"):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        # Send query to FastAPI
        res = requests.post(f"{API_URL}/chat", json={
            "session_id": SESSION_ID,
            "query": prompt
        }).json()

        if res["status"] == "paused":
            # Trigger the HITL UI
            st.session_state.waiting_for_human = True
            st.session_state.bot_attempt = res["bot_attempt"]
            st.rerun()
        else:
            # Display normal bot answer
            st.session_state.messages.append({"role": "assistant", "content": res["response"]})
            with st.chat_message("assistant"):
                st.markdown(res["response"])
