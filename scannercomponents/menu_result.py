import streamlit as st
from scannercomponents.nutrigrade import get_nutrigrade_html

def show_menu_result(menu_items, on_add_multiple_callback=None):
    """
    Displays the list of items found in a menu.
    """
    
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
        st.write("### Select Items")
    with c_legend:
        # The Legend Logic (Aligned Right)
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; gap: 16px; font-size: 11px; color: #475569; padding-top: 10px; align-items: center;">
            <div style="display: flex; align-items: center;">
                {sugar_icon_html} Sugar
            </div>
            <div style="display: flex; align-items: center;">
                {fat_icon_html} Sat. Fat
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
                is_selected = st.checkbox("Select", key=f"menu_item_{idx}", label_visibility="hidden")
                if is_selected:
                    selected_indices.append(idx)
            
            with c2:
                st.markdown(get_nutrigrade_html(item['grade'], 'sm'), unsafe_allow_html=True)
            
            with c3:
                # List Item Details
                st.markdown(f"""
<div style="font-weight: 600; font-size: 16px; color: #1E293B; margin-bottom: 6px;">{item['name']}</div>
<div style="display: flex; gap: 20px; font-size: 13px; color: #64748B;">
<div style="display: flex; align-items: center;">{sugar_icon_html} <span style="font-weight: 600; color: #334155;">{item['sugar_g']}g</span></div>
<div style="display: flex; align-items: center;">{fat_icon_html} <span style="font-weight: 600; color: #334155;">{item['fat_g']}g</span></div>
</div>
""", unsafe_allow_html=True)
            
            st.divider()

    total_sugar = sum([sorted_items[i]['sugar_g'] for i in selected_indices])
    total_fat = sum([sorted_items[i]['fat_g'] for i in selected_indices])
    count = len(selected_indices)

    st.write("")
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("Clear / Reset", use_container_width=True):
            st.session_state['selected_menu_indices'] = []
            st.rerun()

    with col_b:
        if count > 0:
            if st.button(f"Add {count} Items to Log", type="primary", use_container_width=True):
                if on_add_multiple_callback:
                    on_add_multiple_callback(total_sugar, total_fat)
                else:
                    st.success(f"Added {total_sugar}g Sugar and {total_fat}g Fat.")