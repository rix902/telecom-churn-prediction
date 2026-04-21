import streamlit as st
from utils import set_bg

set_bg()

st.set_page_config(page_title="Login")

st.title("🔐 Login / Signup")

# Session me users store (temporary DB)
if "users" not in st.session_state:
    st.session_state["users"] = {}

username = st.text_input("Username")
password = st.text_input("Password", type="password")

col1, col2 = st.columns(2)

# ---------------- LOGIN ----------------
with col1:
    if st.button("Login"):
        users = st.session_state["users"]

        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.success(f"Welcome {username} ✅")
            st.switch_page("pages/1_Information.py")
        else:
            st.error("User not found ❌ (Signup first)")

# ---------------- SIGNUP ----------------
with col2:
    if st.button("Signup"):
        users = st.session_state["users"]

        if username in users:
            st.warning("User already exists ⚠")
        else:
            users[username] = password
            st.success("Account created ✅ Now login")
