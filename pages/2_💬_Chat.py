import streamlit as st
# Import the logic functions from our service file
from services.jamai_service import chat_with_jamai

# --- TRANSLATIONS ---
TRANS = {
    "English": {
        "page_title": "JamAI Chatbot",
        "header_title": "🤖 JamAI Chatbot",
        "subtitle": "Your personal health assistant",
        "input_ph": "Ask JamAI something...",
        "spinner": "Thinking...",
        "error": "❌ An error occurred: {}",
        "agent_prof": "👨‍⚕️ Prof. Manis",
        "agent_makcik": "👵 Mak Cik Manis",
        "init_prof": "Hello! I am Prof. Manis. I can help you analyze your sugar intake scientifically. How can I assist you today?",
        "init_makcik": "Haiya, hello! I am Mak Cik Manis. Don't drink so much sugar ah, later get diabetes! What you want to ask?",
        "clear_chat": "Clear Chat"
    },
    "Malay": {
        "page_title": "Chatbot JamAI",
        "header_title": "🤖 Chatbot JamAI",
        "subtitle": "Pembantu kesihatan peribadi anda",
        "input_ph": "Tanya JamAI sesuatu...",
        "spinner": "Sedang berfikir...",
        "error": "❌ Ralat berlaku: {}",
        "agent_prof": "👨‍⚕️ Prof. Manis",
        "agent_makcik": "👵 Mak Cik Manis",
        "init_prof": "Helo! Saya Prof. Manis. Saya boleh bantu anda analisis pengambilan gula secara saintifik. Apa yang boleh saya bantu?",
        "init_makcik": "Haa, helo! Mak Cik Manis sini. Jangan minum manis sangat woi, nanti kena kencing manis! Nak tanya apa tu?",
        "clear_chat": "Padam Sembang"
    }
}

lang = st.session_state.get('lang', 'English')
t = TRANS[lang]

# Track Page Navigation
st.session_state['last_page'] = 'Chat'

# Dismiss intro from Home page if user visits Chat
if 'intro_shown' in st.session_state:
    st.session_state.intro_shown = True

st.set_page_config(page_title=t['page_title'], page_icon="🤖", layout="wide")

