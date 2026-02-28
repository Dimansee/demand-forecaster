from forecast_models.moving_avg import run_moving_avg
from forecast_models.decision_tree import run_decision_tree
from forecast_models.knn_model import run_knn
from forecast_models.prophet_model import run_prophet

def run_forecast(model_choice, sku_df, industry):

    if model_choice == "Moving Average":
        return run_moving_avg(sku_df)

    elif model_choice == "Decision Tree":
        return run_decision_tree(sku_df)

    elif model_choice == "KNN":
        return run_knn(sku_df)

    else:
        return run_prophet(sku_df, industry=industry)
