import pandas as pd
from sklearn.tree import DecisionTreeRegressor

def run_decision_tree(data):
    data = data.copy()
    
    # Define features to use for learning
    # These must be numeric, so we use the flags we created in data_prep
    features = ['month', 'is_weekend', 'marketing_spend', 'festival_flag', 'event_flag']
    
    # If SKU Master was used, we could add encoded categories here
    X = data[features].fillna(0)
    y = data['sales']

    model = DecisionTreeRegressor(max_depth=10, min_samples_leaf=2)
    model.fit(X, y)

    # Create future dates for 90 days
    last_date = data['date'].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=90)
    
    future = pd.DataFrame({"date": future_dates})
    
    # We must provide the same features for the future
    future['month'] = future['date'].dt.month
    future['is_weekend'] = future['date'].dt.dayofweek.apply(lambda x: 1 if x >= 5 else 0)
    
    # For simplicity in future-forecasting, we assume 0 for unknown future events
    future['marketing_spend'] = 0
    future['festival_flag'] = 0
    future['event_flag'] = 0

    future['forecast'] = model.predict(future[features])

    return future[['date', 'forecast']]