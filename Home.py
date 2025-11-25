import streamlit as st
import plotly.graph_objects as go
import time
from datetime import datetime



# --- Import local utils modules ---

try:
    from utils.state_manager import init_session_state, add_intake, delete_intake
    from utils.components import load_css, donut_chart, stat_card

except ImportError:
    st.error("⚠️ Error: `utils` folder not found.")
    st.stop()



# ==========================================
# 1. Page Configuration & CSS (Final Visual Polish)
# ==========================================

st.set_page_config(
    page_title="Cek Manis",
    page_icon="🍬",
    layout="wide"

)



# Initialize Session State
init_session_state()



# Custom CSS Styling

st.markdown("""

    <style>
    /* --- GENERAL LAYOUT --- */
    .block-container { padding-top: 3rem; padding-bottom: 8rem; }
    .stApp { background-color: #ffffff; }
    #MainMenu, footer, header {visibility: hidden;}
    .stVerticalBlock > div:not(:last-child) { margin-bottom: 15px; }



    /* --- TITLE --- */
    .header-title {
        font-size: 3rem !important;
        font-weight: 900 !important;
        color: #000000 !important;
        line-height: 1.2;
    }

    .header-subtitle {
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 2rem;

    }



    /* --- ANALYTICS ALIGNMENT --- */

    .analytics-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
    }

    .js-plotly-plot { margin: 0 auto !important; }

   

    /* --- STATS BOXES (White) --- */

    .stat-box {
        background-color: #ffffff;
        border: 1px solid #d3d3d3 !important;
        padding: 15px; border-radius: 12px; text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%;

    }

    .stat-value { font-size: 1.3rem; font-weight: 800; color: #0f172a; }

    .stat-label { font-size: 0.7rem; color: #64748b; text-transform: uppercase; font-weight: 700; }



    /* --- POTONG KAKI PREDICTOR (Dark Theme Integration) --- */

    .predictor-header {
        background-color: #1a1a1a;
        color: white;
        padding: 15px 20px;
        border-top-left-radius: 0.5rem;
        border-top-right-radius: 0.5rem;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: -17px;
        margin-left: -17px;
        margin-right: -17px;
        margin-bottom: 20px;

    }

   

    /* Dark Inputs in Predictor */

    .stNumberInput input {
        background-color: #2b2c30 !important;
        color: white !important;
        border: 1px solid #444 !important;

    }

    .stNumberInput label {
        color: #333 !important;
        font-weight: 600;

    }

    .stNumberInput button {
        background-color: #2b2c30 !important;
        color: white !important;
        border-color: #444 !important;

    }



    /* Primary Button (Yellow - Predict Risk) */

    button[kind="primary"] {
        background-color: #f5b700 !important;
        color: #1a1a1a !important;
        border: none !important;
        font-weight: 700 !important;
        width: 100%;
        border-radius: 8px;

    }



    /* --- QUICK ADD BUTTON STYLING --- */

    .drink-card-button-container .stButton > button {
        width: 100% !important; height: 60px !important; min-width: 90px !important;
        border-radius: 12px !important; border: 1px solid #e0e0e0 !important;
        background-color: white !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        display: flex !important; justify-content: flex-start !important; align-items: center !important;
        line-height: 1.2 !important; padding: 5px 10px !important;

    }

    .drink-card-button-container .stButton > button span:last-child {
        margin-left: auto !important; font-size: 14px !important; color: #10b981 !important;
        font-weight: 700 !important; min-width: 50px;

    }

   

    /* =================================================================================
       CUSTOM BUTTON STYLES (Add & Delete)
       ================================================================================= */



    /* 1. ADD BUTTON STYLE (Custom Entry) - TEAL & ALIGNED */

    /* Target buttons inside the BorderWrapper (Custom Entry Container) */

    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"] .stButton > button {

        background-color: #0d9488 !important; /* Teal Green */
        color: white !important;
        border: none !important;
        height: 48px !important;              /* Exact match for Streamlit Input height */
        border-radius: 8px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
            
        /* ALIGNMENT FIX: Push button down to match input box (skipping the label) */
        margin-top: 36px !important;

    }

    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        background-color: #0f766e !important;
    }



    /* 2. DELETE BUTTON STYLE (History) - RED, WIDE & SHORT */

    /* Updated Selector to ensure it hits the button in the 3rd column of history rows */

    /* We target the 3rd column in horizontal blocks that are NOT the custom entry block */

    div[data-testid="stVerticalBlock"]:has(h3:contains("Consumption History")) div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:nth-of-type(3) .stButton > button {

        background-color: #fee2e2 !important; /* Light Red BG */

        color: #ef4444 !important;            /* Red Text */
        border: 1px solid #fecaca !important; /* Red Border */
        border-radius: 6px !important;        /* Rectangular */
        height: 38px !important;              /* Slightly taller to look better */
        width: 100% !important;               /* Full width to match requested look */
        font-size: 0.9rem !important;        
        padding: 0px 5px !important;
        margin-top: 5px !important;          

    }

   

    /* Make sure we don't accidentally style the 3rd column of the Custom Entry block if it exists */
    /* (Custom Entry has 3 columns, but the button is in the 3rd column there too... wait) */
    /* Actually, Custom Entry button has kind="secondary" too. But we styled Custom Entry specifically above with BorderWrapper */
    /* The specific BorderWrapper selector above has higher specificity, so it should be fine. */
    /* But just in case, let's force the Red style only if it DOESN'T match the Teal one */

   

    div[data-testid="stVerticalBlock"]:has(h3:contains("Consumption History")) div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:nth-of-type(3) .stButton > button:hover {

        background-color: #fecaca !important;
        border-color: #ef4444 !important;

    }



    /* Visual Separator */
    div[data-testid="stColumn"]:first-child { border-right: 1px solid #e0e0e0; padding-right: 20px; }
    div[data-testid="stColumn"]:nth-child(2) { padding-left: 20px; }

   

    .history-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; }
    </style>

""", unsafe_allow_html=True)



