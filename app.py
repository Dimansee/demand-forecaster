import streamlit as st
from data_cleaning import auto_clean_sales_file, run_integrity_check
from ui_components import show_static_documentation
from logic_overrides import apply_strategy_logic

st.set_page_config(page_title="Pro Demand Planner v5.6", layout="wide")

# Navigation Logic
if 'page' not in st.session_state: st.session_state.page = "Forecaster"
pg = st.sidebar.radio("Navigation", ["Forecaster", "Documentation"])

if pg == "Documentation":
    show_static_documentation() #
else:
    st.title("📈 Demand Engine & Strategy Simulator")
    tab_data, tab_engine, tab_viz = st.tabs(["📤 Data Sources", "🧠 Model Tuning", "📊 Analytics"])

    with tab_data:
        st.subheader("1. Data Intake (5-File System)")
        c1, c2 = st.columns(2)
        with c1:
            sales_f = st.file_uploader("Sales History (Required)", type=["csv"]) #
            mkt_f = st.file_uploader("Marketing Spend", type=["csv"])
            master_f = st.file_uploader("SKU Master", type=["csv"])
        with c2:
            fest_f = st.file_uploader("Festival Calendar", type=["csv"])
            event_f = st.file_uploader("Events / PR", type=["csv"])

        if sales_f:
            st.divider()
            st.subheader("🔍 Data Integrity Check") #
            cleaned_sales = auto_clean_sales_file(sales_f)
            issues = run_integrity_check(cleaned_sales, "Sales") #
            if not issues:
                st.success("✅ Sales Data Integrity Verified")
            else:
                for issue in issues: st.warning(issue)

        st.divider()
        st.subheader("📥 Download Templates") #
        t1, t2, t3 = st.columns(3)
        t1.download_button("Sales Template", "date,sku,sales\n2026-01-01,SKU01,100", "sales.csv")
        t2.download_button("Marketing Template", "date,spend\n2026-01-01,1500", "mkt.csv")
        t3.download_button("Festival Template", "date,festival\n2026-12-25,Christmas", "fest.csv")
