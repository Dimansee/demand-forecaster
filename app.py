import streamlit as st
import pandas as pd
from data_cleaning import auto_clean_sales_file, run_integrity_check
from ui_components import show_static_documentation

# --- PAGE SETUP ---
st.set_page_config(page_title="Demand Engine", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = "Forecaster"

pg = st.sidebar.radio("Navigation", ["Forecaster", "Documentation"], index=0)

if pg == "Documentation":
    show_static_documentation()
else:
    st.title("📈 Demand Engine & Strategy Simulator")
    tab_data, tab_engine, tab_viz = st.tabs(["📤 Data Sources", "🧠 Model Tuning", "📊 Forecast Analytics"])

    with tab_data:
        # --- 1. DATA INTAKE SECTION ---
        st.header("1. Data Intake")
        
        # Grid for 5 Uploaders (3 in top row, 2 in bottom row to match screenshot)
        col1, col2, col3 = st.columns(3)
        with col1:
            sales_f = st.file_uploader("Sales History (Required)", type=["csv"], help="Upload historical sales data")
        with col2:
            mkt_f = st.file_uploader("Marketing Spend (Optional)", type=["csv"])
        with col3:
            event_f = st.file_uploader("Events / PR (Optional)", type=["csv"])

        col4, col5, _ = st.columns(3)
        with col4:
            master_f = st.file_uploader("SKU Master (Optional)", type=["csv"])
        with col5:
            fest_f = st.file_uploader("Festival Calendar (Optional)", type=["csv"])

        st.divider()

        # --- 2. DATA INTEGRITY CHECK SECTION ---
        st.header("🔍 Data Integrity Check")

        # Injecting custom CSS for the "dark/grayed-out" look
        st.markdown("""
            <style>
            .status-badge {
                padding: 20px;
                border-radius: 5px;
                text-align: center;
                color: white;
                margin-bottom: 10px;
                height: 100px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .status-required { background-color: #4b2525; border: 1px solid #ff4b4b; }
            .status-optional { background-color: #1a2634; border: 1px solid #3d5afe; }
            .status-missing { background-color: #1e1e1e; border: 1px dotted #444; color: #888; }
            .status-success { background-color: #1e3a1e; border: 1px solid #28a745; }
            </style>
        """, unsafe_allow_html=True)

        b1, b2, b3, b4, b5 = st.columns(5)

        # --- Sales Status (Required) ---
        if sales_f:
            cleaned_sales = auto_clean_sales_file(sales_f)
            reports = run_integrity_check(cleaned_sales, "Sales")
            b1.markdown('<div class="status-badge status-success">✅ Sales<br>Loaded</div>', unsafe_allow_html=True)
    
            # Specific integrity alerts
            for r in reports:
                if "⚠️" in r: st.warning(r)
                elif "✅" in r: st.success(r)
    
            # Verification Preview & Download
            st.subheader("📋 Verification Preview")
            st.dataframe(cleaned_sales.head(5), use_container_width=True)
    
            csv = cleaned_sales.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Cleaned Sales for User Verification",
                data=csv,
                file_name="verified_cleaned_sales.csv",
                mime="text/csv"
            )
            st.session_state['ready_data'] = cleaned_sales
        else:
            b1.markdown('<div class="status-badge status-required">Sales<br>Required</div>', unsafe_allow_html=True)

        # --- Optional File Status Badges ---
        # SKU Master
        if master_f:
            b2.markdown('<div class="status-badge status-optional">🔵 SKU Master<br>Loaded</div>', unsafe_allow_html=True)
        else:
            b2.markdown('<div class="status-badge status-missing">SKU Master<br>Optional</div>', unsafe_allow_html=True)

        # Marketing
        if mkt_f:
            b3.markdown('<div class="status-badge status-optional">🔵 Marketing<br>Loaded</div>', unsafe_allow_html=True)
        else:
            b3.markdown('<div class="status-badge status-missing">Marketing<br>Optional</div>', unsafe_allow_html=True)

        # Festivals
        if fest_f:
            b4.markdown('<div class="status-badge status-optional">🔵 Festivals<br>Loaded</div>', unsafe_allow_html=True)
        else:
            b4.markdown('<div class="status-badge status-missing">Festivals<br>Optional</div>', unsafe_allow_html=True)

        # Events
        if event_f:
            b5.markdown('<div class="status-badge status-optional">🔵 Events<br>Loaded</div>', unsafe_allow_html=True)
        else:
            b5.markdown('<div class="status-badge status-missing">Events<br>Optional</div>', unsafe_allow_html=True)

        # --- 3. DOWNLOAD TEMPLATES SECTION ---
        st.header("📥 Download Templates")
        t1, t2, t3, t4, t5 = st.columns(5)
        
        t1.download_button("Sales CSV", "date,sku,sales\n2026-01-01,SKU01,100", "sales_template.csv", use_container_width=True)
        t2.download_button("Master CSV", "sku,category,price\nSKU01,Fashion,49.99", "master_template.csv", use_container_width=True)
        t3.download_button("Marketing CSV", "date,spend\n2026-01-01,5000", "mkt_template.csv", use_container_width=True)
        t4.download_button("Festival CSV", "date,festival\n2026-11-08,Diwali", "fest_template.csv", use_container_width=True)
        t5.download_button("Events CSV", "date,event_name\n2026-05-15,Flash_Sale", "event_template.csv", use_container_width=True)

