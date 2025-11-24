import streamlit as st
from services.jamai_service import analyze_image_with_jamai

st.title("📷 Scan Food")

# 1. Image Input
img_file = st.file_uploader("Upload Food", type=['jpg', 'png', 'jpeg'])
camera_input = st.camera_input("Or take a photo")

target_image = img_file or camera_input

if target_image:
    st.image(target_image, caption="Preview", width=300)
    
    # 2. The "Call JamAI" Button
    if st.button("Analyze with JamAI"):
        with st.spinner("Sending to JamAI Base..."):
            
            # CALL THE SERVICE
            result = analyze_image_with_jamai(target_image)
            
            # DISPLAY RESULTS
            st.success(f"Found: {result['food_name']}")
            st.metric("Sugar Content", f"{result['sugar_g']}g")
            
            # UPDATE DASHBOARD
            if st.button("Add to Daily Log"):
                st.session_state['sugar_intake'] += result['sugar_g']
                st.success("Added! Check Home Page.")