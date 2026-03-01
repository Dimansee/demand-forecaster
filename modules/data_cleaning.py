import pandas as pd
import streamlit as st
import io


# ---------------- SAFE DATE PARSER ----------------
def safe_date_parse(df, col):

    if col not in df.columns:
        st.error(f"❌ Missing required column: {col}")
        st.stop()

    df[col] = pd.to_datetime(
        df[col],
        errors='coerce',     # avoids crash
        dayfirst=True        # supports Indian format
    )

    if df[col].isna().sum() > 0:
        st.warning(f"⚠️ Some invalid dates in '{col}' were removed.")

    df = df.dropna(subset=[col])

    return df


# ---------------- SAFE CSV READER ----------------
def safe_read_csv(uploaded_file, file_label="File"):

    try:
        if uploaded_file is None:
            return None

        # Convert binary upload → readable string
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        df = pd.read_csv(stringio)

        if df.empty:
            st.warning(f"⚠️ {file_label} is empty — skipped")
            return None

        return df

    except Exception as e:
        st.warning(f"⚠️ {file_label} unreadable — skipped")
        return None


# ---------------- MAIN CLEANING FUNCTION ----------------
def clean_all_data(
        sales_file,
        marketing_file=None,
        festival_file=None,
        events_file=None,
        sku_master_file=None
    ):

    # ---------- SALES (REQUIRED) ----------
    sales = safe_read_csv(sales_file, "Sales File")

    if sales is None:
        st.error("❌ Sales file is required and must not be empty.")
        st.stop()

    required_cols = {'date', 'sku', 'sales'}

    if not required_cols.issubset(sales.columns):
        st.error("Sales file must contain: date, sku, sales")
        st.stop()

    sales = safe_date_parse(sales, 'date')
    sales = sales[sales['sales'] >= 0]

    st.success("✅ Sales history loaded")

    df = sales.copy()


    # ---------- SKU MASTER ----------
    sku_master = safe_read_csv(sku_master_file, "SKU Master")

    if sku_master is not None:
        if 'sku' in sku_master.columns:
            df = df.merge(sku_master, on='sku', how='left')
            st.success("✅ SKU Master integrated")
        else:
            st.warning("⚠️ SKU Master missing 'sku' column — skipped")


    # ---------- MARKETING ----------
    marketing = safe_read_csv(marketing_file, "Marketing")

    if marketing is not None:
        if 'date' in marketing.columns:
            marketing = safe_date_parse(marketing, 'date')

        merge_cols = list(set(['date', 'sku']).intersection(marketing.columns))

        if merge_cols:
            df = df.merge(marketing, on=merge_cols, how='left')
            st.success("✅ Marketing linked")


    # ---------- FESTIVAL ----------
    festival = safe_read_csv(festival_file, "Festival")

    if festival is not None:
        if 'date' in festival.columns:
            festival = safe_date_parse(festival, 'date')

        if 'date' in festival.columns:
            df = df.merge(festival, on='date', how='left')
            st.success("✅ Festival synced")


    # ---------- EVENTS ----------
    events = safe_read_csv(events_file, "Events")

    if events is not None:
        if 'date' in events.columns:
            events = safe_date_parse(events, 'date')

        if 'date' in events.columns:
            df = df.merge(events, on='date', how='left')
            st.success("✅ Events synced")


    # ---------- FILL NULLS ----------
    for col in ['marketing_spend', 'festival_flag', 'event_flag']:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = df[col].fillna(0)


    # ---------- FEATURE ENGINEERING ----------
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

    df.fillna(0, inplace=True)

    return df
