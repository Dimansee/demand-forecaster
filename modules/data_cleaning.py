import pandas as pd
import streamlit as st

# ---------- SAFE CSV READER (Fix for Streamlit Upload Crash) ----------
def safe_read_csv(file):
    if file is None:
        return None

    try:
        if file.size == 0:
            st.error("❌ Uploaded file is empty")
            st.stop()

        file.seek(0)   # 🔑 rewind file pointer before reading
        return pd.read_csv(file)

    except Exception as e:
        st.error(f"❌ Failed to read file: {e}")
        st.stop()


# ---------- SAFE DATE PARSER ----------
def safe_date_parse(df, col):

    if col not in df.columns:
        st.error(f"❌ Missing required column: {col}")
        st.stop()

    df = df.copy()

    df[col] = pd.to_datetime(
        df[col],
        errors='coerce',
        dayfirst=True
    )

    if df[col].isna().sum() > 0:
        st.warning(f"⚠️ Some invalid dates found in {col}. They were auto-cleaned.")

    df = df.dropna(subset=[col])

    return df


# ---------- MAIN CLEAN FUNCTION ----------
def clean_all_data(
    sales_file,
    marketing_file=None,
    festival_file=None,
    events_file=None,
    sku_master_file=None
):

    # ---------------- SALES ----------------
    if sales_file is None:
        st.error("❌ Sales file is required")
        st.stop()

    sales = safe_read_csv(sales_file)

    if 'date' not in sales.columns or 'sku' not in sales.columns or 'sales' not in sales.columns:
        st.error("Sales file must contain: date, sku, sales")
        st.stop()

    sales = safe_date_parse(sales, 'date')

    dfs = [sales]

    # ---------------- MARKETING ----------------
    if marketing_file is not None:
        marketing = safe_read_csv(marketing_file)
        if 'date' in marketing.columns:
            marketing = safe_date_parse(marketing, 'date')
        dfs.append(marketing)

    # ---------------- FESTIVALS ----------------
    if festival_file is not None:
        fest = safe_read_csv(festival_file)
        if 'date' in fest.columns:
            fest = safe_date_parse(fest, 'date')
        dfs.append(fest)

    # ---------------- EVENTS ----------------
    if events_file is not None:
        events = safe_read_csv(events_file)
        if 'date' in events.columns:
            events = safe_date_parse(events, 'date')
        dfs.append(events)

    # ---------------- SKU MASTER ----------------
    if sku_master_file is not None:
        sku_master = safe_read_csv(sku_master_file)
        dfs.append(sku_master)

    # ---------------- MERGE ----------------
    df = sales.copy()

    for extra in dfs[1:]:

        common_cols = list(set(['date', 'sku']).intersection(extra.columns))

        if len(common_cols) >= 1:

            duplicate_cols = [col for col in extra.columns if col in df.columns and col not in common_cols]
            extra = extra.drop(columns=duplicate_cols)

            df = df.merge(extra, on=common_cols, how='left')

    df.fillna(0, inplace=True)

    return df
