import streamlit as st
from forecast_engine import run_forecast
from datetime import datetime, timedelta
import plotly.graph_objects as go

def analytics_section(df, config):

    sku_df = df[df['sku'] == config['selected_sku']].sort_values('date')

    forecast_df = run_forecast(
        config['model_choice'],
        sku_df,
        config['business_type']
    )

    forecast_df['forecast'] *= config['surge']
    forecast_df['net'] = forecast_df['forecast'] * (1 - config['returns']/100)
    forecast_df['target'] = forecast_df['net'] * (1 + config['buffer']/100)

    # KPI
    m1,m2,m3,m4 = st.columns(4)

    m1.metric("Gross Demand", int(forecast_df['forecast'].sum()))
    m2.metric("Net Demand", int(forecast_df['net'].sum()))
    m3.metric("Inventory Target", int(forecast_df['target'].sum()))
    m4.metric("Ready By",
        (datetime.now()+timedelta(days=config['lead'])).strftime("%d %b"))

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sku_df['date'], y=sku_df['sales'], name="History"))
    fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['forecast'], name="Forecast"))

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(forecast_df.head(20))

    st.download_button("Download Forecast",
        forecast_df.to_csv(index=False),
        "forecast_output.csv")
