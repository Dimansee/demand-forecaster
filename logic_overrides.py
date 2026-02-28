import pandas as pd
from datetime import timedelta

# Shared Festival Dictionary for 2026
FESTIVAL_DICT = {
    "Christmas": "2026-12-25", "Diwali": "2026-11-08", "Eid": "2026-03-20",
    "Holi": "2026-03-03", "Black Friday": "2026-11-27"
}

def apply_strategy_logic(df, surge, marketing_lift, return_rate, buffer_pct):
    """
    Applies the 4 core KPI formulas defined in the documentation.
    """
    df = df.copy()
    
    # 1. Apply Trend Surge & Marketing Lift to Gross Demand
    # Formula: Gross * Surge * (1 + Marketing%)
    df['forecast'] = df['forecast'] * surge * (1 + (marketing_lift / 100))
    
    # 2. Calculate Net Demand
    # Formula: NetDemand = GrossDemand * (1 - Return%)
    df['net_demand'] = df['forecast'] * (1 - (return_rate / 100))
    
    # 3. Calculate Inventory Target (Safety Buffer)
    # Formula: Target = NetDemand * (1 + Buffer%)
    df['inventory_target'] = df['net_demand'] * (1 + (buffer_pct / 100))
    
    return df

def apply_holiday_boost(df, selected_fests, peak_lift, window_lift):
    """Applies user-defined holiday spikes."""
    for f in selected_fests:
        if f in FESTIVAL_DICT:
            t = pd.to_datetime(FESTIVAL_DICT[f])
            # Peak Day Boost
            df.loc[df['date'] == t, 'forecast'] *= (1 + peak_lift / 100)
            # Window Boost (2 days before, 1 day after)
            window = [t - timedelta(days=2), t - timedelta(days=1), t + timedelta(days=1)]
            df.loc[df['date'].isin(window), 'forecast'] *= (1 + window_lift / 100)
    return df
