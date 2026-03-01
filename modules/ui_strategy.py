import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import calendar
import streamlit as st

def strategy_section(df):

    st.subheader("1. Model & Strategy Selection")

    col1, col2 = st.columns(2)

    with col1:
        business_type = st.selectbox(
            "Industry Strategy",
            ["Fashion","FMCG","Electronics","Seasonal","Custom"]
        )

        selected_sku = st.selectbox("Select Target SKU", df['sku'].unique())

    with col2:
        model_choice = st.selectbox(
            "Forecast Model",
            ["Prophet","Decision Tree","KNN","Moving Average"]
        )

    st.divider()

    st.subheader("2. Operational Levers")

    use_default = st.toggle("Use AI Suggested Settings", value=True)

    if use_default:
        d_returns = 25 if business_type=="Fashion" else 10
        d_buffer = 15
        d_surge = 1.0
        d_marketing = 0
        d_lead = 30

    else:
        col1,col2,col3 = st.columns(3)

        with col1:
            d_returns = st.number_input("Return %",0,100,25)
            d_buffer = st.number_input("Buffer %",0,100,15)

        with col2:
            d_surge = st.number_input("Trend Surge",0.5,5.0,1.0)
            d_lead = st.number_input("Lead Time",1,365,30)

        with col3:
            d_marketing = st.number_input("Marketing Lift %",0,500,0)

    st.divider()
    st.subheader("Advanced model Controls")

    trend_weight = st.slider("Trend sensitivity", 0.01, 0.5, 0.05)
    marketing_weight = st.slider("Marketing Influence", 0.0, 2.0, 0.5)

    st.divider()
    st.subheader("📅 Festival Impact Planning")

    fest_dict = {
        "Christmas": "2026-12-25",
        "Diwali": "2026-11-08",
        "Eid": "2026-03-20",
        "Holi": "2026-03-03",
        "Black Friday": "2026-11-27"
    }

    col_f1, col_f2 = st.columns([1,2])

    with col_f1:
        selected_fests = st.multiselect(
            "Active Festivals",
            list(fest_dict.keys()),
            default=[]
        )

        green_lift = st.slider("Peak Day Lift %", 0, 200, 60)
        orange_lift = st.slider("Window Lift %", 0, 100, 30)

    with col_f2:
        for f_name in selected_fests:
            f_date = pd.to_datetime(fest_dict[f_name])
            year, month = f_date.year, f_date.month
            cal_grid = calendar.monthcalendar(year, month)

            z_data, text_data = [], []

            for week in cal_grid:
                z_week, t_week = [], []
                for day in week:
                    if day == 0:
                        z_week.append(0)
                        t_week.append("")
                    else:
                        curr = datetime(year, month, day)
                        if curr == f_date:
                            z_week.append(2)
                        elif curr in [
                            f_date - timedelta(days=2),
                            f_date - timedelta(days=1),
                            f_date + timedelta(days=1)
                        ]:
                            z_week.append(1)
                        else:
                            z_week.append(0.2)
                        t_week.append(str(day))

                z_data.append(z_week)
                text_data.append(t_week)

            fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
                y=[f"W{i+1}" for i in range(len(cal_grid))],
                colorscale=[[0,"#1e1e1e"],[0.5,"orange"],[1,"green"]],
                showscale=False
            ))

            st.plotly_chart(fig, use_container_width=True)

    forecast_days = st.selectbox(
        "Forecast Horizon",
        [30,60,90,180],
        index = 0
    )

    return {
        "business_type": business_type,
        "selected_sku": selected_sku,
        "model_choice": model_choice,
        "returns": d_returns,
        "buffer": d_buffer,
        "surge": d_surge,
        "marketing": d_marketing,
        "lead": d_lead,
        "trend_weight": trend_weight,
        "marketing_weight": marketing_weight,
        "festivals": selected_fests,
        "green_lift": green_lift,
        "orange_lift": orange_lift,
        "forecast_days":forecast_days
    }
