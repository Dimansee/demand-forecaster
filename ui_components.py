import streamlit as st
import knowledge_center as kc

def show_static_documentation():
    st.title("📖 Comprehensive System Manual")
    tab1, tab2, tab3 = st.tabs(["📊 KPI Definitions", "🧠 Model Mechanics", "🛠️ Module Overview"])

    with tab1:
        st.subheader("Key Performance Indicators (KPIs)")
        st.markdown(f"**1. Gross Demand**: {kc.KPI_DEFINITIONS['Gross Demand']}")
        st.write(f"**2. Return Rate (%)**")
        st.write(f"- Logic: {kc.KPI_DEFINITIONS['Return Rate']['Logic']}")
        st.write(f"- Formula: {kc.KPI_DEFINITIONS['Return Rate']['Formula']}")
        st.write(f"- Business Value: {kc.KPI_DEFINITIONS['Return Rate']['Value']}")
        # ... Add Trend Surge and Safety Buffer similarly ...

    with tab2:
        st.subheader("Algorithmic Logic")
        for model, details in kc.MODEL_MECHANICS.items():
            st.write(f"### {model}")
            if isinstance(details, list):
                for line in details: st.write(line)
            else: st.write(details)

    with tab3:
        st.subheader("Module Functionality")
        for module, desc in kc.MODULE_OVERVIEW.items():
            st.write(f"**{module}**: {desc}")
