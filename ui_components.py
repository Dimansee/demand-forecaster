import streamlit as st
from forecast_engine import run_forecast
from datetime import datetime, timedelta

def data_upload_ui():

    c1, c2, c3 = st.columns(3)

    with c1:
        sales_file = st.file_uploader("Sales History", type=["csv"])
        sku_master_file = st.file_uploader("SKU Master", type=["csv"])

    with c2:
        marketing_file = st.file_uploader("Marketing Spend", type=["csv"])
        festival_file = st.file_uploader("Festival Calendar", type=["csv"])

    with c3:
        events_file = st.file_uploader("Events", type=["csv"])

    return {
        "sales_file": sales_file,
        "sku_master_file": sku_master_file,
        "marketing_file": marketing_file,
        "festival_file": festival_file,
        "events_file": events_file
    }


def model_config_ui(df):

    selected_sku = st.selectbox("Select SKU", df['sku'].unique())
    model_choice = st.selectbox("Forecast Model",
        ["Prophet", "Decision Tree", "KNN", "Moving Average"])

    return {
        "selected_sku": selected_sku,
        "model_choice": model_choice
    }


def show_forecast_dashboard(df, config):

    sku_df = df[df['sku'] == config['selected_sku']].sort_values('date')

    forecast_df = run_forecast(config['model_choice'], sku_df, industry="Custom")

    st.metric("Forecast Total", int(forecast_df['forecast'].sum()))
    st.dataframe(forecast_df.head(20))
