# logic_overrides.py
import pandas as pd

FESTIVAL_DICT = {
    "Christmas": "2026-12-25", "Diwali": "2026-11-08", "Eid": "2026-03-20",
    "Holi": "2026-03-03", "Black Friday": "2026-11-27"
}

def apply_strategy_logic(df, surge, mkt_lift, return_rate, buffer):
    """Ensures results are calculated on a DataFrame and returned as one."""
    if not isinstance(df, pd.DataFrame):
        # Safety check: if it's a list, try to convert it
        df = pd.DataFrame(df)
        
    res = df.copy()
    # 1. Apply Surge and Marketing
    res['forecast'] = res['forecast'] * surge * (1 + (mkt_lift / 100))
    # 2. Net Demand
    res['net_demand'] = res['forecast'] * (1 - (return_rate / 100))
    # 3. Inventory Target
    res['inventory_target'] = res['net_demand'] * (1 + (buffer / 100))
    
    return res

def apply_holiday_boost(df, selected_fests, peak_lift, win_lift):
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    
    for f in selected_fests:
        if f in FESTIVAL_DICT:
            t = pd.to_datetime(FESTIVAL_DICT[f])
            # Peak Day
            df.loc[df['date'] == t, 'forecast'] *= (1 + peak_lift / 100)
            # Window (2 days before/after)
            window = [t - pd.Timedelta(days=i) for i in range(1, 3)] + [t + pd.Timedelta(days=1)]
            df.loc[df['date'].isin(window), 'forecast'] *= (1 + win_lift / 100)
    return df
