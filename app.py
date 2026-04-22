import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import hashlib
import os

# ================= CONFIG =================
st.set_page_config(page_title="TelePredict AI", layout="wide")

MODEL_PATH = "churn_model.pkl"
COLUMNS_PATH = "model_columns.pkl"
USER_FILE = "users.csv"
HISTORY_FILE = "history.csv"

# ================= LOAD MODEL =================
@st.cache_resource
def load_model():
    clf = joblib.load(MODEL_PATH)
    cols = joblib.load(COLUMNS_PATH)
    return clf, cols

clf, MODEL_COLS = load_model()

# ================= HASH =================
def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ================= USER SYSTEM =================
def load_users():
    if not os.path.exists(USER_FILE):
        return pd.DataFrame(columns=["email","password","name"])
    return pd.read_csv(USER_FILE)

def save_user(email, password, name):
    df = load_users()
    if email in df["email"].values:
        return False
    new = pd.DataFrame([[email, hash_pw(password), name]],
                       columns=["email","password","name"])
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(USER_FILE, index=False)
    return True

def verify(email, password):
    df = load_users()
    user = df[df["email"] == email]
    if len(user) == 0:
        return False
    return user.iloc[0]["password"] == hash_pw(password)

# ================= HISTORY =================
def save_history(email, data, prediction, prob):
    row = data.copy()
    row["email"] = email
    row["prediction"] = prediction
    row["probability"] = prob

    df = pd.DataFrame([row])

    if os.path.exists(HISTORY_FILE):
        old = pd.read_csv(HISTORY_FILE)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(HISTORY_FILE, index=False)

# ================= SESSION =================
for k,v in [("logged_in",False),("page","login"),("user_email","")]:
    if k not in st.session_state:
        st.session_state[k]=v

# ================= UI STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#020b18,#001f3f);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
def show_login():
    st.title("🔐 TelePredict Login")

    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify(email,pw):
            st.session_state.logged_in=True
            st.session_state.user_email=email
            st.session_state.page="dashboard"
            st.rerun()
        else:
            st.error("Invalid login")

    if st.button("Signup"):
        st.session_state.page="signup"
        st.rerun()

# ================= SIGNUP =================
def show_signup():
    st.title("📝 Create Account")

    name = st.text_input("Name")
    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")

    if st.button("Create"):
        if save_user(email,pw,name):
            st.success("Account created")
        else:
            st.error("User exists")

    if st.button("Back"):
        st.session_state.page="login"
        st.rerun()

# ================= DASHBOARD =================
def show_dashboard():
    st.title("📊 Dashboard")
    st.write("Welcome:", st.session_state.user_email)

# ================= PREDICT =================
def show_predict():
    st.title("🔮 Churn Predictor")

    vals = [0]*len(MODEL_COLS)
    df = pd.DataFrame([vals], columns=MODEL_COLS)

    if st.button("Predict"):
        pred = clf.predict(df)[0]
        prob = clf.predict_proba(df)[0][1]

        st.success(f"Prediction: {pred}")
        st.write(f"Probability: {prob:.2f}")

        save_history(st.session_state.user_email, df.iloc[0].to_dict(), pred, prob)

        st.download_button("Download",
            pd.DataFrame({"Prediction":[pred],"Prob":[prob]}).to_csv(index=False))

# ================= HISTORY =================
def show_history():
    st.title("📜 History")

    if not os.path.exists(HISTORY_FILE):
        st.info("No history")
        return

    df = pd.read_csv(HISTORY_FILE)
    df = df[df["email"]==st.session_state.user_email]

    st.dataframe(df)

    st.download_button("Download", df.to_csv(index=False))

# ================= BULK =================
def show_bulk():
    st.title("📂 Bulk Prediction")

    file = st.file_uploader("Upload CSV")

    if file:
        df = pd.read_csv(file)

        df["Prediction"] = clf.predict(df)
        df["Prob"] = clf.predict_proba(df)[:,1]

        st.dataframe(df)

        st.download_button("Download", df.to_csv(index=False))

# ================= SIDEBAR =================
def sidebar():
    with st.sidebar:
        st.write("👤", st.session_state.user_email)

        if st.button("Dashboard"): st.session_state.page="dashboard"
        if st.button("Predict"): st.session_state.page="predict"
        if st.button("History"): st.session_state.page="history"
        if st.button("Bulk"): st.session_state.page="bulk"

        if st.button("Logout"):
            st.session_state.logged_in=False
            st.session_state.page="login"

# ================= ROUTER =================
if not st.session_state.logged_in:
    if st.session_state.page=="signup":
        show_signup()
    else:
        show_login()
else:
    sidebar()
    if st.session_state.page=="dashboard": show_dashboard()
    elif st.session_state.page=="predict": show_predict()
    elif st.session_state.page=="history": show_history()
    elif st.session_state.page=="bulk": show_bulk()n_state.page=="history": show_history()
    elif st.session_state.page=="bulk": show_bulk()== "about":     show_about()
    else:                  show_dashboard()
