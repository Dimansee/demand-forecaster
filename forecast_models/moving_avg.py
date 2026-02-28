import pandas as pd

def run_moving_avg(df):

    df = df.copy()
    df['forecast'] = df['sales'].rolling(7).mean().fillna(method='bfill')
    return df[['date','forecast']]
