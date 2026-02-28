import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

# Original Modular Imports (Assumed available in your project structure)
from data_prep import clean_all_data
from forecast_models.moving_avg import run_moving_avg
from forecast_models.decision_tree import run_decision_tree
from forecast_models.knn_model import run_knn
from forecast_models.prophet_model import run_prophet

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Pro Demand Planner v5.0", layout="wide")

# ---------------- STATIC KNOWLEDGE CENTER (IN-DEPTH) ----------------
def show_static_documentation():
    st.title("📖 Comprehensive System Manual")
    
    doc_tabs = st.tabs(["📊 KPI Definitions", "🧠 Model Mechanics", "🛠️ Module Overview"])
    
    with doc_tabs[0]:
        st.subheader("Key Performance Indicators (KPIs)")
        st.markdown("""
        ### 1. Gross Demand
        The raw AI prediction of customer interest before any deductions. It represents the total potential volume.
        
        ### 2. Return Rate (%)
        - **Logic:** The estimated percentage of units that will be returned.
        - **Formula:** $Net Demand = Gross Demand \times (1 - Return\%)$
        - **Business Value:** Prevents over-manufacturing in high-return categories like Fashion.
        
        ### 3. Trend Surge (Multiplier)
        - **Logic:** A user-driven growth factor. 
        - **Values:** 1.0 (Neutral), 1.5 (+50% Surge), 0.8 (-20% Decline).
        
        ### 4. Safety Buffer (%)
        - **Logic:** The "Insurance" stock.
        - **Formula:** $Target = Net Demand \times (1 + Buffer\%)$
        """)

    with doc_tabs[1]:
        st.subheader("Algorithmic Logic")
        st.markdown("""
        ### 1. Prophet (Intelligent Demand)
        Uses an additive regression model. It breaks time-series into:
        - **Trend:** Non-periodic changes.
        - **Seasonality:** Daily, weekly, and yearly cycles.
        - **Holidays:** User-defined spikes.
        
        ### 2. KNN (K-Nearest Neighbors)
        A non-parametric method that finds the 'K' historical days most similar to the target date and uses their average.
        
        ### 3. Decision Tree
        A supervised learning method that uses a tree-like model of decisions. Excellent for identifying if certain factors (like price or marketing) trigger specific demand levels.
        """)

    with doc_tabs[2]:
        st.subheader("Module Functionality")
        st.markdown("""
        - **Data Prep Module:** Cleans date formats, handles null values, and merges disparate files (Marketing, Events, Sales).
        - **Forecast Engine:** A centralized hub that routes your SKU data to the selected math model.
        - **Strategy Overrider:** The layer that takes AI results and applies your manual 'Custom' inputs (Surge, Marketing, Festival Lifts).
        """)
    if st.button("Close Manual"):
        st.session_state.page = "Forecaster"; st.rerun()

# ---------------- MAIN UI ----------------
if 'page' not in st.session_state:
    st.session_state.page = "Forecaster"

pg = st.sidebar.radio("Navigation", ["Forecaster", "Documentation"])

if pg == "Documentation":
    show_static_documentation()
