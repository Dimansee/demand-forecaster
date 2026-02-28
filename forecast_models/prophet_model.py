from prophet import Prophet
import pandas as pd

def run_prophet(df, industry="Custom"):

    model = Prophet()

    temp = df[['date','sales']].rename(columns={'date':'ds','sales':'y'})

    model.fit(temp)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    out = forecast[['ds','yhat']].rename(columns={'ds':'date','yhat':'forecast'})
    return out
