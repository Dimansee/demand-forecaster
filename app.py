import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import io

# Modular Imports (Ensure these files are in your GitHub repo)
from data_prep import clean_all_data
from forecast_models.moving_avg import run_moving_avg
from forecast_models.decision_tree import run_decision_tree
from forecast_models.knn_model import run_knn
from forecast_models.prophet_model import run_prophet

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Pro Demand Planner v5.2", layout="wide")

# --- AUTOMATIC DATA CLEANING ENGINE ---
def auto_clean_sales_file(file):
    try:
        df = pd.read_csv(file)
        # Standardize columns to lowercase and remove spaces
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Flexible Mapping for Date and Sales/Quantity
        rename_map = {
            'date': 'date', 
            'quantity': 'sales', 
            'qty': 'sales', 
            'sales': 'sales',
            'product': 'product_name',
            'order number': 'order_id'
        }
        df = df.rename(columns=rename_map)

        if 'date' not in df.columns:
            st.error("❌ Error: 'Date' column not found. Please check your CSV headers.")
            return None

        # Convert Date and handle errors
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date']) 
        
        # Ensure Sales is numeric
        if 'sales' in df.columns:
            df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
        else:
            df['sales'] = 0

        # Fill optional columns if missing to prevent code crashes
        for col in ['sku', 'product_name', 'order_id']:
            if col not in df.columns:
                df[col] = "N/A"

        # Aggregation: Sum sales by Date and SKU
        df = df.groupby(['date', 'sku']).agg({'sales': 'sum'}).reset_index()
        return df
    except Exception as e:
        st.error(f"Cleaning Error: {e}")
        return None

