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
