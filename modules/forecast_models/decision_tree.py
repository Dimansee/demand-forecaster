
from sklearn.tree import DecisionTreeRegressor
import pandas as pd

def run_decision_tree(df):

    df = df.copy()
    df['day'] = df['date'].dt.day
    X = df[['day']]
    y = df['sales']

    model = DecisionTreeRegressor()
    model.fit(X,y)

    df['forecast'] = model.predict(X)

    return df[['date','forecast']]
