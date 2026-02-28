import streamlit as st
from data_cleaning import clean_all_data
from ui_components import data_upload_ui, model_config_ui, show_forecast_dashboard
from documentation import show_static_documentation

st.set_page_config(page_title="Pro Demand Planner v5.0", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = "Forecaster"

pg = st.sidebar.radio("Navigation", ["Forecaster", "Documentation"])

if pg == "Documentation":
    show_static_documentation()

else:
    st.title("📈 Demand Engine & Strategy Simulator")

    tab_data, tab_engine, tab_viz = st.tabs(["📤 Data Sources", "🧠 Model Tuning", "📊 Forecast Analytics"])

    with tab_data:
        uploaded_files = data_upload_ui()

    with tab_engine:
        if uploaded_files['sales_file']:
            df = clean_all_data(**uploaded_files)
            model_config = model_config_ui(df)

    with tab_viz:
        if uploaded_files['sales_file'] and 'model_config' in locals():
            show_forecast_dashboard(df, model_config)
