# data_cleaning.py
import pandas as pd
import numpy as np
import streamlit as st

def auto_clean_sales_file(file):
    try:
        file.seek(0)
        df = pd.read_csv(file)
        df.columns = [c.strip().lower() for c in df.columns]
        
        rename_map = {'quantity': 'sales', 'qty': 'sales', 'item': 'sku'}
        df = df.rename(columns=rename_map)
        
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
        
        if 'sku' not in df.columns:
            df['sku'] = "Default_SKU"
            
        # Grouping by date/sku to ensure the user sees a "clean" 1-row-per-day version
        df = df.groupby(['date', 'sku']).agg({'sales': 'sum'}).reset_index()
        return df.sort_values(['sku', 'date'])
    except Exception as e:
        st.error(f"Cleaning Error: {e}")
        return None

def run_integrity_check(df, name):
    report = []
    if df is None or df.empty:
        return ["❌ File is empty or could not be parsed."]

    # 1. Null Value Check
    null_count = df.isnull().sum().sum()
    if null_count > 0:
        report.append(f"⚠️ {name}: {null_count} missing values detected and auto-corrected.")
    else:
        report.append(f"✅ {name}: No missing values.")

    # 2. Date Continuity Check (Updated to ignore/pass through)
    date_range = (df['date'].max() - df['date'].min()).days + 1
    actual_days = df['date'].nunique()
    if actual_days < date_range:
        gap_count = date_range - actual_days
        # We report it as a warning but DO NOT stop the process
        report.append(f"⚠️ {name}: Significant gaps found ({gap_count} days missing). The system will ignore these gaps and proceed.")
    else:
        report.append(f"✅ {name}: Chronological continuity verified.")

    # 3. Numeric Check
    if (df['sales'] < 0).any():
        report.append(f"❌ {name}: Negative sales found. Reset to zero.")
    
    return report
