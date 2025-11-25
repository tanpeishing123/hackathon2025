import streamlit as st
# Import the logic functions from our service file
from services.jamai_service import chat_with_jamai

st.set_page_config(page_title="JamAI Super App", page_icon="⚡")
st.title("⚡ JamAI Super App")

# 1. Initialize Chat History (so messages don't disappear)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Display Existing Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Handle New User Input
if prompt := st.chat_input("Ask JamAI something..."):
    # A. Display User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # B. Call Backend Logic (The "Simplified" part)
    with st.spinner("Thinking..."):
        try:
            response = chat_with_jamai(prompt)
        except Exception as e:
            response = f"❌ An error occurred: {e}"

    # C. Display AI Response
    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})