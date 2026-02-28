import pandas as pd
from datetime import timedelta

FESTIVAL_DICT = {
    "Christmas": "2026-12-25", "Diwali": "2026-11-08", "Eid": "2026-03-20",
    "Holi": "2026-03-03", "Black Friday": "2026-11-27"
}

def apply_strategy_modifiers(df, surge, marketing, returns, buffer):
    df = df.copy()
    df['forecast'] *= surge * (1 + (marketing/100))
    df['net_demand'] = df['forecast'] * (1 - (returns/100))
    df['inventory_target'] = df['net_demand'] * (1 + (buffer/100))
    return df

def apply_festival_impact(df, selected_fests, green_lift, orange_lift):
    for f in selected_fests:
        if f in FESTIVAL_DICT:
            t = pd.to_datetime(FESTIVAL_DICT[f])
            # Peak Day
            df.loc[df['date'] == t, 'forecast'] *= (1 + green_lift/100)
            # Window Days
            window = [t-timedelta(days=2), t-timedelta(days=1), t+timedelta(days=1)]
            df.loc[df['date'].isin(window), 'forecast'] *= (1 + orange_lift/100)
    return df
