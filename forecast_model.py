import pandas as pd
from prophet import Prophet

df = pd.read_csv("model_data.csv")
df['ds'] = pd.to_datetime(df['ds'])

skus = df['sku'].unique()

forecast_results = []

for sku in skus:

    sku_df = df[df['sku'] == sku][['ds','y','ad_spend','festival_flag','event_flag','season_score']]

    model = Prophet()

    model.add_regressor('ad_spend')
    model.add_regressor('festival_flag')
    model.add_regressor('event_flag')
    model.add_regressor('season_score')

    model.fit(sku_df)

    future = model.make_future_dataframe(periods=90)

    future = future.merge(
        sku_df[['ds','ad_spend','festival_flag','event_flag','season_score']],
        on='ds',
        how='left'
    )

    future.fillna(0, inplace=True)

    forecast = model.predict(future)

    forecast['sku'] = sku

    forecast_results.append(forecast[['ds','yhat','sku']])

final_forecast = pd.concat(forecast_results)
final_forecast.to_csv("forecast_output.csv", index=False)

print("3 Month Forecast Ready!")