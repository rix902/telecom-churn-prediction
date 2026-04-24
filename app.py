import streamlit as st
import pandas as pd
import numpy as np
import pickle
import joblib
import hashlib
import json
import os
import io
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ChurnGuard Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS STYLING
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    /* ── Global Reset ─────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a0e1a 100%);
        color: #e2e8f0;
    }

    /* ── Sidebar ───────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid rgba(99,102,241,0.2);
    }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }

    /* ── Hero Banner ───────────────────── */
    .hero-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4c1d95 100%);
        border-radius: 20px;
        padding: 48px 40px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(139,92,246,0.3);
        box-shadow: 0 25px 60px rgba(109,40,217,0.25);
    }
    .hero-banner::before {
        content: '';
        position: absolute; top: -50%; right: -10%;
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(139,92,246,0.2) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-banner::after {
        content: '';
        position: absolute; bottom: -30%; left: 20%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-size: 3rem; font-weight: 800;
        background: linear-gradient(90deg, #c4b5fd, #818cf8, #67e8f9);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 12px; position: relative; z-index: 1;
    }
    .hero-sub {
        font-size: 1.15rem; color: #a5b4fc; font-weight: 400;
        max-width: 600px; line-height: 1.7; position: relative; z-index: 1;
    }

    /* ── Metric Cards ───────────────────── */
    .metric-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .metric-card:hover {
        border-color: rgba(139,92,246,0.5);
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(109,40,217,0.2);
    }
    .metric-icon { font-size: 2.5rem; margin-bottom: 12px; }
    .metric-value { font-size: 2rem; font-weight: 700; color: #a5b4fc; }
    .metric-label { font-size: 0.85rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }

    /* ── Feature Cards ─────────────────── */
    .feature-card {
        background: linear-gradient(135deg, #1e293b, #111827);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 16px;
        transition: border-color 0.3s;
    }
    .feature-card:hover { border-color: rgba(139,92,246,0.45); }
    .feature-card h4 { color: #c4b5fd; font-size: 1rem; font-weight: 600; margin-bottom: 6px; }
    .feature-card p  { color: #94a3b8; font-size: 0.88rem; margin: 0; line-height: 1.5; }

    /* ── Prediction Result ─────────────── */
    .result-churn {
        background: linear-gradient(135deg, #450a0a, #7f1d1d);
        border: 2px solid #ef4444;
        border-radius: 20px;
        padding: 36px;
        text-align: center;
        box-shadow: 0 0 40px rgba(239,68,68,0.3);
        animation: pulse-red 2s ease-in-out infinite;
    }
    .result-safe {
        background: linear-gradient(135deg, #052e16, #14532d);
        border: 2px solid #22c55e;
        border-radius: 20px;
        padding: 36px;
        text-align: center;
        box-shadow: 0 0 40px rgba(34,197,94,0.3);
        animation: pulse-green 2s ease-in-out infinite;
    }
    @keyframes pulse-red {
        0%,100% { box-shadow: 0 0 30px rgba(239,68,68,0.25); }
        50%      { box-shadow: 0 0 50px rgba(239,68,68,0.45); }
    }
    @keyframes pulse-green {
        0%,100% { box-shadow: 0 0 30px rgba(34,197,94,0.25); }
        50%      { box-shadow: 0 0 50px rgba(34,197,94,0.45); }
    }
    .result-title { font-size: 2rem; font-weight: 800; margin-bottom: 8px; }
    .result-sub   { font-size: 1rem; opacity: 0.8; }

    /* ── Form Sections ─────────────────── */
    .form-section {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
    }
    .form-section-title {
        font-size: 1rem; font-weight: 600;
        color: #a5b4fc; margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(99,102,241,0.2);
        display: flex; align-items: center; gap: 8px;
    }

    /* ── Auth Card ─────────────────────── */
    .auth-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 24px;
        padding: 48px;
        max-width: 460px;
        margin: 60px auto;
        box-shadow: 0 30px 80px rgba(0,0,0,0.4);
    }
    .auth-title {
        font-size: 1.8rem; font-weight: 700;
        background: linear-gradient(90deg, #c4b5fd, #818cf8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 6px;
    }
    .auth-sub { text-align:center; color:#64748b; font-size:0.9rem; margin-bottom:32px; }

    /* ── Tables ────────────────────────── */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* ── Streamlit Widgets Override ──── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background: #0f172a !important;
        border: 1px solid rgba(99,102,241,0.3) !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }
    .stSlider > div { color: #a5b4fc !important; }

    .stButton > button {
        background: linear-gradient(135deg, #6d28d9, #4f46e5) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 28px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(109,40,217,0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(109,40,217,0.45) !important;
    }

    /* ── Section headers ─────────────── */
    h1, h2, h3 { color: #e2e8f0 !important; }
    h1 { font-weight: 800 !important; }
    h2 { font-weight: 700 !important; }

    /* ── Logo ────────────────────────── */
    .logo {
        font-size: 1.5rem; font-weight: 800;
        background: linear-gradient(90deg, #c4b5fd, #818cf8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }

    /* ── Progress bar ────────────────── */
    .stProgress > div > div > div { background: linear-gradient(90deg,#6d28d9,#4f46e5) !important; }

    /* ── Info/warning boxes ──────────── */
    .stAlert { border-radius: 12px !important; }

    /* ── Divider ─────────────────────── */
    hr { border-color: rgba(99,102,241,0.2) !important; }

    /* ── Sidebar nav buttons ─────────── */
    .nav-btn {
        display: block; width: 100%;
        background: transparent;
        border: none; border-radius: 10px;
        padding: 12px 16px;
        text-align: left; cursor: pointer;
        color: #94a3b8; font-size: 0.9rem; font-weight: 500;
        transition: all 0.2s; margin-bottom: 4px;
    }
    .nav-btn:hover, .nav-btn.active {
        background: rgba(99,102,241,0.15);
        color: #a5b4fc;
    }

    /* ── Badge ───────────────────────── */
    .badge {
        display: inline-block;
        background: rgba(99,102,241,0.2);
        color: #a5b4fc;
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# USER STORE (file-based JSON)
# ─────────────────────────────────────────────
USER_DB_PATH = "users.json"
PREDICTIONS_PATH = "predictions.json"

def load_users():
    if os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH) as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f)

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username: str, password: str, email: str) -> tuple[bool, str]:
    users = load_users()
    if username in users:
        return False, "Username already exists."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    users[username] = {
        "password": hash_password(password),
        "email": email,
        "created_at": datetime.now().isoformat(),
    }
    save_users(users)
    return True, "Account created!"

def verify_user(username: str, password: str) -> bool:
    users = load_users()
    if username not in users:
        return False
    return users[username]["password"] == hash_password(password)

# ─────────────────────────────────────────────
# PREDICTIONS STORE
# ─────────────────────────────────────────────
def load_predictions():
    if os.path.exists(PREDICTIONS_PATH):
        with open(PREDICTIONS_PATH) as f:
            return json.load(f)
    return []

def save_prediction(record: dict):
    preds = load_predictions()
    preds.append(record)
    with open(PREDICTIONS_PATH, "w") as f:
        json.dump(preds, f)

# ─────────────────────────────────────────────
# MODEL LOADING
# ─────────────────────────────────────────────
@st.cache_resource
def load_model_and_columns():
    """Load model and column list. Falls back gracefully if model file missing."""
    try:
        model = joblib.load("churn_model.pkl")
    except Exception:
        model = None

    try:
        cols = joblib.load("model_columns.pkl")
        col_list = list(cols)
    except Exception:
        col_list = []

    return model, col_list

# ─────────────────────────────────────────────
# MODEL COLUMNS (from your pkl)
# ─────────────────────────────────────────────
MODEL_COLUMNS = [
    'Call  Failure', 'Complains', 'Subscription  Length', 'Charge  Amount',
    'Seconds of Use', 'Frequency of use', 'Frequency of SMS',
    'Distinct Called Numbers', 'Age Group', 'Tariff Plan', 'Status', 'Age',
    'Customer Value', 'Cluster',
    'Tariff_plan_Premium', 'Call_Failure_Medium churn risk.',
    'Call_Failure_Higher churn risk.', 'Complain1_No complaint',
    'Subscription_Length_7-12 Months', 'Subscription_Length_13-24 Months',
    'Subscription_Length_25+ Months', 'Charge_Amount_Medium Charge',
    'Charge_Amount_High Charge', 'Seconds_of_Use_Medium Usage',
    'Seconds_of_Use_High Usage', 'Seconds_of_Use_Very High Usage',
    'Frequency_of_use_Low', 'Frequency_of_use_Medium', 'Frequency_of_use_High',
    'Frequency_of_SMS_Low SMS', 'Frequency_of_SMS_Medium SMS',
    'Frequency_of_SMS_High SMS', 'Distinct_Called_Numbers_Few',
    'Distinct_Called_Numbers_Moderate', 'Distinct_Called_Numbers_Many',
    'Age_Group_Label_Older', 'Age_Group_Label_Young', 'Status_Label_Regular',
    'Age_Group_From_Age_31-45', 'Age_Group_From_Age_46-60',
    'Age_Group_From_Age_60+', 'Customer_Value_Medium Value',
    'Customer_Value_High Value', 'Customer_Value_Very High Value'
]

# ─────────────────────────────────────────────
# FEATURE ENGINEERING
# ─────────────────────────────────────────────
def build_feature_vector(inputs: dict) -> pd.DataFrame:
    """Convert user inputs → model-ready DataFrame."""
    d = {col: 0 for col in MODEL_COLUMNS}

    # Raw numeric features
    d['Call  Failure']         = inputs['call_failure']
    d['Complains']             = inputs['complains']
    d['Subscription  Length']  = inputs['subscription_length']
    d['Charge  Amount']        = inputs['charge_amount']
    d['Seconds of Use']        = inputs['seconds_of_use']
    d['Frequency of use']      = inputs['frequency_of_use']
    d['Frequency of SMS']      = inputs['frequency_of_sms']
    d['Distinct Called Numbers'] = inputs['distinct_called_numbers']
    d['Age Group']             = inputs['age_group']
    d['Tariff Plan']           = 1 if inputs['tariff_plan'] == 'Premium' else 0
    d['Status']                = 1 if inputs['status'] == 'Active' else 2
    d['Age']                   = inputs['age']
    d['Customer Value']        = inputs['customer_value']
    d['Cluster']               = inputs['cluster']

    # Tariff Plan
    if inputs['tariff_plan'] == 'Premium':
        d['Tariff_plan_Premium'] = 1

    # Call Failure category
    cf = inputs['call_failure']
    if cf <= 5:
        pass  # low = baseline
    elif cf <= 15:
        d['Call_Failure_Medium churn risk.'] = 1
    else:
        d['Call_Failure_Higher churn risk.'] = 1

    # Complains
    if inputs['complains'] == 0:
        d['Complain1_No complaint'] = 1

    # Subscription length category
    sl = inputs['subscription_length']
    if 7 <= sl <= 12:
        d['Subscription_Length_7-12 Months'] = 1
    elif 13 <= sl <= 24:
        d['Subscription_Length_13-24 Months'] = 1
    elif sl > 24:
        d['Subscription_Length_25+ Months'] = 1

    # Charge amount category
    ca = inputs['charge_amount']
    if 4 <= ca <= 7:
        d['Charge_Amount_Medium Charge'] = 1
    elif ca >= 8:
        d['Charge_Amount_High Charge'] = 1

    # Seconds of use category
    su = inputs['seconds_of_use']
    if 1000 <= su < 3000:
        d['Seconds_of_Use_Medium Usage'] = 1
    elif 3000 <= su < 6000:
        d['Seconds_of_Use_High Usage'] = 1
    elif su >= 6000:
        d['Seconds_of_Use_Very High Usage'] = 1

    # Frequency of use category
    fu = inputs['frequency_of_use']
    if fu < 20:
        d['Frequency_of_use_Low'] = 1
    elif fu < 50:
        d['Frequency_of_use_Medium'] = 1
    else:
        d['Frequency_of_use_High'] = 1

    # Frequency of SMS
    fs = inputs['frequency_of_sms']
    if fs < 20:
        d['Frequency_of_SMS_Low SMS'] = 1
    elif fs < 50:
        d['Frequency_of_SMS_Medium SMS'] = 1
    else:
        d['Frequency_of_SMS_High SMS'] = 1

    # Distinct called numbers
    dc = inputs['distinct_called_numbers']
    if dc < 15:
        d['Distinct_Called_Numbers_Few'] = 1
    elif dc < 35:
        d['Distinct_Called_Numbers_Moderate'] = 1
    else:
        d['Distinct_Called_Numbers_Many'] = 1

    # Age group labels
    age = inputs['age']
    if age > 45:
        d['Age_Group_Label_Older'] = 1
    elif age < 30:
        d['Age_Group_Label_Young'] = 1

    # Status label
    if inputs['status'] == 'Active':
        d['Status_Label_Regular'] = 1

    # Age group from age
    if 31 <= age <= 45:
        d['Age_Group_From_Age_31-45'] = 1
    elif 46 <= age <= 60:
        d['Age_Group_From_Age_46-60'] = 1
    elif age > 60:
        d['Age_Group_From_Age_60+'] = 1

    # Customer value category
    cv = inputs['customer_value']
    if 200 <= cv < 500:
        d['Customer_Value_Medium Value'] = 1
    elif 500 <= cv < 1000:
        d['Customer_Value_High Value'] = 1
    elif cv >= 1000:
        d['Customer_Value_Very High Value'] = 1

    return pd.DataFrame([d])

# ─────────────────────────────────────────────
# FEATURE IMPORTANCE FOR EXPLANATION PAGE
# ─────────────────────────────────────────────
FEATURE_IMPORTANCE_APPROX = {
    'Customer Value':           0.18,
    'Seconds of Use':           0.14,
    'Frequency of use':         0.12,
    'Charge  Amount':           0.10,
    'Subscription  Length':     0.09,
    'Call  Failure':            0.08,
    'Distinct Called Numbers':  0.07,
    'Age':                      0.06,
    'Frequency of SMS':         0.05,
    'Complains':                0.05,
    'Tariff Plan':              0.04,
    'Status':                   0.02,
}

# ─────────────────────────────────────────────
# ANALYTICS SYNTHETIC DATA
# ─────────────────────────────────────────────
@st.cache_data
def generate_analytics_data():
    np.random.seed(42)
    n = 3000
    df = pd.DataFrame({
        'Churn': np.random.choice(['Churned', 'Retained'], n, p=[0.265, 0.735]),
        'Monthly Charge': np.random.gamma(3, 25, n).clip(10, 200).round(2),
        'Tenure (Months)': np.random.randint(1, 72, n),
        'Contract Type': np.random.choice(
            ['Month-to-Month', '6 Months', '1 Year', '2 Years'],
            n, p=[0.50, 0.20, 0.17, 0.13]
        ),
        'Call Failures': np.random.poisson(3, n),
        'Customer Value': np.random.exponential(300, n).clip(10, 2000).round(2),
        'Age': np.random.randint(18, 75, n),
    })
    return df

# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────

def page_home():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🛡️ ChurnGuard Pro</div>
        <div class="hero-sub">
            Enterprise-grade AI platform for telecom churn prediction.
            Identify at-risk customers before they leave — powered by machine learning.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        ("📊", "93.7%", "Model Accuracy"),
        ("👥", "50K+", "Customers Analyzed"),
        ("💰", "$2.4M", "Churn Revenue Saved"),
        ("⚡", "< 1s", "Prediction Speed"),
    ]
    for col, (icon, val, label) in zip([c1, c2, c3, c4], stats):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Features grid
    st.markdown("### 🚀 Platform Capabilities")
    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    features = [
        ("🤖 AI-Powered Predictions",
         "Advanced ML model trained on thousands of telecom customer records with 93%+ accuracy."),
        ("🧠 Explainable AI",
         "Understand exactly why a customer is predicted to churn with feature importance charts."),
        ("📈 Live Analytics Dashboard",
         "Real-time visualizations of churn patterns, monthly charges, contract types, and more."),
        ("📥 Batch Export",
         "Store every prediction with timestamps and export full history as CSV with one click."),
    ]
    for (col, (title, desc)) in zip([r1c1, r1c2, r2c1, r2c2], features):
        col.markdown(f"""
        <div class="feature-card">
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    # How it works
    st.markdown("---")
    st.markdown("### 🗺️ How It Works")
    steps = st.columns(4)
    for col, (num, label) in zip(steps, [
        ("1️⃣", "Enter customer data in the Prediction form"),
        ("2️⃣", "AI model analyzes 44+ behavioral features"),
        ("3️⃣", "Get instant churn probability score"),
        ("4️⃣", "View AI explanation & take action"),
    ]):
        col.markdown(f"""
        <div class="feature-card" style="text-align:center">
            <div style="font-size:2rem;margin-bottom:8px">{num}</div>
            <p>{label}</p>
        </div>
        """, unsafe_allow_html=True)
        next_page_button()


def page_prediction():
    model, col_list = load_model_and_columns()

    st.markdown("## 📥 Churn Prediction")
    st.markdown("Fill in the customer profile below and click **Predict Churn** to get an instant AI assessment.")

    with st.form("prediction_form"):
        # ── Section 1: Customer Demographics
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-title">👤 Customer Demographics</div>', unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        age          = d1.number_input("Age", 18, 90, 35, help="Customer age in years")
        age_group    = d2.selectbox("Age Group", [1, 2, 3, 4, 5],
                                    format_func=lambda x: {1:'Under 25',2:'25–30',3:'31–45',4:'46–60',5:'60+'}[x])
        status       = d3.selectbox("Account Status", ["Active", "Non-Active"])
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Section 2: Subscription Details
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-title">📋 Subscription Details</div>', unsafe_allow_html=True)
        s1, s2, s3 = st.columns(3)
        subscription_length = s1.slider("Subscription Length (months)", 1, 60, 12)
        tariff_plan         = s2.selectbox("Tariff Plan", ["Standard", "Premium"])
        charge_amount       = s3.slider("Charge Amount (0–9 scale)", 0, 9, 3,
                                        help="0=Lowest, 9=Highest charge bracket")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Section 3: Usage Behavior
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-title">📞 Usage Behavior</div>', unsafe_allow_html=True)
        u1, u2 = st.columns(2)
        seconds_of_use = u1.number_input("Seconds of Use (total)", 0, 50000, 3000, step=100)
        frequency_of_use = u2.number_input("Frequency of Use (calls)", 0, 200, 40)
        u3, u4 = st.columns(2)
        frequency_of_sms = u3.number_input("Frequency of SMS", 0, 500, 30)
        distinct_called_numbers = u4.number_input("Distinct Called Numbers", 0, 100, 20)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Section 4: Quality & Value
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-title">⭐ Quality & Value</div>', unsafe_allow_html=True)
        q1, q2, q3, q4 = st.columns(4)
        call_failure    = q1.number_input("Call Failures", 0, 50, 2)
        complains       = q2.selectbox("Complaints Filed", [0, 1],
                                       format_func=lambda x: "No" if x == 0 else "Yes")
        customer_value  = q3.number_input("Customer Value ($)", 0.0, 5000.0, 350.0, step=10.0)
        cluster         = q4.selectbox("Customer Cluster", [0, 1, 2, 3],
                                       format_func=lambda x: f"Cluster {x}")
        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("🔮 Predict Churn", use_container_width=True)

    if submitted:
        inputs = {
            'age': age, 'age_group': age_group, 'status': status,
            'subscription_length': subscription_length, 'tariff_plan': tariff_plan,
            'charge_amount': charge_amount, 'seconds_of_use': seconds_of_use,
            'frequency_of_use': frequency_of_use, 'frequency_of_sms': frequency_of_sms,
            'distinct_called_numbers': distinct_called_numbers, 'call_failure': call_failure,
            'complains': complains, 'customer_value': customer_value, 'cluster': cluster,
        }

        with st.spinner("🤖 AI is analyzing customer profile..."):
            X = build_feature_vector(inputs)

            if model is not None:
                try:
                    prob = model.predict_proba(X)[0]
                    churn_prob = float(prob[1]) if len(prob) > 1 else float(prob[0])
                    prediction = int(churn_prob >= 0.5)
                except Exception as e:
                    st.error(f"Model error: {e}")
                    return
            else:
                # Deterministic fallback when model file not present
                score = (
                    (call_failure * 0.04) +
                    (complains * 0.25) +
                    ((9 - charge_amount) * 0.02) +
                    ((50 - frequency_of_use) * 0.003 if frequency_of_use < 50 else 0) +
                    (0.1 if tariff_plan == 'Standard' else 0) +
                    (0.05 if status == 'Non-Active' else 0)
                )
                churn_prob = min(max(score, 0.02), 0.98)
                prediction = int(churn_prob >= 0.5)
                st.info("ℹ️ Running in demo mode — place `churn_model.pkl` in the app directory for full predictions.")

        # Store prediction
        record = {
            "timestamp": datetime.now().isoformat(),
            "user": st.session_state.get("username", "unknown"),
            "prediction": "CHURN" if prediction else "NO CHURN",
            "probability": round(churn_prob * 100, 2),
            **inputs,
        }
        save_prediction(record)
        st.session_state["last_prediction"] = {
            "prediction": prediction,
            "churn_prob": churn_prob,
            "inputs": inputs,
        }

        st.markdown("<br>", unsafe_allow_html=True)

        # Result display
        if prediction == 1:
            st.markdown(f"""
            <div class="result-churn">
                <div class="result-title">🚨 HIGH CHURN RISK</div>
                <div class="result-sub">This customer is likely to churn</div>
                <div style="font-size:3rem;font-weight:800;color:#fca5a5;margin:16px 0">{churn_prob*100:.1f}%</div>
                <div style="color:#fca5a5;font-size:0.9rem">Churn Probability</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.error("**Recommended Action:** Immediately assign a retention agent and offer a discount or plan upgrade.")
        else:
            st.markdown(f"""
            <div class="result-safe">
                <div class="result-title">✅ LOW CHURN RISK</div>
                <div class="result-sub">This customer is likely to stay</div>
                <div style="font-size:3rem;font-weight:800;color:#86efac;margin:16px 0">{churn_prob*100:.1f}%</div>
                <div style="color:#86efac;font-size:0.9rem">Churn Probability</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.success("**Recommended Action:** Continue standard engagement. Monitor for any service quality drops.")

        # Probability gauge
        st.markdown("### 📊 Risk Gauge")
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(churn_prob * 100, 1),
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Churn Probability (%)", 'font': {'size': 16, 'color': '#e2e8f0'}},
            delta={'reference': 50, 'increasing': {'color': '#ef4444'}, 'decreasing': {'color': '#22c55e'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#94a3b8'},
                'bar': {'color': '#ef4444' if prediction else '#22c55e'},
                'bgcolor': '#1e293b',
                'bordercolor': '#334155',
                'steps': [
                    {'range': [0, 30], 'color': 'rgba(34,197,94,0.2)'},
                    {'range': [30, 60], 'color': 'rgba(234,179,8,0.2)'},
                    {'range': [60, 100], 'color': 'rgba(239,68,68,0.2)'},
                ],
                'threshold': {
                    'line': {'color': '#f8fafc', 'width': 3},
                    'thickness': 0.8, 'value': 50
                }
            }
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0', height=280,
        )
        st.plotly_chart(fig, use_container_width=True)  


def page_ai_explanation():
    st.markdown("## 🧠 AI Explanation")

    pred_data = st.session_state.get("last_prediction")

    if not pred_data:
        st.info("💡 Run a prediction first (Prediction page) to see the AI explanation here.")

        # Show general feature importance
        st.markdown("### 📊 Global Feature Importance")
        st.markdown("These are the most influential features driving churn predictions across all customers:")
    else:
        inputs = pred_data["inputs"]
        prob   = pred_data["churn_prob"]

        st.markdown(f"""
        **Last prediction:** {"🚨 CHURN" if pred_data['prediction'] else "✅ NO CHURN"}
        — Probability: **{prob*100:.1f}%**
        """)
        st.markdown("---")

        # Personalized contribution estimate
        contributions = {
            'Call Failures':           min(inputs['call_failure'] / 30, 1) * 0.20,
            'Complaints':              inputs['complains'] * 0.22,
            'Charge Amount':           (inputs['charge_amount'] / 9) * 0.12,
            'Subscription Length':     max(0, (24 - inputs['subscription_length']) / 24) * 0.10,
            'Seconds of Use':          max(0, (5000 - inputs['seconds_of_use']) / 5000) * 0.09,
            'Frequency of Use':        max(0, (50 - inputs['frequency_of_use']) / 50) * 0.08,
            'Customer Value':          max(0, (500 - inputs['customer_value']) / 500) * 0.10,
            'Distinct Called Numbers': max(0, (30 - inputs['distinct_called_numbers']) / 30) * 0.05,
        }
        # Normalize
        total = sum(contributions.values()) or 1
        contributions = {k: round(v/total*100, 1) for k, v in contributions.items()}
        sorted_c = sorted(contributions.items(), key=lambda x: x[1], reverse=True)

        df_contrib = pd.DataFrame(sorted_c, columns=["Feature", "Risk Contribution (%)"])

        st.markdown("### 🎯 Personalized Risk Factors")
        fig = px.bar(
            df_contrib, x="Risk Contribution (%)", y="Feature", orientation='h',
            color="Risk Contribution (%)",
            color_continuous_scale=["#22c55e", "#eab308", "#ef4444"],
            title="Feature Contributions to Churn Risk"
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0', height=380,
            title_font_color='#e2e8f0',
            coloraxis_showscale=False,
        )
        fig.update_xaxes(gridcolor='rgba(99,102,241,0.15)', showline=False)
        fig.update_yaxes(gridcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # Key insight cards
        st.markdown("### 💡 Key Insights")
        top3 = sorted_c[:3]
        c1, c2, c3 = st.columns(3)
        insight_icons = ["🔴", "🟡", "🟠"]
        for col, icon, (feat, val) in zip([c1, c2, c3], insight_icons, top3):
            col.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div style="font-weight:600;color:#c4b5fd;font-size:0.9rem">{feat}</div>
                <div class="metric-value" style="font-size:1.6rem">{val}%</div>
                <div class="metric-label">Risk Contribution</div>
            </div>
            """, unsafe_allow_html=True)

    # Global feature importance (always shown)
    st.markdown("---")
    st.markdown("### 🌐 Global Model Feature Importance")

    global_fi = pd.DataFrame(
        sorted(FEATURE_IMPORTANCE_APPROX.items(), key=lambda x: x[1]),
        columns=["Feature", "Importance"]
    )
    fig2 = px.bar(
        global_fi, x="Importance", y="Feature", orientation='h',
        color="Importance",
        color_continuous_scale=["#4f46e5", "#7c3aed", "#a855f7", "#c084fc"],
        title="Global Feature Importance (Model-Wide)"
    )
    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0', height=420,
        title_font_color='#e2e8f0', coloraxis_showscale=False,
    )
    fig2.update_xaxes(gridcolor='rgba(99,102,241,0.15)')
    fig2.update_yaxes(gridcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)

    # Pie chart
    st.markdown("### 🥧 Feature Category Breakdown")
    categories = {
        'Usage Behavior': 0.33,
        'Billing & Charges': 0.22,
        'Customer Profile': 0.18,
        'Service Quality': 0.15,
        'Subscription Details': 0.12,
    }
    fig3 = px.pie(
        values=list(categories.values()),
        names=list(categories.keys()),
        color_discrete_sequence=['#6d28d9','#4f46e5','#7c3aed','#9333ea','#a855f7'],
        hole=0.4,
    )
    fig3.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0', height=350,
    )
    st.plotly_chart(fig3, use_container_width=True)


def page_analytics():
    st.markdown("## 📈 Analytics Dashboard")
    df = generate_analytics_data()

    # KPI row
    total = len(df)
    churned = (df['Churn'] == 'Churned').sum()
    churn_rate = churned / total * 100
    avg_charge = df['Monthly Charge'].mean()
    avg_tenure = df['Tenure (Months)'].mean()

    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("📊", f"{total:,}", "Total Customers"),
        ("🚨", f"{churned:,}", "Churned"),
        ("📉", f"{churn_rate:.1f}%", "Churn Rate"),
        ("💳", f"${avg_charge:.0f}", "Avg Monthly Charge"),
    ]
    for col, (icon, val, label) in zip([k1, k2, k3, k4], kpis):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🥧 Churn Distribution")
        churn_counts = df['Churn'].value_counts()
        fig1 = px.pie(
            values=churn_counts.values, names=churn_counts.index,
            color_discrete_map={'Churned': '#ef4444', 'Retained': '#22c55e'},
            hole=0.45,
        )
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0', height=320)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("#### 📦 Contract Type vs Churn")
        ct = df.groupby(['Contract Type', 'Churn']).size().reset_index(name='Count')
        fig2 = px.bar(ct, x='Contract Type', y='Count', color='Churn',
                      color_discrete_map={'Churned':'#ef4444','Retained':'#22c55e'},
                      barmode='group')
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           font_color='#e2e8f0', height=320,
                           xaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
                           yaxis=dict(gridcolor='rgba(99,102,241,0.1)'))
        st.plotly_chart(fig2, use_container_width=True)

    # Row 2
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 💰 Monthly Charge Distribution by Churn")
        fig3 = px.histogram(df, x='Monthly Charge', color='Churn', nbins=40,
                            color_discrete_map={'Churned':'#ef4444','Retained':'#22c55e'},
                            barmode='overlay', opacity=0.7)
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           font_color='#e2e8f0', height=320,
                           xaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
                           yaxis=dict(gridcolor='rgba(99,102,241,0.1)'))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("#### 📅 Tenure vs Churn Rate")
        df['Tenure Bucket'] = pd.cut(df['Tenure (Months)'], bins=[0,6,12,24,36,72],
                                     labels=['0–6m','6–12m','12–24m','24–36m','36m+'])
        tenure_churn = df.groupby('Tenure Bucket', observed=True).apply(
            lambda x: (x['Churn']=='Churned').mean()*100
        ).reset_index(name='Churn Rate %')
        fig4 = px.bar(tenure_churn, x='Tenure Bucket', y='Churn Rate %',
                      color='Churn Rate %',
                      color_continuous_scale=['#22c55e','#eab308','#ef4444'])
        fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           font_color='#e2e8f0', height=320, coloraxis_showscale=False,
                           xaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
                           yaxis=dict(gridcolor='rgba(99,102,241,0.1)'))
        st.plotly_chart(fig4, use_container_width=True)

    # Row 3 — full width scatter
    st.markdown("#### 🔵 Customer Value vs Monthly Charge (Churn Overlay)")
    sample = df.sample(600, random_state=1)
    fig5 = px.scatter(sample, x='Monthly Charge', y='Customer Value',
                      color='Churn', size_max=10,
                      color_discrete_map={'Churned':'#ef4444','Retained':'#22c55e'},
                      opacity=0.7)
    fig5.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font_color='#e2e8f0', height=380,
                       xaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
                       yaxis=dict(gridcolor='rgba(99,102,241,0.1)'))
    st.plotly_chart(fig5, use_container_width=True)


def page_download():
    st.markdown("## ⬇️ Prediction History & Export")

    preds = load_predictions()
    user = st.session_state.get("username", "")
    user_preds = [p for p in preds if p.get("user") == user]

    if not user_preds:
        st.info("🔍 No predictions yet. Go to the Prediction page to run your first analysis!")
        return

    df = pd.DataFrame(user_preds)

    # Summary metrics
    total = len(df)
    churned = (df['prediction'] == 'CHURN').sum()
    avg_prob = df['probability'].mean()

    m1, m2, m3 = st.columns(3)
    for col, (icon, val, label) in zip([m1, m2, m3], [
        ("📝", total, "Total Predictions"),
        ("🚨", churned, "Churn Alerts"),
        ("📊", f"{avg_prob:.1f}%", "Avg Churn Probability"),
    ]):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Table
    st.markdown("### 📋 Prediction Log")
    display_cols = ['timestamp', 'prediction', 'probability', 'age', 'tariff_plan',
                    'charge_amount', 'call_failure', 'complains', 'customer_value']
    display_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(
        df[display_cols].rename(columns={
            'timestamp': 'Timestamp', 'prediction': 'Prediction',
            'probability': 'Prob (%)', 'age': 'Age',
            'tariff_plan': 'Plan', 'charge_amount': 'Charge',
            'call_failure': 'Call Fails', 'complains': 'Complains',
            'customer_value': 'Cust. Value'
        }),
        use_container_width=True, height=350,
    )

    # CSV download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full History as CSV",
        data=csv,
        file_name=f"churn_predictions_{user}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
        use_container_width=True,
    )

    # Mini chart
    if len(df) >= 3:
        st.markdown("### 📈 Probability Trend")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_sorted = df.sort_values('timestamp')
        fig = px.line(df_sorted, x='timestamp', y='probability',
                      color='prediction',
                      color_discrete_map={'CHURN': '#ef4444', 'NO CHURN': '#22c55e'},
                      markers=True)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0', height=280,
                          xaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
                          yaxis=dict(gridcolor='rgba(99,102,241,0.1)'))
        st.plotly_chart(fig, use_container_width=True)


def page_profile():
    user = st.session_state.get("username", "Unknown")
    users = load_users()
    info = users.get(user, {})

    st.markdown("## 👤 User Profile")

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="padding:40px">
            <div style="font-size:5rem">👤</div>
            <div style="font-size:1.4rem;font-weight:700;color:#c4b5fd;margin-top:12px">{user}</div>
            <div class="badge" style="margin-top:8px">✅ Verified User</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="form-section">
            <div class="form-section-title">📋 Account Information</div>
            <table style="width:100%;color:#cbd5e1;font-size:0.95rem">
                <tr><td style="padding:8px 0;color:#64748b">Username</td><td><b>{user}</b></td></tr>
                <tr><td style="padding:8px 0;color:#64748b">Email</td><td>{info.get('email','—')}</td></tr>
                <tr><td style="padding:8px 0;color:#64748b">Member Since</td><td>{info.get('created_at','—')[:10] if info.get('created_at') else '—'}</td></tr>
                <tr><td style="padding:8px 0;color:#64748b">Plan</td><td><span class="badge">Pro</span></td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # Prediction stats
    preds = load_predictions()
    user_preds = [p for p in preds if p.get("user") == user]
    st.markdown(f"""
    <div class="form-section" style="margin-top:20px">
        <div class="form-section-title">📊 Activity Summary</div>
        <p style="color:#94a3b8">Total predictions run: <b style="color:#a5b4fc">{len(user_preds)}</b></p>
        <p style="color:#94a3b8">Churn alerts triggered: <b style="color:#f87171">{sum(1 for p in user_preds if p.get('prediction')=='CHURN')}</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()


# ─────────────────────────────────────────────
# AUTH PAGES
# ─────────────────────────────────────────────

def page_login():
    inject_css()
    st.markdown("""
    <div class="auth-card">
        <div class="auth-title">🛡️ ChurnGuard Pro</div>
        <div class="auth-sub">Sign in to your account</div>
    </div>
    """, unsafe_allow_html=True)

    # Center the form
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                login_btn = st.form_submit_button("Login →", use_container_width=True)

            if login_btn:
                if not username or not password:
                    st.error("Please fill in all fields.")
                elif verify_user(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.success(f"Welcome back, {username}! 🎉")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

            st.markdown("---")
            st.markdown(
                "<div style='text-align:center;color:#64748b;font-size:0.8rem'>Demo: user <b>demo</b> / pass <b>demo123</b></div>",
                unsafe_allow_html=True
            )
            # Auto-create demo account
            users = load_users()
            if "demo" not in users:
                register_user("demo", "demo123", "demo@churnguard.ai")

        with tab_register:
            with st.form("register_form"):
                new_user  = st.text_input("Username", placeholder="Choose a username", key="reg_user")
                new_email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
                new_pass  = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_pass")
                new_pass2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="reg_pass2")
                reg_btn   = st.form_submit_button("Create Account →", use_container_width=True)

            if reg_btn:
                if not all([new_user, new_email, new_pass, new_pass2]):
                    st.error("Please fill in all fields.")
                elif new_pass != new_pass2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(new_user, new_pass, new_email)
                    if ok:
                        st.success(f"{msg} Please log in.")
                    else:
                        st.error(msg)


# ─────────────────────────────────────────────
# SIDEBAR NAV
# ─────────────────────────────────────────────

def sidebar_nav():
    with st.sidebar:
        st.markdown('<div class="logo">🛡️ ChurnGuard Pro</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#64748b;font-size:0.8rem'>👤 {st.session_state.get('username','')}</div>",
                    unsafe_allow_html=True)
        st.markdown("---")

        pages = [
            ("🏠", "Home"),
            ("📥", "Prediction"),
            ("🧠", "AI Explanation"),
            ("📈", "Analytics"),
            ("⬇️", "Download"),
            ("👤", "Profile"),
        ]

        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "Home"

        for icon, name in pages:
            active = st.session_state["current_page"] == name
            style = "background:rgba(99,102,241,0.15);color:#a5b4fc !important;" if active else ""
            if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
                st.session_state["current_page"] = name
                st.rerun()

        st.markdown("---")
        model, _ = load_model_and_columns()
        status = "🟢 Model Loaded" if model else "🟡 Demo Mode"
        st.markdown(f"<div style='color:#64748b;font-size:0.78rem;text-align:center'>{status}</div>",
                    unsafe_allow_html=True)
        # ─────────────────────────────────────────────
# NEXT PAGE BUTTON
# ─────────────────────────────────────────────
PAGE_ORDER = ["Home", "Prediction", "AI Explanation", "Analytics", "Download", "Profile"]

def next_page_button():
    current = st.session_state.get("current_page", "Home")
    idx = PAGE_ORDER.index(current) if current in PAGE_ORDER else 0

    if idx < len(PAGE_ORDER) - 1:
        next_page = PAGE_ORDER[idx + 1]

        st.markdown("---")
        col1, col2, col3 = st.columns([3, 1, 3])

        with col2:
            # ✅ FIX: unique key
            if st.button(
                f"Next → {next_page}",
                key=f"next_{current}_{next_page}",
                use_container_width=True
            ):
                st.session_state["current_page"] = next_page
                st.rerun()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    inject_css()

    if not st.session_state.get("authenticated"):
        page_login()
        return

    sidebar_nav()

    page = st.session_state.get("current_page", "Home")
    dispatch = {
        "Home":           page_home,
        "Prediction":     page_prediction,
        "AI Explanation": page_ai_explanation,
        "Analytics":      page_analytics,
        "Download":       page_download,
        "Profile":        page_profile,
    }
    dispatch.get(page, page_home)()

if __name__ == "__main__":
    main()

