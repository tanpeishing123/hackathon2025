import streamlit as st
from scannercomponents.nutrigrade import get_nutrigrade_html

# --- TRANSLATIONS ---
TRANS = {
    "English": {
        "select_items": "### Choose the drink(s) you want to consume",
        "sugar": "Sugar",
        "sat_fat": "Sat. Fat",
        "select_btn": "Select",
        "serving": "Serving:",
        "per_100ml": "100ml:",
        "btn_clear": "Clear / Reset",
        "btn_add_log": "Consume {} Drink(s)",
        "msg_added": "Added {}g Sugar and {}g Fat.",
        "btn_ask_ai": "✨ **Ask AI**",
        "prompt_template": "I have scanned {names} which grades {grades} respectively give me advice on that",
        "choose_advisor": "Choose your advisor:"
    },
    "Malay": {
        "select_items": "### Pilih minuman yang anda ingin minum",
        "sugar": "Gula",
        "sat_fat": "Lemak Tepu",
        "select_btn": "Pilih",
        "serving": "Hidangan:",
        "per_100ml": "100ml:",
        "btn_clear": "Padam / Tetap Semula",
        "btn_add_log": "Minum {} Minuman",
        "msg_added": "Ditambah {}g Gula dan {}g Lemak.",
        "btn_ask_ai": "✨ **Tanya AI**",
        "prompt_template": "Saya telah mengimbas {names} yang mempunyai gred {grades} masing-masing, berikan nasihat tentang itu",
        "choose_advisor": "Pilih penasihat anda:"
    }
}

