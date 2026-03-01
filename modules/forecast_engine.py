import pandas as pd
import numpy as np
from datetime import timedelta

# -------------------------------
# 1. Pattern Learning: Seasonality & Events
# -------------------------------
def learn_patterns(df):
    """
    Analyzes historical data to extract 'Business DNA': 
    Weekly cycles, Monthly seasonality, and Volatility.
    """
    df = df.copy()
    global_mean = df['sales'].mean()
    
    # Monthly Seasonality (Agnostic to product type)
    monthly_avg = df.groupby(df['date'].dt.month)['sales'].mean()
    season_index = (monthly_avg / global_mean).to_dict()
    
    # Weekly Cycle (Learns if weekends or specific days spike)
    dow_avg = df.groupby(df['date'].dt.dayofweek)['sales'].mean()
    dow_index = (dow_avg / global_mean).to_dict()
    
    return season_index, dow_index

def get_event_impact(date, config):
    """
    Identifies if a future date hits a known holiday or custom marketing event.
    """
    # Standard business holidays / events
    events = {
        (12, 25): 1.3,  # Christmas
        (11, 28): 1.4,  # Generic Late Nov (Black Friday window)
        (1, 1): 0.8,    # New Year's Day (often a dip)
        (7, 4): 1.2     # Mid-summer peak
    }
    
    # Check for custom marketing events passed from the UI
    custom_event_days = config.get("marketing_events", [])
    if date.strftime('%Y-%m-%d') in custom_event_days:
        return config.get("custom_event_boost", 1.5)
        
    return events.get((date.month, date.day), 1.0)

# -------------------------------
# 2. Momentum & Strategy
# -------------------------------
def detect_momentum(df):
    """Uses Weighted Moving Averages to see if the business is currently 'heating up'."""
    if len(df) < 30: return "stable"
    
    short_term = df['sales'].tail(7).mean()
    long_term = df['sales'].tail(30).mean()
    
    diff = (short_term - long_term) / (long_term + 1e-5)
    
    if diff > 0.10: return "ramp_up"
    if diff < -0.10: return "decline"
    return "stable"

def get_strategy_profile(business_type, config=None):
    profiles = {
        "FMCG": {"trend": 0.7, "season": 1.1, "marketing": 1.2},
        "Fashion": {"trend": 1.2, "season": 1.5, "marketing": 1.1},
        "Electronics": {"trend": 1.3, "season": 1.1, "marketing": 1.0},
        "Seasonal": {"trend": 0.9, "season": 1.8, "marketing": 1.0}
    }
    return profiles.get(business_type, {"trend": 1.0, "season": 1.0, "marketing": 1.0})

# -------------------------------
# 3. Main Advanced Forecast Engine
# -------------------------------
def run_forecast(df, model_choice, business_type, config=None, forecast_days=30):
    config = config or {}
    df = df.copy().sort_values("date")
    last_date = df["date"].max()
    
    # 1. Learning Phase
    season_map, dow_map = learn_patterns(df)
    phase = detect_momentum(df)
    strategy = get_strategy_profile(business_type, config)
    
    # 2. Establish Baseline (14-day median is the most stable 'launch pad')
    base_demand = df.tail(14)['sales'].median()
    
    future_dates = pd.date_range(
        start=last_date + timedelta(days=1), 
        periods=forecast_days, 
        freq="D"
    )
    
    forecast_vals = []
    hist_max = df['sales'].max()

    for i, d in enumerate(future_dates):
        # A. Trend Component (Dampened to prevent runaway lines)
        dampening = 0.6
        step = (i + 1) / forecast_days
        trend_weight = config.get("trend_weight", 0.05)
        
        if phase == "ramp_up":
            trend_factor = 1 + (trend_weight * strategy["trend"] * step * dampening)
        elif phase == "decline":
            trend_factor = 1 - (trend_weight * strategy["trend"] * step * dampening)
        else:
            trend_factor = 1.0

        # B. Seasonal & Weekly DNA
        m_factor = season_map.get(d.month, 1.0)
        w_factor = dow_map.get(d.dayofweek, 1.0)
        
        # C. Event / Festival Impact
        e_factor = get_event_multiplier(d, config) if 'get_event_multiplier' in locals() else get_event_impact(d, config)

        # D. Assemble Final Forecast
        # Logic: Base * Weekly Pattern * Monthly Context * Trend Direction * Events
        val = base_demand * w_factor * m_factor * trend_factor * e_factor
        
        # Apply Marketing Strategy Boost
        val *= strategy.get("marketing", 1.0)
        
        # E. Sanity Guard (No negatives, cap at 1.5x historical peak)
        final_val = min(max(val, 0), hist_max * 1.5)
        forecast_vals.append(final_val)

    return pd.DataFrame({
        "date": future_dates, 
        "forecast": forecast_vals
    })
