import streamlit as st
from services.jamai_service import analyze_image_with_jamai

# Initialize state
if "page" not in st.session_state:
    st.session_state.page = "home"
if "mode" not in st.session_state:
    st.session_state.mode = "Nutrition Facts"

def go(page):
    """Sets the session state page for navigation."""
    st.session_state.page = page

# --- Helper function to create a visually distinct clickable card ---
def create_action_card(col, icon_url, title, button_label, key, nav_target):
    """Generates a styled card and an integrated button within a column."""
    with col:
        # Visual Card (Markdown/HTML)
        st.markdown(f"""
        <div style='
            border: 2px dashed #d9d9d9;
            border-radius: 18px 18px 0 0;
            padding: 40px 20px;
            text-align: center;
            background: #fafafa;
            font-size: 18px;
            font-weight: 600;
        '>
            <img src='{icon_url}' width='60' style='margin-bottom: 10px;'>
            <div>{title}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Functional Button (Integrated using use_container_width)
        # Using a distinct color to integrate into the card base.
        if st.button(button_label, key=key, use_container_width=True):
            go(nav_target)

# --- Streamlit Application Pages ---

# Home Page (Refactored Layout)
if st.session_state.page == "home":
    st.set_page_config(page_title="🥤 Beverage Scanner", page_icon="🍹", layout="wide")

    # Inject custom CSS for better visual resemblance (e.g., button integration)
    st.markdown("""
    <style>
        /* Target Streamlit button to make it look like a continuation of the card */
        .stButton>button {
            border-radius: 0 0 18px 18px;
            height: 50px;
            font-weight: 700;
            border-color: #ddd;
            background-color: #f0f2f6; /* Light gray background for integration */
        }
        .stButton>button:hover {
            border-color: #4CAF50;
            background-color: #e0f2e0; /* Subtle hover effect */
        }
        /* Style for the main container to match the centered feeling of the image */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div style='text-align:center; margin-bottom: 20px;'>
        <h1 style='margin-bottom: 0; font-size: 3em;'>🥤 Beverage Scanner</h1>
        <p style='font-size:18px; color:gray;'>Analyze beverages instantly</p>
    </div>
    <hr style='border: 0.5px solid #ddd; margin-bottom: 30px;'>
    """, unsafe_allow_html=True)

    # Mode Selector
    st.markdown("### Choose Analysis Mode")
    st.session_state.mode = st.radio(
        "Select Mode:",
        ["Nutrition Facts", "Common Prediction"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

    st.write("")

    # Columns for action cards
    col1, col2 = st.columns(2, gap="large")

    # 1. Camera Card
    create_action_card(
        col1,
        'https://img.icons8.com/color/96/camera--v1.png',
        "Camera",
        "📸 Take a Photo",
        "camera_btn",
        "camera"
    )

    # 2. Upload Card (renamed to match the visual)
    create_action_card(
        col2,
        'https://img.icons8.com/fluency/96/image.png',
        "Gallery / File",
        "📤 Upload Image",
        "upload_btn",
        "upload"
    )

    # Simple footer simulation (based on the image's bottom navigation)
    st.markdown("""
    <div style='position: fixed; bottom: 0; left: 0; right: 0; background-color: #f7f7f7; border-top: 1px solid #ddd; padding: 10px 0; text-align: center; display: flex; justify-content: space-around; font-size: 12px; color: #555;'>
        <div>🏠 Home</div>
        <div>🔍 Scan (Current)</div>
        <div>💬 AI Chat</div>
        <div>⚙️ Settings</div>
    </div>
    """, unsafe_allow_html=True)


# Camera Page
elif st.session_state.page == "camera":
    st.title("📸 Take a Photo")
    img = st.camera_input("Point your camera at the beverage label:")
    
    col_back, col_analyze = st.columns([1, 2])
    
    with col_back:
        if st.button("⬅ Back"):
            go("home")

    if img:
        st.subheader("Preview")
        st.image(img, width=350)
        
        with col_analyze:
            if st.button("🔍 Analyze Beverage", type="primary"):
                # Ensure img is processed only when the button is pressed
                with st.spinner(f"Analyzing in {st.session_state.mode} mode..."):
                    # The function call is maintained as per the original structure
                    analyze_image_with_jamai(img, mode=st.session_state.mode)
            
# Upload Page
elif st.session_state.page == "upload":
    st.title("📤 Upload Image")
    img = st.file_uploader("Upload an image of the beverage label:", type=['jpg','png','jpeg'])
    
    col_back, col_analyze = st.columns([1, 2])
    
    with col_back:
        if st.button("⬅ Back"):
            go("home")

    if img:
        st.subheader("Preview")
        st.image(img, width=350)
        
        with col_analyze:
            if st.button("🔍 Analyze Beverage", type="primary"):
                # Ensure img is processed only when the button is pressed
                with st.spinner(f"Analyzing in {st.session_state.mode} mode..."):
                    # The function call is maintained as per the original structure
                    analyze_image_with_jamai(img, mode=st.session_state.mode)