# ==========================================
# 2. Core Constants
# ==========================================

LIMIT_SUGAR_DAILY = 50
LIMIT_FAT_DAILY = 25
LIMIT_SUGAR_MONTHLY = 1500



TEA_DRINKS = [

    {"name": "Teh Tarik", "sugar": 24, "fat": 5, "icon": "☕"},
    {"name": "Milo Ais", "sugar": 20, "fat": 3, "icon": "🥤"},
    {"name": "Kopi O", "sugar": 18, "fat": 0, "icon": "☕"},
    {"name": "Teh O", "sugar": 18, "fat": 0, "icon": "🍵"},
    {"name": "Cham", "sugar": 28, "fat": 5, "icon": "☕"},
    {"name": "Teh C", "sugar": 30, "fat": 6, "icon": "☕"},

]

SODA_DRINKS = [

    {"name": "100 Plus", "sugar": 27, "fat": 0, "icon": "🔋"},
    {"name": "7 Up", "sugar": 26, "fat": 0, "icon": "🥤"},
    {"name": "Sprite", "sugar": 25, "fat": 0, "icon": "🥤"},
    {"name": "CocaCola", "sugar": 39, "fat": 0, "icon": "🥤"},
    {"name": "Pepsi", "sugar": 41, "fat": 0, "icon": "🥤"},
    {"name": "Justea", "sugar": 22, "fat": 0, "icon": "🍃"},

]



# Language Dictionary

