import streamlit as st

def display_sugarcube_visual(grams):
    """
    Displays the Sugar Cube visualization component.
    Accurate to 1/4 of a cube (approx 1g).
    High contrast version.
    """
    CUBE_SIZE = 4.0
    full_cubes = int(grams // CUBE_SIZE)
    remainder = grams % CUBE_SIZE
    
    partial_type = None 
    if remainder < 0.5: pass
    elif remainder < 1.5: partial_type = 'quarter'
    elif remainder < 2.5: partial_type = 'half'
    elif remainder < 3.5: partial_type = 'three_quarter'
    else: full_cubes += 1
    
    # NEW STYLE: High Contrast
    # White background, Dark Slate Border (#475569), Hard Shadow for pop
    base_style = "width: 24px; height: 24px; border: 1px solid #475569; border-radius: 3px; margin: 3px; box-shadow: 2px 2px 0px #CBD5E1;"
    
    full_cube_html = f'<div style="{base_style} background-color: white;"></div>'
    
    # Gradients for partials (White to Transparent/Gray)
    quarter_style = f'{base_style} background: linear-gradient(to right, white 25%, #E2E8F0 25%);'
    half_style = f'{base_style} background: linear-gradient(to right, white 50%, #E2E8F0 50%);'
    three_quarter_style = f'{base_style} background: linear-gradient(to right, white 75%, #E2E8F0 75%);'

    cubes_html = ""
    for _ in range(full_cubes):
        cubes_html += full_cube_html
        
    if partial_type == 'quarter': cubes_html += f'<div style="{quarter_style}" title="~1g"></div>'
    elif partial_type == 'half': cubes_html += f'<div style="{half_style}" title="~2g"></div>'
    elif partial_type == 'three_quarter': cubes_html += f'<div style="{three_quarter_style}" title="~3g"></div>'
    
    if full_cubes == 0 and partial_type is None:
        cubes_html = '<span style="color: #64748B; font-size: 14px; font-style: italic;">No significant sugar detected.</span>'

    total_cubes_display = full_cubes
    if partial_type == 'quarter': total_cubes_display += 0.25
    if partial_type == 'half': total_cubes_display += 0.5
    if partial_type == 'three_quarter': total_cubes_display += 0.75

    st.markdown(f"""
<div style="background-color: #F1F5F9; padding: 16px; border-radius: 12px; border: 1px solid #CBD5E1; margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <h3 style="color: #334155; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 0;">
            SUGAR
        </h3>
        <span style="background-color: #E2E8F0; color: #334155; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">
            1 Cube = 4g
        </span>
    </div>
    <div style="display: flex; flex-wrap: wrap; gap: 4px; align-items: center;">{cubes_html}</div>
    <p style="margin-top: 12px; font-size: 14px; color: #475569; font-weight: 500;">
        <span style="font-size: 18px; font-weight: 700; color: #0F172A;">{grams}g</span> 
        <span style="color: #64748B;">≈ {total_cubes_display} cubes</span>
    </p>
</div>
""", unsafe_allow_html=True)