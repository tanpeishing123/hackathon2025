import streamlit as st
import plotly.graph_objects as go

def load_css():
    """
   
    """
    pass

def donut_chart(value, limit, color, label):
    """progress chart"""
    remaining = max(0, limit - value)
    
    fig = go.Figure(data=[go.Pie(
        labels=['Consumed', 'Remaining'], 
        values=[value, remaining], 
        hole=.75,
        marker=dict(colors=[color, '#f1f5f9']), 
        textinfo='none', 
        hoverinfo='label+value', 
        sort=False
    )])
    
    fig.update_layout(
        showlegend=False, 
        margin=dict(t=0, b=0, l=0, r=0), 
        height=160, 
        width=160,
        annotations=[dict(
            text=f"{int(value)}g", 
            x=0.5, y=0.5, 
            font_size=24, 
            font_weight="bold", 
            font_color=color, 
            showarrow=False
        )]
    )
    return fig

def stat_card(label, value, sub_text=""):
    """statistical card"""
    st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{value}</div>
            <div class="stat-label">{label}</div>
            <small style="color:#94a3b8">{sub_text}</small>
        </div>
    """, unsafe_allow_html=True)
