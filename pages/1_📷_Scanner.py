import streamlit as st
import time
import services.jamai_service as jamai_service
from scannercomponents.item_result import show_single_item_result
from scannercomponents.menu_result import show_menu_result
from utils.state_manager import add_intake, init_session_state

# --- TRANSLATIONS ---
TRANS = {
    "English": {
        "page_title": "🥤 Beverage Scanner",
        "subtitle": "Analyze beverages instantly",
        "tab_label": "Nutrition Label",
        "tab_fresh": "Fresh Drinks",
        "tab_menu": "Menu Scan",
        "card_cam_title": "Camera",
        "card_cam_btn": "📸 Take a Photo",
        "card_up_title": "Gallery / File",
        "card_up_btn": "📤 Upload Image",
        "lazy_title": "##### Lazy to take photo? Just type your drink below.",
        "input_ph": "e.g. Teh C Peng",
        "input_label": "Drink Name",
        "slider_label": "Sugar Level (%)",
        "btn_analyze_add": "🔍 Analyze drink",
        "btn_analyze_bev": "🔍 Analyze Beverage",
        "spinner_ask": "Asking JamAI...",
        "spinner_analyze": "Analyzing in {} mode...",
        "back": "⬅ Back",
        "preview": "Preview",
        "adjust_sweet": "#### Adjust Sweetness",
        "selected": "Selected",
        
        # Context Titles
        "title_label": "📸 Scan Nutrition Label",
        "instr_label": "Point camera at the nutrition facts table.",
        "title_fresh": "📸 Snap a Drink",
        "instr_fresh": "Point camera at the drink (e.g. Teh Tarik, Kopi).",
        "title_menu": "📸 Capture Menu",
        "instr_menu": "Point camera at the menu to extract items.",
        
        "up_title_label": "📤 Upload Label Image",
        "up_instr_label": "Upload a clear image of the nutrition facts.",
        "up_title_fresh": "📤 Upload Drink Photo",
        "up_instr_fresh": "Upload a photo of the drink.",
        "up_title_menu": "📤 Upload Menu Image",
        "up_instr_menu": "Upload a photo of the menu.",
        
        # Sugar Labels
        "s_no": "⚪ No Sugar (0%)",
        "s_less25": "🟢 Less Sugar (25%)",
        "s_less50": "🟡 Less Sugar (50%)",
        "s_less75": "🟠 Less Sugar (75%)",
        "s_std": "🔴 Standard (100%)",
        "s_extra": "🟣 Extra Sugar ({}%)",
        "msg_added_menu": "✅ Added {} items to daily log.",
        "msg_added_single": "✅ Added {} to daily log."
    },
    "Malay": {
        "page_title": "🥤 Pengimbas Minuman",
        "subtitle": "Analisis minuman serta-merta",
        "tab_label": "Label Nutrisi",
        "tab_fresh": "Minuman Segar",
        "tab_menu": "Imbas Menu",
        "card_cam_title": "Kamera",
        "card_cam_btn": "📸 Ambil Gambar",
        "card_up_title": "Galeri / Fail",
        "card_up_btn": "📤 Muat Naik Imej",
        "lazy_title": "##### Malas ambil gambar? Taip nama minuman di bawah.",
        "input_ph": "cth. Teh C Peng",
        "input_label": "Nama Minuman",
        "slider_label": "Tahap Gula (%)",
        "btn_analyze_add": "🔍 Analisis Minuman",
        "btn_analyze_bev": "🔍 Analisis Minuman",
        "spinner_ask": "Bertanya JamAI...",
        "spinner_analyze": "Menganalisis dalam mod {}...",
        "back": "⬅ Kembali",
        "preview": "Pratonton",
        "adjust_sweet": "#### Tetapkan Kemanisan",
        "selected": "Pilihan",
        
        # Context Titles
        "title_label": "📸 Imbas Label Nutrisi",
        "instr_label": "Halakan kamera ke jadual fakta nutrisi.",
        "title_fresh": "📸 Tangkap Gambar Minuman",
        "instr_fresh": "Halakan kamera ke minuman (cth. Teh Tarik, Kopi).",
        "title_menu": "📸 Tangkap Menu",
        "instr_menu": "Halakan kamera ke menu untuk ekstrak item.",
        
        "up_title_label": "📤 Muat Naik Imej Label",
        "up_instr_label": "Muat naik imej fakta nutrisi yang jelas.",
        "up_title_fresh": "📤 Muat Naik Foto Minuman",
        "up_instr_fresh": "Muat naik foto minuman.",
        "up_title_menu": "📤 Muat Naik Imej Menu",
        "up_instr_menu": "Muat naik foto menu.",
        
        # Sugar Labels
        "s_no": "⚪ Tiada Gula (0%)",
        "s_less25": "🟢 Kurang Manis (25%)",
        "s_less50": "🟡 Kurang Manis (50%)",
        "s_less75": "🟠 Kurang Manis (75%)",
        "s_std": "🔴 Biasa (100%)",
        "s_extra": "🟣 Lebih Manis ({}%)",
        "msg_added_menu": "✅ Ditambah {} item ke log harian.",
        "msg_added_single": "✅ Ditambah {} ke log harian."
    }
}