st.markdown("""
<style>
/* GENERAL LAYOUT */
.block-container { padding-top: 3rem; padding-bottom: 8rem; }
.stApp { background-color: #ffffff; }
#MainMenu, footer, header {visibility: hidden;}
.stVerticalBlock > div:not(:last-child) { margin-bottom: 15px; }

/* HEADER */
.header-title { font-size: 3rem !important; font-weight: 900 !important; color: #000000 !important; line-height: 1.2; }
.header-subtitle { font-size: 1.2rem; color: #64748b; margin-bottom: 2rem; }

/* CHAT STYLING */
/* Hide markers */
.user-marker, .bot-marker { display: none; }

/* Remove default margins from avatars to allow precise gap control */
div[data-testid="stChatMessage"] div[data-testid="stChatMessageAvatar"] {
    margin-right: 0 !important;
    margin-left: 0 !important;
}

/* USER MESSAGE (Right Aligned, Light Teal) */
div[data-testid="stChatMessage"]:has(span.user-marker) {
    flex-direction: row-reverse !important;
    gap: 6px !important;
    background-color: transparent !important;
}
div[data-testid="stChatMessageContent"]:has(span.user-marker) {
    background-color: #ccfbf1 !important; /* Light Teal */
    color: #0f172a !important; /* Dark Text */
    border: 1px solid #99f6e4 !important;
    border-radius: 12px !important;
    padding: 10px 15px !important;
    margin-right: 0px !important;
    margin-left: auto !important; /* Push to right */
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    width: fit-content !important;
    max-width: 70% !important;
}
/* User Avatar Background */
div[data-testid="stChatMessage"]:has(span.user-marker) div[data-testid="stChatMessageAvatar"] {
    background-color: #0d9488 !important;
    color: white !important;
}

/* BOT MESSAGE (Left Aligned, Slate) */
div[data-testid="stChatMessage"]:has(span.bot-marker) {
    flex-direction: row !important;
    gap: 0px !important; /* Stick to icon */
    background-color: transparent !important;
}
div[data-testid="stChatMessageContent"]:has(span.bot-marker) {
    background-color: #f8fafc !important; /* Very Light Slate */
    color: #1e293b !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 10px 15px !important;
    margin-right: auto !important; /* Push to left */
    margin-left: 0px !important; /* Ensure no left margin */
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    width: fit-content !important;
    max-width: 70% !important;
}
/* Bot Avatar Background */
div[data-testid="stChatMessage"]:has(span.bot-marker) div[data-testid="stChatMessageAvatar"] {
    background-color: #e2e8f0 !important;
    color: #475569 !important;
}

/* UNIFIED BUTTON COLORS (Teal #0d9488) */
.stButton > button {
    background-color: #0d9488 !important; 
    color: white !important; 
    border: none !important; 
    border-radius: 8px !important; 
    font-weight: 600 !important; 
    width: 100% !important;
}

/* Secondary Button Override (for unselected tabs) */
button[kind="secondary"] {
    background-color: #e2e8f0 !important; /* Darker grey */
    color: #475569 !important; /* Darker text */
    border: 1px solid #cbd5e1 !important;
}

/* Hover state for secondary buttons */
button[kind="secondary"]:hover {
    background-color: #cbd5e1 !important;
    color: #1e293b !important;
    border-color: #94a3b8 !important;
}

/* Clear Chat Button (Red) */
div[data-testid="stColumn"]:has(.clear-btn-marker) button {
    background-color: #fee2e2 !important;
    color: #ef4444 !important;
    border: 1px solid #fecaca !important;
}
div[data-testid="stColumn"]:has(.clear-btn-marker) button:hover {
    background-color: #fecaca !important;
    border-color: #ef4444 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="header-title" style="text-align: center;">{t["header_title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="header-subtitle" style="text-align: center;">{t["subtitle"]}</div>', unsafe_allow_html=True)

# --- AGENT SELECTION ---
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = t['agent_prof']

# Unified Row for Agents and Clear Button
c_agent1, c_agent2, c_clear = st.columns([1.2, 1.2, 0.8])

current_agent = st.session_state.selected_agent

with c_agent1:
    if st.button(t['agent_prof'], use_container_width=True, type="primary" if current_agent == t['agent_prof'] else "secondary"):
        st.session_state.selected_agent = t['agent_prof']
        st.rerun()

with c_agent2:
    if st.button(t['agent_makcik'], use_container_width=True, type="primary" if current_agent == t['agent_makcik'] else "secondary"):
        st.session_state.selected_agent = t['agent_makcik']
        st.rerun()

agent_choice = st.session_state.selected_agent

# Determine Table ID and Initial Message based on selection
if agent_choice == t['agent_prof']:
    current_table_id = "chat"
    init_msg = t['init_prof']
    agent_avatar = "👨‍⚕️"
else:
    current_table_id = "chat2"
    init_msg = t['init_makcik']
    agent_avatar = "👵"

# Handle Agent Switch (Clear history if agent changes)
if "last_agent" not in st.session_state:
    st.session_state.last_agent = agent_choice

if st.session_state.last_agent != agent_choice:
    st.session_state.messages = []
    st.session_state.last_agent = agent_choice
    st.rerun()

with c_clear:
    if st.button(t['clear_chat'], use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown('<span class="clear-btn-marker"></span>', unsafe_allow_html=True)

st.markdown("<hr style='border: 0.5px solid #ddd; margin-bottom: 30px;'>", unsafe_allow_html=True)

# 1. Initialize Chat History (so messages don't disappear)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add initial message if history is empty
if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": init_msg})

# Helper to display message with styling
def display_message(role, content):
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(f'<span class="user-marker"></span>{content}', unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar=agent_avatar):
            st.markdown(f'<span class="bot-marker"></span>{content}', unsafe_allow_html=True)

# 2. Display Existing Chat History
for message in st.session_state.messages:
    display_message(message["role"], message["content"])

# 3. Handle Auto-Prompt from Scanner
if 'chat_prompt' in st.session_state and st.session_state.chat_prompt:
    auto_prompt = st.session_state.chat_prompt
    st.session_state.chat_prompt = None # Clear it immediately
    
    # A. Display User Message
    display_message("user", auto_prompt)
    st.session_state.messages.append({"role": "user", "content": auto_prompt})

    # Prepare prompt for AI (Add hidden instruction for Mak Cik in English mode)
    final_prompt = auto_prompt
    if lang == "English" and current_table_id == "chat2":
        final_prompt = f"{auto_prompt} (Please answer in English)"

    # B. Call Backend Logic
    with st.spinner(t['spinner']):
        try:
            response = chat_with_jamai(final_prompt, table_id=current_table_id, language=lang)
        except Exception as e:
            response = t['error'].format(e)

    # C. Display AI Response
    display_message("assistant", response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# 4. Handle New User Input
if prompt := st.chat_input(t['input_ph']):
    # A. Display User Message
    display_message("user", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare prompt for AI (Add hidden instruction for Mak Cik in English mode)
    final_prompt = prompt
    if lang == "English" and current_table_id == "chat2":
        final_prompt = f"{prompt} (Please answer in English)"

    # B. Call Backend Logic (The "Simplified" part)
    with st.spinner(t['spinner']):
        try:
            response = chat_with_jamai(final_prompt, table_id=current_table_id, language=lang)
        except Exception as e:
            response = t['error'].format(e)

    # C. Display AI Response
    display_message("assistant", response)
    st.session_state.messages.append({"role": "assistant", "content": response})