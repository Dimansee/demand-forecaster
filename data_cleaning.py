# data_cleaning.py
import pandas as pd
import streamlit as st

def auto_clean_sales_file(file):
    try:
        file.seek(0)
        df = pd.read_csv(file)
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Standardize
        rename_map = {'quantity': 'sales', 'qty': 'sales', 'item': 'sku', 'sales': 'sales'}
        df = df.rename(columns=rename_map)
        
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
        
        if 'sku' not in df.columns:
            df['sku'] = "Default_SKU"
            
        # Group to daily rows
        return df.groupby(['date', 'sku']).agg({'sales': 'sum'}).reset_index()
    except Exception as e:
        return None

def run_integrity_check(df, name):
    report = []
    if df is None: return ["❌ Parsing Error"]

    # Date Continuity Check
    date_range = (df['date'].max() - df['date'].min()).days + 1
    actual_days = df['date'].nunique()
    
    if actual_days < date_range:
        gap_count = date_range - actual_days
        # WARNING: Significant gaps found - but we continue
        report.append(f"⚠️ {name} Data: Significant gaps found ({gap_count} days missing). System will ignore gaps and proceed.")
    else:
        report.append(f"✅ {name} Data: Continuity Verified.")
        
    return report
