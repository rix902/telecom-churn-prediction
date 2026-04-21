import streamlit as st

st.title("📋 Add Customer Information")

if "logged_in" not in st.session_state:
    st.warning("Please login first")
    st.stop()

call_failure = st.number_input("Call Failure", 0, 100)
subscription_length = st.number_input("Subscription Length", 1, 60)
age = st.number_input("Age", 18, 80)

if st.button("Next ➡"):
    st.session_state["input_data"] = {
        "Call Failure": call_failure,
        "Subscription Length": subscription_length,
        "Age": age
    }
    st.switch_page("pages/2_Prediction.py")
