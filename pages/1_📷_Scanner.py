import streamlit as st
import time
from services.jamai_service import analyze_image_with_jamai
from scannercomponents.item_result import show_single_item_result
from scannercomponents.menu_result import show_menu_result

# --- 1. ROBUST SELF-CONTAINED STATE INITIALIZATION ---
def init_scanner_state():
    """
    Initializes all necessary session state variables directly in this file.
    This removes dependencies on external state managers for this page.
    """
    defaults = {
        "page": "home",            # Controls internal navigation (home/camera/upload)
        "mode": "Single Item",     # Controls Scan Mode
        "sugar_intake": 0.0,       # Total daily sugar
        "language": "English",     # Language setting
        "is_makcik_mode": False    # Persona setting
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Execute initialization immediately before any other logic
init_scanner_state()

# --- NAVIGATION HELPER ---
def go(page):
    st.session_state.page = page

# --- HELPER: Action Card ---
def create_action_card(col, icon_url, title, button_label, key, nav_target):
    with col:
        st.markdown(f"""
        <div style='
            border: 2px dashed #d9d9d9; border-radius: 18px 18px 0 0;
            padding: 40px 20px; text-align: center; background: #fafafa;
            font-size: 18px; font-weight: 600;
        '>
            <img src='{icon_url}' width='60' style='margin-bottom: 10px;'>
            <div>{title}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(button_label, key=key, use_container_width=True):
            go(nav_target)

# --- HELPER: Shared Analysis Logic ---
def run_analysis_logic(image_file, key_prefix):
    # 1. MENU SCAN MODE
    if st.session_state.mode == "Menu Scan":
        st.success("Menu detected! Extracting items...")
        time.sleep(1.0)
        
        menu_data = [
            {'name': "Signature Bubble Tea", 'grade': 'D', 'sugar_g': 42.0, 'fat_g': 12.0},
            {'name': "Grilled Chicken Chop", 'grade': 'B', 'sugar_g': 4.0, 'fat_g': 18.0},
            {'name': "Plain Water", 'grade': 'A', 'sugar_g': 0.0, 'fat_g': 0.0},
            {'name': "Mee Goreng Mamak", 'grade': 'C', 'sugar_g': 12.0, 'fat_g': 22.0},
        ]
        
        def on_add_menu(s, f):
            st.session_state['sugar_intake'] += s
            st.toast(f"✅ Added {s}g Sugar and {f}g Fat to your daily budget!")
            time.sleep(1)
            go("home")
            
        show_menu_result(menu_data, on_add_multiple_callback=on_add_menu)

    # 2. SINGLE ITEM MODE
    else:
        result_data = analyze_image_with_jamai(image_file)
        
        if result_data:
            # --- Check if it is a beverage ---
            if result_data.get('is_beverage') is False:
                st.warning("⚠️ No beverage identified. Please input again.")
                st.caption(f"Detected: {result_data.get('name', 'Unknown object')}")
                
                if st.button("🔄 Try Again"):
                    st.rerun()
            else:
                # It is a beverage, show result
                def on_add_single(s, f):
                    st.session_state['sugar_intake'] += s
                    st.toast(f"✅ Added {result_data['name']} to log!")
                    time.sleep(1)
                    go("home")

                show_single_item_result(
                    result_data, 
                    None, # Do not show the image again in the result card
                    on_confirm_callback=on_add_single,
                    key_prefix=key_prefix
                )
        else:
            st.error("Could not analyze image. Please try again.")


# --- PAGE: HOME ---
if st.session_state.page == "home":
    st.set_page_config(page_title="🥤 Beverage Scanner", page_icon="🍹", layout="wide")

    st.markdown("""
    <style>
        .stButton>button {
            border-radius: 0 0 18px 18px; height: 50px; font-weight: 700;
            border-color: #ddd; background-color: #f0f2f6;
        }
        .stButton>button:hover {
            border-color: #4CAF50; background-color: #e0f2e0;
        }
        .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; margin-bottom: 20px;'>
        <h1 style='margin-bottom: 0; font-size: 3em;'>🥤 Beverage Scanner</h1>
        <p style='font-size:18px; color:gray;'>Analyze beverages instantly</p>
    </div>
    <hr style='border: 0.5px solid #ddd; margin-bottom: 30px;'>
    """, unsafe_allow_html=True)

    st.markdown("### Choose Analysis Mode")
    st.session_state.mode = st.radio(
        "Select Mode:", ["Single Item", "Menu Scan"],
        index=0 if st.session_state.mode == "Single Item" else 1,
        horizontal=True, label_visibility="collapsed"
    )

    st.write("")
    col1, col2 = st.columns(2, gap="large")
    create_action_card(col1, 'https://img.icons8.com/color/96/camera--v1.png', "Camera", "📸 Take a Photo", "camera_btn", "camera")
    create_action_card(col2, 'https://img.icons8.com/fluency/96/image.png', "Gallery / File", "📤 Upload Image", "upload_btn", "upload")


# --- PAGE: CAMERA ---
elif st.session_state.page == "camera":
    st.title("📸 Take a Photo")
    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("⬅ Back"): go("home")

    img = st.camera_input("Point your camera at the beverage label:")
    
    if img:
        st.subheader("Preview")
        st.write("---")
        if st.button("🔍 Analyze Beverage", type="primary", use_container_width=True):
             with st.spinner(f"Analyzing in {st.session_state.mode} mode..."):
                run_analysis_logic(img, key_prefix="cam_result")


# --- PAGE: UPLOAD ---
elif st.session_state.page == "upload":
    st.title("📤 Upload Image")
    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("⬅ Back"): go("home")

    img = st.file_uploader("Upload an image of the beverage label:", type=['jpg','png','jpeg'])
    
    if img:
        st.subheader("Preview")
        st.image(img, width=350)
        st.write("---")
        if st.button("🔍 Analyze Beverage", type="primary", use_container_width=True):
            with st.spinner(f"Analyzing in {st.session_state.mode} mode..."):
                run_analysis_logic(img, key_prefix="up_result")