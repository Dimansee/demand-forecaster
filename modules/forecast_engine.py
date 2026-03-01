from modules.forecast_models.moving_avg import run_moving_avg
from modules.forecast_models.decision_tree import run_decision_tree
from modules.forecast_models.knn_model import run_knn
from modules.forecast_models.prophet_model import run_prophet

import pandas as pd
from datetime import timedelta

def seasonal_multiplier(date, business_type):

    month = date.month

    if business_type == "FMCG":   # Sunscreen-like
        if month in [3,4]:
            return 1.4   # build-up
        elif month in [5,6]:
            return 1.8   # peak
        elif month in [7,8]:
            return 1.2   # taper
        else:
            return 0.8   # winter dip

    if business_type == "Fashion":
        if month in [4,5,10,11]:
            return 1.5
        return 1.0

    if business_type == "Electronics":
        if month in [10,11]:
            return 1.6
        return 1.0

    return 1.0

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

    forecast_vals = []

    for i, d in enumerate(future_dates):

        trend = base * (1 + trend_weight * (i/30))
        season = seasonal_multiplier(d, business_type)

        forecast_vals.append(trend * season)

    return pd.DataFrame({
        "date": future_dates,
        "forecast": forecast_vals
    })
