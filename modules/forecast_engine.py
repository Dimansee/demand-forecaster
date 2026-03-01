import pandas as pd
import numpy as np
from datetime import timedelta

def run_forecast(df, model_choice, business_type, config=None, forecast_days=30):
    config = config or {}
    df = df.copy().sort_values("date")
    
    # 1. PRE-PROCESS: Clean extreme noise
    df['sales'] = df['sales'].clip(upper=df['sales'].quantile(0.98)) #

    # 2. LEARN: Time-Weighted DNA
    # Give 2x more importance to the last 3 months than the start of the year
    weights = np.linspace(0.5, 1.0, len(df)) #
    global_mean = np.average(df['sales'], weights=weights)
    
    # Learn Day-of-Week Patterns (e.g., Weekend vs Weekday)
    dow_map = (df.groupby(df['date'].dt.dayofweek)['sales'].mean() / global_mean).to_dict() #
    
    # Learn Monthly Seasonality
    month_map = (df.groupby(df['date'].dt.month)['sales'].mean() / global_mean).to_dict() #

    # 3. BASELINE: Use Exponential Moving Average (EMA)
    # EMA is more accurate than a simple median as it tracks recent momentum
    base_demand = df['sales'].ewm(span=14).mean().iloc[-1] 

    last_date = df["date"].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days)
    
    forecast_vals = []
    
    for i, d in enumerate(future_dates):
        # A. Weekly & Monthly DNA
        val = base_demand * dow_map.get(d.dayofweek, 1.0) * month_map.get(d.month, 1.0) #
        
        # B. Event 'Halo' Effect (Proximity Logic)
        event_boost = 1.0
        if d.month == 12 and 15 <= d.day <= 24: event_boost = 1.25 # Pre-Christmas
        if d.month == 11 and 20 <= d.day <= 30: event_boost = 1.35 # Black Friday Window
        
        # C. Strategy Overlay
        strat = get_strategy_profile(business_type, config) #
        val = val * event_boost * strat.get("marketing", 1.0)
        
        # D. Sanity Guard
        forecast_vals.append(max(val, 0))

    return pd.DataFrame({"date": future_dates, "forecast": forecast_vals})

def get_strategy_profile(business_type, config):
    # Enhanced profiles based on your uploaded business type
    profiles = {
        "FMCG": {"marketing": 1.15},
        "Fashion": {"marketing": 1.25},
        "Electronics": {"marketing": 1.05},
        "Seasonal": {"marketing": 1.40}
    }
    return profiles.get(business_type, {"marketing": 1.0})
