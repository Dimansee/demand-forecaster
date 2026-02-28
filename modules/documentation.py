import streamlit as st

def show_static_documentation():

    st.title("📖 System Knowledge Center")

    tabs = st.tabs(["📊 KPI Definitions", "🧠 Model Logic"])

    with tabs[0]:
        st.markdown("""
        ### Gross Demand
        Raw AI output before adjustments.

        ### Net Demand
        After returns adjustment.

        ### Inventory Target
        After safety buffer.

        ### Trend Surge
        Demand multiplier.

        ### Marketing Lift
        Promotion impact.
        """)

    with tabs[1]:
        st.markdown("""
        Prophet → Seasonality + Trend  
        Decision Tree → Rule-based logic  
        KNN → Similar day matching  
        Moving Average → Smoothing baseline
        """)
