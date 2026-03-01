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

def get_strategy_profile(business_type):

    profiles = {

        "FMCG": {
            "trend_boost": 0.8,
            "season_boost": 1.1,
            "marketing_boost": 1.3
        },

        "Fashion": {
            "trend_boost": 1.2,
            "season_boost": 1.4,
            "marketing_boost": 1.0
        },

        "Electronics": {
            "trend_boost": 1.3,
            "season_boost": 1.1,
            "marketing_boost": 0.8
        },

        "Seasonal": {
            "trend_boost": 1.0,
            "season_boost": 1.6,
            "marketing_boost": 0.9
        },

        "Custom": {
            "trend_boost": 1.0,
            "season_boost": 1.0,
            "marketing_boost": 1.0
        }
    }

    return profiles.get(business_type, profiles["Custom"])

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
    strategy = get_strategy_profile(business_type)

    forecast_vals = []

    for i, d in enumerate(future_dates):
        trend = base * (1 + trend_weight * strategy["trend_boost"] * (i/30))
        month_factor = season_index.get(d.month,1) * strategy["season_boost"]
        forecast_vals.append(trend * month_factor)


    return pd.DataFrame({
        "date": future_dates,
        "forecast": forecast_vals
    })
