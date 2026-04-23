import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import hashlib
import time
from datetime import datetime
import random

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ChurnSight AI",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    font-family: 'DM Sans', sans-serif;
    background: #080d1a !important;
    color: #e8ecf5 !important;
    overflow-x: hidden;
}

/* ── ANIMATED BG GRID ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,255,200,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,200,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
    z-index: 0;
    pointer-events: none;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0d1f3c 50%, #091322 100%) !important;
    border-right: 1px solid rgba(0,255,200,0.15) !important;
}

section[data-testid="stSidebar"] * {
    color: #e8ecf5 !important;
}

/* ── HIDE DEFAULT ELEMENTS ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; }

/* ── HEADINGS ── */
h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
}

/* ── INPUTS ── */
input[type="text"], input[type="password"], input[type="number"], textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(0,255,200,0.25) !important;
    border-radius: 10px !important;
    color: #e8ecf5 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.3s !important;
}

input[type="text"]:focus, input[type="password"]:focus, input[type="number"]:focus {
    border-color: rgba(0,255,200,0.7) !important;
    box-shadow: 0 0 20px rgba(0,255,200,0.1) !important;
}

/* ── SELECTBOX ── */
div[data-baseweb="select"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(0,255,200,0.25) !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] * {
    color: #e8ecf5 !important;
    background: #0d1f3c !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #00ffc8, #00a8ff) !important;
    color: #080d1a !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s !important;
    letter-spacing: 0.5px;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,255,200,0.35) !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(0,255,200,0.12);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    backdrop-filter: blur(10px);
}

[data-testid="stMetricLabel"] { color: rgba(232,236,245,0.6) !important; }
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    color: #00ffc8 !important;
    font-size: 2rem !important;
}

