import streamlit as st
import pandas as pd
import io
from data_cleaning import auto_clean_sales_file, get_data_health_report
from logic_overrides import apply_overrides, apply_festival_impact, FESTIVAL_DICT
from ui_components import show_static_documentation, render_cal
from forecast_engine import get_forecast

st.set_page_config(page_title="Pro Demand Planner v5.6", layout="wide")

if 'page' not in st.session_state: st.session_state.page = "Forecaster"
pg = st.sidebar.radio("Navigation", ["Forecaster", "Documentation"])

if pg == "Documentation":
    show_static_documentation()
else:
    st.title("📈 Demand Engine & Strategy Simulator")
    tab_data, tab_engine, tab_viz = st.tabs(["📤 Data Sources", "🧠 Model Tuning", "📊 Analytics"])

    with tab_data:
        sales_file = st.file_uploader("Sales History (Required)", type=["csv"])
        if sales_file:
            cleaned_sales = auto_clean_sales_file(sales_file)
            if cleaned_sales is not None:
                st.session_state['cleaned_data'] = cleaned_sales
                health = get_data_health_report(cleaned_sales)
                # Display Metrics...
                h1, h2, h3 = st.columns(3)
                h1.metric("SKUs Found", health['unique_skus'])
                h2.metric("Missing Days", health['missing_days'])
                h3.metric("Zero Sales", health['zero_days'])

    with tab_engine:
        if 'cleaned_data' in st.session_state:
            df = st.session_state['cleaned_data']
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                biz_type = st.selectbox("Industry", ["Fashion", "FMCG", "Electronics"])
                target_sku = st.selectbox("Select SKU", df['sku'].unique())
                sku_df = df[df['sku'] == target_sku].copy()
            with col_p2:
                model_choice = st.selectbox("Algorithm", ["Prophet", "KNN", "Decision Tree"])
            
            # Festival UI
            selected_fests = st.multiselect("Active Festivals", list(FESTIVAL_DICT.keys()))
            for f in selected_fests:
                st.plotly_chart(render_cal(f, FESTIVAL_DICT[f]))
        else:
            st.warning("Upload data first.")

    with tab_viz:
        if 'cleaned_data' in st.session_state and 'sku_df' in locals():
            # Run Engine
            raw_forecast = get_forecast(sku_df, model_choice, biz_type)
            # Apply Lifts
            raw_forecast = apply_festival_impact(raw_forecast, selected_fests, 60, 30)
            # Apply Overrides (Sliders would be defined in tab_engine)
            final_df = apply_overrides(raw_forecast, 1.0, 0, 25, 15)
            
            st.plotly_chart(px.line(final_df, x='date', y='forecast'))
            st.dataframe(final_df)
