import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import io   # ✅ ADDED

# Original Modular Imports
from data_prep import clean_all_data
from forecast_models.moving_avg import run_moving_avg
from forecast_models.decision_tree import run_decision_tree
from forecast_models.knn_model import run_knn
from forecast_models.prophet_model import run_prophet

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Pro Demand Planner v5.5", layout="wide")

# ---------------- AUTO CLEAN ENGINE (ADDED) ----------------
def auto_clean_sales_file(file):
    try:
        file.seek(0)
        df = pd.read_csv(file)

        if df.empty:
            st.error("Uploaded CSV is empty.")
            return None

        df.columns = [c.strip().lower() for c in df.columns]

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
            st.error("❌ 'Date' column missing.")
            return None

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])

        if 'sales' in df.columns:
            df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
        else:
            nums = df.select_dtypes(include=[np.number]).columns
            if len(nums) > 0:
                df = df.rename(columns={nums[0]: 'sales'})
            else:
                df['sales'] = 0

        for col in ['sku', 'product_name', 'order_id']:
            if col not in df.columns:
                df[col] = "Default_SKU" if col == 'sku' else "N/A"

        df = df.groupby(['date', 'sku']).agg({'sales': 'sum'}).reset_index()
        return df

    except Exception as e:
        st.error(f"Auto-Cleaning Error: {e}")
        return None


# ---------------- DOCUMENTATION ----------------
def show_static_documentation():
    st.title("📖 System Documentation")
    t1, t2, t3 = st.tabs(["📊 KPIs", "🧠 Algorithms", "🧼 Data Cleaning"])

    with t1:
        st.markdown("""
        - **Gross Demand** = Raw forecast  
        - **Net Demand** = Gross × (1 - Returns)  
        - **Inventory Target** = Net × (1 + Buffer)
        """)

    with t2:
        st.markdown("""
        - Prophet → Trend + Seasonality  
        - KNN → Similar Day Pattern  
        - Decision Tree → Conditional Demand Drivers
        """)

    with t3:
        st.markdown("""
        Automatically:
        - Cleans headers
        - Detects quantity columns
        - Converts date
        - Aggregates duplicates
        """)

    if st.button("Back"):
        st.session_state.page = "Forecaster"
        st.rerun()


# ---------------- MAIN UI ----------------
if 'page' not in st.session_state:
    st.session_state.page = "Forecaster"

pg = st.sidebar.radio("Navigation", ["Forecaster", "Documentation"])

if pg == "Documentation":
    show_static_documentation()

else:
    st.title("📈 Demand Engine & Strategy Simulator")

    tab_data, tab_engine, tab_viz = st.tabs(
        ["📤 Data Intake", "🧠 Model Tuning", "📊 Forecast Analytics"]
    )

    # ---------------- TAB 1 ----------------
    with tab_data:
        st.subheader("File Upload")

        c1, c2, c3 = st.columns(3)
        with c1:
            sales_file = st.file_uploader("Sales History (Required)", type=["csv"])
            sku_master_file = st.file_uploader("SKU Master", type=["csv"])
        with c2:
            marketing_file = st.file_uploader("Marketing Spend", type=["csv"])
            festival_file = st.file_uploader("Festival Calendar", type=["csv"])
        with c3:
            events_file = st.file_uploader("Events", type=["csv"])

        # ✅ Auto clean preview added
        if sales_file:
            cleaned_sales = auto_clean_sales_file(sales_file)

            if cleaned_sales is not None:
                st.success("✅ Sales Data Verified & Cleaned")
                st.dataframe(cleaned_sales.head(), use_container_width=True)

                buf = io.StringIO()
                cleaned_sales.to_csv(buf, index=False)

                st.download_button(
                    "📥 Download Cleaned CSV",
                    buf.getvalue(),
                    "cleaned_sales.csv",
                    "text/csv"
                )

    # ---------------- TAB 2 ----------------
    with tab_engine:

        if sales_file:

            # ✅ Compatibility logic added
            if 'cleaned_sales' in locals() and cleaned_sales is not None:
                df = cleaned_sales
            else:
                df = clean_all_data(
                    sales_file,
                    marketing_file,
                    festival_file,
                    events_file,
                    sku_master_file
                )

            st.subheader("Model Setup")

            col1, col2 = st.columns(2)

            with col1:
                business_type = st.selectbox("Industry", ["Fashion", "FMCG", "Electronics", "Seasonal"])
                selected_sku = st.selectbox("SKU", df['sku'].unique())
                sku_df = df[df['sku'] == selected_sku].sort_values('date').copy()

            with col2:
                model_choice = st.selectbox("Model", ["Prophet", "Decision Tree", "KNN", "Moving Average"])
                d_lead = st.number_input("Lead Time", 1, 365, 30)

            st.subheader("Strategy Controls")

            c1, c2, c3 = st.columns(3)

            with c1:
                d_returns = st.number_input("Return %", 0, 100, 20)
                d_buffer = st.number_input("Buffer %", 0, 100, 15)

            with c2:
                d_surge = st.number_input("Trend Multiplier", 0.5, 5.0, 1.0)

            with c3:
                c_marketing = st.number_input("Marketing Lift %", 0, 500, 0)

    # ---------------- TAB 3 ----------------
    with tab_viz:

        if sales_file and 'sku_df' in locals():

            if sku_df.empty:
                st.warning("No SKU data available.")
                st.stop()

            if model_choice == "Prophet":
                forecast_df = run_prophet(sku_df, industry=business_type)
            elif model_choice == "Decision Tree":
                forecast_df = run_decision_tree(sku_df)
            elif model_choice == "KNN":
                forecast_df = run_knn(sku_df)
            else:
                forecast_df = run_moving_avg(sku_df)

            forecast_df['forecast'] *= d_surge * (1 + (c_marketing/100))
            forecast_df['net'] = forecast_df['forecast'] * (1 - d_returns/100)
            forecast_df['target'] = forecast_df['net'] * (1 + d_buffer/100)

            past = sku_df['sales'].tail(90).sum()
            future = forecast_df['forecast'].sum()
            growth = ((future - past)/past*100) if past>0 else 0

            m1,m2,m3,m4 = st.columns(4)

            m1.metric("Gross Demand", f"{int(future):,}", f"{growth:+.1f}% vs Past")
            m2.metric("Inventory Target", f"{int(forecast_df['target'].sum()):,}")
            m3.metric("Ready By", (datetime.now()+timedelta(days=d_lead)).strftime("%d %b"))
            m4.metric("Avg Daily", f"{int(forecast_df['forecast'].mean()):,}")

            fig = px.line(forecast_df, x='date', y='forecast', title=f"Forecast: {selected_sku}")
            fig.update_layout(template="plotly_dark")

            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(forecast_df.head(20), use_container_width=True)
