import streamlit as st
from data_cleaning import auto_clean_sales_file, get_data_health_report
from logic_overrides import apply_strategy_modifiers, apply_festival_impact
from forecast_engine import get_forecast
from ui_components import show_static_documentation

st.set_page_config(page_title="Pro Demand Planner v5.6", layout="wide")

# State Management
if 'page' not in st.session_state: st.session_state.page = "Forecaster"

pg = st.sidebar.radio("Navigation", ["Forecaster", "Documentation"])

if pg == "Documentation":
    show_static_documentation()
else:
    st.title("📈 Demand Engine")
    tab_data, tab_engine, tab_viz = st.tabs(["📤 Data", "🧠 Tuning", "📊 Analytics"])

    with tab_data:
        sales_file = st.file_uploader("Upload Sales CSV", type=["csv"])
        if sales_file:
            cleaned_sales = auto_clean_sales_file(sales_file)
            if cleaned_sales is not None:
                st.session_state['data'] = cleaned_sales
                st.success("Data loaded and cleaned!")
                
    with tab_engine:
        if 'data' in st.session_state:
            df = st.session_state['data']
            sku = st.selectbox("Select SKU", df['sku'].unique())
            model = st.selectbox("Algorithm", ["Prophet", "KNN", "Decision Tree", "Moving Average"])
            st.session_state['active_sku'] = df[df['sku'] == sku].copy()
        else:
            st.info("Please upload data in the first tab.")

    with tab_viz:
        if 'active_sku' in st.session_state:
            # Execute forecasting logic here calling logic_overrides and forecast_engine
            st.write(f"Generating analytics for {sku}...")