TRANS = {

    "English": {
        "subtitle": "Daily Health Summary",
        "today_analytics": "Today's Analytics",
        "sugar": "Sugar",
        "fat": "Sat. Fat",
        "remaining": "remaining",
        "monthly_summary": "Monthly Summary",
        "stat_remaining": "Remaining",
        "stat_consumed": "Consumed",
        "stat_daily_avg": "Daily Avg",
        "pk_title": "Potong Kaki & BMI Predictor",
        "age": "Age",
        "weight": "Weight (kg)",
        "height": "Height (cm)",
        "btn_predict": "Predict Risk",
        "quick_add_title_tea": "Tea / Coffee",
        "quick_add_title_soda": "Soda / Canned Drinks",
        "history_title": "📜 Consumption History",
        "history_empty": "No items added yet.",
        "qa_desc": "Select a drink:",
        "btn_delete_item": "Delete",
        "btn_scan": "📸 Scan Food Now",
        "custom_title": "Custom Entry",
        "custom_name_placeholder": "Item Name",
        "btn_add_custom": "Add"

    },

    "Malay": {

        "subtitle": "Ringkasan Kesihatan Harian",
        "today_analytics": "Analisis Hari Ini",
        "sugar": "Gula",
        "fat": "Lemak Tepu",
        "remaining": "baki",
        "monthly_summary": "Ringkasan Bulanan",
        "stat_remaining": "Baki Bulan",
        "stat_consumed": "Telah Diambil",
        "stat_daily_avg": "Purata Harian",
        "pk_title": "Ramalan Potong Kaki & BMI",
        "age": "Umur",
        "weight": "Berat (kg)",
        "height": "Tinggi (cm)",
        "btn_predict": "Ramal Risiko",
        "quick_add_title_tea": "Teh / Kopi",
        "quick_add_title_soda": "Air Kotak / Tin",
        "history_title": "📜 Sejarah Pengambilan",
        "history_empty": "Tiada rekod.",
        "qa_desc": "Pilih Minuman:",
        "btn_delete_item": "Padam",
        "btn_scan": "📸 Imbas Makanan Sekarang",
        "custom_title": "Input Sendiri",
        "custom_name_placeholder": "Nama Item",
        "btn_add_custom": "Tambah"

    }

}

t = TRANS[st.session_state.lang]



# ==========================================
# 3. Helper Functions (Visual)
# ==========================================

def get_status_color(value, limit):

    """Determine color based on percentage of limit used"""

    if limit <= 0: return '#10b981'
    ratio = value / limit
    if ratio < 0.5:
        return '#10b981' # Green (Safe)
    elif ratio < 1.0:
        return '#f59e0b' # Orange (Warning)
    else:
        return '#ef4444' # Red (Danger)



def create_donut(value, limit, label):

    color = get_status_color(value, limit)
    remaining = max(0, limit - value)

   

    fig = go.Figure(data=[go.Pie(
        labels=['Consumed', 'Remaining'], values=[value, remaining], hole=.75,
        marker=dict(colors=[color, '#f1f5f9']), textinfo='none', hoverinfo='label+value', sort=False
    )])

    fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=140, width=140,
        annotations=[dict(text=f"{int(value)}g", x=0.5, y=0.5, font_size=26, font_weight="bold", font_color=color, showarrow=False)])
    return fig



# ==========================================
# 4. Main Layout
# ==========================================



# --- Header ---

col_h1, col_h2 = st.columns([3, 1.5])

with col_h1:
    st.markdown('<div class="header-title">Cek Manis 🍬</div>', unsafe_allow_html=True)

with col_h2:
    if st.button("🌐 English ↔️ Malay", width='stretch'):
        st.session_state.lang = "Malay" if st.session_state.lang == "English" else "English"
        st.rerun()



st.markdown(f'<div class="header-subtitle">{t["subtitle"]}</div>', unsafe_allow_html=True)



# --- Analytics (White Cards) ---

st.markdown("---")
st.subheader(t["today_analytics"])



