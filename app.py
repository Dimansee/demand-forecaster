import streamlit as st
from data_cleaning import auto_clean_sales_file, run_integrity_check
from ui_components import show_static_documentation

# 1. DATA INTAKE (5 CSVs)
st.subheader("1. Data Intake")
c1, c2 = st.columns(2)
with c1:
    sales_file = st.file_uploader("Sales History (Required)", type=["csv"])
    mkt_file = st.file_uploader("Marketing Spend", type=["csv"])
with c2:
    fest_file = st.file_uploader("Festival Calendar", type=["csv"])
    event_file = st.file_uploader("Events / PR", type=["csv"])
    master_file = st.file_uploader("SKU Master", type=["csv"])

# 2. DATA INTEGRITY CHECK
if sales_file:
    st.divider()
    st.subheader("🔍 Data Integrity Check")
    cleaned_sales = auto_clean_sales_file(sales_file)
    issues = run_integrity_check(cleaned_sales, "Sales")
    for issue in issues: st.warning(issue)
    if not issues: st.success("✅ Sales Data Integrity Verified")

# 3. DOWNLOAD TEMPLATES
st.divider()
st.subheader("📥 Download Templates")
t1, t2, t3, t4, t5 = st.columns(5)
t1.download_button("Sales CSV", "date,sku,sales\n2026-01-01,SKU01,50", "template_sales.csv")
t2.download_button("Mkt CSV", "date,spend\n2026-01-01,1000", "template_mkt.csv")
# ... Add t3, t4, t5 templates ...
