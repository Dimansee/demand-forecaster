import pandas as pd
import streamlit as st

def run_integrity_check(df, name):
    """Missing Integrity Check Section logic."""
    issues = []
    if df is None: return ["File not loaded"]
    
    if df.isnull().values.any():
        issues.append(f"⚠️ {name}: Null values detected and auto-filled.")
    if 'date' in df.columns and df['date'].duplicated().any() and 'sku' not in df.columns:
        issues.append(f"⚠️ {name}: Duplicate dates found without SKU separation.")
        
    return issues

def auto_clean_sales_file(file):
    try:
        file.seek(0)
        df = pd.read_csv(file)
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Standardize Columns
        rename_map = {'quantity': 'sales', 'qty': 'sales', 'item': 'sku'}
        df = df.rename(columns=rename_map)
        
        # Repair
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Error cleaning file: {e}")
        return None
