import streamlit as st
import calendar
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_static_documentation():
    """Renders the full system manual with tabs for KPIs and Logic."""
    st.title("📖 Comprehensive System Manual")
    
    doc_tabs = st.tabs(["📊 KPI Definitions", "🧠 Model Mechanics", "🛠️ Module Overview", "🧼 Data Cleaning Logic"])
    
    with doc_tabs[0]:
        st.subheader("Key Performance Indicators (KPIs)")
        st.markdown("""
        ### 1. Gross Demand
        The raw AI prediction of customer interest before any deductions.
        
        ### 2. Return Rate (%)
        - **Logic:** The estimated percentage of units that will be returned.
        - **Formula:** $Net Demand = Gross Demand \\times (1 - Return\\%)$
        
        ### 3. Safety Buffer (%)
        - **Logic:** The "Insurance" stock to prevent stockouts.
        - **Formula:** $Target = Net Demand \\times (1 + Buffer\\%)$
        """)

    with doc_tabs[1]:
        st.subheader("Algorithmic Logic")
        st.markdown("""
        - **Prophet:** Uses additive regression for Trend and Seasonality.
        - **KNN:** Finds similar historical days to predict future volume.
        - **Decision Tree:** Uses branching logic based on features like 'Day of Week'.
        """)

    with doc_tabs[2]:
        st.subheader("Module Functionality")
        st.info("- **Forecast Engine:** Routes SKU data to the selected math model.\n- **Strategy Overrider:** Applies manual multipliers to AI results.")

    with doc_tabs[3]:
        st.subheader("Auto-Cleaning Protocols")
        st.write("- **Standardization:** Handles 'Date' vs 'date' headers.\n- **Deduplication:** Aggregates multi-line sales for the same day.")
        
    if st.button("Close Manual"):
        st.session_state.page = "Forecaster"
        st.rerun()

def render_festival_calendar(f_name, f_date_str, green_lift, orange_lift):
    """Generates a Plotly Heatmap representing a specific festival month."""
    f_date = datetime.strptime(f_date_str, "%Y-%m-%d")
    year, month = f_date.year, f_date.month
    cal_grid = calendar.monthcalendar(year, month)
    
    # Define the impact window (2 days before, 1 day after)
    impact_window = [f_date - timedelta(days=2), f_date - timedelta(days=1), f_date + timedelta(days=1)]
    
    z_data, text_data = [], []
    for week in cal_grid:
        z_week, t_week = [], []
        for day in week:
            if day == 0:
                z_week.append(0)
                t_week.append("")
            else:
                curr = datetime(year, month, day)
                if curr == f_date:
                    z_week.append(2) # Peak Day (Green)
                elif curr in impact_window:
                    z_week.append(1) # Window Day (Orange)
                else:
                    z_week.append(0.2) # Normal Day (Dark)
                t_week.append(str(day))
        z_data.append(z_week)
        text_data.append(t_week)

    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        y=[f"W{i+1}" for i in range(len(cal_grid))],
        colorscale=[[0, "#1e1e1e"], [0.1, "#2d2d2d"], [0.5, "orange"], [1, "green"]],
        showscale=False, xgap=3, ygap=3
    ))
    
    for i, row in enumerate(text_data):
        for j, val in enumerate(row):
            fig.add_annotation(x=j, y=i, text=val, showarrow=False, font=dict(color="white"))
            
    fig.update_layout(
        title=f"{f_name} - {calendar.month_name[month]}",
        height=300,
        yaxis_autorange='reversed',
        template="plotly_dark",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig
