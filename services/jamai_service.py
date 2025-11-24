import streamlit as st
# import requests # You will need this later to send data to JamAI

def analyze_image_with_jamai(uploaded_file):
    """
    TODO: Integrate JamAI Base API here.
    1. Convert 'uploaded_file' to Base64.
    2. Send POST request to your JamAI Project URL.
    3. Return the JSON response.
    """
    
    # --- MOCK RESPONSE (For now, so Teammate A can work) ---
    # Imagine JamAI analyzed the image and sent this back:
    return {
        "food_name": "Sirap Bandung (Detected)",
        "sugar_g": 32,
        "risk_level": "High"
    }

def chat_with_jamai(user_text):
    """
    TODO: Send text to JamAI Chat Table.
    """
    return "This is a dummy response from JamAI service."