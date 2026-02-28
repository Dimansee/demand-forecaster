import pandas as pd
from prophet import Prophet
import streamlit as st

def run_prophet(sku_df, periods=90, industry="General"):
    """
    Runs Meta Prophet forecasting for a specific SKU DataFrame.
    
    Args:
        sku_df (pd.DataFrame): Data containing 'date' and 'sales' columns.
        periods (int): Number of days to forecast into the future.
        industry (str): Strategy type (e.g., 'Fashion', 'FMCG').
    """
    try:
        # 1. Prepare data for Prophet (Requires 'ds' and 'y' columns)
        # We map your cleaned 'date' and 'sales' to Prophet's format
        prophet_df = sku_df.rename(columns={'date': 'ds', 'sales': 'y'})
        
        # 2. Initialize the Model
        # You can adjust seasonality based on the 'industry' strategy
        model = Prophet(
            yearly_seasonality=True, 
            weekly_seasonality=True, 
            daily_seasonality=False
        )

        # 3. Add Regressors (Checks if columns exist in your upload)
        regressors = ['ad_spend', 'festival_flag', 'event_flag', 'season_score']
        for reg in regressors:
            if reg in prophet_df.columns:
                model.add_regressor(reg)

        # 4. Fit the Model
        model.fit(prophet_df)

        # 5. Create Future Timeline
        future = model.make_future_dataframe(periods=periods)

        # 6. Attach Regressor values for the future dates
        # Note: In a production app, you'd merge future marketing plans here
        if any(reg in prophet_df.columns for reg in regressors):
            future = future.merge(
                prophet_df[['ds'] + [r for r in regressors if r in prophet_df.columns]],
                on='ds',
                how='left'
            ).fillna(0)

        # 7. Predict
        forecast = model.predict(future)

        # 8. Clean Output for the App
        # We rename back to your standard 'date' and 'forecast'
        result = forecast[['ds', 'yhat']].rename(columns={'ds': 'date', 'yhat': 'forecast'})
        
        # Return only the future period
        return result.tail(periods)

    except Exception as e:
        st.error(f"Prophet Model Error: {e}")
        return pd.DataFrame(columns=['date', 'forecast'])
