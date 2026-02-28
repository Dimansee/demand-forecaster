import pandas as pd
import numpy as np

# Sales Data

dates = pd.date_range(start="2024-01-01", end="2024-12-31")

skus = ["TSHIRT01", "HOODIE01", "SUNSCREEN01"]

data = []

for date in dates:
    for sku in skus:
        
        base = 100
        
        # Seasonality
        month = date.month
        if sku == "HOODIE01" and month in [11,12,1]:
            base += 50
        if sku == "SUNSCREEN01" and month in [4,5,6]:
            base += 60
            
        # Random noise
        sales = base + np.random.randint(-20,20)
        
        data.append([date, sku, max(0,sales)])

sales = pd.DataFrame(data, columns=["date","sku","units_sold"])

sales.to_csv("sales.csv", index=False)

print("sales.csv created!")

# MARKETING DATA

marketing_data = []

for date in dates:
    for sku in skus:
        spend = 0
        
        # Random campaigns
        if np.random.rand() > 0.85:
            spend = np.random.randint(2000,10000)
            
        marketing_data.append([date, sku, spend, "Digital"])

marketing = pd.DataFrame(marketing_data, columns=["date","sku","ad_spend","campaign_type"])
marketing.to_csv("marketing.csv", index=False)

print("marketing.csv created!")

# FESTIVAL DATA

festival_data = [
    ["2024-01-01", "New Year", 0.2],
    ["2024-03-25", "Holi", 0.3],
    ["2024-08-15", "Independence Day", 0.2],
    ["2024-11-01", "Diwali", 0.5],
    ["2024-12-25", "Christmas", 0.2]
]

festival = pd.DataFrame(festival_data, columns=["date","festival_name","impact_weight"])
festival.to_csv("festival.csv", index=False)

print("festival.csv created!")

# EVENTS DATA

events_data = [
    ["2024-02-10", "Wedding Season", "demand_up"],
    ["2024-04-20", "Heatwave", "demand_up"],
    ["2024-10-05", "Cricket Tournament", "demand_up"],
    ["2024-06-15", "Competitor Launch", "demand_down"]
]

events = pd.DataFrame(events_data, columns=["date","event_name","impact_type"])
events.to_csv("events.csv", index=False)

print("events.csv created!")

# SKU MASTER

sku_master_data = [
    ["TSHIRT01", "Apparel", "All"],
    ["HOODIE01", "Apparel", "Winter"],
    ["SUNSCREEN01", "Skincare", "Summer"]
]

sku_master = pd.DataFrame(sku_master_data, columns=["sku","category","season_type"])
sku_master.to_csv("sku_master.csv", index=False)

print("sku_master.csv created!")