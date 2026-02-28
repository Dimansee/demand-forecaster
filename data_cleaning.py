# data_cleaning.py
import pandas as pd
import numpy as np
import streamlit as st

def auto_clean_sales_file(file):
    """Standardizes and repairs sales data."""
    try:
        file.seek(0)
        df = pd.read_csv(file)
        df.columns = [c.strip().lower() for c in df.columns]
        
        rename_map = {'quantity': 'sales', 'qty': 'sales', 'item': 'sku', 'sales': 'sales'}
        df = df.rename(columns=rename_map)
        
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
        
        if 'sku' not in df.columns:
            df['sku'] = "Default_SKU"
            
        return df.sort_values(['sku', 'date'])
    except Exception as e:
        st.error(f"Cleaning Error: {e}")
        return None

def run_integrity_check(df, name):
    """Specific section for Data Integrity."""
    issues = []
    if df is None: return ["File missing or unreadable."]
    
    if df.isnull().values.any():
        issues.append(f"⚠️ {name}: Null values detected (auto-filled).")
    
    unique_dates = df['date'].nunique()
    total_rows = len(df)
    if total_rows > unique_dates and 'sku' not in df.columns:
         issues.append(f"⚠️ {name}: Duplicate dates found without SKU identifiers.")
            
    return issues
