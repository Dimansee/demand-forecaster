import pandas as pd

def run_moving_avg(data):
    data = data.copy()
    last_date = data['date'].max()

    # Use an Exponential Weighted Moving Average (EWM)
    # This reacts faster to recent fashion trend spikes than a simple rolling mean
    avg = data['sales'].ewm(span=7).mean().iloc[-1]

    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=90)

    forecast = pd.DataFrame({
        "date": future_dates,
        "forecast": avg
    })

    return forecast