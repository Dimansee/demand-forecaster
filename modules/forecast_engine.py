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

    if model_choice == "Moving Average":
        return run_moving_avg(sku_df)

    elif model_choice == "Decision Tree":
        return run_decision_tree(sku_df)

    elif model_choice == "KNN":
        return run_knn(sku_df)

    else:
        return run_prophet(sku_df, industry=industry)
