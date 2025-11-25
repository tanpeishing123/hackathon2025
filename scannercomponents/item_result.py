import streamlit as st
from scannercomponents.nutrigrade import get_nutrigrade_html
from scannercomponents.sugarcube import display_sugarcube_visual
from scannercomponents.fatvisual import display_fat_visual

def show_single_item_result(data, image_file, on_confirm_callback=None, key_prefix="item"):
    """
    Displays the full Result Card for a single scanned item.
    """
    if image_file:
        st.image(image_file, use_container_width=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {data['name']}")
        st.caption("Analyzed Content")
    with col2:
        st.markdown(get_nutrigrade_html(data['grade'], 'md'), unsafe_allow_html=True)

    # Comment Box
    st.markdown(f"""
<div style="background-color: #FEFCE8; color: #854D0E; padding: 12px; border-radius: 8px; border-left: 4px solid #FACC15; font-style: italic; font-size: 14px; margin-bottom: 16px;">
"{data['comment']}"
</div>
""", unsafe_allow_html=True)

    # VISUALIZERS
    display_sugarcube_visual(data['sugar_g'])
    display_fat_visual(data['fat_g'])

    st.write("") 

    # Buttons
    if st.button("🥤 Drink/Eat Anyway (Add to Log)", type="primary", use_container_width=True, key=f"{key_prefix}_btn_add"):
        if on_confirm_callback:
            on_confirm_callback(data['sugar_g'], data['fat_g'])
        else:
            st.success(f"Added {data['name']} to your daily log!")

    if st.button("🔍 Find Healthier Alternative", use_container_width=True, key=f"{key_prefix}_btn_alt"):
        st.info("Feature coming soon: Switch to Grade A/B Option")