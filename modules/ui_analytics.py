
import streamlit as st
from modules.forecast_engine import run_forecast
from datetime import datetime, timedelta
import plotly.graph_objects as go

def analytics_section(df, config):

    sku_df = df[df['sku'] == config['selected_sku']].sort_values('date')

    forecast_df = run_forecast(
        sku_df,
        config['model_choice'],
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
    sku_df['smooth_sales'] = sku_df['sales'].rolling(7).mean()

    fig = go.Figure()

    # Smoothed History
    fig.add_trace(go.Scatter(
        x=sku_df['date'],
        y=sku_df['smooth_sales'],
        name="Historical Trend",
        line=dict(width=3)
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_df['date'],
        y=forecast_df['forecast'],
        name="Forecast",
        line=dict(width=4)
    ))

    # Forecast Start Marker
    forecast_start = forecast_df['date'].min().to_pydatetime()

    fig.add_vline(
        x=forecast_start,
        line_dash="dash",
        line_width=2
    )

    fig.add_annotation(
        x=forecast_start,
        y=max(forecast_df['forecast']),
        text="Forecast Start",
        showarrow=True,
        arrowhead=1
    )

    fig.update_layout(
        title="Demand Trend vs Forecast",
        hovermode="x unified",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)
