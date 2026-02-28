import pandas as pd

def clean_all_data(sales_file, marketing_file=None, festival_file=None, events_file=None, sku_master_file=None):

    sales = pd.read_csv(sales_file)
    sales['date'] = pd.to_datetime(sales['date'])

    dfs = [sales]

    if marketing_file:
        marketing = pd.read_csv(marketing_file)
        marketing['date'] = pd.to_datetime(marketing['date'])
        dfs.append(marketing)

    if festival_file:
        fest = pd.read_csv(festival_file)
        fest['date'] = pd.to_datetime(fest['date'])
        dfs.append(fest)

    if events_file:
        events = pd.read_csv(events_file)
        events['date'] = pd.to_datetime(events['date'])
        dfs.append(events)

    df = sales

    for extra in dfs[1:]:
        df = df.merge(extra, on=['date','sku'], how='left')

    df.fillna(0, inplace=True)

    return df