# ---------------- STATIC DOCUMENTATION ----------------
def show_static_documentation():
    st.title("📖 Comprehensive System Manual")
    doc_tabs = st.tabs(["📊 KPI & Metrics", "🧠 Model Mechanics", "🛠️ Data Cleaning Logic"])
    
    with doc_tabs[0]:
        st.subheader("Key Performance Indicators (KPIs)")
        st.markdown("""
        * **Gross Demand**: The total predicted units before any returns or buffers are applied.
        * **Growth % vs Past**: A direct comparison of the 90-day forecast against the last 90 days of history.
        * **Production Ready Date**: Calculated as `Today + Lead Time`. Tells you when to start manufacturing.
        """)

    with doc_tabs[1]:
        st.subheader("Algorithmic Breakdown")
        st.markdown("""
        * **Prophet**: Uses additive regression to find seasonal patterns and holiday spikes.
        * **KNN**: Finds historical days with similar features (month, festival proximity) to predict future values.
        """)

    with doc_tabs[2]:
        st.subheader("Auto-Cleaning Module")
        st.markdown("""
        * **Standardization**: Automatically converts 'Date' or 'date' or 'DATE' into a standard format.
        * **Deduplication**: If an SKU has multiple orders on one day, the system sums the quantity.
        * **Verification**: Allows you to download the "Cleaned" file before running the AI.
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
    st.title("📦 Pro Demand Forecasting Engine v5.2")
    
    tab_data, tab_engine, tab_viz = st.tabs(["📤 Data Intake", "🧠 Strategy Tuning", "📊 Analytics"])

    # ---------------- TAB 1: DATA INTAKE & AUTO-CLEAN ----------------
    with tab_data:
        st.subheader("1. Upload & Verify Sales Data")
        sales_file = st.file_uploader("Upload Sales CSV (Date, SKU, Quantity/Sales...)", type=["csv"])
        
        if sales_file:
            # Execute Auto-Cleaning
            cleaned_df = auto_clean_sales_file(sales_file)
            
            if cleaned_df is not None:
                st.success("✅ Data Cleaned & Standardized Automatically")
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write("Preview of Cleaned Dataset:")
                    st.dataframe(cleaned_df.head(10), use_container_width=True)
                with c2:
                    # Verification Download Button
                    csv_buffer = io.StringIO()
                    cleaned_df.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label="📥 Download Cleaned File for Verification",
                        data=csv_buffer.getvalue(),
                        file_name="verified_cleaned_data.csv",
                        mime="text/csv"
                    )
        
        st.divider()
        st.subheader("2. Metadata & Templates")
        t_cols = st.columns(3)
        t_cols[0].download_button("Download Sales Template", "Date,SKU,Quantity,Order Number\n2026-01-01,SKU01,50,ORD101", "template.csv")

    # ---------------- TAB 2: MODEL TUNING & MULTI-CALENDAR ----------------
    with tab_engine:
        if sales_file and 'cleaned_df' in locals():
            st.subheader("1. Strategy Configuration")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                business_type = st.selectbox("Industry Strategy", ["Fashion", "FMCG", "Electronics", "Seasonal"])
                selected_sku = st.selectbox("Select SKU to Forecast", cleaned_df['sku'].unique())
                sku_df = cleaned_df[cleaned_df['sku'] == selected_sku].sort_values('date').copy()
            with col_p2:
                model_choice = st.selectbox("Forecast Algorithm", ["Prophet", "Decision Tree", "KNN", "Moving Average"])
                d_lead = st.number_input("Lead Time (Days)", 1, 365, 30)

            st.divider()
            st.subheader("2. Operational Settings")
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                d_returns = st.number_input("Return Rate %", 0, 100, 25)
                d_buffer = st.number_input("Safety Buffer %", 0, 100, 15)
            with col_s2:
                d_surge = st.number_input("Trend Surge (x)", 0.5, 5.0, 1.0)
            with col_s3:
                c_marketing = st.number_input("Marketing Lift %", 0, 500, 0)

            st.divider()
            st.subheader("3. 📅 Multi-Festival Calendar & Impact")
            
            fest_dict = {"Christmas": "2026-12-25", "Diwali": "2026-11-08", "Eid": "2026-03-20", "Holi": "2026-03-03"}
            col_f1, col_f2 = st.columns([1, 2])
            with col_f1:
                selected_fests = st.multiselect("Active Festivals", list(fest_dict.keys()), default=["Christmas"])
                green_lift = st.slider("Peak Day Lift %", 0, 200, 60)
                orange_lift = st.slider("Window Days Lift %", 0, 100, 30)
            
            with col_f2:
                # Loop through all selected festivals to show multiple calendars
                for f_name in selected_fests:
                    f_date = pd.to_datetime(fest_dict[f_name])
                    year, month = f_date.year, f_date.month
                    cal_grid = calendar.monthcalendar(year, month)
                    impact_window = [f_date - timedelta(days=2), f_date - timedelta(days=1), f_date + timedelta(days=1)]
                    
                    z_data, text_data = [], []
                    for week in cal_grid:
                        z_week, t_week = [], []
                        for day in week:
                            if day == 0: z_week.append(0); t_week.append("")
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

    # ---------------- TAB 3: ANALYTICS ----------------
    with tab_viz:
        if sales_file and 'sku_df' in locals():
            # Comparison Baseline
            past_90_sum = sku_df['sales'].tail(90).sum()
            
            # Forecast Execution
            if model_choice == "Prophet": forecast_df = run_prophet(sku_df, industry=business_type)
            elif model_choice == "KNN": forecast_df = run_knn(sku_df)
            else: forecast_df = run_moving_avg(sku_df)

            # Apply Festival Lifts
            for f in selected_fests:
                t = pd.to_datetime(fest_dict[f])
                forecast_df.loc[forecast_df['date'] == t, 'forecast'] *= (1 + green_lift/100)
                forecast_df.loc[forecast_df['date'].isin([t-timedelta(days=2), t-timedelta(days=1), t+timedelta(days=1)]), 'forecast'] *= (1 + orange_lift/100)

            # Final Math
            forecast_df['forecast'] *= d_surge * (1 + (c_marketing/100))
            forecast_df['net_demand'] = forecast_df['forecast'] * (1 - (d_returns/100))
            forecast_df['target'] = forecast_df['net_demand'] * (1 + (d_buffer/100))

            # Growth Comparison Logic
            future_sum = forecast_df['forecast'].sum()
            growth_pct = ((future_sum - past_90_sum) / past_90_sum * 100) if past_90_sum > 0 else 0

            # METRICS WITH COMPARISONS
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Gross Demand", f"{int(future_sum):,}", f"{growth_pct:+.1f}% vs Past 90d")
            m2.metric("Inventory Goal", f"{int(forecast_df['target'].sum()):,}", f"Buffer: {d_buffer}%")
            m3.metric("Lead Time Readiness", (datetime.now() + timedelta(days=d_lead)).strftime("%d %b"))
            m4.metric("Avg Daily Demand", f"{int(forecast_df['forecast'].mean()):,}")

            # CHART
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=sku_df['date'], y=sku_df['sales'], name="History", line=dict(color='royalblue')))
            fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['forecast'], name="Forecast", line=dict(color='#00ffcc')))
            
            for f in selected_fests:
                t = pd.to_datetime(fest_dict[f])
                fig.add_vrect(x0=t-timedelta(days=2), x1=t+timedelta(days=1), fillcolor="orange", opacity=0.1, line_width=0)

            fig.update_layout(template="plotly_dark", title="Demand Outlook")
            st.plotly_chart(fig, use_container_width=True)
            st.download_button("Export Final Plan", forecast_df.to_csv(index=False), "demand_plan.csv")
