import streamlit as st
import plotly.graph_objects as go
import time
from datetime import datetime
import requests
import os 

# --- Import local utils modules ---
try:
    from utils.state_manager import init_session_state, add_intake, delete_intake
    from utils.components import load_css, donut_chart, stat_card, calculate_diabetes_risk

except ImportError:
    # Temp fix for missing utils
    def init_session_state():
         if 'sugar_today' not in st.session_state: st.session_state['sugar_today'] = 0
         if 'fat_today' not in st.session_state: st.session_state['fat_today'] = 0
         if 'sugar_month_total' not in st.session_state: st.session_state['sugar_month_total'] = 0
         if 'fat_month_total' not in st.session_state: st.session_state['fat_month_total'] = 0
         if 'history' not in st.session_state: st.session_state['history'] = []
         if 'lang' not in st.session_state: st.session_state['lang'] = 'English'
         if 'intro_shown' not in st.session_state: st.session_state['intro_shown'] = False

    st.warning("⚠️ Warning: `utils` folder not found. Using temporary session state.")

# ==========================================
# 1. Page Configuration & CSS
# ==========================================

st.set_page_config(
    page_title="Cek Manis",
    page_icon="🍬",
    layout="wide"
)

# Initialize Session State
try:
    init_session_state()
except:
    pass

# Defensive Checks
if 'intro_shown' not in st.session_state: st.session_state.intro_shown = False
if 'lang' not in st.session_state: st.session_state.lang = 'English'
if 'sugar_today' not in st.session_state: st.session_state.sugar_today = 0
if 'fat_today' not in st.session_state: st.session_state.fat_today = 0
if 'sugar_month_total' not in st.session_state: st.session_state.sugar_month_total = st.session_state.sugar_today
if 'fat_month_total' not in st.session_state: st.session_state.fat_month_total = st.session_state.fat_today

