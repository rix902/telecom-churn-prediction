import streamlit as st
import pandas as pd
import numpy as np
import os
import hashlib
from sklearn.ensemble import RandomForestClassifier

# ───────── CONFIG ─────────
st.set_page_config(page_title="TelePredict AI", layout="wide")

USER_FILE = "users.csv"
PRED_FILE = "predictions.csv"

# ───────── SECURITY ─────────
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ───────── USER SYSTEM ─────────
def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    return pd.DataFrame(columns=["email", "password", "name"])

def save_user(email, password, name):
    df = load_users()
    if email in df["email"].values:
        return False

    new_user = pd.DataFrame([[email, hash_password(password), name]],
                            columns=["email", "password", "name"])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_FILE, index=False)
    return True

def verify(email, pw):
    df = load_users()
    user = df[df["email"] == email]
    if not user.empty:
        return user.iloc[0]["password"] == hash_password(pw)
    return False

# ───────── PREDICTION SAVE ─────────
def save_prediction(email, result):
    if os.path.exists(PRED_FILE):
        df = pd.read_csv(PRED_FILE)
    else:
        df = pd.DataFrame(columns=["email", "result"])

    new_row = pd.DataFrame([[email, result]], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(PRED_FILE, index=False)

# ───────── MODEL ─────────
@st.cache_resource
def train_model():
    X = np.random.rand(200, 3)
    y = np.random.randint(0, 2, 200)
    model = RandomForestClassifier()
    model.fit(X, y)
    return model

# ───────── SESSION ─────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"

# ───────── LOGIN ─────────
def show_login():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify(email, password):
            df = load_users()
            user = df[df["email"] == email].iloc[0]

            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.session_state.user_name = user["name"]
            st.session_state.page = "dashboard"

            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Create Account"):
        st.session_state.page = "signup"
        st.rerun()

# ───────── SIGNUP ─────────
def show_signup():
    st.title("🆕 Signup")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if name and email and password:
            if save_user(email, password, name):
                st.success("Account created! Go to login")
            else:
                st.error("User already exists")
        else:
            st.error("Fill all fields")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# ───────── DASHBOARD ─────────
def show_dashboard():
    st.title(f"📊 Welcome {st.session_state.user_name}")
    st.write("TelePredict AI Dashboard")

# ───────── PREDICTOR ─────────
def show_predictor():
    st.title("🔮 Churn Predictor")

    model = train_model()

    x1 = st.slider("Feature 1", 0.0, 1.0)
    x2 = st.slider("Feature 2", 0.0, 1.0)
    x3 = st.slider("Feature 3", 0.0, 1.0)

    if st.button("Predict"):
        pred = model.predict([[x1, x2, x3]])[0]

        save_prediction(st.session_state.user_email, pred)

        st.success(f"Prediction: {pred}")

# ───────── HISTORY ─────────
def show_history():
    st.title("📁 Prediction History")

    if os.path.exists(PRED_FILE):
        df = pd.read_csv(PRED_FILE)
        user_df = df[df["email"] == st.session_state.user_email]

        st.dataframe(user_df)

        csv = user_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "history.csv")
    else:
        st.info("No data available")

# ───────── SIDEBAR ─────────
def show_sidebar():
    with st.sidebar:
        st.title("Navigation")

        if st.button("Dashboard"):
            st.session_state.page = "dashboard"
        if st.button("Predict"):
            st.session_state.page = "predict"
        if st.button("History"):
            st.session_state.page = "history"

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()

# ───────── ROUTER ─────────
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
    elif st.session_state.page == "history":
        show_history()
    else:
        show_dashboard()
