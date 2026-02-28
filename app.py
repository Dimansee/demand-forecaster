# app.py
import streamlit as st
from data_cleaning import auto_clean_sales_file, run_integrity_check
from ui_components import show_static_documentation

st.set_page_config(page_title="Pro Demand Planner v5.6", layout="wide")

# Navigation Control
if 'page' not in st.session_state: st.session_state.page = "Forecaster"
pg = st.sidebar.radio("Navigation", ["Forecaster", "Documentation"])

if pg == "Documentation":
    show_static_documentation() #
else:
    st.title("📈 Demand Engine & Strategy Simulator")
    tab_data, tab_engine, tab_viz = st.tabs(["📤 Data Sources", "🧠 Model Tuning", "📊 Analytics"])

    with tab_data:
        st.subheader("1. Data Intake")
        sales_f = st.file_uploader("Upload Sales History", type=["csv"])
    
        if sales_f:
            # Step A: Clean the data
            cleaned_sales = auto_clean_sales_file(sales_f)
        
            # Step B: Display Integrity Check
            st.divider()
            st.subheader("🔍 Data Integrity Check")
            health_reports = run_integrity_check(cleaned_sales, "Sales Data")
            for report in health_reports:
                if "✅" in report: st.success(report)
                elif "⚠️" in report: st.warning(report)
                else: st.info(report)
            
            # Step C: THE RE-CHECK OPTION (New Requirement)
            st.divider()
            st.subheader("2. Verify & Re-Check Cleaned Data")
            st.info("Download the cleaned version below to verify how the AI has repaired your headers and dates.")
        
            # Convert cleaned dataframe to CSV for download
            csv_buffer = cleaned_sales.to_csv(index=False).encode('utf-8')
        
            st.download_button(
                label="📥 Download Cleaned Sales for Verification",
                data=csv_buffer,
                file_name="verified_cleaned_sales.csv",
                mime="text/csv",
                help="Click here to see the file after column renaming and daily aggregation."
            )
        
            # Save to session state for other tabs
            st.session_state['ready_data'] = cleaned_sales

        # --- COMPLETE DOWNLOAD TEMPLATES SECTION ---
        st.divider()
        st.subheader("📥 Download All Templates")
        t1, t2, t3, t4, t5 = st.columns(5)
        
        t1.download_button("Sales Template", 
            "date,sku,sales\n2026-01-01,SKU001,150\n2026-01-02,SKU001,120", "template_sales.csv")
        
        t2.download_button("Marketing Template", 
            "date,spend,channel\n2026-01-01,5000,Social_Media", "template_marketing.csv")
        
        t3.download_button("SKU Master", 
            "sku,category,unit_price,lead_time_days\nSKU001,Fashion,45.00,14", "template_sku_master.csv")
        
        t4.download_button("Festival Template", 
            "date,festival_name,impact_score\n2026-11-08,Diwali,high", "template_festivals.csv")
        
        t5.download_button("Event Template", 
            "date,event_type,description\n2026-05-15,Flash_Sale,50% Storewide", "template_events.csv")

    with tab_engine:
        st.write("Model Tuning configurations will appear here once data is verified.")


