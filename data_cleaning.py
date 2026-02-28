import pandas as pd
import numpy as np
import streamlit as st

def auto_clean_sales_file(file):
    try:
        file.seek(0)
        df = pd.read_csv(file)
        if df.empty: return None

        df.columns = [c.strip().lower() for c in df.columns]
        rename_map = {
            'date': 'date', 'dat': 'date', 'timestamp': 'date',
            'quantity': 'sales', 'qty': 'sales', 'sales': 'sales', 'sold': 'sales'
        }
        df = df.rename(columns=rename_map)

        if 'date' not in df.columns:
            st.error("❌ 'Date' column missing.")
            return None

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        
        if 'sales' in df.columns:
            df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
        
        if 'sku' not in df.columns:
            df['sku'] = "Default_SKU"

        # Daily Aggregation to prevent duplicates
        df = df.groupby(['date', 'sku']).agg({'sales': 'sum'}).reset_index()
        return df.sort_values(['sku', 'date'])
    except Exception as e:
        st.error(f"Cleaning Error: {e}")
        return None

def get_data_health_report(df):
    expected_range = pd.date_range(start=df['date'].min(), end=df['date'].max())
    return {
        'total_records': len(df),
        'unique_skus': df['sku'].nunique(),
        'date_range': f"{df['date'].min().date()} to {df['date'].max().date()}",
        'missing_days': len(expected_range) - df['date'].nunique(),
        'zero_days': len(df[df['sales'] == 0])
    }
