import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import hashlib

# ─── CONFIG ─────────────────────────
st.set_page_config(page_title="TelePredict AI", layout="wide")

# ─── USER SYSTEM ─────────────────────
USERS = {
    "admin@telepredict.ai": {"password": hashlib.sha256("Admin@123".encode()).hexdigest(), "name": "Admin"},
    "demo@telepredict.ai": {"password": hashlib.sha256("Demo@123".encode()).hexdigest(), "name": "Demo User"},
}

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def verify(email, pw):
    return email in USERS and USERS[email]["password"] == hash_password(pw)

def save_user(email, password, name):
    USERS[email] = {
        "password": hash_password(password),
        "name": name
    }

# ─── SESSION ─────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "page" not in st.session_state:
    st.session_state.page = "login"

# ─── MODEL ───────────────────────────
@st.cache_resource
def train_model():
    X = np.random.rand(200, 3)
    y = np.random.randint(0, 2, 200)
    model = RandomForestClassifier()
    model.fit(X, y)
    return model

# ─── LOGIN PAGE ──────────────────────
def show_login():
    st.title("📡 TelePredict AI - Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            if verify(email, password):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_name = USERS[email]["name"]
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials")

    with col2:
        if st.button("Create Account"):
            st.session_state.page = "signup"
            st.rerun()

# ─── SIGNUP PAGE ─────────────────────
def show_signup():
    st.title("🆕 Create Account")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if email in USERS:
            st.error("User already exists")
        elif name and email and password:
            save_user(email, password, name)
            st.success("Account created successfully")
        else:
            st.error("Fill all fields")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# ─── DASHBOARD ───────────────────────
def show_dashboard():
    st.title("📊 Dashboard")
    st.write(f"Welcome {st.session_state.user_name}")

# ─── PREDICTOR ───────────────────────
def show_predictor():
    st.title("🔮 Churn Predictor")

    model = train_model()

    x1 = st.slider("Feature 1", 0.0, 1.0)
    x2 = st.slider("Feature 2", 0.0, 1.0)
    x3 = st.slider("Feature 3", 0.0, 1.0)

    if st.button("Predict"):
        pred = model.predict([[x1, x2, x3]])
        st.success(f"Prediction: {pred[0]}")

# ─── SIDEBAR ─────────────────────────
def show_sidebar():
    with st.sidebar:
        st.title("Navigation")

        if st.button("Dashboard"):
            st.session_state.page = "dashboard"
        if st.button("Predict"):
            st.session_state.page = "predict"

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()

# ─── ROUTER ──────────────────────────
if not st.session_state.logged_in:
    if st.session_state.page == "signup":
        show_signup()
    else:
        show_login()
else:
    show_sidebar()

    if st.session_state.page == "dashboard":
        show_dashboard()
    elif st.session_state.page == "predict":
        show_predictor()
    else:
        show_dashboard()
    else:
        show_dashboard()
