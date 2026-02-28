
import streamlit as st

def show_static_documentation():

    st.title("📖 Comprehensive System Manual")

    tabs = st.tabs(["📊 KPI Definitions", "🧠 Model Mechanics"])

    with tabs[0]:
        st.markdown("""
        ### Gross Demand
        Raw AI prediction.

        ### Net Demand
        `Gross * (1 - Return%)`

        ### Inventory Target
        `Net * (1 + Buffer%)`
        """)

    with tabs[1]:
        st.markdown("""
        Prophet → Trend + Seasonality  
        KNN → Similar days  
        Decision Tree → Rule-based demand  
        Moving Avg → Baseline smoothing
        """)
