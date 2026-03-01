from modules.forecast_models.moving_avg import run_moving_avg
from modules.forecast_models.decision_tree import run_decision_tree
from modules.forecast_models.knn_model import run_knn
from modules.forecast_models.prophet_model import run_prophet

import pandas as pd
from datetime import timedelta
import numpy as np


# -------------------------------
# 1. Learn RECENT Seasonality
# -------------------------------
def learn_seasonality(df, lookback_days=180):

    df = df.copy()
    df = df.sort_values("date")

    recent_df = df[df['date'] >= df['date'].max() - pd.Timedelta(days=lookback_days)]

    recent_df['month'] = recent_df['date'].dt.month

    monthly_avg = recent_df.groupby('month')['sales'].mean()
    overall_avg = monthly_avg.mean()

    seasonality_index = monthly_avg / overall_avg

    return seasonality_index.to_dict()


# -------------------------------
# 2. Detect Demand Phase
# -------------------------------
def detect_season_phase(df):

    last_60 = df.tail(60)['sales']

    if len(last_60) < 20:
        return "stable"

    slope = last_60.diff().mean()

    if slope > 0.5:
        return "ramp_up"
    elif slope < -0.5:
        return "decline"
    else:
        return "stable"


# -------------------------------
# 3. Strategy Profiles
# -------------------------------
def get_strategy_profile(business_type, config=None):

    if business_type == "Custom" and config:
        return {
            "trend_boost": config.get("custom_trend",1.0),
            "season_boost": config.get("custom_season",1.0),
            "marketing_boost": config.get("custom_marketing",1.0)
        }

    profiles = {

        "FMCG": {"trend_boost":0.6,"season_boost":1.2,"marketing_boost":1.3},
        "Fashion": {"trend_boost":1.2,"season_boost":1.4,"marketing_boost":1.0},
        "Electronics": {"trend_boost":1.3,"season_boost":1.1,"marketing_boost":0.8},
        "Seasonal": {"trend_boost":0.8,"season_boost":1.5,"marketing_boost":0.9}
    }

    return profiles.get(business_type, {"trend_boost":1,"season_boost":1,"marketing_boost":1})


# -------------------------------
# 4. Smooth Seasonality Impact
# -------------------------------
def smooth_seasonality(month_factor):
    return 1 + ((month_factor - 1) * 0.6)


# -------------------------------
# 5. Main Forecast Engine
# -------------------------------
def run_forecast(df, model_choice, business_type, config=None, forecast_days=30):

    trend_weight = config.get("trend_weight",0.05) if config else 0.05

    df = df.copy().sort_values("date")

    last_date = df["date"].max()

    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=forecast_days,
        freq="D"
    )

    # --- Base Demand = weighted recent avg ---
    recent = df.tail(60)['sales']
    base = recent.median()

    # --- Learn seasonality ---
    season_index = learn_seasonality(df)

    # --- Detect phase ---
    phase = detect_season_phase(df)

    # --- Strategy ---
    strategy = get_strategy_profile(business_type, config)

    forecast_vals = []

    for i, d in enumerate(future_dates):

        # ------------------------
        # Phase-aware trend
        # ------------------------
        if phase == "ramp_up":
            trend = base * (1 + trend_weight * strategy["trend_boost"] * (i/20))

        elif phase == "decline":
            trend = base * (1 - trend_weight * strategy["trend_boost"] * (i/25))

        else:  # stable
            trend = base

        # ------------------------
        # Seasonality
        # ------------------------
        month_factor = season_index.get(d.month, 1)
        month_factor = smooth_seasonality(month_factor)
        month_factor *= strategy["season_boost"]

        forecast = trend * month_factor

        forecast_vals.append(max(forecast,0))  # prevent negative demand


    return pd.DataFrame({
        "date": future_dates,
        "forecast": forecast_vals
    })
