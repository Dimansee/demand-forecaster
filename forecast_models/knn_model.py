import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler

def run_knn(data):
    data = data.copy()
    features = ['month', 'is_weekend', 'festival_flag']
    
    X = data[features].fillna(0)
    y = data['sales']

    # KNN performs much better with scaled data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KNeighborsRegressor(n_neighbors=3, weights='distance')
    model.fit(X_scaled, y)

    last_date = data['date'].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=90)
    future = pd.DataFrame({"date": future_dates})
    
    future['month'] = future['date'].dt.month
    future['is_weekend'] = future['date'].dt.dayofweek.apply(lambda x: 1 if x >= 5 else 0)
    future['festival_flag'] = 0
    
    X_future_scaled = scaler.transform(future[features])
    future['forecast'] = model.predict(X_future_scaled)

    return future[['date', 'forecast']]