c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="analytics-wrapper">', unsafe_allow_html=True)
    st.markdown(f"<h5 style='text-align:center; margin-bottom:-5px;'>{t['sugar']}</h5>", unsafe_allow_html=True)
    st.plotly_chart(create_donut(st.session_state.sugar_today, LIMIT_SUGAR_DAILY, t['sugar']), width='stretch', config={'displayModeBar':False})

   

    rem_sugar = max(0, LIMIT_SUGAR_DAILY - st.session_state.sugar_today)
    sugar_color = get_status_color(st.session_state.sugar_today, LIMIT_SUGAR_DAILY)
    bg_color = f"{sugar_color}20"

    st.markdown(f"<div style='text-align:center; margin-top:-10px;'><span style='background:{bg_color}; color:{sugar_color}; border-radius:20px; font-size:0.8rem; padding:2px 8px; font-weight:bold;'>Limit: {LIMIT_SUGAR_DAILY}g</span></div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



with c2:
    st.markdown('<div class="analytics-wrapper">', unsafe_allow_html=True)
    st.markdown(f"<h5 style='text-align:center; margin-bottom:-5px;'>{t['fat']}</h5>", unsafe_allow_html=True)
    st.plotly_chart(create_donut(st.session_state.fat_today, LIMIT_FAT_DAILY, t['fat']), width='stretch', config={'displayModeBar':False})

   

    rem_fat = max(0, LIMIT_FAT_DAILY - st.session_state.fat_today)
    fat_color = get_status_color(st.session_state.fat_today, LIMIT_FAT_DAILY)
    bg_color_fat = f"{fat_color}20"

    st.markdown(f"<div style='text-align:center; margin-top:-10px;'><span style='background:{bg_color_fat}; color:{fat_color}; border-radius:20px; font-size:0.8rem; padding:2px 8px; font-weight:bold;'>Limit: {LIMIT_FAT_DAILY}g</span></div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



# --- Monthly Stats ---

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### 🗓️ " + t['monthly_summary'])

m1, m2, m3 = st.columns(3)

month_consumed = int(st.session_state.sugar_month_total)
month_remaining = max(0, LIMIT_SUGAR_MONTHLY - month_consumed)
current_day = max(1, datetime.now().day)
daily_avg = round(month_consumed / current_day, 1)



with m1: st.markdown(f"<div class='stat-box'><div class='stat-value'>{month_remaining}g</div><div class='stat-label'>{t['stat_remaining']}</div></div>", unsafe_allow_html=True)

with m2: st.markdown(f"<div class='stat-box'><div class='stat-value'>{month_consumed}g</div><div class='stat-label'>{t['stat_consumed']}</div></div>", unsafe_allow_html=True)

with m3: st.markdown(f"<div class='stat-box'><div class='stat-value'>{daily_avg}g</div><div class='stat-label'>{t['stat_daily_avg']}</div></div>", unsafe_allow_html=True)



# --- Potong Kaki Predictor ---

st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):

    st.markdown(f"""

    <div class="predictor-header">
        <span style="font-size: 24px;">⚠️</span>
        <span style="font-weight: bold; font-size: 1.1rem; margin-left: 10px;">{t['pk_title']}</span>
    </div>

    """, unsafe_allow_html=True)

   

    p1, p2, p3 = st.columns(3)

    with p1:
        pk_age = st.number_input(t['age'], min_value=0, max_value=120, value=25)

    with p2:
        pk_weight = st.number_input(t['weight'], min_value=0, max_value=300, value=60)

    with p3:
        pk_height = st.number_input(t['height'], min_value=0, max_value=250, value=170)

   

    if st.button(t['btn_predict'], type="primary", use_container_width=True):

        if pk_height > 0:
            bmi = pk_weight / ((pk_height/100)**2)
            if bmi < 18.5: status, color = "Underweight", "blue"
            elif 18.5 <= bmi < 25: status, color = "Normal Range", "green"
            elif 25 <= bmi < 30: status, color = "Overweight", "orange"
            else: status, color = "Obese (High Risk)", "red"

           

            st.markdown(f"""

            <div style="margin-top:15px; padding:15px; border-radius:8px; background-color:{'#dbeafe' if color=='blue' else '#dcfce7' if color=='green' else '#ffedd5' if color=='orange' else '#fee2e2'}; color:black;">
                <h4 style="margin:0; color:{color};">BMI: {bmi:.1f} - {status}</h4>
            </div>
            """, unsafe_allow_html=True)



# --- Quick Add Toolkit ---

st.markdown("---")

with st.expander("🛠️ Quick Entry Toolkit", expanded=True):

    col_tea, col_soda = st.columns(2)

    with col_tea:

        st.markdown(f"**{t['quick_add_title_tea']}**")
        st.markdown('<div class="drink-card-button-container">', unsafe_allow_html=True)

        tea_cols = st.columns(2)
        for i, drink in enumerate(TEA_DRINKS):
            with tea_cols[i % 2]:
                if st.button(f"{drink['icon']} {drink['name']} +{drink['sugar']}g", key=f"tea_{i}"):
                    add_intake(drink['sugar'], drink['fat'], drink['name'])
                    st.toast(f"✅ Added {drink['name']}", icon="🥤")
                    time.sleep(0.5)
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)



    with col_soda:

        st.markdown(f"**{t['quick_add_title_soda']}**")
        st.markdown('<div class="drink-card-button-container">', unsafe_allow_html=True)

        soda_cols = st.columns(2)
        for i, drink in enumerate(SODA_DRINKS):
            with soda_cols[i % 2]:
                if st.button(f"{drink['icon']} {drink['name']} +{drink['sugar']}g", key=f"soda_{i}"):
                    add_intake(drink['sugar'], drink['fat'], drink['name'])
                    st.toast(f"✅ Added {drink['name']}", icon="🥤")
                    time.sleep(0.5)
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)



