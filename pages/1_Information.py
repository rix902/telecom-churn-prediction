import streamlit as st
from utils import set_bg

set_bg()

st.title("📋 Customer Information")

if "logged_in" not in st.session_state:
    st.warning("Login first")
    st.stop()

# Inputs
call_failure = st.number_input("Call Failure", 0, 100)
subscription_length = st.number_input("Subscription Length", 1, 60)
frequency_of_use = st.number_input("Frequency of use", 0, 1000)
customer_value = st.number_input("Customer Value", 0, 1000)
age = st.number_input("Age", 18, 80)

complains = st.selectbox("Complains", ["No", "Yes"])

if st.button("Next ➡"):
    st.session_state["input_data"] = {
        "Call  Failure": call_failure,
        "Subscription  Length": subscription_length,
        "Frequency of use": frequency_of_use,
        "Customer Value": customer_value,
        "Age": age,
        "Complains": 1 if complains == "Yes" else 0
    }
    st.switch_page("pages/2_Prediction.py")
