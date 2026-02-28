import streamlit as st
import knowledge_center as kc
import calendar
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_static_documentation():
    """Renders the 3-tab manual requested."""
    st.title("📖 Comprehensive System Manual")
    tab1, tab2, tab3 = st.tabs(["📊 KPI Definitions", "🧠 Model Mechanics", "🛠️ Module Overview"])

    with tab1:
        st.subheader("Key Performance Indicators (KPIs)")
        st.markdown(f"**1. Gross Demand**: {kc.KPI_DEFINITIONS['Gross Demand']}")
        
        st.markdown("**2. Return Rate (%)**")
        st.write(f"Logic: {kc.KPI_DEFINITIONS['Return Rate']['Logic']}")
        st.write(f"Formula: {kc.KPI_DEFINITIONS['Return Rate']['Formula']}")
        st.info(f"Business Value: {kc.KPI_DEFINITIONS['Return Rate']['Value']}")
        
        st.markdown("**3. Trend Surge (Multiplier)**")
        st.write(f"Logic: {kc.KPI_DEFINITIONS['Trend Surge']['Logic']}")
        st.write(f"Values: {kc.KPI_DEFINITIONS['Trend Surge']['Values']}")
        
        st.markdown("**4. Safety Buffer (%)**")
        st.write(f"Logic: {kc.KPI_DEFINITIONS['Safety Buffer']['Logic']}")
        st.write(f"Formula: {kc.KPI_DEFINITIONS['Safety Buffer']['Formula']}")

    with tab2:
        st.subheader("Algorithmic Logic")
        for model, details in kc.MODEL_MECHANICS.items():
            st.write(f"### {model}")
            if isinstance(details, list):
                for line in details: st.markdown(f"{line}")
            else: st.markdown(f"{details}")

    with tab3:
        st.subheader("Module Functionality")
        for module, desc in kc.MODULE_OVERVIEW.items():
            st.write(f"**{module}**: {desc}")

def render_festival_calendar(f_name, f_date_str):
    """Generates the dark-themed holiday impact calendar."""
    f_date = datetime.strptime(f_date_str, "%Y-%m-%d")
    year, month = f_date.year, f_date.month
    cal = calendar.monthcalendar(year, month)
    
    z_data = []
    for week in cal:
        row = []
        for day in week:
            if day == 0: row.append(0)
            elif day == f_date.day: row.append(2) # Peak
            else: row.append(0.5) # Normal
        z_data.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=z_data, x=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
        colorscale=[[0, "#1e1e1e"], [0.5, "#2d2d2d"], [1, "green"]],
        showscale=False
    ))
    fig.update_layout(title=f"{f_name} Impact", height=250, template="plotly_dark")
    return fig
