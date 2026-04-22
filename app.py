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
if "page" not in st.session_state:
    st.session_state.page = "login"

# ─── MODEL ───────────────────────────
@st.cache_resource
def train_model():
    X = np.random.rand(100, 3)
    y = np.random.randint(0, 2, 100)
    model = RandomForestClassifier()
    model.fit(X, y)
    return model

# ─── PAGES ───────────────────────────

def show_login():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify(email, password):
            st.session_state.logged_in = True
            st.session_state.page = "dashboard"
            st.success("Login Success")
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Create Account"):
        st.session_state.page = "signup"
        st.rerun()


def show_signup():
    st.title("🆕 Signup")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if email in USERS:
            st.error("User already exists")
        else:
            save_user(email, password, name)
            st.success("Account created! Go to login")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


def show_dashboard():
    st.title("📊 Dashboard")
    st.write("Welcome to TelePredict AI")


def show_predictor():
    st.title("🔮 Predictor")
    model = train_model()

    x1 = st.slider("Feature 1", 0.0, 1.0)
    x2 = st.slider("Feature 2", 0.0, 1.0)
    x3 = st.slider("Feature 3", 0.0, 1.0)

    if st.button("Predict"):
        pred = model.predict([[x1, x2, x3]])
        st.success(f"Prediction: {pred[0]}")


# ─── ROUTER (IMPORTANT) ──────────────

if not st.session_state.logged_in:
    if st.session_state.page == "signup":
        show_signup()
    else:
        show_login()
else:
    page = st.session_state.page

    if page == "dashboard":
        show_dashboard()
    elif page == "predict":
        show_predictor()
    else:
        show_dashboard()
