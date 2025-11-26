import streamlit as st
import time

def init_session_state():
    """initialize Session State variable"""
    
    # basic data
    if 'sugar_today' not in st.session_state:
        st.session_state.sugar_today = 0
    if 'fat_today' not in st.session_state:
        st.session_state.fat_today = 0
    if 'sugar_month_total' not in st.session_state:
        st.session_state.sugar_month_total = 0
        
    # history record
    if 'history' not in st.session_state:
        st.session_state.history = []
        
    # language setting
    if 'lang' not in st.session_state:
        st.session_state.lang = "English"

    # --- intro pop up ---
    if 'intro_shown' not in st.session_state:
        st.session_state.intro_shown = False
        
    # --- jamAi analyze  temporary storage ---
    if 'analyzed_data' not in st.session_state:
        st.session_state.analyzed_data = None

def add_intake(sugar, fat, name):
    """add intake"""
    st.session_state.sugar_today += sugar
    st.session_state.fat_today += fat
    st.session_state.sugar_month_total += sugar
    
    # Generate unique ID based on time
    item_id = time.time()
    st.session_state.history.append({
        'id': item_id,
        'name': name,
        'sugar': sugar,
        'fat': fat
    })

def delete_intake(item_id):
    """delete intake"""
    for i, item in enumerate(st.session_state.history):
        if item['id'] == item_id:
            # deduction value
            st.session_state.sugar_today -= item['sugar']
            st.session_state.fat_today -= item.get('fat', 0) # Handle old records without fat
            st.session_state.sugar_month_total -= item['sugar']
            
            # delete  list
            st.session_state.history.pop(i)
            break