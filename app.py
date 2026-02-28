import streamlit as st
from modules.ui_data import data_section
from modules.ui_strategy import strategy_section
from modules.ui_analytics import analytics_section
from modules.data_cleaning import clean_all_data
from modules.documentation import show_static_documentation

st.set_page_config(page_title="Demand Planner", layout="wide")

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Demand Forecaster", "System Documentation"]
)

# ---------------- PAGE ROUTING ----------------
if page == "System Documentation":
    show_static_documentation()

else:

    st.title("📈 Demand Engine & Strategy Simulator")

    tab1, tab2, tab3 = st.tabs(["📤 Data Sources", "🧠 Model Tuning", "📊 Forecast Analytics"])

    with tab1:
        uploaded = data_section()

    with tab2:
        if uploaded['sales_file']:
            df = clean_all_data(**uploaded)
            config = strategy_section(df)

    with tab3:
        if uploaded['sales_file']:
            analytics_section(df, config)
