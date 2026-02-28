# forecast_engine.py
from forecast_models.moving_avg import run_moving_avg
from forecast_models.decision_tree import run_decision_tree
from forecast_models.knn_model import run_knn
from forecast_models.prophet_model import run_prophet

def get_forecast(df, selected_sku, model_choice, business_type):
    # CRITICAL: Filter data for the specific SKU first
    sku_df = df[df['sku'] == selected_sku].copy()
    
    if model_choice == "Moving Average": 
        return run_moving_avg(sku_df)
    elif model_choice == "Decision Tree": 
        return run_decision_tree(sku_df)
    elif model_choice == "KNN": 
        return run_knn(sku_df)
    else: 
        return run_prophet(sku_df, industry=business_type)
