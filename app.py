import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

st.title("🔐 Login Page")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username == "admin" and password == "1234":
        st.session_state["logged_in"] = True
        st.success("Login Successful ✅")
        st.switch_page("pages/1_Add_Information.py")
    else:
        st.error("Invalid Credentials ❌")------------
st.markdown("---")
st.markdown("🚀 Telecom Churn Prediction | BCA Project create by  RAVI PRAJAPATI")
