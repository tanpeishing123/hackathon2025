import streamlit as st

def display_fat_visual(grams):
    """
    Displays the Saturated Fat visualization (Oil Droplets).
    1 Droplet (Teaspoon) approx 5g.
    """
    TEASPOON_SIZE = 5.0 # 5g per tsp
    full_drops = int(grams // TEASPOON_SIZE)
    remainder = grams % TEASPOON_SIZE
    
    partial_type = None
    # Thresholds for 5g unit:
    # < 0.8g: Ignore
    # 0.8g - 2.0g: Quarter (~1.25g)
    # 2.0g - 3.2g: Half (~2.5g)
    # 3.2g - 4.2g: Three Quarter (~3.75g)
    # > 4.2g: Full
    
    if remainder < 0.8: pass
    elif remainder < 2.0: partial_type = 'quarter'
    elif remainder < 3.2: partial_type = 'half'
    elif remainder < 4.2: partial_type = 'three_quarter'
    else: full_drops += 1
    
    path = "M12 2L7.5 10C5.5 13.5 5.5 18 12 22C18.5 18 18.5 13.5 16.5 10L12 2Z"
    
    # Flattened HTML string (No indentation)
    drop_html_template = """<div style="width: 24px; height: 24px; margin: 2px; filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.1));"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="{path}" fill="{fill}" stroke="#B45309" stroke-width="1.5"/></svg></div>"""
    
    drops_html = ""
    for _ in range(full_drops):
        drops_html += drop_html_template.format(path=path, fill="#FACC15")
        
    # Templates for partial fills using Linear Gradients
    # The 'bg_color' is #FEFCE8 (the container background) to make the empty part look transparent relative to the container
    
    if partial_type == 'quarter':
        drops_html += f"""<div style="width: 24px; height: 24px; margin: 2px; filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.1));" title="~1.25g"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_fat_25"><stop offset="25%" stop-color="#FACC15"/><stop offset="25%" stop-color="#FEFCE8"/></linearGradient></defs><path d="{path}" fill="url(#grad_fat_25)" stroke="#B45309" stroke-width="1.5"/></svg></div>"""
    elif partial_type == 'half':
        drops_html += f"""<div style="width: 24px; height: 24px; margin: 2px; filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.1));" title="~2.5g"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_fat_50"><stop offset="50%" stop-color="#FACC15"/><stop offset="50%" stop-color="#FEFCE8"/></linearGradient></defs><path d="{path}" fill="url(#grad_fat_50)" stroke="#B45309" stroke-width="1.5"/></svg></div>"""
    elif partial_type == 'three_quarter':
        drops_html += f"""<div style="width: 24px; height: 24px; margin: 2px; filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.1));" title="~3.75g"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_fat_75"><stop offset="75%" stop-color="#FACC15"/><stop offset="75%" stop-color="#FEFCE8"/></linearGradient></defs><path d="{path}" fill="url(#grad_fat_75)" stroke="#B45309" stroke-width="1.5"/></svg></div>"""

    if full_drops == 0 and partial_type is None:
        drops_html = '<span style="color: #94A3B8; font-size: 14px; font-style: italic;">Low fat content.</span>'

    total_tsp_display = full_drops
    if partial_type == 'quarter': total_tsp_display += 0.25
    if partial_type == 'half': total_tsp_display += 0.5
    if partial_type == 'three_quarter': total_tsp_display += 0.75

    # Flattened container HTML
    st.markdown(f"""
<div style="background-color: #FEFCE8; padding: 16px; border-radius: 12px; border: 1px solid #FEF08A; margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<h3 style="color: #854D0E; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 0;">SATURATED FAT</h3>
<span style="background-color: #FFF9C4; color: #854D0E; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">1 Tsp = 5g</span>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 4px; align-items: center;">{drops_html}</div>
<p style="margin-top: 12px; font-size: 14px; color: #713F12; font-weight: 500;">
<span style="font-size: 18px; font-weight: 700; color: #422006;">{grams}g</span> 
<span style="color: #A16207;">≈ {total_tsp_display} tsp oil</span>
</p>
</div>
""", unsafe_allow_html=True)