else:
    st.title("📈 Demand Engine & Strategy Simulator")
    
    tab_data, tab_engine, tab_viz = st.tabs(["📤 Data Sources", "🧠 Model Tuning", "📊 Forecast Analytics"])

    # ---------------- TAB 1: DATA SOURCES & INTEGRITY ----------------
    with tab_data:
        st.subheader("1. Data Intake")
        c1, c2, c3 = st.columns(3)
        with c1:
            sales_file = st.file_uploader("Sales History (Required)", type=["csv"])
            sku_master_file = st.file_uploader("SKU Master (Optional)", type=["csv"])
        with c2:
            marketing_file = st.file_uploader("Marketing Spend (Optional)", type=["csv"])
            festival_file = st.file_uploader("Festival Calendar (Optional)", type=["csv"])
        with c3:
            events_file = st.file_uploader("Events / PR (Optional)", type=["csv"])

        st.divider()
        st.subheader("🔍 Data Integrity Check")
        status_cols = st.columns(5)
        files_to_check = [("Sales", sales_file, True), ("SKU Master", sku_master_file, False), ("Marketing", marketing_file, False), ("Festivals", festival_file, False), ("Events", events_file, False)]
        for i, (name, f, req) in enumerate(files_to_check):
            with status_cols[i]:
                if f: st.success(f"**{name}**\nLoaded")
                elif req: st.error(f"**{name}**\nRequired")
                else: st.info(f"**{name}**\nOptional")

        st.divider()
        st.subheader("📥 Download Templates")
        t_cols = st.columns(5)
        t_cols[0].download_button("Sales CSV", "date,sku,sales\n2026-01-01,SKU01,50", "sales.csv")
        t_cols[1].download_button("Master CSV", "sku,category,color,fabric\nSKU01,Topwear,Red,Silk", "master.csv")
        t_cols[2].download_button("Marketing CSV", "date,sku,marketing_spend\n2026-01-01,SKU01,1500", "marketing.csv")
        t_cols[3].download_button("Festival CSV", "date,festival_flag\n2026-12-25,1", "festivals.csv")
        t_cols[4].download_button("Events CSV", "date,event_flag\n2026-06-01,1", "events.csv")

    # ---------------- TAB 2: MODEL TUNING & MULTI-CALENDAR ----------------
    with tab_engine:
        if sales_file:
            df = clean_all_data(sales_file, marketing_file, festival_file, events_file, sku_master_file)
            
            st.subheader("1. Model & Strategy Selection")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                business_type = st.selectbox("Industry Strategy", ["Fashion", "FMCG", "Electronics", "Seasonal", "Custom Strategy"])
                selected_sku = st.selectbox("Select Target SKU", df['sku'].unique())
                sku_df = df[df['sku'] == selected_sku].sort_values('date').copy()
            with col_p2:
                model_choice = st.selectbox("Forecast Algorithm", ["Intelligent Demand Forecast (Prophet)", "Decision Tree", "KNN", "Moving Average"])

            st.divider()
            st.subheader("2. Operational Levers")
            use_default = st.toggle("Use AI-Suggested Settings", value=True)
            col_s1, col_s2, col_s3 = st.columns(3)
            
            if use_default:
                d_returns, d_buffer, d_surge, c_marketing, d_lead = (25 if business_type=="Fashion" else 10), 15, 1.0, 0, 30
            else:
                with col_s1:
                    d_returns = st.number_input("Expected Return Rate (%)", 0, 100, 25)
                    d_buffer = st.number_input("Safety Buffer (%)", 0, 100, 15)
                with col_s2:
                    d_surge = st.number_input("Trend Surge Factor (x)", 0.5, 5.0, 1.0, step=0.1)
                    d_lead = st.number_input("Lead Time (Days)", 1, 365, 30)
                with col_s3:
                    c_marketing = st.number_input("Marketing Lift (%)", 0, 500, 0)

            st.divider()
            st.subheader("3. 📅 Multi-Festival Calendar & Impact Control")
            
            fest_dict = {
                "Christmas": "2026-12-25", "Diwali": "2026-11-08", "Eid": "2026-03-20",
                "Holi": "2026-03-03", "Ganesh Chaturthi": "2026-09-14", "Black Friday": "2026-11-27"
            }
            
            col_f1, col_f2 = st.columns([1, 2])
            with col_f1:
                selected_fests = st.multiselect("Active Festivals", list(fest_dict.keys()), default=["Christmas"])
                st.info("**Customize Impact Strength:**")
                green_lift = st.slider("Peak Day Lift (Green) %", 10, 200, 60)
                orange_lift = st.slider("Window Days Lift (Orange) %", 5, 100, 30)
            
            with col_f2:
                if selected_fests:
                    # Logic to show all months for all selected festivals
                    for f_name in selected_fests:
                        f_date = pd.to_datetime(fest_dict[f_name])
                        year, month = f_date.year, f_date.month
                        cal_grid = calendar.monthcalendar(year, month)
                        impact_window = [f_date - timedelta(days=2), f_date - timedelta(days=1), f_date + timedelta(days=1)]
                        
                        z_data, text_data = [], []
                        for week in cal_grid:
                            z_week, t_week = [], []
                            for day in week:
                                if day == 0:
                                    z_week.append(0); t_week.append("")
                                else:
                                    curr = datetime(year, month, day)
                                    if curr == f_date: z_week.append(2)
                                    elif curr in impact_window: z_week.append(1)
                                    else: z_week.append(0.2)
                                    t_week.append(str(day))
                            z_data.append(z_week); text_data.append(t_week)

                        fig_cal = go.Figure(data=go.Heatmap(
                            z=z_data, x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                            y=[f"W{i+1}" for i in range(len(cal_grid))],
                            colorscale=[[0, "#1e1e1e"], [0.1, "#2d2d2d"], [0.5, "orange"], [1, "green"]],
                            showscale=False, xgap=3, ygap=3
                        ))
                        for i, row in enumerate(text_data):
                            for j, val in enumerate(row):
                                fig_cal.add_annotation(x=j, y=i, text=val, showarrow=False, font=dict(color="white"))
                        fig_cal.update_layout(title=f"{f_name} - {calendar.month_name[month]}", height=300, yaxis_autorange='reversed', template="plotly_dark")
                        st.plotly_chart(fig_cal, use_container_width=True)

    # ---------------- TAB 3: ANALYTICS & COMPARISONS ----------------
    with tab_viz:
        if sales_file and selected_sku:
            # 1. Past Sales Baseline (Last 90 Days)
            past_total = sku_df['sales'].tail(90).sum()
            avg_past = sku_df['sales'].tail(90).mean()

            with st.spinner("Executing Strategy Engine..."):
                if model_choice == "Moving Average": forecast_df = run_moving_avg(sku_df)
                elif model_choice == "Decision Tree": forecast_df = run_decision_tree(sku_df)
                elif model_choice == "KNN": forecast_df = run_knn(sku_df)
                else: forecast_df = run_prophet(sku_df, industry=business_type)

                # Manual Calibration
                for f in selected_fests:
                    if f in fest_dict:
                        t = pd.to_datetime(fest_dict[f])
                        forecast_df.loc[forecast_df['date'] == t, 'forecast'] *= (1 + green_lift/100)
                        forecast_df.loc[forecast_df['date'].isin([t-timedelta(days=2), t-timedelta(days=1), t+timedelta(days=1)]), 'forecast'] *= (1 + orange_lift/100)

                forecast_df['forecast'] *= d_surge * (1 + (c_marketing/100))
                forecast_df['net_demand'] = forecast_df['forecast'] * (1 - (d_returns/100))
                forecast_df['inventory_target'] = forecast_df['net_demand'] * (1 + (d_buffer/100))

                # Comparison Logic
                future_total = forecast_df['forecast'].sum()
                growth_v_past = ((future_total - past_total) / past_total) * 100 if past_total > 0 else 0

            # METRICS WITH COMPARISON %
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Gross Demand Forecast", f"{int(future_total):,}", f"{growth_v_past:+.1f}% vs Past 90d")
            m2.metric("Inventory Target", f"{int(forecast_df['inventory_target'].sum()):,}", f"Buffer: {d_buffer}%")
            m3.metric("Avg Daily Demand", f"{int(forecast_df['forecast'].mean()):,}", f"{((forecast_df['forecast'].mean() - avg_past)/avg_past)*100:+.1f}% vs Avg Past")
            m4.metric("Production Ready By", (datetime.now() + timedelta(days=d_lead)).strftime("%d %b"))

            # VISUALIZATION
            
            sku_df['sales_smooth'] = sku_df['sales'].rolling(window=7, center=True).mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=sku_df['date'], y=sku_df['sales_smooth'], name="Historical (Smooth)", line=dict(color='royalblue', width=3)))
            fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['forecast'], name="Strategy Plan", line=dict(color='#00ffcc', width=4)))
            
            for f in selected_fests:
                if f in fest_dict:
                    t = pd.to_datetime(fest_dict[f])
                    fig.add_vrect(x0=t-timedelta(days=2), x1=t+timedelta(days=1), fillcolor="orange", opacity=0.15, layer="below", line_width=0, annotation_text=f)

            fig.update_layout(template="plotly_dark", hovermode="x unified", title=f"Forecast Strategy vs History: {selected_sku}")
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 Production Execution Schedule")
            st.dataframe(forecast_df[['date', 'forecast', 'net_demand', 'inventory_target']].head(20), use_container_width=True)
            st.download_button("📥 Export Production Plan CSV", forecast_df.to_csv(index=False), "strategy_export.csv")
            
            