from modules.forecast_models.moving_avg import run_moving_avg
from modules.forecast_models.decision_tree import run_decision_tree
from modules.forecast_models.knn_model import run_knn
from modules.forecast_models.prophet_model import run_prophet
from datetime import timedelta

def extend_future_dates(df, forecast_df, horizon=30):

    last_date = df['date'].max()

    future_dates = [
        last_date + timedelta(days=i)
        for i in range(1, horizon+1)
    ]

    forecast_df = forecast_df.tail(horizon).copy()
    forecast_df['date'] = future_dates

    return forecast_df

def run_forecast(model_choice, sku_df, industry):
    forecast_df = model_output   # whatever model returns
    forecast_df = extend_future_dates(sku_df, forecast_df)

    return forecast_df
