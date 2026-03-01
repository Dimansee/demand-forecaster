import pandas as pd
import numpy as np
from datetime import timedelta

# --- HELPER 1: Agnostic Seasonality ---
def learn_seasonality(df):
    """Calculates monthly multipliers relative to global performance."""
    global_mean = df['sales'].mean()
    monthly_avg = df.groupby(df['date'].dt.month)['sales'].mean()
    # If a month has no data, fill with 1.0 (neutral)
    season_index = (monthly_avg / global_mean).to_dict()
    return season_index

# --- HELPER 2: Momentum Detection ---
def detect_season_phase(df):
    """Uses Exponential Moving Averages to detect trend direction."""
    if len(df) < 30: return "stable"
    ema_short = df['sales'].ewm(span=7).mean().iloc[-1]
    ema_long = df['sales'].ewm(span=30).mean().iloc[-1]
    diff_pct = (ema_short - ema_long) / (ema_long + 1e-5) # Prevent div by zero

    if diff_pct > 0.05: return "ramp_up"
    elif diff_pct < -0.05: return "decline"
    return "stable"

# --- HELPER 3: Strategy Profiles ---
def get_strategy_profile(business_type, config=None):
    """Provides boost factors based on business category."""
    profiles = {
        "FMCG": {"trend_boost": 0.6, "season_boost": 1.2, "marketing_boost": 1.3},
        "Fashion": {"trend_boost": 1.2, "season_boost": 1.4, "marketing_boost": 1.0},
        "Electronics": {"trend_boost": 1.3, "season_boost": 1.1, "marketing_boost": 0.8},
        "Seasonal": {"trend_boost": 0.8, "season_boost": 1.5, "marketing_boost": 0.9}
    }
    return profiles.get(business_type, {"trend_boost": 1.0, "season_boost": 1.0, "marketing_boost": 1.0})

# --- MAIN ENGINE ---
def run_forecast(df, model_choice, business_type, config=None, forecast_days=30):
    config = config or {}
    strategy = get_strategy_profile(business_type, config) # Error was here!
    
    df = df.copy().sort_values("date")
    last_date = df["date"].max()
    
    # Use 14-day median to ground the 'starting point' (prevents spikes)
    base_demand = df.tail(14)['sales'].median()
    season_index = learn_seasonality(df)
    phase = detect_season_phase(df)

    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days, freq="D")
    forecast_vals = []
    historical_max = df['sales'].max()

    for i, d in enumerate(future_dates):
        # Dampened trend to prevent exponential runaway
        dampening = 0.7 
        step_progress = (i + 1) / forecast_days
        
        if phase == "ramp_up":
            trend_mod = 1 + (config.get("trend_weight", 0.05) * strategy["trend_boost"] * step_progress * dampening)
        elif phase == "decline":
            trend_mod = 1 - (config.get("trend_weight", 0.05) * strategy["trend_boost"] * step_progress * dampening)
        else:
            trend_mod = 1.0

        m_factor = season_index.get(d.month, 1.0)
        # Final calculation combining trend, seasonality, and strategy
        val = base_demand * trend_mod * m_factor * strategy.get("marketing_boost", 1.0)
        
        # Sanity Guard: No negatives and cap at 1.5x historical max
        forecast_vals.append(min(max(val, 0), historical_max * 1.5))

    return pd.DataFrame({"date": future_dates, "forecast": forecast_vals})