# --- Custom CSS Styling ---
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

    /* STAT BOXES */
    .stat-box { 
        background-color: #ffffff; 
        border: 1px solid #d3d3d3 !important; 
        padding: 15px; 
        border-radius: 12px; 
        text-align: center; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.05); 
        height: 100%; 
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .stat-value { font-size: 1.3rem; font-weight: 800; color: #0f172a; }
    .stat-label { font-size: 0.9rem; color: #64748b; text-transform: uppercase; font-weight: 700; margin-bottom: 10px; }

    /* PREDICTOR STYLES */
    .predictor-header { background-color: #1a1a1a; color: white; padding: 15px 20px; border-radius: 0.5rem; display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
    .risk-score-card { padding: 20px; border-radius: 12px; margin-top: 15px; text-align: center; border: 2px solid #eee; }
    
    /* --- FIXED NUMBER INPUT STYLING (Seamless Dark Look) --- */
    
    /* 1. Input Box */
    .stNumberInput input { 
        background-color: #2b2c30 !important; 
        color: white !important; 
        border: 1px solid #2b2c30 !important; /* Border same as bg */
        border-radius: 4px !important;
    }
    
    /* 2. Plus/Minus Buttons Container */
    div[data-testid="stNumberInput"] > div {
        background-color: #2b2c30 !important;
        border-radius: 4px !important;
        border: 1px solid #444 !important; /* Outer border for the whole group */
        color: white !important;
    }

    /* 3. The Buttons Themselves */
    div[data-testid="stNumberInput"] button {
        background-color: #2b2c30 !important; 
        color: white !important; 
        border: none !important; /* Remove split borders */
    }
    
    /* 4. Button Hover */
    div[data-testid="stNumberInput"] button:hover {
        background-color: #3d3e42 !important; /* Slightly lighter on hover */
        color: #0d9488 !important;
    }
    
    /* --- UNIFIED BUTTON COLORS (Teal #0d9488) --- */
    
    /* 1. Global Button Style (Applies to Language, Analyze, etc.) */
    .stButton > button {
        background-color: #0d9488 !important; 
        color: white !important; 
        border: none !important; 
        border-radius: 8px !important; 
        font-weight: 600 !important; 
        width: 100% !important;
    }

    /* 2. Calculate Risk Button (Force Teal) */
    button[kind="primary"] {
        background-color: #0d9488 !important;
        color: white !important;
        border: none !important;
    }

    /* 3. Bottom Nav Button (Force Teal) */
    div[data-testid="stVerticalBlock"] > .stButton:last-child > button {
        background-color: #0d9488 !important; /* Same as others now */
        height: 60px !important;
        font-size: 1.2rem !important;
    }

    /* --- EXCEPTIONS --- */

    /* History Delete Button (Red) */
    div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:nth-of-type(4) button {
         background-color: #fee2e2 !important;
         color: #ef4444 !important;
         border: 1px solid #fecaca !important;
         height: 32px !important; 
         font-size: 0.8rem !important;
         padding: 0px 10px !important;
    }
    
    /* HISTORY ITEM STYLE */
    .history-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Logic & Constants
# ==========================================

LIMIT_SUGAR_DAILY = 50
LIMIT_FAT_DAILY = 25
LIMIT_SUGAR_MONTHLY = 1500
LIMIT_FAT_MONTHLY = 750 

TRANS = {
    "English": {
        "subtitle": "Daily Health Summary",
        "today_analytics": "Today's Analytics",
        "sugar_label": "Sugar",
        "fat_label": "Saturated Fat",
        "daily_left": "Daily Left",
        "monthly_left": "Monthly Left",
        
        "intro_welcome_title": "👋 Welcome to Cek Manis!",
        "intro_content": """
        ##### Did you know Malaysia has the highest diabetes rate in Asia? 🥤😱
        
        **Cek Manis** is your AI-powered companion to fight this silent killer.
        
        * ✨ **Smart Tracking:** Log your Teh Tarik & Milo instantly.
        * 🤖 **JamAI Scanner:** Not sure about that drink? Let AI analyze it.
        * ⚖️ **Risk Predictor:** See how your weight & sugar intake affect your future health.
        
        Let's make healthier choices together!
        """,
        "intro_btn_start": "Let's Start!",

        "pk_title": "Diabetes & Weight Predictor",
        "risk_intro": "Calculate Risk based on BMI + Sugar.",
        "age": "Age",
        "weight": "Weight (kg)",
        "height": "Height (cm)",
        "btn_calc_risk": "Calculate Risk",
        "risk_result_title": "x Higher Risk",
        "risk_result_desc": "Compared to a healthy person drinking water.",
        "bmi_label": "BMI Factor",
        "sugar_penalty": "Sugar Penalty",
        "future_view": "Future View",
        "bmi_msg": "Your BMI is",
        "sugar_msg": "Intake today adds",
        "future_msg": "If everyday like today:",
        "walk_msg": "You need to walk",
        "steps": "steps",
        "burn": "to burn off today's sugar!",
        "jamai_title": "JamAI Drink Analyzer",
        "jamai_caption": "Enter drink name and adjust sugar level to analyze.",
        "jamai_ph": "e.g. Teh C Peng",
        "jamai_sweet_label": "Sugar Level (%)",
        "jamai_selected": "Selected",
        "analyze_btn": "🔍 Analyze & Add",
        "add_log_btn": "✅ Add to Daily Log",
        "history_title": "Consumption History",
        "history_empty": "No items added yet.",
        "btn_delete": "Del",
        "btn_scan": "📸 Scan Food Now",
        "toast_added": "Added",
        "sw_kosong": "No Sugar",
        "sw_less": "Less Sugar",
        "sw_half": "Half Sugar",
        "sw_std": "Standard",
        "sw_extra": "Extra Sugar",
        "sw_orig": "Original"
    },
    "Malay": {
        "subtitle": "Ringkasan Kesihatan Harian",
        "today_analytics": "Analisis Hari Ini",
        "sugar_label": "Gula",
        "fat_label": "Lemak Tepu",
        "daily_left": "Baki Harian",
        "monthly_left": "Baki Bulanan",
        
        "intro_welcome_title": "👋 Selamat Datang ke Cek Manis!",
        "intro_content": """
        ##### Tahukah anda Malaysia mempunyai kadar diabetes tertinggi di Asia? 🥤😱
        
        **Cek Manis** adalah rakan AI anda untuk melawan pembunuh senyap ini.
        
        * ✨ **Jejak Pantas:** Rekod Teh Tarik & Milo anda dengan mudah.
        * 🤖 **Imbasan JamAI:** Tak pasti kandungan gula? Biar AI analisa.
        * ⚖️ **Ramalan Risiko:** Lihat kesan berat & gula terhadap masa depan anda.
        
        Ayuh jadikan Malaysia lebih sihat!
        """,
        "intro_btn_start": "Mula Sekarang!",

        "pk_title": "Ramalan Risiko & Berat Badan",
        "risk_intro": "Kira Risiko berdasarkan BMI + Gula.",
        "age": "Umur",
        "weight": "Berat (kg)",
        "height": "Tinggi (cm)",
        "btn_calc_risk": "Kira Risiko",
        "risk_result_title": "x Risiko Lebih Tinggi",
        "risk_result_desc": "Berbanding orang sihat yang minum air masak.",
        "bmi_label": "Faktor BMI",
        "sugar_penalty": "Penalti Gula",
        "future_view": "Masa Depan",
        "bmi_msg": "BMI anda ialah",
        "sugar_msg": "Pengambilan hari ini menambah",
        "future_msg": "Jika setiap hari begini:",
        "walk_msg": "Anda perlu berjalan",
        "steps": "langkah",
        "burn": "untuk bakar gula hari ini!",
        
        "jamai_title": "Penganalisa Minuman JamAI",
        "jamai_caption": "Masukkan nama minuman dan pilih tahap gula.",
        "jamai_ph": "cth. Teh C Peng",
        "jamai_sweet_label": "Tahap Gula (%)",
        "jamai_selected": "Pilihan",
        "analyze_btn": "🔍 Analisis & Tambah",
        "add_log_btn": "✅ Tambah ke Log",
        "history_title": "Sejarah Pengambilan",
        "history_empty": "Tiada rekod lagi.",
        "btn_delete": "Padam",
        "btn_scan": "📸 Imbas Makanan Sekarang",
        "toast_added": "Ditambah",
        "sw_kosong": "Kosong",
        "sw_less": "Kurang Manis",
        "sw_half": "Separuh Manis",
        "sw_std": "Biasa (Standard)",
        "sw_extra": "Tambah Manis",
        "sw_orig": "Asli"
    }
}

t = TRANS[st.session_state.lang]

# --- 2.1 INTRODUCTION POP-UP ---
if not st.session_state.intro_shown:
    st.toast(t['intro_welcome_title'], icon="🍬")
    with st.expander("ℹ️ Info", expanded=True):
        st.markdown(t['intro_content'])
        if st.button(t['intro_btn_start']):
            st.session_state.intro_shown = True
            st.rerun()

# --- 2.2 HELPER: JAMAI FUNCTION ---
def call_jamai_api(drink_name, sweetness_pct):
    time.sleep(1.0) 
    drink_name_lower = drink_name.lower()
    base_sugar = 30 
    is_soda = any(x in drink_name_lower for x in ["coke", "cola", "pepsi", "100", "sprite", "7up", "sarsi", "f&n", "fanta"])
    if is_soda:
        base_sugar = 35 
    else:
        if "teh" in drink_name_lower or "tea" in drink_name_lower: base_sugar = 24
        elif "kopi" in drink_name_lower or "coffee" in drink_name_lower: base_sugar = 18
        elif "milo" in drink_name_lower: base_sugar = 20

    final_sugar = int(base_sugar * (sweetness_pct / 100))
    
    if final_sugar <= 1: grade = "A"
    elif final_sugar <= 10: grade = "B"
    elif final_sugar <= 25: grade = "C"
    else: grade = "D"

    return {
        "sugar": final_sugar,
        "grade": grade,
        "display_sweetness": f"{sweetness_pct}%"
    }

# ==========================================
# 3. Main Layout
# ==========================================

# --- Header ---
col_h1, col_h2 = st.columns([3, 1.5])
with col_h1:
    st.markdown('<div class="header-title">Cek Manis 🍬</div>', unsafe_allow_html=True)
with col_h2:
    if st.session_state.lang == "English": btn_text = "🇲🇾 Bahasa Melayu"
    else: btn_text = "🇬🇧 English"
    if st.button(btn_text, width='stretch'):
        st.session_state.lang = "Malay" if st.session_state.lang == "English" else "English"
        st.rerun()

st.markdown(f'<div class="header-subtitle">{t["subtitle"]}</div>', unsafe_allow_html=True)

# --- Analytics ---
st.markdown("---")
st.subheader(t["today_analytics"])

c1, c2 = st.columns(2)

# SUGAR CARD
with c1:
    with st.container(border=True):
        st.markdown(f"<h5 style='text-align: center; margin-bottom: 0;'>{t['sugar_label']}</h5>", unsafe_allow_html=True)
        st.plotly_chart(donut_chart(st.session_state.sugar_today, LIMIT_SUGAR_DAILY, 'Sugar'), width='stretch', config={'displayModeBar':False})
        
        rem_day_sugar = max(0, LIMIT_SUGAR_DAILY - st.session_state.sugar_today)
        rem_month_sugar = max(0, LIMIT_SUGAR_MONTHLY - st.session_state.sugar_month_total)
        day_color = "#ef4444" if rem_day_sugar <= 5 else "#0f172a"
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-around; margin-top: 10px; border-top: 1px solid #f1f5f9; padding-top: 12px;">
            <div style="text-align: center;">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">{t['daily_left']}</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: {day_color};">{rem_day_sugar}g</div>
            </div>
            <div style="border-right: 1px solid #e2e8f0;"></div>
            <div style="text-align: center;">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">{t['monthly_left']}</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: #0f172a;">{rem_month_sugar}g</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# FAT CARD
with c2:
    with st.container(border=True):
        st.markdown(f"<h5 style='text-align: center; margin-bottom: 0;'>{t['fat_label']}</h5>", unsafe_allow_html=True)
        st.plotly_chart(donut_chart(st.session_state.fat_today, LIMIT_FAT_DAILY, 'Fat'), width='stretch', config={'displayModeBar':False})
        
        rem_day_fat = max(0, LIMIT_FAT_DAILY - st.session_state.fat_today)
        rem_month_fat = max(0, LIMIT_FAT_MONTHLY - st.session_state.fat_month_total)
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-around; margin-top: 10px; border-top: 1px solid #f1f5f9; padding-top: 12px;">
            <div style="text-align: center;">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">{t['daily_left']}</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: #0f172a;">{rem_day_fat}g</div>
            </div>
            <div style="border-right: 1px solid #e2e8f0;"></div>
            <div style="text-align: center;">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">{t['monthly_left']}</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: #0f172a;">{rem_month_fat}g</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 4. POTONG KAKI PREDICTOR
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown(f"""
    <div class="predictor-header">
        <span style="font-size: 24px;">🧬</span>
        <div>
            <span style="font-weight: bold; font-size: 1.1rem;">{t['pk_title']}</span><br>
            <span style="font-size: 0.8rem; opacity: 0.8;">{t['risk_intro']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    pk_c1, pk_c2, pk_c3 = st.columns(3)
    with pk_c1: pk_age = st.number_input(t['age'], 10, 100, 20)
    with pk_c2: pk_weight = st.number_input(t['weight'], 30, 200, 60)
    with pk_c3: pk_height = st.number_input(t['height'], 100, 250, 170)

    st.markdown("<br>", unsafe_allow_html=True)
    # UNIFIED BUTTON COLOR (TEAL)
    if st.button(t['btn_calc_risk'], type="primary", use_container_width=True):
        if pk_height > 0:
            bmi = pk_weight / ((pk_height/100)**2)
            current_sugar = st.session_state.sugar_today
            res = calculate_diabetes_risk(bmi, current_sugar)
            
            risk_color = "#10b981" if res['risk_score'] < 1.5 else "#f59e0b" if res['risk_score'] < 3.0 else "#ef4444"
            
            st.markdown(f"""
            <div class="risk-score-card" style="border-color: {risk_color}; background-color: {risk_color}10;">
                <h3 style="color: {risk_color}; margin: 0;">{res['risk_score']}{t['risk_result_title']}</h3>
                <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #555;">{t['risk_result_desc']}</p>
            </div>
            """, unsafe_allow_html=True)

            res_c1, res_c2, res_c3 = st.columns(3)
            with res_c1: st.info(f"**{t['bmi_label']}**\n\n{t['bmi_msg']} **{bmi:.1f}** ({res['bmi_status']}).") 
            with res_c2: st.warning(f"**{t['sugar_penalty']}**\n\n{t['sugar_msg']} **+{res['sugar_increase_pct']}%** risk.") 
            with res_c3: st.error(f"**{t['future_view']}**\n\n{t['future_msg']} **+{res['yearly_gain']}kg** / year.")

            if current_sugar > 0:
                st.markdown(f"""
                <div style="margin-top: 10px; padding: 10px; border: 1px dashed #ccc; border-radius: 8px; text-align: center;">
                    🏃‍♂️ {t['walk_msg']} <b>{res['steps_needed']} {t['steps']}</b> {t['burn']}
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# 5. JAMAI ANALYZER
# ==========================================
st.markdown("---")
st.subheader(t['jamai_title'])

with st.container(border=True):
    st.caption(t['jamai_caption'])
    
    drink_input = st.text_input("Drink Name", placeholder=t['jamai_ph'], label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    sweetness_pct = st.slider(t['jamai_sweet_label'], min_value=0, max_value=150, value=100, step=25)
    
    if sweetness_pct == 0: label = f"⚪ {t['sw_kosong']}"
    elif sweetness_pct == 25: label = f"🟢 {t['sw_less']}"
    elif sweetness_pct == 50: label = f"🟡 {t['sw_half']}"
    elif sweetness_pct == 75: label = f"🟠 {t['sw_std']} (75%)"
    elif sweetness_pct == 100: label = f"🔴 {t['sw_std']} (100%)"
    else: label = f"🟣 {t['sw_extra']}"
    st.caption(f"{t['jamai_selected']}: **{label}**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button(t['analyze_btn'], use_container_width=True, type="primary"):
        if drink_input:
            with st.spinner("Asking JamAI..."):
                result = call_jamai_api(drink_input, sweetness_pct)
                st.session_state.analyzed_data = result
                st.session_state.analyzed_name = f"{drink_input} ({sweetness_pct}%)"

    if 'analyzed_data' in st.session_state and st.session_state.analyzed_data:
        data = st.session_state.analyzed_data
        grade = data['grade']
        
        grade_colors = { "A": "#009E73", "B": "#88C425", "C": "#E69F00", "D": "#D55E00" }
        g_color = grade_colors.get(grade, "#888")
        
        with st.container(border=True):
            st.markdown(f"### 🥤 {st.session_state.analyzed_name}")
            rc1, rc2 = st.columns([1, 3])
            with rc1:
                st.markdown(f"""
                <div style="background-color:{g_color}; color:white; 
                            border-radius:12px; padding:15px; text-align:center; 
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <span style="font-size:1rem; font-weight:bold;">GRADE</span><br>
                    <span style="font-size:3.5rem; font-weight:900; line-height:1;">{grade}</span>
                </div>
                """, unsafe_allow_html=True)
            with rc2:
                st.metric(label=t['sugar_label'], value=f"{data['sugar']}g")
                progress_val = min(1.0, data['sugar'] / 50.0)
                st.progress(progress_val, text=f"Daily Limit Usage: {int(progress_val*100)}%")
        
        if st.button(t['add_log_btn'], use_container_width=True):
            add_intake(data['sugar'], 0, st.session_state.analyzed_name)
            st.toast(f"{t['toast_added']} {st.session_state.analyzed_name}!", icon="✅")
            st.session_state.analyzed_data = None 
            time.sleep(1)
            st.rerun()

# --- Consumption History ---
st.markdown("---")
with st.expander(f"📜 {t['history_title']}", expanded=True):
    if not st.session_state.history:
        st.caption(t['history_empty'])
    else:
        for item in reversed(st.session_state.history):
            s_val = item['sugar']
            if s_val <= 1: h_grade, h_col = "A", "#009E73"
            elif s_val <= 10: h_grade, h_col = "B", "#88C425"
            elif s_val <= 25: h_grade, h_col = "C", "#E69F00"
            else: h_grade, h_col = "D", "#D55E00"

            c1, c2, c3, c4 = st.columns([1, 4, 1.5, 1])
            with c1:
                st.markdown(f"""
                <div style='margin-top:5px; background-color:{h_col}; color:white; 
                            font-weight:bold; border-radius:6px; text-align:center; 
                            padding:2px 0px; font-size:0.8rem; width:30px;'>
                    {h_grade}
                </div>
                """, unsafe_allow_html=True)
            with c2: 
                st.markdown(f"<div style='padding-top:5px; font-weight:600;'>{item['name']}</div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div style='padding-top:5px; color:#10b981; font-weight:bold;'>+{s_val}g</div>", unsafe_allow_html=True)
            with c4:
                if st.button(t['btn_delete'], key=f"del_{item['id']}"):
                    delete_intake(item['id'])
                    st.rerun()
            st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)

# --- Bottom Nav ---
st.markdown("<br><br>", unsafe_allow_html=True)
if st.button(t['btn_scan'], use_container_width=True):
    try:
        st.switch_page("pages/1_📷_Scanner.py")
    except:
        st.warning("Scanner page not created yet.")