from modules.forecast_models.moving_avg import run_moving_avg
from modules.forecast_models.decision_tree import run_decision_tree
from modules.forecast_models.knn_model import run_knn
from modules.forecast_models.prophet_model import run_prophet

def run_forecast(data, model_choice, industry):
    forecast = None

    if model_choice == "Moving Average":
        forecast = run_moving_avg(data)

    elif model_choice == "Decision Tree":
        forecast = run_decision_tree(data)

    elif model_choice == "KNN":
        forecast = run_knn(data)

    else:
        forecast = run_prophet(data, industry=industry)

    if forecast is None:
        raise ValueError("Forecast model failed")

    forecast['forecast'] = forecast['forecast'].clip(lower=0)

    return forecast
