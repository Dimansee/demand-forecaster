import pandas as pd
import numpy as np
from datetime import timedelta

# --- 1. Pattern Learning (Business DNA) ---
def learn_business_dna(df):
    """Extracts seasonality with Time-Decay (Recent data = Higher Weight)."""
    df = df.copy()
    
    # Create weights: newer dates are up to 2x more influential than old ones
    weights = np.linspace(0.5, 1.0, len(df))
    global_mean = np.average(df['sales'], weights=weights)
    
    # Weekly patterns (Mon-Sun) - Fixed the .to_dict() typo here
    dow_map = (df.groupby(df['date'].dt.dayofweek)['sales'].mean() / global_mean).to_dict()
    
    # Monthly patterns (Jan-Dec)
    month_map = (df.groupby(df['date'].dt.month)['sales'].mean() / global_mean).to_dict()
    
    return dow_map, month_map

# --- 2. Event & Holiday Intelligence ---
def get_event_multiplier(date):
    """Calculates 'Halo Effect' (Demand increases as we get closer to a holiday)."""
    # Key global events
    events = {
        "Christmas": (12, 25),
        "Black Friday Window": (11, 25), # Simplified proxy
        "Summer Peak": (7, 15)
    }
    
    max_boost = 1.0
    for event_name, (m, d) in events.items():
        event_date = pd.Timestamp(date.year, m, d)
        days_diff = (date - event_date).days
        
        # If we are in the 14 days LEADING UP to the event
        if -14 <= days_diff <= 0:
            # Gaussian-style ramp up: boost grows as days_diff approaches 0
            proximity_boost = 1 + (0.4 * (1 + days_diff / 14))
            max_boost = max(max_boost, proximity_boost)
            
    return max_boost

# --- 3. Strategy Profiles ---
def get_strategy_profile(business_type):
    profiles = {
        "FMCG": {"marketing": 1.1},
        "Fashion": {"marketing": 1.3},
        "Electronics": {"marketing": 1.05},
        "Seasonal": {"marketing": 1.5}
    }
    return profiles.get(business_type, {"marketing": 1.0})

# --- 4. Main Engine ---
def run_forecast(df, model_choice, business_type, config=None, forecast_days=30):
    config = config or {}
    df = df.copy().sort_values("date")
    
    # Pre-process: Clean outliers (Clips top 2% of extreme spikes)
    df['sales'] = df['sales'].clip(upper=df['sales'].quantile(0.98))
    
    # Analysis
    dow_map, month_map = learn_business_dna(df)
    strategy = get_strategy_profile(business_type)
    
    # Baseline: Use Exponential Moving Average (reacts better to recent trends)
    base_demand = df['sales'].ewm(span=14).mean().iloc[-1]
    
    last_date = df["date"].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days)
    
    forecast_vals = []
    hist_max = df['sales'].max()

    for d in future_dates:
        # A. Start with base and apply DNA (Weekly + Monthly)
        val = base_demand * dow_map.get(d.dayofweek, 1.0) * month_map.get(d.month, 1.0)
        
        # B. Apply Holiday/Event Ramps
        val *= get_event_multiplier(d)
        
        # C. Apply Strategy & Config Boosts
        val *= strategy["marketing"]
        val *= config.get("custom_marketing", 1.0)
        
        # D. Safety Guards
        final_val = min(max(val, 0), hist_max * 1.6) # Cap at 160% of hist max
        forecast_vals.append(final_val)

    return pd.DataFrame({"date": future_dates, "forecast": forecast_vals})