# --- Custom Entry ---

st.markdown("---")

st.subheader(t['custom_title'])



with st.container(border=True):
    ce_col1, ce_col2, ce_col3 = st.columns([3, 2, 1.5])

   

    with ce_col1:
        c_name = st.text_input("Item Name", placeholder=t['custom_name_placeholder'])

    with ce_col2:
        c_sugar = st.number_input("Sugar (gram)", min_value=0, value=0)

    with ce_col3:

        # NOTE: Removed the <br> here as requested, CSS now handles alignment via margin-top
        if st.button(t['btn_add_custom'], use_container_width=True, type="secondary"):

            if c_name:
                add_intake(c_sugar, 0, c_name)
                st.toast(f"✅ Added {c_name}", icon="✅")
                time.sleep(0.5)
                st.rerun()

            else:

                st.warning("⚠️ Please enter a name")



# --- Consumption History ---

st.markdown("---")
st.subheader(t['history_title'])



if not st.session_state.history:
    st.caption(t['history_empty'])
else:
    for item in reversed(st.session_state.history):
        c1, c2, c3 = st.columns([6, 3, 2])

       

        with c1:
            # INCREASED FONT SIZE HERE
            st.markdown(f"<div style='padding-top:12px; font-weight:600; font-size:1.15rem;'>{item['name']}</div>", unsafe_allow_html=True)

       

        with c2:
            st.markdown(f"<div style='padding-top:12px; color:#10b981; font-weight:bold;'>+{item['sugar']}g</div>", unsafe_allow_html=True)

       

        with c3:

            # Removed wrapper div as CSS now targets directly via column structure

            if st.button(t['btn_delete_item'], key=f"del_{item['id']}"):
                delete_intake(item['id'])
                st.rerun()

       

        st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)



# ==========================================
# 5. BOTTOM NAVIGATION: SCAN BUTTON
# ==========================================

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""

<style>

.stButton > button:last-child {
    background-color: #0d9488 !important;
    color: white !important;
    border: none !important;
    height: 70px !important;
    font-size: 1.2rem !important;
    font-weight: 900 !important;
    box-shadow: 0 4px 14px 0 rgba(13, 148, 136, 0.39) !important;
    transition: transform 0.2s;

}

.stButton > button:last-child:hover {
    transform: scale(1.02);
    background-color: #0f766e !important;

}

</style>

""", unsafe_allow_html=True)



if st.button(t['btn_scan'], use_container_width=True):

    try:
        st.switch_page("pages/1_📷_Scanner.py")
    except Exception as e:
        st.warning("⚠️ Scanner page not found. Please create 'pages/1_📷_Scanner.py'.")
