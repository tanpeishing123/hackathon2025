import streamlit as st

def init_session_state():
    # Just track the numbers and chat
    if 'sugar_intake' not in st.session_state:
        st.session_state['sugar_intake'] = 0
        
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []