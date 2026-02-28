import pandas as pd
from prophet import Prophet

def run_prophet(df, industry="General", season_months=None, trend_weight=0.05, marketing_weight=0.5):
    """
    Advanced Prophet implementation that uses external 'Regressors' 
    (Marketing, Festivals, Events) to improve accuracy.
    """
    
    # 1. Prepare data for Prophet (Prophet requires columns 'ds' and 'y')
    prophet_df = df.rename(columns={'date': 'ds', 'sales': 'y'})
    
    # 2. Initialize Model
    # changepoint_prior_scale controls how flexible the trend is (trend_weight)
    model = Prophet(
        changepoint_prior_scale=trend_weight, 
        yearly_seasonality=True, 
        weekly_seasonality=True, 
        daily_seasonality=False
    )

    # 3. ADD EXTRA REGRESSORS (The "Intelligence")
    # We only add them if they exist in your cleaned dataframe
    if 'marketing_spend' in prophet_df.columns:
        # prior_scale here controls how much the model 'trusts' marketing impact
        model.add_regressor('marketing_spend', prior_scale=marketing_weight)
        
    if 'festival_flag' in prophet_df.columns:
        model.add_regressor('festival_flag')
        
    if 'event_flag' in prophet_df.columns:
        model.add_regressor('event_flag')

    if 'is_weekend' in prophet_df.columns:
        model.add_regressor('is_weekend')

    # 4. Fit the Model
    model.fit(prophet_df)

    # 5. Create Future Dates (90 Days)
    future = model.make_future_dataframe(periods=90)

    # 6. IMPORTANT: Future regressors must be known
    # Since we don't know future marketing/festivals yet, we fill with 0 
    # OR you could extend your files to include future dates!
    for col in ['marketing_spend', 'festival_flag', 'event_flag', 'is_weekend']:
        if col in prophet_df.columns:
            # For 'is_weekend', we can actually calculate the future values
            if col == 'is_weekend':
                future['is_weekend'] = future['ds'].dt.dayofweek.apply(lambda x: 1 if x >= 5 else 0)
            else:
                future[col] = 0 # Default to 0 if future marketing isn't provided

    # 7. Predict
    forecast = model.predict(future)

    # 8. Clean Output for App
    # We only want the future 90 days for the forecast table
    forecast_results = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(90)
    forecast_results = forecast_results.rename(columns={'ds': 'date', 'yhat': 'forecast'})
    
    # Ensure no negative forecasts (Prophet can sometimes dip below 0)
    forecast_results['forecast'] = forecast_results['forecast'].clip(lower=0)
    
    return forecast_results