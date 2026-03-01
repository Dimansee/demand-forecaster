from modules.forecast_models.moving_avg import run_moving_avg
from modules.forecast_models.decision_tree import run_decision_tree
from modules.forecast_models.knn_model import run_knn
from modules.forecast_models.prophet_model import run_prophet

import pandas as pd
from datetime import timedelta

def learn_seasonality(df):

    df = df.copy()
    df['month'] = df['date'].dt.month

    monthly_avg = df.groupby('month')['sales'].mean()

    overall_avg = monthly_avg.mean()

    seasonality_index = monthly_avg / overall_avg

    return seasonality_index.to_dict()

def run_forecast(df, model_choice, business_type, config=None, forecast_days=30):

    trend_weight = config.get("trend_weight",0.05) if config else 0.05

    df = df.copy().sort_values("date")

    last_date = df["date"].max()

    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=forecast_days,
        freq="D"
    )

    base = df["sales"].tail(14).mean()

    season_index = learn_seasonality(df)

    forecast_vals = []

    for i, d in enumerate(future_dates):
        trend = base * (1 + trend_weight * (i/30))
        month_factor = season_indx.get(d.month,1)
        forecast_vals.append(trend * month_factor)


    return pd.DataFrame({
        "date": future_dates,
        "forecast": forecast_vals
    })
