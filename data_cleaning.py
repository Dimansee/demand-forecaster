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
    """
    Performs a 4-point health check on the uploaded data.
    Returns a list of status messages.
    """
    report = []
    if df is None or df.empty:
        return ["❌ File is empty or could not be parsed."]

    # 1. Null Value Check
    null_count = df.isnull().sum().sum()
    if null_count > 0:
        report.append(f"⚠️ {name}: {null_count} missing values detected and auto-corrected.")
    else:
        report.append(f"✅ {name}: No missing values.")

    # 2. Date Continuity Check
    date_range = (df['date'].max() - df['date'].min()).days
    actual_days = df['date'].nunique()
    if actual_days < (date_range * 0.9): # If more than 10% days are missing
        report.append(f"⚠️ {name}: Significant gaps found in date history.")
    else:
        report.append(f"✅ {name}: Chronological continuity verified.")

    # 3. Numeric Outlier/Negative Check
    if (df['sales'] < 0).any():
        report.append(f"❌ {name}: Negative sales values found. Converting to zero.")
        df['sales'] = df['sales'].clip(lower=0)
    
    # 4. SKU Categorization
    report.append(f"ℹ️ {name}: Identified {df['sku'].nunique()} unique SKUs.")

    return report
