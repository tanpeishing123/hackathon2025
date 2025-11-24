import streamlit as st
from utils.state_manager import init_session_state

# 1. Setup
st.set_page_config(page_title="Cek Manis", layout="wide", page_icon="🍬")
init_session_state()

# 2. Header
st.title("🏠 Cek Manis Dashboard")
st.markdown("### Your Daily Health Summary")

# 3. Simple Metrics
col1, col2 = st.columns(2)

with col1:
    # Standard Clinical View
    st.metric("Sugar Today", f"{st.session_state['sugar_intake']}g", "50g Limit", delta_color="inverse")

with col2:
    st.info("💡 **Tip:** Keep sugar below 50g to avoid Potong Kaki risk!")

# 4. Debug / Reset Button
if st.button("Reset Counter"):
    st.session_state['sugar_intake'] = 0
    st.rerun()