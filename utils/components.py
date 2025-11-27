import streamlit as st
import plotly.graph_objects as go

# --- Load CSS ---
def load_css():
   
    pass

# --- Diabetes Risk Algorithm  ---
def calculate_diabetes_risk(bmi, daily_sugar_grams):
    """
    Calculates Relative Risk of T2 Diabetes based on BMI and Sugar.
    """
    # 1. Constants
    GRAMS_PER_SERVING = 26.0 
    RISK_PER_SERVING = 0.18  # 18% increase per serving

    # 2. Calculate Sugar Multiplier
    servings = daily_sugar_grams / GRAMS_PER_SERVING
    sugar_risk_increase = servings * RISK_PER_SERVING
    
    # 3. Determine Base Risk (BMI)
    if bmi < 25:
        base_risk = 1.0  # Healthy
        bmi_status = "Healthy"
    elif bmi < 30:
        base_risk = 1.5  # Overweight
        bmi_status = "Overweight"
    else:
        base_risk = 3.0  # Obese
        bmi_status = "Obese (High Risk)"
        
    # 4. Final Calculation
    total_risk = base_risk * (1 + sugar_risk_increase)
    
    # 5. Limit Percentage (for display)
    limit_pct = (daily_sugar_grams / 50.0) * 100

    # 6. Extra: Walking & Weight Gain
    # Future Weight Gain (Total sugar contribution to weight)
    # 7700kcal = 1kg fat. 1g sugar = 4kcal.
    yearly_gain = (daily_sugar_grams * 4 * 365) / 7700 
    
    # Steps to burn: 1g sugar = 4 kcal. Walking 1 step burns approx 0.04 kcal.
    steps_needed = int((daily_sugar_grams * 4) / 0.04)
    
    return {
        "risk_score": round(total_risk, 1),
        "sugar_increase_pct": int(sugar_risk_increase * 100), # Kept for backward compatibility if needed, but limit_pct is preferred for display
        "limit_pct": round(limit_pct, 1),
        "bmi_status": bmi_status,
        "steps_needed": steps_needed,
        "yearly_gain": round(yearly_gain, 1)
    }

# --- Chart Components ---
def get_status_color(value, limit):
    if limit <= 0: return '#10b981'
    ratio = value / limit
    if ratio < 0.5: return '#10b981'
    elif ratio < 1.0: return '#f59e0b'
    else: return '#ef4444'

def donut_chart(value, limit, label):
    color = get_status_color(value, limit)
    remaining = max(0, limit - value)
    
    fig = go.Figure(data=[go.Pie(
        labels=['Consumed', 'Remaining'], values=[value, remaining], hole=.75,
        marker=dict(colors=[color, '#f1f5f9']), textinfo='none', hoverinfo='label+value', sort=False
    )])
    
    fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=140, width=140,annotations=[dict(text=f"{int(value)}g", x=0.5, y=0.5, font_size=26, font_weight="bold", font_color=color, showarrow=False)])
    
    return fig

def stat_card(label, value, sublabel=""):
    return f"""
    <div class='stat-box'>
        <div class='stat-value'>{value}</div>
        <div class='stat-label'>{label}</div>
        <div style='font-size:0.6rem; color:#94a3b8;'>{sublabel}</div>
    </div>
    """