import streamlit as st
import pandas as pd
import io
from data_cleaning import auto_clean_sales_file, run_integrity_check
from ui_components import show_static_documentation, render_festival_calendar
from logic_overrides import apply_strategy_logic, FESTIVAL_DICT
from forecast_engine import get_forecast

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Pro Demand Planner v5.6", layout="wide", page_icon="📈")

# --- CUSTOM CSS FOR STATUS BADGES ---
st.markdown("""
    <style>
    .status-badge {
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        color: white;
        margin-bottom: 10px;
        height: 110px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 14px;
    }
    .status-required { background-color: #4b2525; border: 1px solid #ff4b4b; }
    .status-optional { background-color: #1a2634; border: 1px solid #3d5afe; }
    .status-missing { background-color: #1e1e1e; border: 1px dotted #444; color: #888; }
    .status-success { background-color: #1e3a1e; border: 1px solid #28a745; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state:
    st.session_state.page = "Forecaster"
if 'cleaned_df' not in st.session_state:
    st.session_state['cleaned_df'] = None
if 'current_forecast' not in st.session_state:
    st.session_state['current_forecast'] = None

# --- NAVIGATION ---
pg = st.sidebar.radio("Navigation", ["Forecaster", "Documentation"], index=0)

if pg == "Documentation":
    show_static_documentation() #
else:
    st.title("📈 Demand Engine & Strategy Simulator")
    tab_data, tab_engine, tab_viz = st.tabs(["📤 Data Sources", "🧠 Model Tuning", "📊 Forecast Analytics"])

    # ==========================================
    # TAB 1: DATA SOURCES
    # ==========================================
    with tab_data:
        st.header("1. Data Intake")
        
        # Grid for 5 Uploaders
        col1, col2, col3 = st.columns(3)
        with col1:
            sales_f = st.file_uploader("Sales History (Required)", type=["csv"])
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

        # --- 2. DATA INTEGRITY CHECK ---
        st.header("🔍 Data Integrity Check")
        b1, b2, b3, b4, b5 = st.columns(5)
        
        # Sales Handling
        if sales_f:
            cleaned_sales = auto_clean_sales_file(sales_f) #
            st.session_state['cleaned_df'] = cleaned_sales
            reports = run_integrity_check(cleaned_sales, "Sales") #
            
            b1.markdown('<div class="status-badge status-success">✅ Sales<br>Loaded</div>', unsafe_allow_html=True)
            
            # Display Integrity Warnings/Success
            for r in reports:
                if "⚠️" in r: st.warning(r)
                elif "✅" in r: st.success(r)
            
            # --- VERIFICATION PREVIEW & DOWNLOAD ---
            st.subheader("📋 Verification Preview")
            st.dataframe(cleaned_sales.head(10), use_container_width=True)
            
            csv = cleaned_sales.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Cleaned Sales for User Verification",
                data=csv,
                file_name="verified_cleaned_sales.csv",
                mime="text/csv"
            )
        else:
            b1.markdown('<div class="status-badge status-required">Sales<br>Required</div>', unsafe_allow_html=True)

        # Optional Badges
        b2.markdown(f'<div class="status-badge {"status-optional" if master_f else "status-missing"}">SKU Master<br>{"Loaded" if master_f else "Optional"}</div>', unsafe_allow_html=True)
        b3.markdown(f'<div class="status-badge {"status-optional" if mkt_f else "status-missing"}">Marketing<br>{"Loaded" if mkt_f else "Optional"}</div>', unsafe_allow_html=True)
        b4.markdown(f'<div class="status-badge {"status-optional" if fest_f else "status-missing"}">Festivals<br>{"Loaded" if fest_f else "Optional"}</div>', unsafe_allow_html=True)
        b5.markdown(f'<div class="status-badge {"status-optional" if event_f else "status-missing"}">Events<br>{"Loaded" if event_f else "Optional"}</div>', unsafe_allow_html=True)

        st.divider()

        # --- 3. DOWNLOAD TEMPLATES ---
        st.header("📥 Download Templates")
        t1, t2, t3, t4, t5 = st.columns(5)
        t1.download_button("Sales CSV", "date,sku,sales\n2026-01-01,SKU01,100", "sales_template.csv", use_container_width=True)
        t2.download_button("Master CSV", "sku,category,price\nSKU01,Fashion,49.99", "master_template.csv", use_container_width=True)
        t3.download_button("Marketing CSV", "date,spend\n2026-01-01,5000", "mkt_template.csv", use_container_width=True)
        t4.download_button("Festival CSV", "date,festival\n2026-11-08,Diwali", "fest_template.csv", use_container_width=True)
        t5.download_button("Events CSV", "date,event_name\n2026-05-15,Flash_Sale", "event_template.csv", use_container_width=True)

    # ==========================================
    # TAB 2: MODEL TUNING
    # ==========================================
    with tab_engine:
        if st.session_state['cleaned_df'] is not None:
            df = st.session_state['cleaned_df']
            
            st.header("🧠 Model Tuning & Strategy")
            col_tune1, col_tune2 = st.columns(2)
            
            with col_tune1:
                selected_sku = st.selectbox("Select Target SKU", options=df['sku'].unique())
                model_choice = st.selectbox("AI Algorithm", ["Prophet", "KNN", "Decision Tree", "Moving Average"])
                industry = st.selectbox("Industry Context", ["Fashion", "FMCG", "Electronics"])
                
            with col_tune2:
                horizon = st.slider("Forecast Horizon (Days)", 30, 180, 90)
                selected_fests = st.multiselect("Apply Festival Lifts", list(FESTIVAL_DICT.keys()))
                
            st.divider()
            
            # KPI Overrides Sliders
            st.subheader("⚙️ Business Strategy Overrides")
            s1, s2, s3, s4 = st.columns(4)
            surge = s1.number_input("Trend Surge (Multiplier)", 0.5, 3.0, 1.0, 0.1)
            mkt_lift = s2.slider("Marketing Impact %", 0, 100, 0)
            ret_rate = s3.slider("Est. Return Rate %", 0, 50, 15)
            buffer = s4.slider("Safety Buffer %", 0, 100, 20)

            if st.button("🚀 Run Forecast Simulation", use_container_width=True):
                with st.spinner("Processing AI Models..."):
                    # 1. Get raw forecast from engine
                    raw_forecast = get_forecast(df, selected_sku, model_choice, industry) #
                    
                    # 2. Apply Strategy Logic
                    final_forecast = apply_strategy_logic(raw_forecast, surge, mkt_lift, ret_rate, buffer) #
                    
                    st.session_state['current_forecast'] = final_forecast
                    st.success("Analysis Complete! Move to 'Forecast Analytics' to view results.")
        else:
            st.warning("⚠️ Please upload and verify Sales Data in 'Data Sources' first.")

    # ==========================================
    # TAB 3: ANALYTICS
    # ==========================================
    with tab_viz:
        if st.session_state['current_forecast'] is not None:
            res = st.session_state['current_forecast']
            st.header("📊 Forecast Analytics")
            
            # Metric Row
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Forecasted Units", f"{int(res['forecast'].sum()):,}")
            m2.metric("Net Demand (Post-Returns)", f"{int(res['net_demand'].sum()):,}")
            m3.metric("Recommended Production", f"{int(res['inventory_target'].sum()):,}")
            
            # Chart
            import plotly.express as px
            fig = px.line(res, x='date', y=['forecast', 'net_demand', 'inventory_target'], 
                          title="90-Day Demand Projection", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 Detailed Output Table")
            st.dataframe(res, use_container_width=True)
        else:
            st.info("No forecast generated yet. Configure and run the model in the 'Model Tuning' tab.")
