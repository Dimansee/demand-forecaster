import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import io

# Original Modular Imports
from data_prep import clean_all_data
from forecast_models.moving_avg import run_moving_avg
from forecast_models.decision_tree import run_decision_tree
from forecast_models.knn_model import run_knn
from forecast_models.prophet_model import run_prophet

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Pro Demand Planner v5.2", layout="wide")

# ---------------- AUTO CLEAN FUNCTION (NEW) ----------------
def auto_clean_sales(file):
    try:
        df = pd.read_csv(file)
        df.columns = [c.strip().lower() for c in df.columns]

        rename_map = {
            'date':'date','order date':'date',
            'quantity':'sales','qty':'sales','sales':'sales',
            'sku':'sku','product':'product'
        }
        df = df.rename(columns=rename_map)

        if 'date' not in df.columns:
            st.error("❌ 'Date' column not found")
            return None

        if 'sales' not in df.columns:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols)>0:
                df = df.rename(columns={numeric_cols[0]:'sales'})
            else:
                df['sales']=0

        if 'sku' not in df.columns:
            df['sku']="SKU_DEFAULT"

        if 'product' not in df.columns:
            df['product']="N/A"

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)

        df = df.groupby(['date','sku','product']).agg({'sales':'sum'}).reset_index()
        return df

    except Exception as e:
        st.error(f"Cleaning Error: {e}")
        return None

# ---------------- STATIC KNOWLEDGE CENTER ----------------
def show_static_documentation():
    st.title("📖 Comprehensive System Manual")

    doc_tabs = st.tabs(["📊 KPI Definitions", "🧠 Model Mechanics", "🛠️ Module Overview","🧹 Data Cleaning"])

    with doc_tabs[3]:
        st.subheader("Auto Cleaning Logic")
        st.markdown("""
        - Accepts messy ERP exports
        - Detects Quantity / Qty / Sales automatically
        - Converts all dates
        - Aggregates daily per SKU
        - Prevents model crashes
        """)

    if st.button("Close Manual"):
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

    tab_data, tab_engine, tab_viz = st.tabs(["📤 Data Sources", "🧠 Model Tuning", "📊 Forecast Analytics"])

# ---------------- TAB 1 ----------------
    with tab_data:
        st.subheader("1. Upload Raw Sales File")

        sales_file = st.file_uploader("Upload Raw Sales CSV", type=["csv"])

        cleaned_df=None

        if sales_file:
            cleaned_df = auto_clean_sales(sales_file)

            if cleaned_df is not None:
                st.success("✅ Data Auto-Cleaned")

                c1,c2=st.columns(2)
                with c1:
                    st.dataframe(cleaned_df.head())

                with c2:
                    buf = io.StringIO()
                    cleaned_df.to_csv(buf,index=False)
                    st.download_button("📥 Download Cleaned File",buf.getvalue(),"cleaned_sales.csv")

        st.divider()
        st.subheader("Optional Data")
        sku_master_file = st.file_uploader("SKU Master", type=["csv"])
        marketing_file = st.file_uploader("Marketing Spend", type=["csv"])
        festival_file = st.file_uploader("Festival Calendar", type=["csv"])
        events_file = st.file_uploader("Events / PR", type=["csv"])

# ---------------- TAB 2 ----------------
    with tab_engine:

        if cleaned_df is not None:

            df = clean_all_data(cleaned_df, marketing_file, festival_file, events_file, sku_master_file)

            col1,col2 = st.columns(2)

            with col1:
                selected_sku = st.selectbox("Select SKU", df['sku'].unique())
                sku_df = df[df['sku']==selected_sku].sort_values('date')

            with col2:
                model_choice = st.selectbox("Forecast Algorithm",
                ["Intelligent Demand Forecast (Prophet)","Decision Tree","KNN","Moving Average"])

            d_lead = st.number_input("Lead Time (Days)",1,365,30)

            st.subheader("Festival Impact")
            fest_dict = {"Christmas":"2026-12-25","Diwali":"2026-11-08","Eid":"2026-03-20"}
            selected_fests = st.multiselect("Active Festivals",list(fest_dict.keys()),default=["Christmas"])

            green_lift = st.slider("Peak Lift %",0,200,60)
            orange_lift = st.slider("Window Lift %",0,100,30)

# ---------------- TAB 3 ----------------
    with tab_viz:
        if cleaned_df is not None:

            if model_choice=="Moving Average":
                forecast_df=run_moving_avg(sku_df)
            elif model_choice=="Decision Tree":
                forecast_df=run_decision_tree(sku_df)
            elif model_choice=="KNN":
                forecast_df=run_knn(sku_df)
            else:
                forecast_df=run_prophet(sku_df)

            for f in selected_fests:
                t=pd.to_datetime(fest_dict[f])
                forecast_df.loc[forecast_df['date']==t,'forecast']*= (1+green_lift/100)
                forecast_df.loc[
                    forecast_df['date'].isin([t-timedelta(days=2),t-timedelta(days=1),t+timedelta(days=1)]),
                    'forecast'
                ]*= (1+orange_lift/100)

            past_total=sku_df['sales'].tail(90).sum()
            future_total=forecast_df['forecast'].sum()
            growth=((future_total-past_total)/past_total*100) if past_total>0 else 0

            m1,m2,m3=st.columns(3)
            m1.metric("Gross Demand",int(future_total),f"{growth:+.1f}%")
            m2.metric("Inventory Target",int(future_total*1.1))
            m3.metric("Production Ready",(datetime.now()+timedelta(days=d_lead)).strftime("%d %b"))

            fig=px.line(forecast_df,x='date',y='forecast',title="Forecast Plan")
            st.plotly_chart(fig,use_container_width=True)
            

            
