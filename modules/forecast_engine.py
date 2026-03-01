from modules.forecast_models.moving_avg import run_moving_avg
from modules.forecast_models.decision_tree import run_decision_tree
from modules.forecast_models.knn_model import run_knn
from modules.forecast_models.prophet_model import run_prophet

import pandas as pd
from datetime import timedelta
import numpy as np


# -------------------------------
# 1. Learn RECENT Seasonality
# -------------------------------
def learn_seasonality(df):
    df = df.copy()
    # Calculate the global mean of the entire dataset
    global_mean = df['sales'].mean()
    
    # Monthly averages
    monthly_avg = df.groupby(df['date'].dt.month)['sales'].mean()
    
    # Create an index: (Month Avg / Global Avg)
    # If index > 1, it's a peak month. If < 1, it's off-season.
    season_index = monthly_avg / global_mean
    
    return season_index.to_dict()

# -------------------------------
# 2. Detect Demand Phase
# -------------------------------
def detect_season_phase(df):
    # EMA gives a smoother, more reliable trend line
    ema_short = df['sales'].ewm(span=7).mean().iloc[-1]
    ema_long = df['sales'].ewm(span=30).mean().iloc[-1]
    
    diff_pct = (ema_short - ema_long) / ema_long

    if diff_pct > 0.05: # 5% growth momentum
        return "ramp_up"
    elif diff_pct < -0.05:
        return "decline"
    return "stable"


# -------------------------------
# 3. Strategy Profiles
# -------------------------------
def get_strategy_profile(business_type, config=None):

    if business_type == "Custom" and config:
        return {
            "trend_boost": config.get("custom_trend",1.0),
            "season_boost": config.get("custom_season",1.0),
            "marketing_boost": config.get("custom_marketing",1.0)
        }

    profiles = {

        "FMCG": {"trend_boost":0.6,"season_boost":1.2,"marketing_boost":1.3},
        "Fashion": {"trend_boost":1.2,"season_boost":1.4,"marketing_boost":1.0},
        "Electronics": {"trend_boost":1.3,"season_boost":1.1,"marketing_boost":0.8},
        "Seasonal": {"trend_boost":0.8,"season_boost":1.5,"marketing_boost":0.9}
    }

    return profiles.get(business_type, {"trend_boost":1,"season_boost":1,"marketing_boost":1})


# -------------------------------
# 4. Smooth Seasonality Impact
# -------------------------------
def smooth_seasonality(month_factor):
    return 1 + ((month_factor - 1) * 0.6)


# -------------------------------
# 5. Main Forecast Engine
# -------------------------------
def run_forecast(df, model_choice, business_type, config=None, forecast_days=30):
    # 1. Configuration & Strategy Setup
    config = config or {}
    trend_weight = config.get("trend_weight", 0.05)
    strategy = get_strategy_profile(business_type, config)
    
    df = df.copy().sort_values("date")
    last_date = df["date"].max()
    
    # 2. Dynamic Baseline (Use 30-day median to ignore one-off outliers)
    # This prevents a single high-sales day from bloating the entire forecast.
    base_demand = df.tail(30)['sales'].median()

    # 3. Agnostic Seasonality & Phase Detection
    # These functions now look at statistical distribution, not specific months.
    season_index = learn_seasonality(df)
    phase = detect_season_phase(df)

    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=forecast_days,
        freq="D"
    )

    forecast_vals = []
    
    # Historical Cap: Ensure we don't forecast something 2x higher than ever seen
    historical_max = df['sales'].max()

    for i, d in enumerate(future_dates):
        # --- A. Dampened Trend Calculation ---
        # Instead of infinite growth, we apply a 'decay' to the trend
        # so it stabilizes over time rather than spiking.
        dampening = 0.7 
        step_impact = (i + 1) / forecast_days
        
        if phase == "ramp_up":
            # Linear growth based on trend weight and strategy boost
            trend_mod = 1 + (trend_weight * strategy["trend_boost"] * step_impact * dampening)
        elif phase == "decline":
            trend_mod = 1 - (trend_weight * strategy["trend_boost"] * step_impact * dampening)
        else:
            trend_mod = 1.0

        # --- B. Agnostic Seasonality ---
        # Get the multiplier for this month. If no data exists, default to 1.0.
        m_factor = season_index.get(d.month, 1.0)
        
        # Smooth the impact of the strategy's seasonal boost
        # (prevents doubling the demand accidentally)
        strat_season_impact = 1 + ((strategy["season_boost"] - 1) * 0.5)
        
        # --- C. Final Assembly ---
        # Formula: Base * Trend * (Historical Seasonality * Strategy Overlay)
        forecast = base_demand * trend_mod * m_factor * strat_season_impact
        
        # Apply Marketing Boost as a final multiplier
        forecast *= strategy.get("marketing_boost", 1.0)

        # --- D. Sanity Guards ---
        # 1. No negative demand.
        # 2. Cap at 150% of historical max to prevent "algorithmic hallucinations."
        final_val = max(forecast, 0)
        final_val = min(final_val, historical_max * 1.5)
        
        forecast_vals.append(final_val)

    return pd.DataFrame({
        "date": future_dates,
        "forecast": forecast_vals
    })

