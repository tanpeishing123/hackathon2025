import streamlit as st

def get_nutrigrade_html(grade, size='md'):
    """
    Returns HTML string for the NutriGrade Badge.
    """
    grade = str(grade).upper()
    
    colors = {
        'A': 'background-color: #10B981; color: white;',
        'B': 'background-color: #A3E635; color: black;',
        'C': 'background-color: #FACC15; color: black;',
        'D': 'background-color: #EF4444; color: white;',
    }
    
    style = colors.get(grade, 'background-color: #E5E7EB; color: #1F2937;')
    
    sizes = {
        'sm': 'width: 32px; height: 32px; font-size: 14px;',
        'md': 'width: 48px; height: 48px; font-size: 20px;',
        'lg': 'width: 80px; height: 80px; font-size: 36px;',
    }
    current_size = sizes.get(size, sizes['md'])

    html = f"""
<div style="{style} {current_size} border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border: 2px solid rgba(255,255,255,0.2);">
    {grade}
</div>
"""
    return html

def display_nutrigrade(grade, size='md'):
    st.markdown(get_nutrigrade_html(grade, size), unsafe_allow_html=True)