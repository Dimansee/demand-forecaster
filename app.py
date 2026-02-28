import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import io

# Original Modular Imports (Assumed available in your project structure)
from data_prep import clean_all_data
from forecast_models.moving_avg import run_moving_avg
from forecast_models.decision_tree import run_decision_tree
from forecast_models.knn_model import run_knn
from forecast_models.prophet_model import run_prophet

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Pro Demand Planner v5.4", layout="wide")

# --- NEW: ADVANCED AUTO-CLEANING ENGINE ---
def auto_clean_sales_file(file):
    try:
        df = pd.read_csv(file)
        # 1. Standardize column names (lowercase and stripped)
        df.columns = [c.strip().lower() for c in df.columns]
        
        # 2. Flexible Mapping for required fields
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
            st.error("❌ 'Date' column missing in Sales CSV.")
            return None

        # 3. Type Conversion & Cleaning
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date']) 
        
        if 'sales' in df.columns:
            df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
        else:
            df['sales'] = 0

        # Fill optional columns with "N/A" if they don't exist
        for col in ['sku', 'product_name', 'order_id']:
            if col not in df.columns:
                df[col] = "N/A"

        # 4. Aggregation to Daily SKU level
        df = df.groupby(['date', 'sku']).agg({'sales': 'sum'}).reset_index()
        return df
    except Exception as e:
        st.error(f"Auto-Cleaning Error: {e}")
        return None

# ---------------- STATIC KNOWLEDGE CENTER (IN-DEPTH) ----------------
def show_static_documentation():
    st.title("📖 Comprehensive System Manual")
    
    doc_tabs = st.tabs(["📊 KPI Definitions", "🧠 Model Mechanics", "🛠️ Module Overview", "🧼 Data Cleaning Logic"])
    
    with doc_tabs[0]:
        st.subheader("Key Performance Indicators (KPIs)")
        st.markdown("""
        ### 1. Gross Demand
        The raw AI prediction of customer interest before any deductions. It represents the total potential volume.
        
        ### 2. Return Rate (%)
        - **Logic:** The estimated percentage of units that will be returned.
        - **Formula:** $Net Demand = Gross Demand \times (1 - Return\%)$
        
        ### 3. Trend Surge (Multiplier)
        - **Logic:** A user-driven growth factor for scaling predictions.
        
        ### 4. Safety Buffer (%)
        - **Logic:** The "Insurance" stock to prevent stockouts.
        """)

    with doc_tabs[1]:
        st.subheader("Algorithmic Logic")
        st.markdown("""
        ### 1. Prophet (Intelligent Demand)
        Uses an additive regression model. It breaks time-series into Trend, Seasonality, and Holidays.
        
        ### 2. KNN (K-Nearest Neighbors)
        Finds 'K' historical days most similar to the target date.
        
        ### 3. Decision Tree
        A tree-like model that identifies how factors like marketing trigger specific demand levels.
        """)

    with doc_tabs[2]:
        st.subheader("Module Functionality")
        st.markdown("""
        - **Data Prep Module:** Cleans date formats and merges disparate files.
        - **Forecast Engine:** Routes data to the selected model.
        - **Strategy Overrider:** Applies manual 'Custom' inputs (Festival Lifts).
        """)

    with doc_tabs[3]:
        st.subheader("Auto-Cleaning Protocols")
        st.markdown("""
        - **Standardization:** Automatically handles 'Date' vs 'date' vs 'DATE'.
        - **Deduplication:** Sums multiple quantities sold on the same day for a single SKU.
        - **Safety:** Converts non-numeric sales entries to 0 to prevent model failure.
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
        st.subheader("🔍 Data Integrity & Auto-Cleaning")
        if sales_file:
            cleaned_sales = auto_clean_sales_file(sales_file)
            if cleaned_sales is not None:
                st.success("✅ Sales Data Cleaned Successfully")
                st.write("Preview of Cleaned Data:")
                st.dataframe(cleaned_sales.head(5), use_container_width=True)
                
                # New: Download Cleaned Data for verification
                csv_buffer = io.StringIO()
                cleaned_sales.to_csv(csv_buffer, index=False)
                st.download_button("📥 Download Cleaned Sales File for Verification", csv_buffer.getvalue(), "cleaned_sales.csv", "text/csv")
        
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
        t_cols[0].download_button("Sales Template", "date,sku,sales,order_number\n2026-01-01,SKU01,50,ORD123", "sales.csv")
        t_cols[1].download_button("Master Template", "sku,category,product\nSKU01,Topwear,Shirt", "master.csv")
        t_cols[2].download_button("Marketing Template", "date,sku,spend\n2026-01-01,SKU01,1500", "marketing.csv")
        t_cols[3].download_button("Festival Template", "date,festival_name\n2026-12-25,Christmas", "festivals.csv")
        t_cols[4].download_button("Events Template", "date,event_type\n2026-06-01,Launch", "events.csv")

    # ---------------- TAB 2: MODEL TUNING & MULTI-CALENDAR ----------------
    with tab_engine:
        if sales_file and 'cleaned_sales' in locals():
            # Merging additional data using your data_prep logic
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
            past_total = sku_df['sales'].tail(90).sum()
            avg_past = sku_df['sales'].tail(90).mean()

            with st.spinner("Executing Strategy Engine..."):
                if model_choice == "Moving Average": forecast_df = run_moving_avg(sku_df)
                elif model_choice == "Decision Tree": forecast_df = run_decision_tree(sku_df)
                elif model_choice == "KNN": forecast_df = run_knn(sku_df)
                else: forecast_df = run_prophet(sku_df, industry=business_type)

                for f in selected_fests:
                    if f in fest_dict:
                        t = pd.to_datetime(fest_dict[f])
                        forecast_df.loc[forecast_df['date'] == t, 'forecast'] *= (1 + green_lift/100)
                        forecast_df.loc[forecast_df['date'].isin([t-timedelta(days=2), t-timedelta(days=1), t+timedelta(days=1)]), 'forecast'] *= (1 + orange_lift/100)

                forecast_df['forecast'] *= d_surge * (1 + (c_marketing/100))
                forecast_df['net_demand'] = forecast_df['forecast'] * (1 - (d_returns/100))
                forecast_df['inventory_target'] = forecast_df['net_demand'] * (1 + (d_buffer/100))

                future_total = forecast_df['forecast'].sum()
                growth_v_past = ((future_total - past_total) / past_total) * 100 if past_total > 0 else 0

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Gross Demand Forecast", f"{int(future_total):,}", f"{growth_v_past:+.1f}% vs Past 90d")
            m2.metric("Inventory Target", f"{int(forecast_df['inventory_target'].sum()):,}", f"Buffer: {d_buffer}%")
            m3.metric("Avg Daily Demand", f"{int(forecast_df['forecast'].mean()):,}", f"{((forecast_df['forecast'].mean() - avg_past)/avg_past)*100:+.1f}% vs Avg Past")
            m4.metric("Production Ready By", (datetime.now() + timedelta(days=d_lead)).strftime("%d %b"))

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
