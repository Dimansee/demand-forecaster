import streamlit as st
import calendar
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_static_documentation():
    st.title("📖 System Manual")
    doc_tabs = st.tabs(["📊 KPIs", "🧠 Models", "🧼 Cleaning"])
    with doc_tabs[0]:
        st.markdown("### KPI Logic\n- **Net Demand**: $Gross \times (1 - Returns\%)$")
    # ... Add other doc content here ...
    if st.button("Close Manual"):
        st.session_state.page = "Forecaster"
        st.rerun()

def render_cal(f_name, f_date_str):
    f_date = datetime.strptime(f_date_str, "%Y-%m-%d")
    year, month = f_date.year, f_date.month
    cal_grid = calendar.monthcalendar(year, month)
    # ... (Insert heatmap logic from original code here) ...
    return fig_cal
