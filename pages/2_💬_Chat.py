import streamlit as st
from services.jamai_service import chat_with_jamai

st.title("💬 Chat")

# Show history
for msg in st.session_state['chat_history']:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle Input
if prompt := st.chat_input("Ask JamAI..."):
    # 1. Show user message
    st.chat_message("user").write(prompt)
    st.session_state['chat_history'].append({"role": "user", "content": prompt})
    
    # 2. Get response from JamAI Service
    with st.spinner("Thinking..."):
        response_text = chat_with_jamai(prompt)
    
    # 3. Show AI message
    st.chat_message("assistant").write(response_text)
    st.session_state['chat_history'].append({"role": "assistant", "content": response_text})