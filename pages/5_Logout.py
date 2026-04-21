import streamlit as st

st.title("🚪 Logout")

st.session_state.clear()

st.success("Logged out successfully")

if st.button("Go Login"):
    st.switch_page("app.py")
