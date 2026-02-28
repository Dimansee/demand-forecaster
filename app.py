import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from data_cleaning import auto_clean_sales_file, run_integrity_check
from ui_components import show_static_documentation, render_festival_calendar
from logic_overrides import apply_strategy_logic, FESTIVAL_DICT, apply_holiday_boost
from forecast_engine import get_forecast

st.set_page_config(page_title="Pro Demand Planner v5.6", layout="wide")

# --- CUSTOM CSS FOR BADGES ---
st.markdown("""
    <style>
    .status-badge { padding: 15px; border-radius: 8px; text-align: center; color: white; margin-bottom: 10px; height: 110px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
    .status-required { background-color: #4b2525; border: 1px solid #ff4b4b; }
    .status-optional { background-color: #1a2634; border: 1px solid #3d5afe; }
    .status-missing { background-color: #1e1e1e; border: 1px dotted #444; color: #888; }
    .status-success { background-color: #1e3a1e; border: 1px solid #28a745; }
    </style>
""", unsafe_allow_html=True)

# Navigation
pg = st.sidebar.radio("Navigation", ["Forecaster", "Documentation"], index=0)

if pg == "Documentation":
    show_static_documentation()
else:
    st.title("📈 Demand Engine & Strategy Simulator")
    tab_data, tab_engine, tab_viz = st.tabs(["📤 Data Sources", "🧠 Model Tuning", "📊 Forecast Analytics"])

    with tab_data:
        st.header("1. Data Intake")
        col1, col2, col3 = st.columns(3)
        with col1: sales_f = st.file_uploader("Sales History (Required)", type=["csv"])
        with col2: mkt_f = st.file_uploader("Marketing Spend (Optional)", type=["csv"])
        with col3: event_f = st.file_uploader("Events / PR (Optional)", type=["csv"])
        col4, col5, _ = st.columns(3)
        with col4: master_f = st.file_uploader("SKU Master (Optional)", type=["csv"])
        with col5: fest_f = st.file_uploader("Festival Calendar (Optional)", type=["csv"])

        st.divider()
        st.header("🔍 Data Integrity Check")
        b1, b2, b3, b4, b5 = st.columns(5)
        
        if sales_f:
            cleaned_sales = auto_clean_sales_file(sales_f)
            st.session_state['cleaned_df'] = cleaned_sales
            reports = run_integrity_check(cleaned_sales, "Sales")
            b1.markdown('<div class="status-badge status-success">✅ Sales<br>Loaded</div>', unsafe_allow_html=True)
            for r in reports:
                if "⚠️" in r: st.warning(r)
                elif "✅" in r: st.success(r)
            
            st.subheader("📋 Verification Preview")
            st.dataframe(cleaned_sales.head(5), use_container_width=True)
            st.download_button("📥 Download Cleaned Sales", cleaned_sales.to_csv(index=False).encode('utf-8'), "verified_sales.csv")
        else:
            b1.markdown('<div class="status-badge status-required">Sales<br>Required</div>', unsafe_allow_html=True)

        # Status Badges for Optional Files
        for b, f, n in zip([b2, b3, b4, b5], [master_f, mkt_f, fest_f, event_f], ["SKU Master", "Marketing", "Festivals", "Events"]):
            status = "status-optional" if f else "status-missing"
            label = "Loaded" if f else "Optional"
            b.markdown(f'<div class="status-badge {status}">{n}<br>{label}</div>', unsafe_allow_html=True)

    with tab_engine:
        if 'cleaned_df' in st.session_state:
            df = st.session_state['cleaned_df']
            st.header("🧠 Model Tuning & Strategy")
            
            # --- 1. SELECTION ---
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                # ADDED: "Custom" strategy option
                biz_type = st.selectbox("Industry Strategy", ["Fashion", "FMCG", "Electronics", "Seasonal", "Custom"])
                selected_sku = st.selectbox("Select Target SKU", df['sku'].unique())
            with c_p2:
                model_choice = st.selectbox("Forecast Algorithm", ["Prophet", "Decision Tree", "KNN", "Moving Average"])
            
            st.divider()

            # --- 2. OPERATIONAL LEVERS (User Customization) ---
            st.subheader("⚙️ Operational Levers")
            use_ai = st.toggle("Use AI-Suggested Settings", value=True)
            l1, l2, l3 = st.columns(3)
            
            if use_ai:
                d_ret, d_buff, d_surge, d_mkt = (25 if biz_type=="Fashion" else 10), 15, 1.0, 0
            else:
                with l1:
                    d_ret = st.number_input("Expected Return Rate (%)", 0, 100, 25)
                    d_buff = st.number_input("Safety Buffer (%)", 0, 100, 15)
                with l2:
                    d_surge = st.number_input("Trend Surge Factor (x)", 0.5, 5.0, 1.0, 0.1)
                with l3:
                    d_mkt = st.number_input("Marketing Lift (%)", 0, 500, 0)

            st.divider()

            # --- 3. FESTIVAL CALENDAR ---
            st.subheader("📅 Multi-Festival Calendar Control")
            cf1, cf2 = st.columns([1, 2])
            with cf1:
                selected_fests = st.multiselect("Active Festivals", list(FESTIVAL_DICT.keys()), default=["Christmas"])
                peak_lift = st.slider("Peak Day Lift %", 10, 200, 60)
                win_lift = st.slider("Window Days Lift %", 5, 100, 30)
            
            with cf2:
                for f_name in selected_fests:
                    f_date = FESTIVAL_DICT[f_name]
                    fig = render_festival_calendar(f_name, f_date)
                    st.plotly_chart(fig, use_container_width=True)

            if st.button("🚀 Run Forecast Simulation", use_container_width=True):
                raw = get_forecast(df, selected_sku, model_choice, biz_type)
                # Apply Festival Logic
                raw = apply_holiday_boost(raw, selected_fests, peak_lift, win_lift)
                # Apply Strategy Logic
                final = apply_strategy_logic(raw, d_surge, d_mkt, d_ret, d_buff)
                st.session_state['current_forecast'] = final
                st.success("Simulation Complete!")
        else:
            st.warning("Please upload Sales Data first.")

    with tab_viz:
        if 'current_forecast' in st.session_state and 'cleaned_df' in st.session_state:
            res = st.session_state['current_forecast']
            hist_df = st.session_state['cleaned_df']

            # 1. Prepare Historical Data (Last 90-180 days for context)
            sku_hist = hist_df[hist_df['sku'] == selected_sku].copy().sort_values('date')
            sku_hist['type'] = 'Historical (Smooth)'
            # Optional: 7-day rolling average to match your reference image
            sku_hist['sales_smooth'] = sku_hist['sales']

            # 2. Prepare Forecast Data
            res['type'] = 'Strategy Plan'
    
            st.header("📊 Forecast Analytics")
    
            # METRICS ROW (Same as your reference image)
            m1, m2, m3, m4 = st.columns(4)
            past_total = sku_hist['sales'].tail(90).sum()
            future_total = res['forecast'].sum()
            growth = ((future_total - past_total) / past_total) * 100 if past_total > 0 else 0
    
            m1.metric("Gross Demand Forecast", f"{int(future_total):,}", f"{growth:+.1f}% vs Past 90d")
            m2.metric("Inventory Target", f"{int(res['inventory_target'].sum()):,}", f"Buffer: {d_buff}%")
            m3.metric("Avg Daily Demand", f"{int(res['forecast'].mean()):,}")
            m4.metric("Production Ready By", (datetime.now() + timedelta(days=30)).strftime("%d %b"))

            # 3. COMBINED VISUALIZATION (Plotly Graph Objects)
            import plotly.graph_objects as go
    
            fig = go.Figure()

            # Add Historical Line
            fig.add_trace(go.Scatter(
                x=sku_hist['date'], y=sku_hist['sales_smooth'],
                name="Historical (Smooth)",
                line=dict(color='royalblue', width=3)
            ))

            # Add Forecast Line (Strategy Plan)
            fig.add_trace(go.Scatter(
                x=res['date'], y=res['forecast'],
                name="Strategy Plan",
                line=dict(color='#00ffcc', width=4)
            ))

            # Add Festival Highlight Rectangles (Optional, but in your reference)
            for f in selected_fests:
                if f in FESTIVAL_DICT:
                    t = pd.to_datetime(FESTIVAL_DICT[f])
                    fig.add_vrect(
                        x0=t-timedelta(days=2), x1=t+timedelta(days=2),
                        fillcolor="orange", opacity=0.15, layer="below", line_width=0,
                        annotation_text=f
                    )

            fig.update_layout(
                template="plotly_dark", 
                hovermode="x unified",
                height = 600,
                margin = dict(l=0, r=0, t=0, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
    
            st.plotly_chart(fig, use_container_width=True)
    
            # Detailed Table
            st.subheader("📋 Production Execution Schedule")
            st.dataframe(res[['date', 'forecast', 'net_demand', 'inventory_target']].head(20), use_container_width=True)




