import pandas as pd
import streamlit as st

def clean_dates(df):
    """Ensures consistent date formatting across all files."""
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['date'])
    return df

def clean_all_data(sales_file, marketing_file=None, festival_file=None, events_file=None, sku_master_file=None):
    df = pd.DataFrame()

    # 1. PRIMARY SALES DATA
    try:
        df = pd.read_csv(sales_file)
        df = clean_dates(df)
        if not all(col in df.columns for col in ['date', 'sku', 'sales']):
            st.error("Sales file must contain: date, sku, sales")
            st.stop()
        df = df[df['sales'] >= 0]
        st.success("✅ Sales history loaded")
    except Exception as e:
        st.error(f"❌ Sales file error: {e}")
        st.stop()

    # 2. SKU MASTER (THE INTELLIGENCE LAYER)
    if sku_master_file:
        try:
            sku_master = pd.read_csv(sku_master_file)
            # Merge attributes (Category, Color, Fabric, etc.) onto the sales data
            df = df.merge(sku_master, on='sku', how='left')
            st.success("✅ SKU Master attributes integrated")
        except Exception as e:
            st.error(f"❌ SKU Master error: {e}")

    # 3. MARKETING DATA
    if marketing_file:
        try:
            marketing = pd.read_csv(marketing_file)
            marketing = clean_dates(marketing)
            df = df.merge(marketing, on=['date', 'sku'], how='left')
            st.success("✅ Marketing spend linked")
        except:
            st.error("⚠️ Marketing file format incorrect - skipping")

    # 4. FESTIVAL & EVENTS (TIME REGRESSORS)
    if festival_file:
        try:
            festival = pd.read_csv(festival_file)
            festival = clean_dates(festival)
            df = df.merge(festival, on='date', how='left')
            st.success("✅ Festival calendar synced")
        except:
            st.error("⚠️ Festival file error - skipping")

    if events_file:
        try:
            events = pd.read_csv(events_file)
            events = clean_dates(events)
            df = df.merge(events, on='date', how='left')
            st.success("✅ External events synced")
        except:
            st.error("⚠️ Events file error - skipping")

    # 5. DATA ENRICHMENT & FEATURE ENGINEERING
    # Fill missing values for regressors
    fill_cols = ['marketing_spend', 'festival_flag', 'event_flag']
    for col in fill_cols:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = df[col].fillna(0)

    # Advanced Time Features (Crucial for Fashion/Retail)
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    # Calculate days since last festival (The 'Hangover' or 'Anticipation' effect)
    if 'festival_flag' in df.columns:
        df['is_festival_season'] = df['month'].apply(lambda x: 1 if x in [10, 11, 12] else 0)

    # 6. CATEGORICAL CLEANING
    # If SKU Master was uploaded, fill missing attributes with 'Unknown'
    # This prevents ML models from crashing due to NaN values
    text_cols = df.select_dtypes(include=['object']).columns
    df[text_cols] = df[text_cols].fillna('Unknown')

    return df