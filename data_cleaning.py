import pandas as pd
import numpy as np
import streamlit as st
import io

def auto_clean_sales_file(file):
    """
    Standardizes column names, repairs data types, and aggregates 
    daily sales to ensure time-series integrity.
    """
    try:
        # Crucial fix for "No columns to parse": Reset file pointer
        file.seek(0)
        df = pd.read_csv(file)
        
        if df.empty:
            st.error("The uploaded file is empty.")
            return None

        # 1. Standardize column names (lowercase and stripped)
        df.columns = [c.strip().lower() for c in df.columns]
        
        # 2. Advanced Mapping (Handles variations in user CSVs)
        rename_map = {
            'date': 'date', 'dat': 'date', 'timestamp': 'date',
            'quantity': 'sales', 'qty': 'sales', 'sales': 'sales', 'sold': 'sales',
            'product': 'product_name', 'item': 'product_name',
            'order number': 'order_id', 'id': 'order_id'
        }
        df = df.rename(columns=rename_map)

        # 3. Structural Validation
        if 'date' not in df.columns:
            st.error("❌ 'Date' column missing. Expected headers like: Date, SKU, Sales.")
            return None

        # 4. Data Type Repair
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date']) 
        
        # Numeric Repair for Sales
        if 'sales' in df.columns:
            df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
        else:
            # Fallback: Find first available numeric column
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if not numeric_cols.empty:
                df = df.rename(columns={numeric_cols[0]: 'sales'})
            else:
                df['sales'] = 0

        # Fill optional columns
        for col in ['sku', 'product_name', 'order_id']:
            if col not in df.columns:
                df[col] = "Default_SKU" if col == 'sku' else "N/A"

        # 5. Deduplication & Daily Aggregation
        # This prevents duplicate dates for the same SKU which breaks Prophet/ML models
        df = df.groupby(['date', 'sku']).agg({'sales': 'sum'}).reset_index()
        
        # 6. Sorting
        df = df.sort_values(['sku', 'date'])
        
        return df
    except Exception as e:
        st.error(f"Auto-Cleaning System Error: {e}")
        return None

def get_data_health_report(df):
    """
    Generates statistics regarding data gaps and quality.
    """
    report = {}
    report['total_records'] = len(df)
    report['unique_skus'] = df['sku'].nunique()
    report['date_range'] = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
    
    # Identify Gaps in dates (Expected vs Actual)
    expected_range = pd.date_range(start=df['date'].min(), end=df['date'].max())
    report['missing_days'] = len(expected_range) - df['date'].nunique()
    
    # Identify Zero Sales Days
    report['zero_days'] = len(df[df['sales'] == 0])
    return report

def convert_to_csv(df):
    """
    Helper to prepare data for the download button.
    """
    return df.to_csv(index=False).encode('utf-8')
