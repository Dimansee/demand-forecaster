from modules.forecast_models.moving_avg import run_moving_avg
from modules.forecast_models.decision_tree import run_decision_tree
from modules.forecast_models.knn_model import run_knn
from modules.forecast_models.prophet_model import run_prophet

import pandas as pd
from datetime import timedelta

def run_forecast(df, model_choice, business_type, config=None):

    # -------- SAFE CONFIG --------
    trend_weight = config.get("trend_weight", 0.05) if config else 0.05
    marketing_weight = config.get("marketing_weight", 0.5) if config else 0.5

    df = df.copy()
    df = df.sort_values("date")

    last_date = df["date"].max()

    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=30,
        freq="D"
    )

    avg_sales = df["sales"].tail(14).mean()

    # -------- SIMPLE TREND --------
    trend = avg_sales * (1 + trend_weight)

    forecast_values = []

    for i in range(len(future_dates)):
        val = trend * (1 + (i/100))
        forecast_values.append(val)

    forecast_df = pd.DataFrame({
        "date": future_dates,
        "forecast": forecast_values
    })

    return forecast_df
