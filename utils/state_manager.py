import streamlit as st

def init_session_state():
    """
    Initializes session state variables if they don't exist yet.
    Call this at the very top of your main_app.py and every page.
    """
    
    # Track the total sugar intake (Integer/Float)
    if 'sugar_intake' not in st.session_state:
        st.session_state['sugar_intake'] = 0
        
    # Track chat messages (List of dicts)
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Track language preference (String)
    if 'language' not in st.session_state:
        st.session_state['language'] = 'English'

    # Track if user is in "Mak Cik" mode (Boolean)
    if 'is_makcik_mode' not in st.session_state:
        st.session_state['is_makcik_mode'] = False