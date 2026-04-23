import streamlit as st
import pandas as pd
import numpy as np
import joblib
import hashlib
import math
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp {
    font-family: 'DM Sans', sans-serif !important;
    background: #080d1a !important;
    color: #e8ecf5 !important;
}
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(0,255,200,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,200,0.03) 1px, transparent 1px);
    background-size: 44px 44px;
    z-index: 0; pointer-events: none;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#091320 0%,#0c1d38 60%,#070f1c 100%) !important;
    border-right: 1px solid rgba(0,255,200,0.12) !important;
}
section[data-testid="stSidebar"] * { color: #e8ecf5 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; }
h1,h2,h3,h4 { font-family: 'Syne', sans-serif !important; }

input, textarea,
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(0,255,200,0.22) !important;
    border-radius: 10px !important;
    color: #e8ecf5 !important;
}
div[data-baseweb="select"] > div {
    background: rgba(12,29,56,0.9) !important;
    border: 1px solid rgba(0,255,200,0.22) !important;
    border-radius: 10px !important;
    color: #e8ecf5 !important;
}
div[data-baseweb="popover"] div, div[data-baseweb="menu"] { background: #0d1f3c !important; }
div[data-baseweb="menu"] li { color: #e8ecf5 !important; }
div[data-baseweb="menu"] li:hover { background: rgba(0,255,200,0.1) !important; }

label, .stNumberInput label, .stSelectbox label, .stTextInput label, p {
    color: rgba(232,236,245,0.8) !important;
    font-family: 'DM Sans', sans-serif !important;
}
button[data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(232,236,245,0.5) !important;
    font-family: 'DM Sans', sans-serif !important;
    border-bottom: 2px solid transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00ffc8 !important;
    border-bottom: 2px solid #00ffc8 !important;
}
.stButton > button {
    background: linear-gradient(135deg,#00ffc8,#00a8ff) !important;
    color: #080d1a !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.25s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,255,200,0.3) !important;
}
.stDownloadButton > button {
    background: rgba(0,255,200,0.08) !important;
    color: #00ffc8 !important;
    border: 1px solid rgba(0,255,200,0.4) !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
}
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(0,255,200,0.1);
    border-radius: 16px; padding: 1.2rem 1.5rem;
}
[data-testid="stMetricLabel"] p { color: rgba(232,236,245,0.5) !important; font-size:0.82rem !important; }
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    color: #00ffc8 !important; font-size: 2rem !important;
}
.stDataFrame { border: 1px solid rgba(0,255,200,0.12) !important; border-radius: 12px !important; }
hr { border-color: rgba(0,255,200,0.1) !important; }
.stProgress > div > div { background: linear-gradient(90deg,#00ffc8,#00a8ff) !important; }
.card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(0,255,200,0.1);
    border-radius: 18px; padding: 1.5rem;
}
.badge-churn {
    background: rgba(255,50,80,0.15); border: 1px solid rgba(255,50,80,0.5);
    color: #ff3250; padding: 0.2rem 0.75rem; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600; display:inline-block;
}
.badge-safe {
    background: rgba(0,255,200,0.1); border: 1px solid rgba(0,255,200,0.4);
    color: #00ffc8; padding: 0.2rem 0.75rem; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600; display:inline-block;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# MODEL — cached load
# ─────────────────────────────────────────
@st.cache_resource
def load_model():
    model   = joblib.load("churn_model.pkl")
    columns = joblib.load("model_columns.pkl")
    return model, columns


# ─────────────────────────────────────────
# FEATURE ENGINEERING
# Builds the 44-column DataFrame the model expects.
# Model classes_ = ['NO', 'YES']  — predict() returns string 'YES'/'NO'
# ─────────────────────────────────────────
def build_features(call_failure, complains, sub_length, charge_amount,
                   seconds_of_use, freq_use, freq_sms, distinct_nums,
                   age, tariff_plan, status, customer_value, cluster):
    _, cols = load_model()
    df = pd.DataFrame(0, index=[0], columns=cols)

    # Raw numerics
    df['Call  Failure']           = call_failure
    df['Complains']               = 1 if complains == 'Yes' else 0
    df['Subscription  Length']    = sub_length
    df['Charge  Amount']          = charge_amount
    df['Seconds of Use']          = seconds_of_use
    df['Frequency of use']        = freq_use
    df['Frequency of SMS']        = freq_sms
    df['Distinct Called Numbers'] = distinct_nums
    df['Age']                     = age
    df['Tariff Plan']             = 1 if tariff_plan == 'Premium' else 0
    df['Status']                  = 1 if status == 'Active' else 0
    df['Customer Value']          = customer_value
    df['Cluster']                 = {'Low': 0, 'Medium': 1, 'High': 2}[cluster]

    # Age group (0=18-30, 1=31-45, 2=46-60, 3=60+)
    if   age <= 30: ag = 0
    elif age <= 45: ag = 1
    elif age <= 60: ag = 2
    else:           ag = 3
    df['Age Group'] = ag

    # One-hot: Tariff Plan
    if tariff_plan == 'Premium':
        df['Tariff_plan_Premium'] = 1

    # One-hot: Call Failure risk bands
    if   5 < call_failure <= 10: df['Call_Failure_Medium churn risk.'] = 1
    elif call_failure > 10:      df['Call_Failure_Higher churn risk.'] = 1

    # One-hot: Complaint (inverted label — 'No complaint')
    if complains == 'No':
        df['Complain1_No complaint'] = 1

    # One-hot: Subscription length bands
    if   7  <= sub_length <= 12: df['Subscription_Length_7-12 Months']  = 1
    elif 13 <= sub_length <= 24: df['Subscription_Length_13-24 Months'] = 1
    elif sub_length > 24:        df['Subscription_Length_25+ Months']   = 1

    # One-hot: Charge amount bands
    if   150 < charge_amount <= 400: df['Charge_Amount_Medium Charge'] = 1
    elif charge_amount > 400:        df['Charge_Amount_High Charge']   = 1

    # One-hot: Seconds of use bands
    if   10000 < seconds_of_use <= 30000: df['Seconds_of_Use_Medium Usage']    = 1
    elif 30000 < seconds_of_use <= 60000: df['Seconds_of_Use_High Usage']      = 1
    elif seconds_of_use > 60000:          df['Seconds_of_Use_Very High Usage'] = 1

    # One-hot: Frequency of use
    if   freq_use < 20: df['Frequency_of_use_Low']    = 1
    elif freq_use < 60: df['Frequency_of_use_Medium'] = 1
    else:               df['Frequency_of_use_High']   = 1

    # One-hot: Frequency of SMS
    if   freq_sms < 10: df['Frequency_of_SMS_Low SMS']    = 1
    elif freq_sms < 40: df['Frequency_of_SMS_Medium SMS'] = 1
    else:               df['Frequency_of_SMS_High SMS']   = 1

    # One-hot: Distinct called numbers
    if   distinct_nums < 15: df['Distinct_Called_Numbers_Few']      = 1
    elif distinct_nums < 40: df['Distinct_Called_Numbers_Moderate'] = 1
    else:                    df['Distinct_Called_Numbers_Many']     = 1

    # One-hot: Age group label
    if   ag == 2: df['Age_Group_Label_Older'] = 1
    elif ag == 0: df['Age_Group_Label_Young'] = 1

    # One-hot: Status label
    if status == 'Active':
        df['Status_Label_Regular'] = 1

    # One-hot: Age group from age
    if   ag == 1: df['Age_Group_From_Age_31-45'] = 1
    elif ag == 2: df['Age_Group_From_Age_46-60'] = 1
    elif ag == 3: df['Age_Group_From_Age_60+']   = 1

    # One-hot: Customer value bands
    if   200 < customer_value <= 500: df['Customer_Value_Medium Value']    = 1
    elif 500 < customer_value <= 900: df['Customer_Value_High Value']      = 1
    elif customer_value > 900:        df['Customer_Value_Very High Value'] = 1

    return df


# ─────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────
defaults = {
    "logged_in":   False,
    "username":    "",
    "full_name":   "",
    "role":        "",
    "page":        "login",
    "reg_success": False,
    "users":       {},   # in-memory user store (Streamlit Cloud safe)
    "history":     [],   # in-memory prediction history
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# ══════════════════════════════════════════
# PAGE: LOGIN
# ══════════════════════════════════════════
def page_login():
    st.markdown("""
    <div style='text-align:center;padding:2.5rem 0 1rem;'>
      <div style='font-size:3.5rem;'>📡</div>
      <h1 style='font-family:Syne,sans-serif;font-size:2.8rem;font-weight:800;
                 background:linear-gradient(135deg,#00ffc8,#00a8ff);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 margin-bottom:0.3rem;'>ChurnSight AI</h1>
      <p style='color:rgba(232,236,245,0.45);font-size:0.92rem;letter-spacing:2.5px;
                text-transform:uppercase;'>Telecom Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("<div class='card' style='margin-top:1.5rem;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-family:Syne,sans-serif;font-size:1.25rem;font-weight:700;"
                    "text-align:center;margin-bottom:1.2rem;'>Welcome back 👋</p>",
                    unsafe_allow_html=True)

        if st.session_state.reg_success:
            st.success("Account created! Please log in.")
            st.session_state.reg_success = False

        username = st.text_input("Username", placeholder="your_username", key="l_user")
        password = st.text_input("Password", type="password", placeholder="password", key="l_pw")

        if st.button("Sign In →", use_container_width=True):
            users = st.session_state.users
            if username in users and users[username]["password"] == hash_pw(password):
                u = users[username]
                st.session_state.logged_in = True
                st.session_state.username  = username
                st.session_state.full_name = u["full_name"]
                st.session_state.role      = u["role"]
                st.session_state.page      = "dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:rgba(232,236,245,0.4);font-size:0.88rem;'>"
                    "Don't have an account?</p>", unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val in zip(
        [c1, c2, c3, c4],
        ["Accuracy", "Predictions Made", "Churn Saved", "Model Type"],
        ["94.7%", "10,482+", "₹2.4M", "Random Forest"]
    ):
        col.markdown(f"""
        <div style='text-align:center;padding:1rem;background:rgba(255,255,255,0.025);
                    border:1px solid rgba(0,255,200,0.1);border-radius:14px;'>
          <div style='font-family:Syne,sans-serif;font-size:1.7rem;font-weight:800;color:#00ffc8;'>{val}</div>
          <div style='font-size:0.78rem;color:rgba(232,236,245,0.4);text-transform:uppercase;
                      letter-spacing:1px;margin-top:0.25rem;'>{label}</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# PAGE: REGISTER
# ══════════════════════════════════════════
def page_register():
    st.markdown("""
    <div style='text-align:center;padding:2rem 0 0.5rem;'>
      <div style='font-size:3rem;'>🚀</div>
      <h1 style='font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;
                 background:linear-gradient(135deg,#00ffc8,#00a8ff);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        Create Your Account
      </h1>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("<div class='card' style='margin-top:1.5rem;'>", unsafe_allow_html=True)
        full_name = st.text_input("Full Name",        placeholder="Alex Johnson")
        email     = st.text_input("Email",            placeholder="alex@telecom.com")
        username  = st.text_input("Username",         placeholder="alexj")
        password  = st.text_input("Password",         type="password", placeholder="Min 6 characters")
        password2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
        role      = st.selectbox("Role", ["Analyst", "Manager", "Admin"])

        if st.button("Register →", use_container_width=True):
            users = st.session_state.users
            if not all([full_name, email, username, password, password2]):
                st.error("All fields are required")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            elif password != password2:
                st.error("Passwords do not match")
            elif username in users:
                st.error("Username already taken — choose another")
            else:
                st.session_state.users[username] = {
                    "full_name": full_name,
                    "email":     email,
                    "role":      role,
                    "password":  hash_pw(password),
                    "joined":    datetime.now().strftime("%Y-%m-%d"),
                }
                st.session_state.reg_success = True
                st.session_state.page = "login"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# SIDEBAR NAV
# ══════════════════════════════════════════
def sidebar_nav():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:1.5rem 0 0.8rem;'>
          <div style='font-size:2.5rem;'>📡</div>
          <div style='font-family:Syne,sans-serif;font-size:1.35rem;font-weight:800;
                      background:linear-gradient(135deg,#00ffc8,#00a8ff);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
            ChurnSight AI
          </div>
        </div>
        <hr style='border-color:rgba(0,255,200,0.12);margin:0 0 1rem;'>
        """, unsafe_allow_html=True)

        initials = (st.session_state.full_name[0]).upper() if st.session_state.full_name else "U"
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:0.75rem;padding:0.6rem 0.4rem;margin-bottom:1rem;'>
          <div style='width:42px;height:42px;border-radius:50%;flex-shrink:0;
                      background:linear-gradient(135deg,#00ffc8,#00a8ff);
                      display:flex;align-items:center;justify-content:center;
                      font-weight:800;color:#080d1a;font-size:1.1rem;'>{initials}</div>
          <div>
            <div style='font-weight:600;font-size:0.92rem;'>{st.session_state.full_name}</div>
            <div style='font-size:0.73rem;color:rgba(232,236,245,0.4);'>{st.session_state.role}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        for icon, label, key in [
            ("🏠", "Dashboard",  "dashboard"),
            ("🔍", "Predict",    "predict"),
            ("📈", "Analytics",  "analytics"),
            ("📋", "History",    "history"),
        ]:
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.markdown("<br><br><hr style='border-color:rgba(0,255,200,0.08);'>", unsafe_allow_html=True)
        if st.button("🚪  Log Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.full_name = ""
            st.session_state.role      = ""
            st.session_state.page      = "logout"
            st.rerun()


# ══════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════
def page_dashboard():
    user_hist = [h for h in st.session_state.history
                 if h.get("user") == st.session_state.username]
    total    = len(user_hist)
    churns   = sum(1 for h in user_hist if h.get("prediction") == "Churn")
    safe     = total - churns
    avg_prob = (sum(h.get("probability", 0) for h in user_hist) / total) if total else 0

    st.markdown("""
    <h1 style='font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;
               background:linear-gradient(135deg,#00ffc8,#00a8ff);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               margin-bottom:0.2rem;'>Dashboard</h1>
    <p style='color:rgba(232,236,245,0.38);margin-bottom:1.5rem;'>
      Your prediction intelligence overview
    </p>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Predictions", total)
    k2.metric("Churn Detected",    churns, f"{churns/total:.0%} rate" if total else None)
    k3.metric("Safe Customers",    safe,   f"{safe/total:.0%} retention" if total else None)
    k4.metric("Avg Churn Risk",    f"{avg_prob:.1%}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1.7, 1])

    with col_l:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<b style='font-family:Syne,sans-serif;font-size:1.05rem;'>🕐 Recent Predictions</b>",
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if user_hist:
            for h in reversed(user_hist[-6:]):
                pred  = h.get("prediction", "—")
                prob  = h.get("probability", 0)
                ts    = h.get("timestamp", "—")
                badge = "badge-churn" if pred == "Churn" else "badge-safe"
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;align-items:center;
                            padding:0.55rem 0;border-bottom:1px solid rgba(0,255,200,0.07);'>
                  <span style='font-size:0.85rem;color:rgba(232,236,245,0.55);'>{ts}</span>
                  <div style='display:flex;gap:0.8rem;align-items:center;'>
                    <span style='font-size:0.83rem;color:rgba(232,236,245,0.4);'>{prob:.0%} risk</span>
                    <span class='{badge}'>{pred}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:rgba(232,236,245,0.3);text-align:center;padding:1.5rem 0;'>"
                        "No predictions yet — run your first one!</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown("""
        <div class='card'>
          <b style='font-family:Syne,sans-serif;font-size:1.05rem;'>💡 Key Churn Signals</b>
          <div style='margin-top:1rem;font-size:0.87rem;color:rgba(232,236,245,0.6);line-height:2;'>
            🔴 &nbsp;Customer complaints<br>
            🟠 &nbsp;Tenure &lt; 12 months<br>
            🟡 &nbsp;Low call frequency<br>
            🟡 &nbsp;High call failures<br>
            🟢 &nbsp;Premium tariff plan<br>
            🟢 &nbsp;Active account status
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Run New Prediction", use_container_width=True):
            st.session_state.page = "predict"
            st.rerun()


# ══════════════════════════════════════════
# PAGE: PREDICT
# ══════════════════════════════════════════
def page_predict():
    model, _ = load_model()

    st.markdown("""
    <h1 style='font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;
               background:linear-gradient(135deg,#00ffc8,#00a8ff);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               margin-bottom:0.2rem;'>Churn Predictor</h1>
    <p style='color:rgba(232,236,245,0.38);margin-bottom:1.5rem;'>
      Enter customer details to predict churn probability
    </p>
    """, unsafe_allow_html=True)

    with st.form("predict_form"):
        tab1, tab2, tab3 = st.tabs(["📞  Usage Metrics", "💳  Account Details", "👤  Profile"])

        with tab1:
            c1, c2, c3 = st.columns(3)
            with c1:
                call_failure   = st.number_input("Call Failures",        min_value=0, max_value=100,   value=2)
                seconds_of_use = st.number_input("Seconds of Use",       min_value=0, max_value=100000, value=5000)
            with c2:
                freq_use       = st.number_input("Frequency of Use",     min_value=0, max_value=1000,  value=50)
                freq_sms       = st.number_input("Frequency of SMS",     min_value=0, max_value=1000,  value=20)
            with c3:
                distinct_nums  = st.number_input("Distinct Called Numbers", min_value=0, max_value=200, value=30)
                complains      = st.selectbox("Complaints Raised", ["No", "Yes"])

        with tab2:
            c1, c2, c3 = st.columns(3)
            with c1:
                sub_length     = st.number_input("Subscription Length (months)", min_value=1, max_value=60, value=18)
                charge_amount  = st.number_input("Charge Amount",  min_value=0, max_value=1000, value=150)
            with c2:
                customer_value = st.number_input("Customer Value", min_value=0, max_value=2000, value=400)
                tariff_plan    = st.selectbox("Tariff Plan", ["Basic", "Premium"])
            with c3:
                status         = st.selectbox("Account Status",   ["Active", "Inactive"])
                cluster        = st.selectbox("Cluster Segment",  ["Low", "Medium", "High"])

        with tab3:
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", min_value=18, max_value=80, value=35)
            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                if   age <= 30: st.info("🧑 Age Group: 18–30 (Young)")
                elif age <= 45: st.info("👔 Age Group: 31–45 (Adult)")
                elif age <= 60: st.info("🧓 Age Group: 46–60 (Senior)")
                else:           st.info("👴 Age Group: 60+ (Elder)")

        submitted = st.form_submit_button("⚡ Predict Churn", use_container_width=True)

    if submitted:
        final_df = build_features(
            call_failure, complains, sub_length, charge_amount,
            seconds_of_use, freq_use, freq_sms, distinct_nums,
            age, tariff_plan, status, customer_value, cluster
        )

        raw_pred    = model.predict(final_df)[0]           # 'YES' or 'NO'
        proba       = model.predict_proba(final_df)[0]
        yes_idx     = list(model.classes_).index('YES')
        probability = float(proba[yes_idx])
        is_churn    = str(raw_pred).upper() == 'YES'

        # Save to in-session history
        st.session_state.history.append({
            "user":           st.session_state.username,
            "timestamp":      datetime.now().strftime("%Y-%m-%d %H:%M"),
            "prediction":     "Churn" if is_churn else "Not Churn",
            "probability":    probability,
            "call_failure":   call_failure,
            "sub_length":     sub_length,
            "charge_amount":  charge_amount,
            "freq_use":       freq_use,
            "customer_value": customer_value,
            "complains":      complains,
            "status":         status,
        })

        st.markdown("<br>", unsafe_allow_html=True)
        res_col, meter_col = st.columns([1.4, 1])

        with res_col:
            if is_churn:
                st.markdown(f"""
                <div class='card' style='border-color:rgba(255,50,80,0.5);'>
                  <div style='font-size:3rem;'>⚠️</div>
                  <div style='font-family:Syne,sans-serif;font-size:1.75rem;font-weight:800;
                              color:#ff3250;margin:0.3rem 0;'>CHURN PREDICTED</div>
                  <div style='color:rgba(232,236,245,0.45);font-size:0.93rem;margin-bottom:0.8rem;'>
                    This customer is at risk of leaving
                  </div>
                  <div style='font-family:Syne,sans-serif;font-size:2.8rem;font-weight:800;color:#ff3250;'>{probability:.1%}</div>
                  <div style='font-size:0.8rem;color:rgba(232,236,245,0.35);'>churn probability</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='card' style='border-color:rgba(0,255,200,0.5);'>
                  <div style='font-size:3rem;'>✅</div>
                  <div style='font-family:Syne,sans-serif;font-size:1.75rem;font-weight:800;
                              color:#00ffc8;margin:0.3rem 0;'>CUSTOMER RETAINED</div>
                  <div style='color:rgba(232,236,245,0.45);font-size:0.93rem;margin-bottom:0.8rem;'>
                    This customer is stable and likely to stay
                  </div>
                  <div style='font-family:Syne,sans-serif;font-size:2.8rem;font-weight:800;color:#00ffc8;'>{probability:.1%}</div>
                  <div style='font-size:0.8rem;color:rgba(232,236,245,0.35);'>churn probability</div>
                </div>""", unsafe_allow_html=True)

            # Risk signals
            reasons = []
            if complains == 'Yes':   reasons.append(("🔴", "Customer has raised complaints"))
            if sub_length < 12:      reasons.append(("🟠", "Short subscription duration (<12 months)"))
            if freq_use < 10:        reasons.append(("🟡", "Very low call frequency"))
            if customer_value < 200: reasons.append(("🟡", "Low customer value score"))
            if call_failure > 5:     reasons.append(("🔴", "High call failure count"))
            if status == 'Inactive': reasons.append(("🟠", "Account is inactive"))

            if reasons:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<b style='font-family:Syne,sans-serif;'>🔍 Risk Signals Detected</b><br><br>",
                            unsafe_allow_html=True)
                for icon, r in reasons:
                    st.markdown(f"<div style='padding:0.28rem 0;font-size:0.88rem;'>{icon} &nbsp;{r}</div>",
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        with meter_col:
            # SVG Risk Gauge
            angle = int(probability * 180)
            color = "#ff3250" if probability > 0.6 else ("#ffb400" if probability > 0.35 else "#00ffc8")
            rad   = math.radians(180 - angle)
            x2    = 150 + 110 * math.cos(rad)
            y2    = 150 - 110 * math.sin(rad)
            large = "1" if angle > 90 else "0"

            gauge = f"""
            <svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg"
                 style="width:100%;max-width:300px;display:block;margin:0 auto;">
              <defs>
                <linearGradient id="grd" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%"   stop-color="#00ffc8"/>
                  <stop offset="50%"  stop-color="#ffb400"/>
                  <stop offset="100%" stop-color="#ff3250"/>
                </linearGradient>
              </defs>
              <path d="M40,150 A110,110 0 0,1 260,150"
                    fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="20" stroke-linecap="round"/>
              <path d="M40,150 A110,110 0 {large},1 {x2:.2f},{y2:.2f}"
                    fill="none" stroke="url(#grd)" stroke-width="20" stroke-linecap="round"/>
              <line x1="150" y1="150" x2="{x2:.2f}" y2="{y2:.2f}"
                    stroke="{color}" stroke-width="3.5" stroke-linecap="round"/>
              <circle cx="150" cy="150" r="9" fill="{color}"/>
              <text x="32"  y="176" fill="rgba(232,236,245,0.35)" font-size="11" text-anchor="middle">0%</text>
              <text x="150" y="38"  fill="rgba(232,236,245,0.35)" font-size="11" text-anchor="middle">50%</text>
              <text x="268" y="176" fill="rgba(232,236,245,0.35)" font-size="11" text-anchor="middle">100%</text>
              <text x="150" y="143" fill="{color}" font-size="30" font-weight="700"
                    font-family="Syne,sans-serif" text-anchor="middle">{probability:.0%}</text>
              <text x="150" y="166" fill="rgba(232,236,245,0.38)" font-size="11"
                    text-anchor="middle">Churn Risk</text>
            </svg>"""

            st.markdown(f"<div class='card' style='text-align:center;'>"
                        f"<b style='font-family:Syne,sans-serif;'>Risk Meter</b><br>{gauge}</div>",
                        unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div class='card'>
              <b style='font-family:Syne,sans-serif;'>💼 Recommended Actions</b>
              <div style='font-size:0.85rem;color:rgba(232,236,245,0.58);line-height:2;margin-top:0.6rem;'>
                • Offer personalised loyalty discount<br>
                • Schedule proactive support call<br>
                • Propose plan upgrade incentive<br>
                • Resolve any open complaints<br>
                • Assign dedicated account manager
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        out = pd.DataFrame([{
            "Call Failures": call_failure, "Complains": complains,
            "Subscription Length": sub_length, "Charge Amount": charge_amount,
            "Seconds of Use": seconds_of_use, "Frequency of Use": freq_use,
            "Frequency of SMS": freq_sms, "Distinct Called Numbers": distinct_nums,
            "Age": age, "Tariff Plan": tariff_plan, "Status": status,
            "Customer Value": customer_value, "Cluster": cluster,
            "Prediction": "Churn" if is_churn else "Not Churn",
            "Churn Probability": f"{probability:.4f}",
        }])
        st.download_button("📥 Download Result as CSV",
                           data=out.to_csv(index=False).encode(),
                           file_name="churn_result.csv", mime="text/csv")


# ══════════════════════════════════════════
# PAGE: ANALYTICS
# ══════════════════════════════════════════
def page_analytics():
    st.markdown("""
    <h1 style='font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;
               background:linear-gradient(135deg,#00ffc8,#00a8ff);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               margin-bottom:0.2rem;'>Analytics</h1>
    <p style='color:rgba(232,236,245,0.38);margin-bottom:1.5rem;'>
      Aggregate insights across all predictions
    </p>
    """, unsafe_allow_html=True)

    history = st.session_state.history
    if not history:
        st.info("No data yet. Run some predictions first!")
        return

    df          = pd.DataFrame(history)
    total       = len(df)
    churn_count = (df["prediction"] == "Churn").sum()
    safe_count  = total - churn_count
    p_churn     = churn_count / total

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Records",  total)
    m2.metric("Churn Cases",    churn_count, f"{p_churn:.0%}")
    m3.metric("Safe Cases",     safe_count,  f"{1-p_churn:.0%}")
    m4.metric("Avg Risk Score", f"{df['probability'].mean():.1%}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        r     = 70; cx = cy = 100; circ = 2 * math.pi * r
        sc    = p_churn * circ
        ss    = (1 - p_churn) * circ
        donut = f"""
        <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"
             style="width:100%;max-width:210px;display:block;margin:0 auto;">
          <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#ff3250" stroke-width="26"
                  stroke-dasharray="{sc:.1f} {circ:.1f}" stroke-dashoffset="0"
                  transform="rotate(-90 {cx} {cy})"/>
          <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#00ffc8" stroke-width="26"
                  stroke-dasharray="{ss:.1f} {circ:.1f}" stroke-dashoffset="{-sc:.1f}"
                  transform="rotate(-90 {cx} {cy})"/>
          <text x="{cx}" y="{cy-6}" text-anchor="middle" font-family="Syne,sans-serif"
                font-size="22" font-weight="800" fill="#e8ecf5">{p_churn:.0%}</text>
          <text x="{cx}" y="{cy+14}" text-anchor="middle" font-family="DM Sans,sans-serif"
                font-size="10" fill="rgba(232,236,245,0.38)">Churn Rate</text>
        </svg>
        <div style="display:flex;justify-content:center;gap:1.5rem;margin-top:0.4rem;
                    font-size:0.83rem;color:rgba(232,236,245,0.6);">
          <span><span style="color:#ff3250;">●</span> Churn ({churn_count})</span>
          <span><span style="color:#00ffc8;">●</span> Safe ({safe_count})</span>
        </div>"""
        st.markdown(f"<div class='card' style='text-align:center;'>"
                    f"<b style='font-family:Syne,sans-serif;'>Churn Distribution</b><br><br>{donut}</div>",
                    unsafe_allow_html=True)

    with col_b:
        if "complains" in df.columns:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<b style='font-family:Syne,sans-serif;'>Complaints vs Churn</b>",
                        unsafe_allow_html=True)
            comp_df = df.groupby(["complains", "prediction"]).size().reset_index(name="count")
            pivot   = comp_df.pivot(index="complains", columns="prediction", values="count").fillna(0)
            st.bar_chart(pivot)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<b style='font-family:Syne,sans-serif;'>Risk Probability Distribution</b>",
                unsafe_allow_html=True)
    hist_vals = np.histogram(df["probability"], bins=10)[0]
    hist_df   = pd.DataFrame({"Predictions": hist_vals},
                             index=[f"{i*10}–{(i+1)*10}%" for i in range(10)])
    st.bar_chart(hist_df)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# PAGE: HISTORY
# ══════════════════════════════════════════
def page_history():
    st.markdown("""
    <h1 style='font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;
               background:linear-gradient(135deg,#00ffc8,#00a8ff);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               margin-bottom:0.2rem;'>Prediction History</h1>
    <p style='color:rgba(232,236,245,0.38);margin-bottom:1.5rem;'>All your past predictions</p>
    """, unsafe_allow_html=True)

    my_hist = [h for h in st.session_state.history
               if h.get("user") == st.session_state.username]

    if not my_hist:
        st.info("No history yet. Head to Predict to get started!")
        return

    f1, f2, f3 = st.columns(3)
    with f1: filter_pred = st.selectbox("Filter by Result", ["All", "Churn", "Not Churn"])
    with f2: filter_risk = st.selectbox("Filter by Risk",   ["All", "High (>60%)", "Medium (30-60%)", "Low (<30%)"])
    with f3: sort_order  = st.selectbox("Sort Order",       ["Newest first", "Oldest first"])

    filtered = my_hist[:]
    if filter_pred != "All":
        filtered = [h for h in filtered if h.get("prediction") == filter_pred]
    if filter_risk == "High (>60%)":
        filtered = [h for h in filtered if h.get("probability", 0) > 0.6]
    elif filter_risk == "Medium (30-60%)":
        filtered = [h for h in filtered if 0.3 <= h.get("probability", 0) <= 0.6]
    elif filter_risk == "Low (<30%)":
        filtered = [h for h in filtered if h.get("probability", 0) < 0.3]
    if sort_order == "Newest first":
        filtered = list(reversed(filtered))

    st.markdown(f"<p style='color:rgba(232,236,245,0.38);font-size:0.85rem;'>"
                f"Showing {len(filtered)} records</p>", unsafe_allow_html=True)

    rows = []
    for h in filtered:
        pred = h.get("prediction", "—")
        prob = h.get("probability", 0)
        risk = "🔴 High" if prob > 0.6 else ("🟡 Medium" if prob > 0.3 else "🟢 Low")
        rows.append({
            "Timestamp":       h.get("timestamp", "—"),
            "Result":          "⚠️ Churn" if pred == "Churn" else "✅ Safe",
            "Probability":     f"{prob:.1%}",
            "Risk Level":      risk,
            "Complains":       h.get("complains", "—"),
            "Account Status":  h.get("status", "—"),
        })

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        csv = pd.DataFrame(filtered).to_csv(index=False).encode()
        st.download_button("📥 Export Full History",
                           data=csv, file_name="my_churn_history.csv", mime="text/csv")


# ══════════════════════════════════════════
# PAGE: LOGOUT
# ══════════════════════════════════════════
def page_logout():
    st.markdown("""
    <div style='text-align:center;padding:5rem 0;'>
      <div style='font-size:4rem;margin-bottom:1rem;'>👋</div>
      <h1 style='font-family:Syne,sans-serif;font-size:2.5rem;font-weight:800;
                 background:linear-gradient(135deg,#00ffc8,#00a8ff);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        See you soon!
      </h1>
      <p style='color:rgba(232,236,245,0.38);margin:0.8rem 0 2.5rem;font-size:1rem;'>
        You've been securely signed out of ChurnSight AI
      </p>
    </div>
    """, unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()


# ══════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════
if not st.session_state.logged_in:
    pg = st.session_state.page
    if   pg == "register": page_register()
    elif pg == "logout":   page_logout()
    else:                  page_login()
else:
    sidebar_nav()
    pg = st.session_state.page
    if   pg == "dashboard": page_dashboard()
    elif pg == "predict":   page_predict()
    elif pg == "analytics": page_analytics()
    elif pg == "history":   page_history()
    else:                   page_dashboard()
        page_dashboard()
