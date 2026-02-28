import streamlit as st

def strategy_section(df):

    st.subheader("1. Model & Strategy Selection")

    col1, col2 = st.columns(2)

    with col1:
        business_type = st.selectbox(
            "Industry Strategy",
            ["Fashion","FMCG","Electronics","Seasonal","Custom"]
        )

        selected_sku = st.selectbox("Select Target SKU", df['sku'].unique())

    with col2:
        model_choice = st.selectbox(
            "Forecast Model",
            ["Prophet","Decision Tree","KNN","Moving Average"]
        )

    st.divider()

    st.subheader("2. Operational Levers")

    use_default = st.toggle("Use AI Suggested Settings", value=True)

    if use_default:
        d_returns = 25 if business_type=="Fashion" else 10
        d_buffer = 15
        d_surge = 1.0
        d_marketing = 0
        d_lead = 30

    else:
        col1,col2,col3 = st.columns(3)

        with col1:
            d_returns = st.number_input("Return %",0,100,25)
            d_buffer = st.number_input("Buffer %",0,100,15)

        with col2:
            d_surge = st.number_input("Trend Surge",0.5,5.0,1.0)
            d_lead = st.number_input("Lead Time",1,365,30)

        with col3:
            d_marketing = st.number_input("Marketing Lift %",0,500,0)

    return {
        "business_type": business_type,
        "selected_sku": selected_sku,
        "model_choice": model_choice,
        "returns": d_returns,
        "buffer": d_buffer,
        "surge": d_surge,
        "marketing": d_marketing,
        "lead": d_lead
    }