/* ── DATAFRAME ── */
.stDataFrame {
    border: 1px solid rgba(0,255,200,0.15) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* ── DIVIDER ── */
hr { border-color: rgba(0,255,200,0.12) !important; }

/* ── LABELS ── */
label, .stSelectbox label, .stNumberInput label {
    color: rgba(232,236,245,0.8) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #00ffc8, #00a8ff) !important;
}

/* ── ALERTS ── */
.stSuccess { background: rgba(0,255,200,0.08) !important; border-left: 4px solid #00ffc8 !important; }
.stError   { background: rgba(255,50,80,0.08) !important; border-left: 4px solid #ff3250 !important; }
.stWarning { background: rgba(255,180,0,0.08) !important; border-left: 4px solid #ffb400 !important; }
.stInfo    { background: rgba(0,168,255,0.08) !important; border-left: 4px solid #00a8ff !important; }

/* ── SIDEBAR NAV BUTTON STYLE ── */
.nav-btn {
    display: block;
    width: 100%;
    padding: 0.7rem 1.2rem;
    margin: 0.25rem 0;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    color: rgba(232,236,245,0.7);
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s;
}
.nav-btn:hover, .nav-btn.active {
    background: rgba(0,255,200,0.1);
    border-color: rgba(0,255,200,0.3);
    color: #00ffc8;
}

/* ── CARD ── */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(0,255,200,0.12);
    border-radius: 18px;
    padding: 1.5rem;
    backdrop-filter: blur(12px);
}

/* ── GLOW BADGE ── */
.badge-churn {
    background: rgba(255,50,80,0.15);
    border: 1px solid rgba(255,50,80,0.4);
    color: #ff3250;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}
.badge-safe {
    background: rgba(0,255,200,0.1);
    border: 1px solid rgba(0,255,200,0.4);
    color: #00ffc8;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# USER STORE  (file-based persistence)
# ─────────────────────────────────────────
USERS_FILE   = "users.json"
HISTORY_FILE = "history.json"

def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_users():
    return load_json(USERS_FILE, {})

def save_users(u):
    save_json(USERS_FILE, u)

def get_history():
    return load_json(HISTORY_FILE, [])

def save_history(h):
    save_json(HISTORY_FILE, h)

# ─────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────
for k, v in {
    "logged_in": False, "username": "",
    "page": "login", "reg_success": False
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────
# MODEL LOAD
# ─────────────────────────────────────────
@st.cache_resource
def load_model():
    model   = joblib.load("churn_model.pkl")
    columns = joblib.load("model_columns.pkl")
    return model, columns

# ══════════════════════════════════════════
# PAGE 1 — LOGIN
# ══════════════════════════════════════════
def page_login():
    st.markdown("""
    <div style='text-align:center; padding: 2rem 0 1rem;'>
        <div style='font-size:3.5rem; margin-bottom:0.5rem;'>📡</div>
        <h1 style='font-family:Syne,sans-serif; font-size:2.8rem; font-weight:800;
                   background: linear-gradient(135deg,#00ffc8,#00a8ff);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                   margin-bottom:0.3rem;'>ChurnSight AI</h1>
        <p style='color:rgba(232,236,245,0.5); font-size:1rem; letter-spacing:2px;
                  text-transform:uppercase;'>Telecom Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("""
        <div class='card' style='margin-top:1.5rem;'>
        <p style='font-family:Syne,sans-serif; font-size:1.3rem; font-weight:700;
                  color:#e8ecf5; margin-bottom:1.2rem; text-align:center;'>
          Welcome back 👋
        </p>
        """, unsafe_allow_html=True)

        if st.session_state.reg_success:
            st.success("Account created! Please log in.")
            st.session_state.reg_success = False

        username = st.text_input("Username", key="login_user", placeholder="your_username")
        password = st.text_input("Password", type="password", key="login_pw", placeholder="••••••••")

        if st.button("Sign In →", use_container_width=True):
            users = get_users()
            if username in users and users[username]["password"] == hash_pw(password):
                st.session_state.logged_in = True
                st.session_state.username  = username
                st.session_state.page      = "dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:rgba(232,236,245,0.45); font-size:0.88rem;'>Don't have an account?</p>", unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # floating stats
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val in zip(
        [c1,c2,c3,c4],
        ["Models Trained","Predictions Made","Churn Saved","Accuracy"],
        ["3","10,482","₹2.4M","94.7%"]
    ):
        col.markdown(f"""
        <div style='text-align:center; padding:1rem;
                    background:rgba(255,255,255,0.03);
                    border:1px solid rgba(0,255,200,0.1);
                    border-radius:14px;'>
          <div style='font-family:Syne,sans-serif; font-size:1.8rem; font-weight:800;
                      color:#00ffc8;'>{val}</div>
          <div style='font-size:0.8rem; color:rgba(232,236,245,0.45);
                      text-transform:uppercase; letter-spacing:1px;'>{label}</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════
# PAGE 2 — REGISTER
# ══════════════════════════════════════════
def page_register():
    st.markdown("""
    <div style='text-align:center; padding:2rem 0 0.5rem;'>
        <div style='font-size:3rem;'>🚀</div>
        <h1 style='font-family:Syne,sans-serif; font-size:2.2rem; font-weight:800;
                   background:linear-gradient(135deg,#00ffc8,#00a8ff);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
          Create Your Account
        </h1>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("<div class='card' style='margin-top:1.5rem;'>", unsafe_allow_html=True)

        full_name  = st.text_input("Full Name", placeholder="Alex Johnson")
        email      = st.text_input("Email",     placeholder="alex@telecom.com")
        username   = st.text_input("Username",  placeholder="alexj")
        password   = st.text_input("Password",  type="password", placeholder="Min 6 chars")
        password2  = st.text_input("Confirm",   type="password", placeholder="Repeat password")
        role       = st.selectbox("Role", ["Analyst","Manager","Admin"])

        if st.button("Register →", use_container_width=True):
            users = get_users()
            if not all([full_name, email, username, password, password2]):
                st.error("All fields are required")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            elif password != password2:
                st.error("Passwords do not match")
            elif username in users:
                st.error("Username already taken")
            else:
                users[username] = {
                    "full_name": full_name,
                    "email":     email,
                    "role":      role,
                    "password":  hash_pw(password),
                    "joined":    datetime.now().strftime("%Y-%m-%d")
                }
                save_users(users)
                st.session_state.reg_success = True
                st.session_state.page = "login"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# SIDEBAR NAVIGATION (logged-in only)
# ══════════════════════════════════════════
def sidebar_nav():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding:1.5rem 0 1rem;'>
            <div style='font-size:2.5rem;'>📡</div>
            <div style='font-family:Syne,sans-serif; font-size:1.4rem; font-weight:800;
                        background:linear-gradient(135deg,#00ffc8,#00a8ff);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
              ChurnSight AI
            </div>
        </div>
        <hr style='border-color:rgba(0,255,200,0.15); margin:0 0 1rem;'>
        """, unsafe_allow_html=True)

        users    = get_users()
        udata    = users.get(st.session_state.username, {})
        initials = (udata.get("full_name","U")[0]).upper()

        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:0.8rem;
                    padding:0.7rem 0.5rem; margin-bottom:1.2rem;'>
          <div style='width:40px; height:40px; border-radius:50%;
                      background:linear-gradient(135deg,#00ffc8,#00a8ff);
                      display:flex; align-items:center; justify-content:center;
                      font-weight:700; color:#080d1a; font-size:1.1rem;'>{initials}</div>
          <div>
            <div style='font-weight:600; font-size:0.95rem;'>{udata.get("full_name","User")}</div>
            <div style='font-size:0.75rem; color:rgba(232,236,245,0.45);'>{udata.get("role","Analyst")}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        pages = [
            ("🏠", "Dashboard",   "dashboard"),
            ("🔍", "Predict",     "predict"),
            ("📈", "Analytics",   "analytics"),
            ("📋", "History",     "history"),
        ]
        for icon, label, key in pages:
            active = "active" if st.session_state.page == key else ""
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:rgba(0,255,200,0.1);'>", unsafe_allow_html=True)
        if st.button("🚪  Log Out", use_container_width=True):
            st.session_state.page      = "logout"
            st.rerun()


# ══════════════════════════════════════════
# PAGE 3 — DASHBOARD
# ══════════════════════════════════════════
def page_dashboard():
    history = get_history()
    user_history = [h for h in history if h.get("user") == st.session_state.username]

    total    = len(user_history)
    churns   = sum(1 for h in user_history if h.get("prediction") == "Churn")
    safe     = total - churns
    avg_prob = (sum(h.get("probability",0) for h in user_history)/total) if total else 0

    st.markdown("""
    <h1 style='font-family:Syne,sans-serif; font-size:2.2rem; font-weight:800;
               background:linear-gradient(135deg,#00ffc8,#00a8ff);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               margin-bottom:0.2rem;'>Dashboard</h1>
    <p style='color:rgba(232,236,245,0.4); margin-bottom:1.5rem;'>
        Your prediction intelligence overview
    </p>
    """, unsafe_allow_html=True)

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    for col, label, val, delta in zip(
        [k1,k2,k3,k4],
        ["Total Predictions","Churn Detected","Safe Customers","Avg Churn Prob"],
        [total, churns, safe, f"{avg_prob:.1%}"],
        [None, f"{churns/total:.0%} churn rate" if total else None,
         f"{safe/total:.0%} retention" if total else None, None]
    ):
        col.metric(label, val, delta)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent activity + quick tips
    col_left, col_right = st.columns([1.6, 1])

    with col_left:
        st.markdown("""
        <div class='card'>
          <div style='font-family:Syne,sans-serif; font-size:1.1rem; font-weight:700;
                      margin-bottom:1rem;'>🕐 Recent Predictions</div>
        """, unsafe_allow_html=True)

        if user_history:
            last5 = user_history[-5:][::-1]
            for h in last5:
                pred    = h.get("prediction","—")
                prob    = h.get("probability", 0)
                ts      = h.get("timestamp","—")
                badge   = "badge-churn" if pred == "Churn" else "badge-safe"
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between; align-items:center;
                            padding:0.6rem 0; border-bottom:1px solid rgba(0,255,200,0.08);'>
                  <div>
                    <span style='font-size:0.88rem; color:rgba(232,236,245,0.6);'>{ts}</span>
                  </div>
                  <div style='display:flex; gap:0.8rem; align-items:center;'>
                    <span style='font-size:0.85rem; color:rgba(232,236,245,0.5);'>
                        {prob:.0%} risk</span>
                    <span class='{badge}'>{pred}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:rgba(232,236,245,0.35); text-align:center; padding:1.5rem 0;'>No predictions yet — run your first one!</p>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class='card'>
          <div style='font-family:Syne,sans-serif; font-size:1.1rem; font-weight:700;
                      margin-bottom:1rem;'>💡 Churn Risk Factors</div>
          <div style='font-size:0.88rem; color:rgba(232,236,245,0.6); line-height:1.9;'>
            <div>🔴 &nbsp;<b>Complaints</b> — #1 churn driver</div>
            <div>🟠 &nbsp;<b>Short tenure</b> — &lt; 12 months</div>
            <div>🟡 &nbsp;<b>Low frequency</b> — infrequent calls</div>
            <div>🟡 &nbsp;<b>High failures</b> — call drop rate</div>
            <div>🟢 &nbsp;<b>High value</b> — loyal premium users</div>
            <div>🟢 &nbsp;<b>Active status</b> — engaged subscribers</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Run New Prediction", use_container_width=True):
            st.session_state.page = "predict"
            st.rerun()


# ══════════════════════════════════════════
# PAGE 4 — PREDICT
# ══════════════════════════════════════════
def page_predict():
    model, model_columns = load_model()

    st.markdown("""
    <h1 style='font-family:Syne,sans-serif; font-size:2.2rem; font-weight:800;
               background:linear-gradient(135deg,#00ffc8,#00a8ff);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               margin-bottom:0.2rem;'>Churn Predictor</h1>
    <p style='color:rgba(232,236,245,0.4); margin-bottom:1.5rem;'>
        Enter customer data to predict churn probability
    </p>
    """, unsafe_allow_html=True)

    with st.form("predict_form"):
        tab1, tab2, tab3 = st.tabs(["📞 Usage", "💳 Account", "👤 Profile"])

        with tab1:
            c1, c2, c3 = st.columns(3)
            with c1:
                call_failure       = st.number_input("Call Failures", 0, 100, 2)
                seconds_of_use     = st.number_input("Seconds of Use", 0, 100000, 5000)
            with c2:
                frequency_of_use   = st.number_input("Frequency of Use", 0, 1000, 50)
                frequency_sms      = st.number_input("Frequency of SMS", 0, 1000, 20)
            with c3:
                distinct_numbers   = st.number_input("Distinct Called Numbers", 0, 200, 30)
                complains          = st.selectbox("Complaints Raised", ["No","Yes"])

        with tab2:
            c1, c2, c3 = st.columns(3)
            with c1:
                subscription_length = st.number_input("Subscription Length (mo)", 1, 60, 18)
                charge_amount        = st.number_input("Charge Amount", 0, 1000, 150)
            with c2:
                customer_value = st.number_input("Customer Value", 0, 2000, 400)
                tariff_plan    = st.selectbox("Tariff Plan", ["Basic","Premium"])
            with c3:
                status  = st.selectbox("Status", ["Active","Inactive"])
                cluster = st.selectbox("Cluster", ["Low","Medium","High"])

        with tab3:
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", 18, 80, 35)
            with c2:
                age_group = st.selectbox("Age Group", ["18-30","31-45","46-60","60+"])

        submitted = st.form_submit_button("⚡ Predict Churn", use_container_width=True)

    if submitted:
        # ── encode ──
        complains_val  = 1 if complains  == "Yes"     else 0
        tariff_val     = 1 if tariff_plan== "Premium"  else 0
        status_val     = 1 if status     == "Active"   else 0
        cluster_map    = {"Low":0,"Medium":1,"High":2}
        cluster_val    = cluster_map[cluster]
        ag_map         = {"18-30":0,"31-45":1,"46-60":2,"60+":3}
        age_group_val  = ag_map[age_group]

        raw = {
            'Call  Failure':           call_failure,
            'Complains':               complains_val,
            'Subscription  Length':    subscription_length,
            'Charge  Amount':          charge_amount,
            'Seconds of Use':          seconds_of_use,
            'Frequency of use':        frequency_of_use,
            'Frequency of SMS':        frequency_sms,
            'Distinct Called Numbers': distinct_numbers,
            'Age':                     age,
            'Age Group':               age_group_val,
            'Tariff Plan':             tariff_val,
            'Status':                  status_val,
            'Customer Value':          customer_value,
            'Cluster':                 cluster_val,
        }
        input_df  = pd.DataFrame([raw])
        final_df  = pd.DataFrame(0, index=[0], columns=model_columns)
        for col in input_df.columns:
            if col in final_df.columns:
                final_df[col] = input_df[col].values[0]

        prediction  = model.predict(final_df)[0]
        probability = model.predict_proba(final_df)[0][1]

        # ── save history ──
        history = get_history()
        history.append({
            "user":        st.session_state.username,
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M"),
            "prediction":  "Churn" if prediction == 1 else "Not Churn",
            "probability": float(probability),
            "inputs":      raw
        })
        save_history(history)

        # ── result UI ──
        st.markdown("<br>", unsafe_allow_html=True)
        res_col, meter_col = st.columns([1.4, 1])

        with res_col:
            if prediction == 1:
                st.markdown(f"""
                <div class='card' style='border-color:rgba(255,50,80,0.4);'>
                  <div style='font-size:3rem; margin-bottom:0.5rem;'>⚠️</div>
                  <div style='font-family:Syne,sans-serif; font-size:1.8rem; font-weight:800;
                              color:#ff3250;'>CHURN PREDICTED</div>
                  <div style='font-size:1rem; color:rgba(232,236,245,0.5); margin:0.5rem 0;'>
                    This customer is likely to leave
                  </div>
                  <div style='font-family:Syne,sans-serif; font-size:2.5rem; font-weight:800;
                              color:#ff3250;'>{probability:.1%}</div>
                  <div style='font-size:0.85rem; color:rgba(232,236,245,0.4);'>churn probability</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='card' style='border-color:rgba(0,255,200,0.4);'>
                  <div style='font-size:3rem; margin-bottom:0.5rem;'>✅</div>
                  <div style='font-family:Syne,sans-serif; font-size:1.8rem; font-weight:800;
                              color:#00ffc8;'>CUSTOMER RETAINED</div>
                  <div style='font-size:1rem; color:rgba(232,236,245,0.5); margin:0.5rem 0;'>
                    Customer appears stable
                  </div>
                  <div style='font-family:Syne,sans-serif; font-size:2.5rem; font-weight:800;
                              color:#00ffc8;'>{probability:.1%}</div>
                  <div style='font-size:0.85rem; color:rgba(232,236,245,0.4);'>churn probability</div>
                </div>
                """, unsafe_allow_html=True)

            # risk factors
            reasons = []
            if complains_val == 1:          reasons.append(("🔴", "Customer has raised complaints"))
            if subscription_length < 12:    reasons.append(("🟠", "Short subscription duration"))
            if frequency_of_use < 10:       reasons.append(("🟡", "Low usage frequency"))
            if customer_value < 200:        reasons.append(("🟡", "Low customer value score"))
            if call_failure > 5:            reasons.append(("🔴", "High call failure rate"))
            if status_val == 0:             reasons.append(("🟠", "Account is inactive"))

            if reasons:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='card'><b style='font-family:Syne,sans-serif;'>🔍 Risk Signals</b><br><br>", unsafe_allow_html=True)
                for icon, reason in reasons:
                    st.markdown(f"<div style='padding:0.3rem 0; font-size:0.9rem;'>{icon} &nbsp;{reason}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        with meter_col:
            # Probability gauge (SVG)
            angle  = int(probability * 180)
            color  = "#ff3250" if probability > 0.6 else ("#ffb400" if probability > 0.35 else "#00ffc8")
            rad    = (180 - angle) * 3.14159 / 180
            x2     = 150 + 110 * (-1 if angle > 90 else 1) * abs(round(__import__('math').cos(rad),3))
            y2     = 150 - 110 * round(__import__('math').sin(rad), 3)

            import math
            rad = math.radians(180 - angle)
            x2  = 150 + 110 * math.cos(rad)
            y2  = 150 - 110 * math.sin(rad)

            gauge_svg = f"""
            <svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:320px;display:block;margin:0 auto;">
              <defs>
                <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#00ffc8"/>
                  <stop offset="50%" style="stop-color:#ffb400"/>
                  <stop offset="100%" style="stop-color:#ff3250"/>
                </linearGradient>
              </defs>
              <!-- track -->
              <path d="M 40 150 A 110 110 0 0 1 260 150"
                    fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="18" stroke-linecap="round"/>
              <!-- fill -->
              <path d="M 40 150 A 110 110 0 {"1" if angle > 90 else "0"} 1 {x2:.1f} {y2:.1f}"
                    fill="none" stroke="url(#g1)" stroke-width="18" stroke-linecap="round"/>
              <!-- needle -->
              <line x1="150" y1="150" x2="{x2:.1f}" y2="{y2:.1f}"
                    stroke="{color}" stroke-width="3" stroke-linecap="round"/>
              <circle cx="150" cy="150" r="8" fill="{color}"/>
              <!-- labels -->
              <text x="35" y="175" fill="rgba(232,236,245,0.4)" font-size="12" text-anchor="middle">0%</text>
              <text x="150" y="40" fill="rgba(232,236,245,0.4)" font-size="12" text-anchor="middle">50%</text>
              <text x="265" y="175" fill="rgba(232,236,245,0.4)" font-size="12" text-anchor="middle">100%</text>
              <!-- center text -->
              <text x="150" y="145" fill="{color}" font-size="28" font-weight="700"
                    font-family="Syne,sans-serif" text-anchor="middle">{probability:.0%}</text>
              <text x="150" y="168" fill="rgba(232,236,245,0.4)" font-size="11"
                    text-anchor="middle">Churn Risk</text>
            </svg>
            """
            st.markdown(f"<div class='card' style='text-align:center;'><b style='font-family:Syne,sans-serif;'>Risk Meter</b><br>{gauge_svg}</div>", unsafe_allow_html=True)

            # recommendations
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div class='card'>
              <b style='font-family:Syne,sans-serif;'>💼 Recommendations</b><br><br>
              <div style='font-size:0.85rem; color:rgba(232,236,245,0.6); line-height:1.9;'>
                • Offer loyalty discount<br>
                • Proactive support call<br>
                • Upgrade plan incentive<br>
                • Resolve open complaints
              </div>
            </div>
            """, unsafe_allow_html=True)

        # download
        st.markdown("<br>", unsafe_allow_html=True)
        result_df = input_df.copy()
        result_df["Prediction"]  = "Churn" if prediction == 1 else "Not Churn"
        result_df["Probability"] = probability
        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Result CSV", data=csv,
                           file_name="churn_result.csv", mime="text/csv")


# ══════════════════════════════════════════
# PAGE 5 — ANALYTICS
# ══════════════════════════════════════════
def page_analytics():
    st.markdown("""
    <h1 style='font-family:Syne,sans-serif; font-size:2.2rem; font-weight:800;
               background:linear-gradient(135deg,#00ffc8,#00a8ff);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               margin-bottom:0.2rem;'>Analytics</h1>
    <p style='color:rgba(232,236,245,0.4); margin-bottom:1.5rem;'>
        Aggregate insights from all predictions
    </p>
    """, unsafe_allow_html=True)

    history = get_history()

    if not history:
        st.info("No prediction data yet. Run some predictions first!")
        return

    df = pd.DataFrame(history)
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date

    churn_count = (df["prediction"] == "Churn").sum()
    safe_count  = (df["prediction"] != "Churn").sum()
    total       = len(df)

    # ── Metric row ──
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Total Records",   total)
    m2.metric("Churn Cases",     churn_count, f"{churn_count/total:.0%}")
    m3.metric("Safe Cases",      safe_count,  f"{safe_count/total:.0%}")
    m4.metric("Avg Risk Score",  f"{df['probability'].mean():.1%}")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Donut chart (SVG)
        p_churn = churn_count / total if total else 0
        p_safe  = 1 - p_churn
        r = 70; cx = cy = 100; circ = 2 * 3.14159 * r
        stroke_churn = p_churn * circ
        stroke_safe  = p_safe  * circ

        donut = f"""
        <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:220px;display:block;margin:0 auto;">
          <circle cx="{cx}" cy="{cy}" r="{r}" fill="none"
                  stroke="#ff3250" stroke-width="28"
                  stroke-dasharray="{stroke_churn:.1f} {circ:.1f}"
                  stroke-dashoffset="0"
                  transform="rotate(-90 {cx} {cy})"/>
          <circle cx="{cx}" cy="{cy}" r="{r}" fill="none"
                  stroke="#00ffc8" stroke-width="28"
                  stroke-dasharray="{stroke_safe:.1f} {circ:.1f}"
                  stroke-dashoffset="{-stroke_churn:.1f}"
                  transform="rotate(-90 {cx} {cy})"/>
          <text x="{cx}" y="{cy-8}" text-anchor="middle"
                font-family="Syne,sans-serif" font-size="22" font-weight="800" fill="#e8ecf5">
            {p_churn:.0%}
          </text>
          <text x="{cx}" y="{cy+12}" text-anchor="middle"
                font-family="DM Sans,sans-serif" font-size="11" fill="rgba(232,236,245,0.45)">
            Churn Rate
          </text>
        </svg>
        <div style="display:flex;justify-content:center;gap:1.5rem;margin-top:0.5rem;font-size:0.85rem;">
          <span><span style="color:#ff3250;">●</span> Churn ({churn_count})</span>
          <span><span style="color:#00ffc8;">●</span> Safe ({safe_count})</span>
        </div>
        """
        st.markdown(f"<div class='card' style='text-align:center;'><b style='font-family:Syne,sans-serif;'>Churn Distribution</b><br><br>{donut}</div>", unsafe_allow_html=True)

    with col_b:
        # Bar chart: predictions per day (last 7 unique dates)
        daily = df.groupby("date")["prediction"].count().reset_index()
        daily.columns = ["date","count"]
        daily = daily.tail(7)

        if not daily.empty:
            max_c = daily["count"].max()
            bars  = ""
            bar_w = 200 // max(len(daily),1)
            for i, row in daily.iterrows():
                h = int((row["count"] / max_c) * 100)
                bars += f"""
                <g>
                  <rect x="{i*35+20}" y="{110-h}" width="25" height="{h}"
                        fill="url(#bg1)" rx="5"/>
                  <text x="{i*35+32}" y="125" text-anchor="middle"
                        font-size="8" fill="rgba(232,236,245,0.4)">
                    {str(row["date"])[-5:]}
                  </text>
                  <text x="{i*35+32}" y="{106-h}" text-anchor="middle"
                        font-size="10" fill="#00ffc8">{row["count"]}</text>
                </g>
                """
            chart = f"""
            <svg viewBox="0 0 300 140" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:300px;display:block;margin:0 auto;">
              <defs>
                <linearGradient id="bg1" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" style="stop-color:#00ffc8"/>
                  <stop offset="100%" style="stop-color:#00a8ff;stop-opacity:0.4"/>
                </linearGradient>
              </defs>
              {bars}
            </svg>
            """
            st.markdown(f"<div class='card' style='text-align:center;'><b style='font-family:Syne,sans-serif;'>Daily Predictions</b><br><br>{chart}</div>", unsafe_allow_html=True)

    # ── risk distribution histogram ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<b style='font-family:Syne,sans-serif;'>Probability Distribution</b>", unsafe_allow_html=True)
    st.bar_chart(df["probability"].value_counts(bins=10, sort=False))
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# PAGE 6 — HISTORY
# ══════════════════════════════════════════
def page_history():
    st.markdown("""
    <h1 style='font-family:Syne,sans-serif; font-size:2.2rem; font-weight:800;
               background:linear-gradient(135deg,#00ffc8,#00a8ff);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               margin-bottom:0.2rem;'>Prediction History</h1>
    <p style='color:rgba(232,236,245,0.4); margin-bottom:1.5rem;'>
        All your past predictions
    </p>
    """, unsafe_allow_html=True)

    history = get_history()
    my_hist = [h for h in history if h.get("user") == st.session_state.username]

    if not my_hist:
        st.info("You have no prediction history yet.")
        return

    # filter controls
    f1, f2, f3 = st.columns(3)
    with f1:
        filter_pred = st.selectbox("Filter by Result", ["All","Churn","Not Churn"])
    with f2:
        filter_risk = st.selectbox("Filter by Risk", ["All","High (>60%)","Medium (30-60%)","Low (<30%)"])
    with f3:
        sort_order = st.selectbox("Sort", ["Newest first","Oldest first"])

    # apply filters
    filtered = my_hist[:]
    if filter_pred != "All":
        filtered = [h for h in filtered if h.get("prediction") == filter_pred]
    if filter_risk == "High (>60%)":
        filtered = [h for h in filtered if h.get("probability",0) > 0.6]
    elif filter_risk == "Medium (30-60%)":
        filtered = [h for h in filtered if 0.3 <= h.get("probability",0) <= 0.6]
    elif filter_risk == "Low (<30%)":
        filtered = [h for h in filtered if h.get("probability",0) < 0.3]

    if sort_order == "Newest first":
        filtered = filtered[::-1]

    st.markdown(f"<p style='color:rgba(232,236,245,0.4); font-size:0.88rem;'>Showing {len(filtered)} records</p>", unsafe_allow_html=True)

    # table
    if filtered:
        rows = []
        for h in filtered:
            pred  = h.get("prediction","—")
            prob  = h.get("probability", 0)
            badge = "🔴 Churn" if pred == "Churn" else "🟢 Safe"
            risk  = "High" if prob > 0.6 else ("Medium" if prob > 0.3 else "Low")
            rows.append({
                "Timestamp":   h.get("timestamp","—"),
                "Result":      badge,
                "Probability": f"{prob:.1%}",
                "Risk Level":  risk,
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # export
        export_df = pd.DataFrame(filtered)
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export All History", data=csv,
                           file_name="my_churn_history.csv", mime="text/csv")


# ══════════════════════════════════════════
# PAGE 7 — LOGOUT
# ══════════════════════════════════════════
def page_logout():
    st.markdown("""
    <div style='text-align:center; padding:4rem 0;'>
      <div style='font-size:4rem; margin-bottom:1rem;'>👋</div>
      <h1 style='font-family:Syne,sans-serif; font-size:2.5rem; font-weight:800;
                 background:linear-gradient(135deg,#00ffc8,#00a8ff);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        See you soon!
      </h1>
      <p style='color:rgba(232,236,245,0.4); margin:0.8rem 0 2rem;'>
        You've been securely logged out of ChurnSight AI
      </p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1,1,1])
    with col_m:
        if st.button("← Back to Login", use_container_width=True):
            for k in ["logged_in","username","page"]:
                st.session_state[k] = {"logged_in": False,"username":"","page":"login"}[k]
            st.rerun()

    # auto-clear session
    st.session_state.logged_in = False
    st.session_state.username  = ""


# ══════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════
if not st.session_state.logged_in:
    if st.session_state.page == "register":
        page_register()
    elif st.session_state.page == "logout":
        page_logout()
    else:
        page_login()
else:
    sidebar_nav()
    page = st.session_state.page
    if   page == "dashboard":  page_dashboard()
    elif page == "predict":    page_predict()
    elif page == "analytics":  page_analytics()
    elif page == "history":    page_history()
    elif page == "logout":
        st.session_state.logged_in = False
        st.session_state.username  = ""
        st.session_state.page      = "logout"
        st.rerun()
    else:
        page_dashboard()