# --- GLOBAL CSS (Applies to all pages in Scanner) ---
st.markdown("""
<style>
/* UNIFIED BUTTON COLORS (Teal #0d9488) */
.stButton > button {
    background-color: #0d9488 !important; 
    color: white !important; 
    border: none !important; 
    border-radius: 8px !important; 
    font-weight: 600 !important; 
    width: 100% !important;
}

/* Secondary Button Override (for unselected tabs) */
button[kind="secondary"] {
    background-color: #e2e8f0 !important; /* Darker grey */
    color: #475569 !important; /* Darker text */
    border: 1px solid #cbd5e1 !important;
}

/* Hover state for secondary buttons */
button[kind="secondary"]:hover {
    background-color: #cbd5e1 !important;
    color: #1e293b !important;
    border-color: #94a3b8 !important;
}
</style>
""", unsafe_allow_html=True)

# --- 1. ROBUST SELF-CONTAINED STATE INITIALIZATION ---
def init_scanner_state():
    """
    Initializes all necessary session state variables directly in this file.
    This removes dependencies on external state managers for this page.
    """
    # Ensure global state is initialized
    init_session_state()

    defaults = {
        "page": "home",            # Controls internal navigation (home/camera/upload)
        "mode": "Nutrition Label", # Controls Scan Mode
        # "language": "English",     # Language setting (Managed globally now)
        "is_makcik_mode": False,   # Persona setting
        "scan_results": None       # Store analysis results
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # --- RESET LOGIC: If coming from another page, reset to home ---
    if st.session_state.get('last_page') != 'Scanner':
        st.session_state.page = 'home'
        st.session_state.scan_results = None
    
    # Mark current page as Scanner
    st.session_state['last_page'] = 'Scanner'

# Execute initialization immediately before any other logic
init_scanner_state()

# Dismiss intro from Home page if user visits Scanner
if 'intro_shown' in st.session_state:
    st.session_state.intro_shown = True

# Get Language
lang = st.session_state.get('lang', 'English')
t = TRANS[lang]

# --- NAVIGATION HELPER ---
def go(page):
    st.session_state.page = page

def clear_results():
    st.session_state.scan_results = None

def reset_scanner_ui_state():
    """
    Resets the UI state for scanner results (Ask AI, Find Alternative, Added status)
    to ensure a clean slate when switching modes.
    """
    prefixes = ["manual_result", "cam_result", "up_result"]
    suffixes = ["_show_alt", "_ask_ai_mode", "_added"]
    for p in prefixes:
        for s in suffixes:
            key = f"{p}{s}"
            if key in st.session_state:
                del st.session_state[key]

# --- HELPER: Action Card ---
def create_action_card(col, icon_url, title, button_label, key, nav_target):
    with col:
        st.markdown(f"""
        <div class="action-card">
            <img src='{icon_url}' width='60' style='margin-bottom: 10px;'>
            <div>{title}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(button_label, key=key, use_container_width=True):
            go(nav_target)

# --- HELPER: Nutri-Grade Calculation ---
def calculate_nutrigrade(sugar_value, saturatedFat_value):
    """
    Recalculates Nutri-Grade based on sugar and saturated fat per 100ml.
    Logic provided by user.
    """
    initial_grade = ""

    if sugar_value <= 1.0:
        initial_grade = 'A'
    elif 1.0 < sugar_value <= 5.0:
        initial_grade = 'B'
    elif 5.0 < sugar_value <= 10.0:
        initial_grade = 'C'
    elif sugar_value > 10.0:
        initial_grade = 'D'
    else:
        initial_grade = 'D' # Fallback

    if initial_grade == 'D':
         final_grade = 'D'
    else:
        final_grade = initial_grade

        if final_grade == 'A' and saturatedFat_value > 0.7:
            final_grade = 'B'

        if final_grade == 'B' and saturatedFat_value > 1.2:
            final_grade = 'C'

        if final_grade == 'C' and saturatedFat_value > 2.8:
            final_grade = 'D'
            
    return final_grade

# --- HELPER: Shared Analysis Logic ---
def perform_analysis(image_file, multiplier=1.0):
    """
    Performs the analysis and stores the result in session state.
    """
    # Get current language
    lang = st.session_state.get('lang', 'English')

    # 1. MENU SCAN MODE
    if st.session_state.mode == "Menu Scan":
        status_msg = st.empty()
        status_msg.success("Menu detected! Extracting items...")
        
        # Call JamAI Menu Analysis
        result_json = jamai_service.analyze_menu_with_jamai(image_file)
        
        status_msg.empty()
        
        # Handle different JSON keys (menuitems vs menu_items)
        items_list = []
        if result_json:
            items_list = result_json.get("menuitems") or result_json.get("menu_items")

        if items_list:
            menu_data = []
            for item in items_list:
                # Normalize keys to match what show_menu_result expects
                # New JSON structure support
                sugar_serving = float(item.get('sugar_per_serving', item.get('sugarg', item.get('sugar_g', 0))))
                fat_serving = float(item.get('saturated_fat_per_serving', item.get('fatg', item.get('fat_g', 0))))
                
                sugar_100 = float(item.get('sugar_per_100ml', 0))
                fat_100 = float(item.get('saturated_fat_per', 0))

                # Recalculate grade locally
                calculated_grade = calculate_nutrigrade(sugar_100, fat_100)

                menu_data.append({
                    'name': item.get('name', 'Unknown Item'),
                    'grade': calculated_grade,
                    'sugar_g': sugar_serving,
                    'fat_g': fat_serving,
                    'sugar_100g': sugar_100,
                    'fat_100g': fat_100
                })
            
            st.session_state.scan_results = {"type": "menu", "data": menu_data}
        else:
            st.error("Could not analyze menu. Please try again.")
            if result_json:
                st.json(result_json) # Debugging aid
            st.session_state.scan_results = None

    # 2. FRESH DRINKS MODE
    elif st.session_state.mode == "Fresh Drinks":
        result_data = jamai_service.analyze_drink_with_jamai(image_file, multiplier, language=lang)
        
        if result_data:
            # --- Check if it is a beverage ---
            if result_data.get('is_beverage') is False:
                st.session_state.scan_results = {"type": "not_beverage", "data": result_data}
            else:
                st.session_state.scan_results = {"type": "single", "data": result_data}
        else:
            st.error("Could not analyze drink. Please try again.")
            st.session_state.scan_results = None

    # 3. NUTRITION LABEL MODE (Formerly Single Item)
    else:
        result_data = jamai_service.analyze_image_with_jamai(image_file, language=lang)
        
        if result_data:
            # --- Check if it is a beverage ---
            if result_data.get('is_beverage') is False:
                st.session_state.scan_results = {"type": "not_beverage", "data": result_data}
            else:
                st.session_state.scan_results = {"type": "single", "data": result_data}
        else:
            st.error("Could not analyze image. Please try again.")
            st.session_state.scan_results = None

def display_scan_results(key_prefix):
    """
    Displays the results stored in session state.
    """
    if not st.session_state.scan_results:
        return

    result_type = st.session_state.scan_results["type"]
    data = st.session_state.scan_results["data"]

    if result_type == "menu":
        def on_add_menu(items):
            # Update global state via state_manager
            for item in items:
                add_intake(item['sugar_g'], item['fat_g'], item['name'])
            
            # Show success message instead of switching page
            st.success(t['msg_added_menu'].format(len(items)))
            
        show_menu_result(data, on_add_multiple_callback=on_add_menu)

    elif result_type == "not_beverage":
        st.warning("⚠️ No beverage identified. Please input again.")
        st.caption(f"Detected: {data.get('name', 'Unknown object')}")
        
        if st.button("🔄 Try Again", key=f"{key_prefix}_try_again"):
            st.session_state.scan_results = None
            st.rerun()

    elif result_type == "single":
        def on_add_single(s, f):
            # Update global state via state_manager
            add_intake(s, f, data['name'])
            
            # Show success message instead of switching page
            st.success(t['msg_added_single'].format(data['name']))

        show_single_item_result(
            data, 
            None, # Do not show the image again in the result card
            on_confirm_callback=on_add_single,
            key_prefix=key_prefix
        )


# --- PAGE: HOME ---
if st.session_state.page == "home":
    st.set_page_config(page_title=t['page_title'], page_icon="🍹", layout="wide")

    st.markdown("""
    <style>
    /* GENERAL LAYOUT */
    .block-container { padding-top: 3rem; padding-bottom: 8rem; }
    .stApp { background-color: #ffffff; }
    #MainMenu, footer, header {visibility: hidden;}
    .stVerticalBlock > div:not(:last-child) { margin-bottom: 15px; }

    /* HEADER */
    .header-title { font-size: 3rem !important; font-weight: 900 !important; color: #000000 !important; line-height: 1.2; }
    .header-subtitle { font-size: 1.2rem; color: #64748b; margin-bottom: 2rem; }

    /* Action Card Styling */
    .action-card {
        border: 2px dashed #d9d9d9; 
        border-radius: 18px 18px 0 0;
        padding: 40px 20px; 
        text-align: center; 
        background: #fafafa;
        font-size: 18px; 
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="header-title" style="text-align: center;">{t["page_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-subtitle" style="text-align: center;">{t["subtitle"]}</div>', unsafe_allow_html=True)
    st.markdown("<hr style='border: 0.5px solid #ddd; margin-bottom: 30px;'>", unsafe_allow_html=True)

    
    # Custom Tab Bar using Columns and Buttons
    t_col1, t_col2, t_col3 = st.columns(3)
    
    with t_col1:
        if st.button(t['tab_label'], use_container_width=True, type="primary" if st.session_state.mode == "Nutrition Label" else "secondary"):
            st.session_state.mode = "Nutrition Label"
            st.session_state.scan_results = None
            reset_scanner_ui_state()
            st.rerun()
            
    with t_col2:
        if st.button(t['tab_fresh'], use_container_width=True, type="primary" if st.session_state.mode == "Fresh Drinks" else "secondary"):
            st.session_state.mode = "Fresh Drinks"
            st.session_state.scan_results = None
            reset_scanner_ui_state()
            st.rerun()
            
    with t_col3:
        if st.button(t['tab_menu'], use_container_width=True, type="primary" if st.session_state.mode == "Menu Scan" else "secondary"):
            st.session_state.mode = "Menu Scan"
            st.session_state.scan_results = None
            reset_scanner_ui_state()
            st.rerun()

    st.write("")
    col1, col2 = st.columns(2, gap="large")
    create_action_card(col1, 'https://img.icons8.com/color/96/camera--v1.png', t['card_cam_title'], t['card_cam_btn'], "camera_btn", "camera")
    create_action_card(col2, 'https://img.icons8.com/fluency/96/image.png', t['card_up_title'], t['card_up_btn'], "upload_btn", "upload")

    # --- TEXT INPUT SECTION (Moved from Home.py) ---
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.markdown(t['lazy_title'])
    
    with st.container(border=True):
        drink_input = st.text_input(t['input_label'], placeholder=t['input_ph'], label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        sweetness_pct = st.slider(t['slider_label'], min_value=0, max_value=150, value=100, step=25, key="text_slider")
        
        # Updated Labels Logic
        if sweetness_pct == 0: label = t['s_no']
        elif sweetness_pct == 25: label = t['s_less25']
        elif sweetness_pct == 50: label = t['s_less50']
        elif sweetness_pct == 75: label = t['s_less75']
        elif sweetness_pct == 100: label = t['s_std']
        else: label = t['s_extra'].format(sweetness_pct)
        st.caption(f"{t['selected']}: **{label}**")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button(t['btn_analyze_add'], use_container_width=True, type="primary"):
            if drink_input:
                with st.spinner(t['spinner_ask']):
                    multiplier = sweetness_pct / 100.0
                    result = jamai_service.analyze_manual_input_with_jamai(drink_input, multiplier, language=lang)
                    
                    if result:
                        st.session_state.scan_results = {"type": "single", "data": result, "source": "manual"}
                        st.rerun()

        # Display results if they exist (using the standard display function)
        if st.session_state.scan_results and st.session_state.scan_results.get("type") == "single" and st.session_state.scan_results.get("source") == "manual":
             display_scan_results(key_prefix="manual_result")


# --- PAGE: CAMERA ---
elif st.session_state.page == "camera":
    # Context-Aware Titles & Instructions
    if st.session_state.mode == "Nutrition Label":
        page_title = t['title_label']
        instr_text = t['instr_label']
    elif st.session_state.mode == "Fresh Drinks":
        page_title = t['title_fresh']
        instr_text = t['instr_fresh']
    else: # Menu Scan
        page_title = t['title_menu']
        instr_text = t['instr_menu']

    st.title(page_title)
    
    # Larger Instruction Text
    st.markdown(f"<h4 style='font-weight: 400; color: #555;'>{instr_text}</h4>", unsafe_allow_html=True)

    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        # Green Back Button (using type="primary" + global CSS)
        if st.button(t['back'], type="primary"): go("home")

    img = st.camera_input(instr_text, label_visibility="collapsed")
    
    if img:
        st.subheader(t['preview'])
        
        multiplier = 1.0
        if st.session_state.mode == "Fresh Drinks":
            st.markdown(t['adjust_sweet'])
            sweetness_pct = st.slider(t['slider_label'], min_value=0, max_value=150, value=100, step=25, key="cam_slider", on_change=clear_results)
            
            if sweetness_pct == 0: label = t['s_no']
            elif sweetness_pct == 25: label = t['s_less25']
            elif sweetness_pct == 50: label = t['s_less50']
            elif sweetness_pct == 75: label = t['s_less75']
            elif sweetness_pct == 100: label = t['s_std']
            else: label = t['s_extra'].format(sweetness_pct)
            st.caption(f"{t['selected']}: **{label}**")
            
            multiplier = sweetness_pct / 100.0

        st.write("---")
        if st.button(t['btn_analyze_bev'], type="primary", use_container_width=True):
             # Get translated mode name
             mode_key_map = {
                 "Nutrition Label": "tab_label",
                 "Fresh Drinks": "tab_fresh",
                 "Menu Scan": "tab_menu"
             }
             mode_trans = t[mode_key_map.get(st.session_state.mode, "tab_label")]
             
             with st.spinner(t['spinner_analyze'].format(mode_trans)):
                perform_analysis(img, multiplier)
        
        # Display results if they exist
        display_scan_results(key_prefix="cam_result")


# --- PAGE: UPLOAD ---
elif st.session_state.page == "upload":
    # Context-Aware Titles & Instructions
    if st.session_state.mode == "Nutrition Label":
        page_title = t['up_title_label']
        instr_text = t['up_instr_label']
    elif st.session_state.mode == "Fresh Drinks":
        page_title = t['up_title_fresh']
        instr_text = t['up_instr_fresh']
    else: # Menu Scan
        page_title = t['up_title_menu']
        instr_text = t['up_instr_menu']

    st.title(page_title)
    
    # Larger Instruction Text
    st.markdown(f"<h4 style='font-weight: 400; color: #555;'>{instr_text}</h4>", unsafe_allow_html=True)

    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        # Green Back Button (using type="primary" + global CSS)
        if st.button(t['back'], type="primary"): go("home")

    img = st.file_uploader(instr_text, type=['jpg','png','jpeg'], label_visibility="collapsed")
    
    if img:
        st.subheader(t['preview'])
        st.image(img, width=350)
        
        multiplier = 1.0
        if st.session_state.mode == "Fresh Drinks":
            st.markdown(t['adjust_sweet'])
            sweetness_pct = st.slider(t['slider_label'], min_value=0, max_value=150, value=100, step=25, key="up_slider", on_change=clear_results)
            
            if sweetness_pct == 0: label = t['s_no']
            elif sweetness_pct == 25: label = t['s_less25']
            elif sweetness_pct == 50: label = t['s_less50']
            elif sweetness_pct == 75: label = t['s_less75']
            elif sweetness_pct == 100: label = t['s_std']
            else: label = t['s_extra'].format(sweetness_pct)
            st.caption(f"{t['selected']}: **{label}**")
            
            multiplier = sweetness_pct / 100.0

        st.write("---")
        if st.button(t['btn_analyze_bev'], type="primary", use_container_width=True):
            # Get translated mode name
            mode_key_map = {
                "Nutrition Label": "tab_label",
                "Fresh Drinks": "tab_fresh",
                "Menu Scan": "tab_menu"
            }
            mode_trans = t[mode_key_map.get(st.session_state.mode, "tab_label")]

            with st.spinner(t['spinner_analyze'].format(mode_trans)):
                perform_analysis(img, multiplier)
        
        # Display results if they exist
        display_scan_results(key_prefix="up_result")