import pandas as pd
import streamlit as st

def safe_date_parse(df, col):

    if col not in df.columns:
        st.error(f"❌ Missing required column: {col}")
        st.stop()

    df = df.copy()   # prevents SettingWithCopy warning

    df[col] = pd.to_datetime(
        df[col],
        errors='coerce',   # converts bad values to NaT instead of crashing
        dayfirst=True      # important for Indian date format
    )

    if df[col].isna().sum() > 0:
        st.warning(f"⚠️ Some invalid dates found in {col}. They were auto-cleaned.")

    df = df.dropna(subset=[col])

    return df


def clean_all_data(sales_file, marketing_file=None, festival_file=None, events_file=None, sku_master_file=None):

    # ---------------- SALES ----------------
    if sales_file is None:
        st.error("❌ Sales file is required")
        st.stop()

    sales = pd.read_csv(sales_file)

    if 'date' not in sales.columns or 'sku' not in sales.columns or 'sales' not in sales.columns:
        st.error("Sales file must contain: date, sku, sales")
        st.stop()

    sales = safe_date_parse(sales, 'date')

    dfs = [sales]

    # ---------------- MARKETING ----------------
    if marketing_file is not None:
        marketing = pd.read_csv(marketing_file)
        if 'date' in marketing.columns:
            marketing = safe_date_parse(marketing, 'date')
        dfs.append(marketing)

    # ---------------- FESTIVALS ----------------
    if festival_file is not None:
        fest = pd.read_csv(festival_file)
        if 'date' in fest.columns:
            fest = safe_date_parse(fest, 'date')
        dfs.append(fest)

    # ---------------- EVENTS ----------------
    if events_file is not None:
        events = pd.read_csv(events_file)
        if 'date' in events.columns:
            events = safe_date_parse(events, 'date')
        dfs.append(events)

    # ---------------- MERGE ----------------
    df = sales.copy()

    for extra in dfs[1:]:

        # find common keys safely
        common_cols = list(set(['date', 'sku']).intersection(extra.columns))

        if len(common_cols) >= 1:

            # avoid duplicate column clashes
            duplicate_cols = [col for col in extra.columns if col in df.columns and col not in common_cols]
            extra = extra.drop(columns=duplicate_cols)

            df = df.merge(extra, on=common_cols, how='left')

    df.fillna(0, inplace=True)

    return df
