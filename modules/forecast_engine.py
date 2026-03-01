import pandas as pd
import numpy as np
from datetime import timedelta

def run_forecast(df, model_choice, business_type, config=None, forecast_days=30):
    """
    Generic Forecast Engine: Agnostic to product type.
    Uses dampened seasonality and momentum-based trend detection.
    """
    # 1. Configuration & Strategy Setup
    config = config or {}
    trend_weight = config.get("trend_weight", 0.05)
    strategy = get_strategy_profile(business_type, config)
    
    df = df.copy().sort_values("date")
    last_date = df["date"].max()
    
    # 2. Dynamic Baseline 
    # Use a 14-day median to establish a stable 'starting point' that ignores spikes
    base_demand = df.tail(14)['sales'].median()

    # 3. Component Analysis
    # Calculates monthly index (Sales_Month / Sales_Avg) and detects trend momentum
    season_index = learn_seasonality(df)
    phase = detect_season_phase(df)

    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=forecast_days,
        freq="D"
    )

    forecast_vals = []
    
    # Guardrail: Never let the forecast exceed 150% of the highest historical point
    historical_max = df['sales'].max()

    for i, d in enumerate(future_dates):
        # --- A. Dampened Trend ---
        # Instead of growing forever, we apply a dampening factor (0.7)
        # to ensure the trend remains realistic over time.
        dampening = 0.7 
        step_progress = (i + 1) / forecast_days
        
        if phase == "ramp_up":
            trend_mod = 1 + (trend_weight * strategy["trend_boost"] * step_progress * dampening)
        elif phase == "decline":
            trend_mod = 1 - (trend_weight * strategy["trend_boost"] * step_progress * dampening)
        else:
            trend_mod = 1.0

        # --- B. Agnostic Seasonality ---
        # Retrieves the index for the specific month (e.g., if Jan = 0.9, demand is lower)
        m_factor = season_index.get(d.month, 1.0)
        
        # Soften the impact of strategy boosts to prevent "compounding explosion"
        strat_season_impact = 1 + ((strategy["season_boost"] - 1) * 0.5)
        
        # --- C. Final Assembly ---
        # Formula: Base Start * Trend Direction * Seasonal Context * Strategy Overlay
        forecast = base_demand * trend_mod * m_factor * strat_season_impact
        
        # Apply Marketing Boost as a linear multiplier
        forecast *= strategy.get("marketing_boost", 1.0)

        # --- D. Sanity Guards ---
        final_val = max(forecast, 0)
        final_val = min(final_val, historical_max * 1.5)
        
        forecast_vals.append(final_val)

    return pd.DataFrame({
        "date": future_dates,
        "forecast": forecast_vals
    })
