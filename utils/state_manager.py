import streamlit as st
import uuid
import datetime

def init_session_state():
    """initialized session state variable"""
    defaults = {
        'sugar_today': 0.0,
        'fat_today': 0.0,
        'sugar_month_total': 0.0,
        'history': [],
        'lang': 'English',
        'user_profile': {'age': 25, 'weight': 60, 'height': 170},
       
        'custom_name': '',
        'custom_sugar': 0
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def add_intake(sugar, fat, name):
    """add record"""
    # initialized first if no record
    if 'history' not in st.session_state:
        init_session_state()
        
    # update total
    st.session_state.sugar_today += sugar
    st.session_state.fat_today += fat
    st.session_state.sugar_month_total += sugar
    
    # create new record including id and timing
    new_item = {
        'id': str(uuid.uuid4()),
        'name': name,
        'sugar': sugar,
        'fat': fat,
        'time': datetime.datetime.now().strftime("%H:%M")
    }
    # add to history 
    st.session_state.history.append(new_item)

def delete_intake(item_id):
    # find history session to find the match id
    for i, item in enumerate(st.session_state.history):
        if item['id'] == item_id:
            # subtract the value from the total
            st.session_state.sugar_today = max(0, st.session_state.sugar_today - item['sugar'])
            st.session_state.fat_today = max(0, st.session_state.fat_today - item['fat'])
            st.session_state.sugar_month_total = max(0, st.session_state.sugar_month_total - item['sugar'])
            
            # delte this entry from the list
            del st.session_state.history[i]
            return True
    return False