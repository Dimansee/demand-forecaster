from forecast_models.moving_avg import run_moving_avg
from forecast_models.decision_tree import run_decision_tree
from forecast_models.knn_model import run_knn
from forecast_models.prophet_model import run_prophet

def get_forecast(df, model_choice, business_type):
    if model_choice == "Moving Average": return run_moving_avg(df)
    if model_choice == "Decision Tree": return run_decision_tree(df)
    if model_choice == "KNN": return run_knn(df)
    return run_prophet(df, industry=business_type)
