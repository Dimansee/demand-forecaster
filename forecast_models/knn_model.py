from sklearn.neighbors import KNeighborsRegressor

def run_knn(df):

    df = df.copy()
    df['day'] = df['date'].dt.day

    X = df[['day']]
    y = df['sales']

    model = KNeighborsRegressor(n_neighbors=3)
    model.fit(X,y)

    df['forecast'] = model.predict(X)

    return df[['date','forecast']]
