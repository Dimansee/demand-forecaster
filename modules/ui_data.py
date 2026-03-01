import streamlit as st
import pandas as pd

def data_section():

    st.subheader("1. Data Intake")

    c1, c2, c3 = st.columns(3)

    with c1:
        sales_file = st.file_uploader("Sales History (Required)", type=["csv"])
        sku_master_file = st.file_uploader("SKU Master (Optional)", type=["csv"])

    with c2:
        marketing_file = st.file_uploader("Marketing Spend (Optional)", type=["csv"])
        festival_file = st.file_uploader("Festival Calendar (Optional)", type=["csv"])

    with c3:
        events_file = st.file_uploader("Events / PR (Optional)", type=["csv"])

    st.divider()

    st.subheader("🔍 Data Integrity Check")

    status_cols = st.columns(5)
    files = [
        ("Sales", sales_file, True),
        ("SKU Master", sku_master_file, False),
        ("Marketing", marketing_file, False),
        ("Festivals", festival_file, False),
        ("Events", events_file, False)
    ]

    for i, (name, f, req) in enumerate(files):
        with status_cols[i]:
            if f:
                st.success(f"{name} Loaded")
            elif req:
                st.error(f"{name} Required")
            else:
                st.info(f"{name} Optional")

    st.divider()

    st.subheader("📥 Download Templates")

    t_cols = st.columns(5)

    t_cols[0].download_button("Sales CSV",
        "date,sku,sales\n2026-01-01,SKU01,50", "sales_template.csv")

    t_cols[1].download_button("Master CSV",
        "sku,category\nSKU01,Topwear", "master_template.csv")

    t_cols[2].download_button("Marketing CSV",
        "date,sku,marketing_spend\n2026-01-01,SKU01,1500", "marketing_template.csv")

    t_cols[3].download_button("Festival CSV",
        "date,festival_flag\n2026-12-25,1", "festival_template.csv")

    t_cols[4].download_button("Events CSV",
        "date,event_flag\n2026-06-01,1", "events_template.csv")

    # ---------- CLEAN + PREVIEW ----------
    if sales_file:

        from modules.data_cleaning import clean_all_data

        df_preview = clean_all_data(
            sales_file,
            marketing_file,
            festival_file,
            events_file,
            sku_master_file
        )

        st.divider()
        st.subheader("🧹 Cleaned Data Preview")
        st.dataframe(df_preview.head(10), use_container_width=True)

        st.download_button(
            "📥 Download Cleaned Data",
            df_preview.to_csv(index=False),
            "cleaned_data.csv"
        )

    return {
        "sales_file": sales_file,
        "sku_master_file": sku_master_file,
        "marketing_file": marketing_file,
        "festival_file": festival_file,
        "events_file": events_file
    }
