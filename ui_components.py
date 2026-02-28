# ui_components.py
import streamlit as st
import knowledge_center as kc
import calendar
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_static_documentation():
    """Renders the 3-tab manual."""
    st.title("📖 Comprehensive System Manual")
    t1, t2, t3 = st.tabs(["📊 KPI Definitions", "🧠 Model Mechanics", "🛠️ Module Overview"])

    with t1:
        st.subheader("Key Performance Indicators (KPIs)")
        st.markdown(f"**1. Gross Demand**: {kc.KPI_DEFINITIONS['Gross Demand']}")
        st.markdown(f"**2. Return Rate (%)**")
        st.write(f"Logic: {kc.KPI_DEFINITIONS['Return Rate']['Logic']}")
        st.write(f"Formula: {kc.KPI_DEFINITIONS['Return Rate']['Formula']}")
        st.info(f"Business Value: {kc.KPI_DEFINITIONS['Return Rate']['Value']}")
        st.markdown(f"**3. Trend Surge**: {kc.KPI_DEFINITIONS['Trend Surge']['Logic']}")
        st.markdown(f"**4. Safety Buffer**: {kc.KPI_DEFINITIONS['Safety Buffer']['Logic']}")
        st.write(f"Formula: {kc.KPI_DEFINITIONS['Safety Buffer']['Formula']}")

    with t2:
        st.subheader("Algorithmic Logic")
        for model, details in kc.MODEL_MECHANICS.items():
            st.write(f"### {model}")
            if isinstance(details, list):
                for line in details: st.markdown(line)
            else: st.markdown(details)

    with t3:
        st.subheader("Module Functionality")
        for module, desc in kc.MODULE_OVERVIEW.items():
            st.write(f"**{module}**: {desc}")

def render_festival_calendar(f_name, f_date_str):
    """Builds the heatmaps from the prior code."""
    f_date = datetime.strptime(f_date_str, "%Y-%m-%d")
    cal_grid = calendar.monthcalendar(f_date.year, f_date.month)
    # (Heatmap logic as defined in previous steps)
    return go.Figure() # Simplified for structure
