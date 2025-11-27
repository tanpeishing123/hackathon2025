import streamlit as st
import os
from scannercomponents.nutrigrade import get_nutrigrade_html
from scannercomponents.sugarcube import display_sugarcube_visual
from scannercomponents.fatvisual import display_fat_visual

# --- TRANSLATIONS ---
TRANS = {
    "English": {
        "analyzed_content": "Analyzed Content",
        "nutrition_info": "Nutrition Info",
        "per_serving": "PER SERVING",
        "per_100ml": "PER 100ML",
        "btn_drink_anyway": "🥤 Drink anyway",
        "msg_added": "Added {} to your daily log!",
        "btn_find_alt": "🔍 Find Healthier Alternative",
        "alt_title": "**Healthier Alternative:**",
        "alt_none": "No alternative found.",
        "btn_ask_ai": "✨ **Ask AI**",
        "prompt_template": "I just search {name}, which is a grade {grade} drink with {sugar} g sugar and {fat}g sat fat per 100ml. give me advice about that",
        "choose_advisor": "Choose your advisor:"
    },
    "Malay": {
        "analyzed_content": "Kandungan Dianalisis",
        "nutrition_info": "Maklumat Nutrisi",
        "per_serving": "SETIAP HIDANGAN",
        "per_100ml": "SETIAP 100ML",
        "btn_drink_anyway": "🥤 Minum Saja",
        "msg_added": "Ditambah {} ke log harian anda!",
        "btn_find_alt": "🔍 Cari Alternatif Lebih Sihat",
        "alt_title": "**Alternatif Lebih Sihat:**",
        "alt_none": "Tiada alternatif dijumpai.",
        "btn_ask_ai": "✨ **Tanya AI**",
        "prompt_template": "Saya baru cari {name}, iaitu minuman gred {grade} dengan {sugar} g gula dan {fat}g lemak tepu setiap 100ml. berikan nasihat tentang itu",
        "choose_advisor": "Pilih penasihat anda:"
    }
}

def show_single_item_result(data, image_file, on_confirm_callback=None, key_prefix="item"):
    """
    Displays the full Result Card for a single scanned item.
    """
    # Get Language
    lang = st.session_state.get('lang', 'English')
    t = TRANS[lang]

    if image_file:
        st.image(image_file, use_container_width=True)

    st.markdown(f"### {data['name']}")
    
    # Display Nutri-Grade Image
    grade = data.get('grade', 'C').upper()
    # Ensure grade is valid for filename
    if grade not in ['A', 'B', 'C', 'D']:
        grade = 'C' 
        
    image_path = f"scannercomponents/png/{grade}.jpg"
    
    if os.path.exists(image_path):
        st.image(image_path, width=250)
    else:
        # Fallback to HTML if image missing
        st.markdown(get_nutrigrade_html(grade, 'md'), unsafe_allow_html=True)

    st.caption(t['analyzed_content'])

    # Comment Box
    st.markdown(f"""
<div style="background-color: #FEFCE8; color: #854D0E; padding: 12px; border-radius: 8px; border-left: 4px solid #FACC15; font-style: italic; font-size: 14px; margin-bottom: 16px;">
"{data['comment']}"
</div>
""", unsafe_allow_html=True)

    # VISUALIZERS
    st.markdown(f"#### {t['nutrition_info']}")
    
    v_col1, v_col2 = st.columns(2, gap="medium")
    
    with v_col1:
        serving_label = data.get('serving_text', '')
        st.markdown(f"""
        <div style="background-color: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; height: 100%;">
            <div style='text-align: center; font-weight: bold; margin-bottom: 15px; color: #334155; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;'>{t['per_serving']} {serving_label}</div>
        """, unsafe_allow_html=True)
        
        display_sugarcube_visual(data['sugar_g'])
        display_fat_visual(data['fat_g'])
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with v_col2:
        st.markdown(f"""
        <div style="background-color: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; height: 100%;">
            <div style='text-align: center; font-weight: bold; margin-bottom: 15px; color: #334155; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;'>{t['per_100ml']}</div>
        """, unsafe_allow_html=True)
        
        # Use .get() with default 0 in case keys are missing for some reason
        display_sugarcube_visual(data.get('sugar_100g', 0))
        display_fat_visual(data.get('fat_100g', 0))
        
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("") 

    # State for alternative button
    alt_key = f"{key_prefix}_show_alt"
    if alt_key not in st.session_state:
        st.session_state[alt_key] = False

    # State for added button
    added_key = f"{key_prefix}_added"
    if added_key not in st.session_state:
        st.session_state[added_key] = False

    # Buttons
    # Disable "Drink Anyway" if Alternative is shown OR if already added
    add_disabled = st.session_state[alt_key] or st.session_state[added_key]
    
    # Disable "Find Alternative" if "Drink Anyway" was pressed
    alt_disabled = st.session_state[added_key]
    
    if st.button(t['btn_drink_anyway'], type="primary", use_container_width=True, key=f"{key_prefix}_btn_add", disabled=add_disabled):
        st.session_state[added_key] = True # Mark as added
        if on_confirm_callback:
            on_confirm_callback(data['sugar_g'], data['fat_g'])
        else:
            st.success(t['msg_added'].format(data['name']))
        st.rerun()

    if st.button(t['btn_find_alt'], use_container_width=True, key=f"{key_prefix}_btn_alt", disabled=alt_disabled):
        st.session_state[alt_key] = True
        st.rerun()
        
    if st.session_state[alt_key]:
        st.info(f"{t['alt_title']}\n\n{data.get('alternative', t['alt_none'])}")

    # New Button: Ask AI
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    
    # Special CSS for the AI button (Gradient Purple) - Targeted specifically using :has()
    st.markdown("""
    <span id="ask_ai_marker"></span>
    <style>
    /* Target the container holding the marker, then the next container, then the button */
    div.element-container:has(span#ask_ai_marker) + div.element-container button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    div.element-container:has(span#ask_ai_marker) + div.element-container button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(124, 58, 237, 0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # State for AI selection visibility
    ask_ai_key = f"{key_prefix}_ask_ai_mode"
    if ask_ai_key not in st.session_state:
        st.session_state[ask_ai_key] = False

    if st.button(t['btn_ask_ai'], use_container_width=True, key=f"{key_prefix}_btn_ask_ai"):
        st.session_state[ask_ai_key] = not st.session_state[ask_ai_key]
        st.rerun()

    if st.session_state[ask_ai_key]:
        st.markdown(f"##### {t['choose_advisor']}")
        c1, c2 = st.columns(2)
        
        prompt = t['prompt_template'].format(
            name=data['name'],
            grade=data.get('grade', 'C'),
            sugar=data.get('sugar_100g', 0),
            fat=data.get('fat_100g', 0)
        )

        with c1:
            if st.button("👨‍⚕️ Prof. Manis", use_container_width=True, key=f"{key_prefix}_ask_prof"):
                st.session_state['selected_agent'] = "👨‍⚕️ Prof. Manis"
                st.session_state['chat_prompt'] = prompt
                st.switch_page("pages/2_💬_Chat.py")
        with c2:
            if st.button("👵 Mak Cik Manis", use_container_width=True, key=f"{key_prefix}_ask_makcik"):
                st.session_state['selected_agent'] = "👵 Mak Cik Manis"
                st.session_state['chat_prompt'] = prompt
                st.switch_page("pages/2_💬_Chat.py")