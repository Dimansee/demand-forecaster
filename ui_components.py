import streamlit as st
import knowledge_center as kc  # Import the new instruction file

def show_static_documentation():
    st.title("📖 Comprehensive System Manual")
    
    doc_tabs = st.tabs(["📊 KPI Definitions", "🧠 Model Mechanics", "🧼 Data Logic"])
    
    with doc_tabs[0]:
        st.subheader("Key Performance Indicators")
        st.markdown(kc.KPI_INFO["gross_demand"])
        st.markdown(kc.KPI_INFO["return_rate"])
        st.markdown(kc.KPI_INFO["safety_buffer"])

    with doc_tabs[1]:
        st.subheader("Algorithmic Logic")
        for model, desc in kc.MODEL_MECHANICS.items():
            st.write(f"**{model}**: {desc}")

    with doc_tabs[2]:
        st.subheader("Cleaning & System Guide")
        st.markdown(kc.SYSTEM_GUIDE)
        st.divider()
        st.markdown(kc.CLEANING_PROTOCOLS)
        
    if st.button("Close Manual"):
        st.session_state.page = "Forecaster"
        st.rerun()
