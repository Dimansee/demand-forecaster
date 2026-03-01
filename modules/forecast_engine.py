import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.ensemble import GradientBoostingRegressor

# --- MODULE 1: Pattern Learning (The DNA) ---
def learn_business_dna(df):
    """Extracts high-precision seasonality and time-decayed weights."""
    df = df.copy()
    # Time-Decay: Recent data is 2x more important than old data
    weights = np.linspace(0.5, 1.0, len(df))
    global_mean = np.average(df['sales'], weights=weights)
    
    # Weekly patterns (Mon-Sun)
    dow_map = (df.groupby(df['date'].dt.dayofweek)['sales'].mean() / global_mean).to_dbict()
    # Monthly patterns (Jan-Dec)
    month_map = (df.groupby(df['date'].dt.month)['sales'].mean() / global_mean).to_dict()
    
    return dow_map, month_map

# --- MODULE 2: Gradient Boosting (New Module) ---
def run_gradient_boosting(df, forecast_days):
    """Learns non-linear residuals to fix errors other models miss."""
    df = df.copy()
    df['day_of_year'] = df['date'].dt.dayofyear
    df['day_of_week'] = df['date'].dt.dayofweek
    
    X = df[['day_of_year', 'day_of_week']]
    y = df['sales']
    
    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
    model.fit(X, y)
    
    last_date = df['date'].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days)
    X_future = pd.DataFrame({
        'day_of_year': future_dates.dayofyear,
        'day_of_week': future_dates.dayofweek
    })
    
    return model.predict(X_future)

# --- MODULE 3: Event & Holiday Overlay ---
def get_advanced_event_boost(date):
    """Gaussian-style ramp up for major festivals."""
    # Example: Christmas peak
    christmas = pd.Timestamp(date.year, 12, 25)
    days_to = (date - christmas).days
    
    if -14 <= days_to <= 0: # 14-day shopping ramp-up
        return 1.0 + (0.4 * (1 + days_to / 14))
    
    # Black Friday Window
    if date.month == 11 and 20 <= date.day <= 30:
        return 1.35
        
    return 1.0

# --- MAIN ENGINE ---
def run_forecast(df, model_choice, business_type, config=None, forecast_days=30):
    config = config or {}
    df = df.copy().sort_values("date")
    
    # 1. CLEANING: Remove outliers that skew 'learning'
    df['sales'] = df['sales'].clip(upper=df['sales'].quantile(0.98))
    
    # 2. ANALYSIS: Learn the DNA and Momentum
    dow_map, month_map = learn_business_dna(df)
    base_demand = df['sales'].ewm(span=14).mean().iloc[-1] # Exponential baseline
    
    # 3. GENERATE FUTURE DATES
    last_date = df["date"].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days)
    
    # 4. MODULE SELECTION
    if model_choice == "Gradient Boosting":
        core_forecast = run_gradient_boosting(df, forecast_days)
    else:
        # Fallback to pattern-based logic for other types
        core_forecast = [base_demand] * forecast_days

    forecast_vals = []
    for i, d in enumerate(future_dates):
        # Apply DNA factors
        val = core_forecast[i] if model_choice == "Gradient Boosting" else base_demand
        val *= dow_map.get(d.dayofweek, 1.0)
        val *= month_map.get(d.month, 1.0)
        
        # Apply Festival/Event Overlay
        val *= get_advanced_event_boost(d)
        
        # Strategy Overlay
        strat = {"FMCG": 1.1, "Fashion": 1.3, "Electronics": 1.05}.get(business_type, 1.0)
        val *= strat
        
        forecast_vals.append(max(val, 0))

    return pd.DataFrame({"date": future_dates, "forecast": forecast_vals})