def show_menu_result(menu_items, on_add_multiple_callback=None):
    """
    Displays the list of items found in a menu.
    """
    # Get Language
    lang = st.session_state.get('lang', 'English')
    t = TRANS[lang]
    
    # 1. DEFINE ICONS
    
    # Sugar: 3D Cube Style
    # Made distinct from checkbox: Thicker border, solid offset shadow, slightly larger size
    sugar_icon_html = """<span style="display: inline-block; width: 14px; height: 14px; background-color: white; border: 1.5px solid #1E293B; margin-right: 6px; border-radius: 3px; box-shadow: 3px 3px 0px #94A3B8; vertical-align: middle;"></span>"""
    
    # Fat: Yellow Droplet SVG
    # Using the standard upright droplet shape for both Legend and List
    fat_icon_svg = """<svg viewBox="0 0 24 24" fill="#FACC15" stroke="#B45309" stroke-width="2" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 100%; display: block;"><path d="M12 2L7.5 10C5.5 13.5 5.5 18 12 22C18.5 18 18.5 13.5 16.5 10L12 2Z"/></svg>"""
    fat_icon_html = f"""<span style="display: inline-block; width: 14px; height: 14px; margin-right: 6px; vertical-align: middle;">{fat_icon_svg}</span>"""

    # 2. HEADER WITH LEGEND
    c_head, c_legend = st.columns([1, 1])
    with c_head:
        st.write(t['select_items'])
    with c_legend:
        # The Legend Logic (Aligned Right)
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; gap: 16px; font-size: 11px; color: #475569; padding-top: 10px; align-items: center;">
            <div style="display: flex; align-items: center;">
                {sugar_icon_html} {t['sugar']}
            </div>
            <div style="display: flex; align-items: center;">
                {fat_icon_html} {t['sat_fat']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if 'selected_menu_indices' not in st.session_state:
        st.session_state['selected_menu_indices'] = []

    sorted_items = sorted(menu_items, key=lambda x: x['grade'])

    selected_indices = []
    
    for idx, item in enumerate(sorted_items):
        with st.container():
            c1, c2, c3 = st.columns([0.8, 1, 4])
            
            with c1:
                # The actual Checkbox
                is_selected = st.checkbox(t['select_btn'], key=f"menu_item_{idx}", label_visibility="hidden")
                if is_selected:
                    selected_indices.append(idx)
            
            with c2:
                st.markdown(get_nutrigrade_html(item['grade'], 'sm'), unsafe_allow_html=True)
            
            with c3:
                # List Item Details
                st.markdown(f"""
<div style="font-weight: 600; font-size: 16px; color: #1E293B; margin-bottom: 6px;">{item['name']}</div>
<div style="font-size: 12px; color: #64748B;">
    <div style="display: flex; align-items: center; margin-bottom: 4px;">
        <span style="width: 70px; font-weight: 600; color: #475569;">{t['serving']}</span>
        <div style="display: flex; align-items: center; width: 80px;">{sugar_icon_html} <span style="font-weight: 600; color: #334155;">{item['sugar_g']}g</span></div>
        <div style="display: flex; align-items: center;">{fat_icon_html} <span style="font-weight: 600; color: #334155;">{item['fat_g']}g</span></div>
    </div>
    <div style="display: flex; align-items: center;">
        <span style="width: 70px; font-weight: 600; color: #475569;">{t['per_100ml']}</span>
        <div style="display: flex; align-items: center; width: 80px;">{sugar_icon_html} <span style="font-weight: 600; color: #334155;">{item.get('sugar_100g', 0)}g</span></div>
        <div style="display: flex; align-items: center;">{fat_icon_html} <span style="font-weight: 600; color: #334155;">{item.get('fat_100g', 0)}g</span></div>
    </div>
</div>
""", unsafe_allow_html=True)
            
            st.divider()

    total_sugar = sum([sorted_items[i]['sugar_g'] for i in selected_indices])
    total_fat = sum([sorted_items[i]['fat_g'] for i in selected_indices])
    count = len(selected_indices)
    
    # Collect selected items data
    selected_items_data = [sorted_items[i] for i in selected_indices]

    st.write("")
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button(t['btn_clear'], use_container_width=True):
            st.session_state['selected_menu_indices'] = []
            st.rerun()

    with col_b:
        if count > 0:
            if st.button(t['btn_add_log'].format(count), type="primary", use_container_width=True):
                if on_add_multiple_callback:
                    on_add_multiple_callback(selected_items_data)
                else:
                    st.success(t['msg_added'].format(total_sugar, total_fat))

    # --- Ask AI Button ---
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # Special CSS for the AI button (Gradient Purple)
    st.markdown("""
    <span id="menu_ask_ai_marker"></span>
    <style>
    div.element-container:has(span#menu_ask_ai_marker) + div.element-container button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    div.element-container:has(span#menu_ask_ai_marker) + div.element-container button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(124, 58, 237, 0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # State for AI selection visibility
    ask_ai_key = "menu_ask_ai_mode"
    if ask_ai_key not in st.session_state:
        st.session_state[ask_ai_key] = False

    if st.button(t['btn_ask_ai'], use_container_width=True, key="menu_btn_ask_ai"):
        st.session_state[ask_ai_key] = not st.session_state[ask_ai_key]
        st.rerun()

    if st.session_state[ask_ai_key]:
        st.markdown(f"##### {t['choose_advisor']}")
        c1, c2 = st.columns(2)
        
        # Construct prompt
        item_names = [item['name'] for item in sorted_items]
        item_grades = [item['grade'] for item in sorted_items]
        
        names_str = ", ".join(item_names)
        grades_str = ", ".join(item_grades)
        
        prompt = t['prompt_template'].format(names=names_str, grades=grades_str)

        with c1:
            if st.button("👨‍⚕️ Prof. Manis", use_container_width=True, key="menu_ask_prof", type="secondary"):
                st.session_state['selected_agent'] = "👨‍⚕️ Prof. Manis"
                st.session_state['chat_prompt'] = prompt
                st.switch_page("pages/2_💬_Chat.py")
        with c2:
            if st.button("👵 Mak Cik Manis", use_container_width=True, key="menu_ask_makcik", type="secondary"):
                st.session_state['selected_agent'] = "👵 Mak Cik Manis"
                st.session_state['chat_prompt'] = prompt
                st.switch_page("pages/2_💬_Chat.py")