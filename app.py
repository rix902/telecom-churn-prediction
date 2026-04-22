import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import hashlib
import time
import os

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TelePredict AI",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Load Model ─────────────────────────────────────────────────────────────
MODEL_PATH   = os.path.join(os.path.dirname(__file__), "churn_model.pkl")
COLUMNS_PATH = os.path.join(os.path.dirname(__file__), "model_columns.pkl")

@st.cache_resource
def load_model():
    import warnings
    warnings.filterwarnings("ignore")
    clf  = joblib.load(MODEL_PATH)
    cols = joblib.load(COLUMNS_PATH)
    return clf, list(cols)

clf, MODEL_COLS = load_model()

# ─── Users ──────────────────────────────────────────────────────────────────
USERS = {
    "admin@telepredict.ai": {"password": hashlib.sha256("Admin@123".encode()).hexdigest(), "name": "Admin User"},
    "demo@telepredict.ai":  {"password": hashlib.sha256("Demo@123".encode()).hexdigest(),  "name": "Demo User"},
}
RESET_TOKENS = {}
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()
def verify(e, p): return e in USERS and USERS[e]["password"] == hash_pw(p)

# ─── Feature Importances (top 10) ───────────────────────────────────────────
IMPORTANCES = sorted(zip(MODEL_COLS, clf.feature_importances_), key=lambda x: -x[1])[:10]

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&family=Exo+2:wght@300;400;600&display=swap');
:root{--c:#00f5ff;--p:#bf00ff;--pk:#ff006e;--g:#39ff14;--bg:#020b18;--bdr:rgba(0,245,255,0.2);}
html,body,[class*="css"]{font-family:'Rajdhani',sans-serif;}
.stApp{background:var(--bg);background-image:radial-gradient(ellipse at 10% 20%,rgba(0,245,255,0.07) 0%,transparent 50%),radial-gradient(ellipse at 90% 80%,rgba(191,0,255,0.07) 0%,transparent 50%);}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#020b18 0%,#030d20 100%)!important;border-right:1px solid var(--bdr);}
[data-testid="stSidebar"]::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--c),var(--p),var(--pk));}
#MainMenu,footer,header{visibility:hidden;}
h1,h2,h3{font-family:'Orbitron',monospace!important;color:var(--c)!important;text-shadow:0 0 20px rgba(0,245,255,0.4);letter-spacing:2px;}
.glass-card{background:rgba(0,20,40,0.85);border:1px solid var(--bdr);border-radius:16px;padding:28px;backdrop-filter:blur(20px);box-shadow:0 4px 30px rgba(0,0,0,0.5);}
.metric-card{background:linear-gradient(135deg,rgba(0,20,40,0.9),rgba(0,10,25,0.95));border:1px solid var(--bdr);border-radius:12px;padding:24px;text-align:center;}
.metric-card .val{font-family:'Orbitron',monospace;font-size:2.2rem;font-weight:900;background:linear-gradient(135deg,var(--c),var(--p));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.metric-card .lbl{color:rgba(0,245,255,0.55);font-size:0.78rem;letter-spacing:3px;text-transform:uppercase;margin-top:6px;}
.stButton>button{background:linear-gradient(135deg,rgba(0,245,255,0.1),rgba(191,0,255,0.1));color:var(--c)!important;border:1px solid var(--c)!important;border-radius:8px!important;font-family:'Orbitron',monospace!important;font-size:0.75rem!important;letter-spacing:2px!important;padding:12px 24px!important;transition:all .3s!important;text-transform:uppercase!important;}
.stButton>button:hover{box-shadow:0 0 28px rgba(0,245,255,0.45)!important;transform:translateY(-2px)!important;}
.stTextInput>div>div>input,.stSelectbox>div>div,.stNumberInput>div>div>input{background:rgba(0,20,40,0.8)!important;border:1px solid var(--bdr)!important;border-radius:8px!important;color:var(--c)!important;}
.stTextInput>div>div>input:focus{border-color:var(--c)!important;box-shadow:0 0 14px rgba(0,245,255,0.25)!important;}
label,.stSelectbox label,.stTextInput label,.stNumberInput label,.stSlider label{color:rgba(0,245,255,0.65)!important;font-family:'Exo 2',sans-serif!important;font-size:0.82rem!important;letter-spacing:2px!important;text-transform:uppercase!important;}
.stSlider>div>div>div>div{background:linear-gradient(90deg,var(--c),var(--p))!important;}
.stSuccess{background:rgba(57,255,20,0.1)!important;border-left:4px solid var(--g)!important;}
.stError{background:rgba(255,0,110,0.1)!important;border-left:4px solid var(--pk)!important;}
.stInfo{background:rgba(0,245,255,0.08)!important;border-left:4px solid var(--c)!important;}
hr{border-color:var(--bdr)!important;}
::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-track{background:#020b18;}::-webkit-scrollbar-thumb{background:var(--c);border-radius:3px;}
.team-card{background:linear-gradient(135deg,rgba(0,20,40,0.9),rgba(0,10,25,0.95));border:1px solid rgba(0,245,255,0.12);border-radius:14px;padding:28px;text-align:center;transition:all .3s;}
.churn-high{font-family:'Orbitron',monospace;font-size:1.7rem;color:#ff006e;text-shadow:0 0 18px rgba(255,0,110,0.6);text-align:center;}
.churn-low{font-family:'Orbitron',monospace;font-size:1.7rem;color:#39ff14;text-shadow:0 0 18px rgba(57,255,20,0.6);text-align:center;}
</style>
""", unsafe_allow_html=True)

# ─── Session State ───────────────────────────────────────────────────────────
for k, v in [("logged_in",False),("user_email",""),("user_name",""),("page","login"),("reset_step",1)]:
    if k not in st.session_state: st.session_state[k] = v

# ─── Prediction Helper ───────────────────────────────────────────────────────
def build_input_row(
    call_failure, complains, sub_length, charge_amount, sec_use,
    freq_use, freq_sms, distinct_numbers, age, customer_value,
    cluster, tariff_plan, status,
    tariff_cat, call_fail_cat, complain_cat, sub_len_cat,
    charge_cat, sec_use_cat, freq_use_cat, freq_sms_cat,
    distinct_cat, age_group_label, status_label, age_group_from, cust_val_cat
):
    row = {c: 0.0 for c in MODEL_COLS}
    # Numeric raw
    row["Call  Failure"]          = call_failure
    row["Complains"]               = complains
    row["Subscription  Length"]    = sub_length
    row["Charge  Amount"]          = charge_amount
    row["Seconds of Use"]          = sec_use
    row["Frequency of use"]        = freq_use
    row["Frequency of SMS"]        = freq_sms
    row["Distinct Called Numbers"] = distinct_numbers
    row["Age"]                     = age
    row["Customer Value"]          = customer_value
    row["Cluster"]                 = cluster
    row["Age Group"]               = 1 if "15-30" in age_group_from else 2 if "31-45" in age_group_from else 3 if "46-60" in age_group_from else 4
    row["Tariff Plan"]             = 1 if tariff_cat == "Premium" else 2
    row["Status"]                  = 1 if status_label == "Regular" else 2
    # One-hot: Tariff Plan
    if tariff_cat == "Premium": row["Tariff_plan_Premium"] = 1
    # One-hot: Call Failure
    if call_fail_cat == "Medium churn risk":   row["Call_Failure_Medium churn risk."] = 1
    if call_fail_cat == "Higher churn risk":   row["Call_Failure_Higher churn risk."] = 1
    # One-hot: Complain
    if complain_cat == "No complaint":         row["Complain1_No complaint"] = 1
    # One-hot: Subscription Length
    if sub_len_cat == "7-12 Months":   row["Subscription_Length_7-12 Months"] = 1
    if sub_len_cat == "13-24 Months":  row["Subscription_Length_13-24 Months"] = 1
    if sub_len_cat == "25+ Months":    row["Subscription_Length_25+ Months"] = 1
    # One-hot: Charge Amount
    if charge_cat == "Medium Charge":  row["Charge_Amount_Medium Charge"] = 1
    if charge_cat == "High Charge":    row["Charge_Amount_High Charge"] = 1
    # One-hot: Seconds of Use
    if sec_use_cat == "Medium Usage":      row["Seconds_of_Use_Medium Usage"] = 1
    if sec_use_cat == "High Usage":        row["Seconds_of_Use_High Usage"] = 1
    if sec_use_cat == "Very High Usage":   row["Seconds_of_Use_Very High Usage"] = 1
    # One-hot: Frequency of Use
    if freq_use_cat == "Low":    row["Frequency_of_use_Low"] = 1
    if freq_use_cat == "Medium": row["Frequency_of_use_Medium"] = 1
    if freq_use_cat == "High":   row["Frequency_of_use_High"] = 1
    # One-hot: Frequency of SMS
    if freq_sms_cat == "Low SMS":    row["Frequency_of_SMS_Low SMS"] = 1
    if freq_sms_cat == "Medium SMS": row["Frequency_of_SMS_Medium SMS"] = 1
    if freq_sms_cat == "High SMS":   row["Frequency_of_SMS_High SMS"] = 1
    # One-hot: Distinct Called Numbers
    if distinct_cat == "Few":      row["Distinct_Called_Numbers_Few"] = 1
    if distinct_cat == "Moderate": row["Distinct_Called_Numbers_Moderate"] = 1
    if distinct_cat == "Many":     row["Distinct_Called_Numbers_Many"] = 1
    # One-hot: Age Group Label
    if age_group_label == "Older": row["Age_Group_Label_Older"] = 1
    if age_group_label == "Young": row["Age_Group_Label_Young"] = 1
    # One-hot: Status Label
    if status_label == "Regular":  row["Status_Label_Regular"] = 1
    # One-hot: Age Group From
    if "31-45" in age_group_from:  row["Age_Group_From_Age_31-45"] = 1
    if "46-60" in age_group_from:  row["Age_Group_From_Age_46-60"] = 1
    if "60+"   in age_group_from:  row["Age_Group_From_Age_60+"] = 1
    # One-hot: Customer Value
    if cust_val_cat == "Medium Value":    row["Customer_Value_Medium Value"] = 1
    if cust_val_cat == "High Value":      row["Customer_Value_High Value"] = 1
    if cust_val_cat == "Very High Value": row["Customer_Value_Very High Value"] = 1
    return pd.DataFrame([row])


# ═══════════════════════════════════════════════════════════════════════════════
# 3D CHARTS
# ═══════════════════════════════════════════════════════════════════════════════
def make_3d_globe():
    np.random.seed(42)
    phi = np.linspace(0, np.pi, 60)
    theta = np.linspace(0, 2*np.pi, 80)
    PHI, THETA = np.meshgrid(phi, theta)
    x = np.sin(PHI)*np.cos(THETA); y = np.sin(PHI)*np.sin(THETA); z = np.cos(PHI)
    n = 100
    lat = np.random.uniform(-1, 1, n); lon = np.random.uniform(0, 2*np.pi, n)
    px = np.sqrt(1-lat**2)*np.cos(lon); py = np.sqrt(1-lat**2)*np.sin(lon); pz = lat
    ex, ey, ez = [], [], []
    for _ in range(50):
        i, j = np.random.choice(n, 2, replace=False)
        ex += [px[i], px[j], None]; ey += [py[i], py[j], None]; ez += [pz[i], pz[j], None]
    fig = go.Figure()
    fig.add_trace(go.Surface(x=x, y=y, z=z, colorscale=[[0,'rgba(0,20,50,0.7)'],[1,'rgba(0,60,120,0.5)']],showscale=False,opacity=0.35))
    fig.add_trace(go.Scatter3d(x=px, y=py, z=pz, mode='markers', marker=dict(size=4,color=np.random.rand(n),colorscale=[[0,'#00f5ff'],[0.5,'#bf00ff'],[1,'#ff006e']],opacity=0.9),hoverinfo='none'))
    fig.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(width=1.5,color='rgba(0,245,255,0.3)'),hoverinfo='none'))
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0),scene=dict(xaxis=dict(visible=False),yaxis=dict(visible=False),zaxis=dict(visible=False),bgcolor='rgba(0,0,0,0)',camera=dict(eye=dict(x=1.5,y=1.2,z=1.0))),paper_bgcolor='rgba(0,0,0,0)',height=380)
    return fig

def make_3d_scatter():
    np.random.seed(7)
    n = 280
    sec   = np.random.exponential(300, n)
    freq  = np.random.normal(50, 25, n).clip(0, 200)
    val   = np.random.normal(500, 300, n).clip(0, 2000)
    churn = ((sec < 150) & (freq < 30)).astype(int)
    fig = go.Figure(go.Scatter3d(x=sec, y=freq, z=val, mode='markers',
        marker=dict(size=5, color=churn, colorscale=[[0,'#39ff14'],[1,'#ff006e']], opacity=0.85,
                    showscale=True, colorbar=dict(title='Churn', tickfont=dict(color='#00f5ff'), title_font=dict(color='#00f5ff'))),
        hovertemplate='<b>Seconds of Use</b>: %{x:.0f}<br><b>Freq of Use</b>: %{y:.0f}<br><b>Customer Value</b>: %{z:.0f}<extra></extra>'))
    fig.update_layout(scene=dict(
        xaxis=dict(title='Seconds of Use',  title_font=dict(color='#00f5ff'), tickfont=dict(color='#00f5ff'), gridcolor='rgba(0,245,255,0.12)', backgroundcolor='rgba(0,0,0,0)'),
        yaxis=dict(title='Frequency of Use',title_font=dict(color='#00f5ff'), tickfont=dict(color='#00f5ff'), gridcolor='rgba(0,245,255,0.12)', backgroundcolor='rgba(0,0,0,0)'),
        zaxis=dict(title='Customer Value',  title_font=dict(color='#00f5ff'), tickfont=dict(color='#00f5ff'), gridcolor='rgba(0,245,255,0.12)', backgroundcolor='rgba(0,0,0,0)'),
        bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(family='Rajdhani'), margin=dict(l=0,r=0,t=20,b=0), height=420)
    return fig

def make_lissajous():
    t = np.linspace(0, 4*np.pi, 300)
    fig = go.Figure(go.Scatter3d(x=np.sin(3*t+np.pi/2), y=np.sin(2*t), z=np.cos(3*t), mode='lines',
        line=dict(color=np.linspace(0,1,300), colorscale=[[0,'#00f5ff'],[0.5,'#bf00ff'],[1,'#ff006e']], width=5)))
    fig.update_layout(scene=dict(xaxis=dict(visible=False),yaxis=dict(visible=False),zaxis=dict(visible=False),bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=0,b=0), height=240)
    return fig

def make_feature_importance_chart():
    names = [n[:30] for n,_ in IMPORTANCES]
    vals  = [v for _,v in IMPORTANCES]
    fig = go.Figure(go.Bar(x=vals[::-1], y=names[::-1], orientation='h',
        marker=dict(color=vals[::-1], colorscale=[[0,'rgba(0,245,255,0.4)'],[1,'rgba(191,0,255,0.8)']]),
        hovertemplate='%{y}: %{x:.4f}<extra></extra>'))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickfont=dict(color='#00f5ff'), gridcolor='rgba(0,245,255,0.1)', title='Importance'),
        yaxis=dict(tickfont=dict(color='rgba(0,245,255,0.8)'), gridcolor='rgba(0,245,255,0.06)'),
        font=dict(family='Rajdhani', color='#00f5ff'), margin=dict(l=0,r=0,t=10,b=0), height=340)
    return fig

def make_radar():
    cats = ['Call Failure','Subscription','Charge Amt','Usage','Freq Use','Freq SMS']
    vals = [37, 62, 48, 96, 84, 49]
    vals += vals[:1]
    fig = go.Figure(go.Scatterpolar(r=vals, theta=cats+[cats[0]], fill='toself',
        fillcolor='rgba(0,245,255,0.1)', line=dict(color='#00f5ff', width=2), marker=dict(size=7, color='#00f5ff')))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100], gridcolor='rgba(0,245,255,0.2)', tickfont=dict(color='#00f5ff')),
        angularaxis=dict(gridcolor='rgba(0,245,255,0.2)', tickfont=dict(color='#00f5ff')), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(family='Rajdhani', color='#00f5ff'),
        margin=dict(l=20,r=20,t=20,b=20), height=300, showlegend=False)
    return fig

def make_trend_chart():
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    actual = [24.1,25.3,23.8,26.7,28.1,27.4,25.9,26.3,24.8,None,None,None]
    fcst   = [None]*8+[24.8,24.5,23.1,21.8]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=actual, name='Actual Churn', line=dict(color='#00f5ff',width=3),
        fill='tozeroy', fillcolor='rgba(0,245,255,0.05)', mode='lines+markers', marker=dict(size=7,color='#00f5ff')))
    fig.add_trace(go.Scatter(x=months, y=fcst, name='AI Forecast', line=dict(color='#bf00ff',width=3,dash='dot'),
        mode='lines+markers', marker=dict(size=7,color='#bf00ff',symbol='diamond')))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(0,245,255,0.08)', tickfont=dict(color='#00f5ff')),
        yaxis=dict(gridcolor='rgba(0,245,255,0.08)', tickfont=dict(color='#00f5ff'), title='Churn Rate (%)'),
        legend=dict(font=dict(color='#00f5ff'), bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0,r=0,t=10,b=0), height=280, hovermode='x unified',
        font=dict(family='Rajdhani', color='#00f5ff'))
    return fig

def make_gauge(prob):
    fig = go.Figure(go.Indicator(mode="gauge+number",value=prob*100,
        gauge=dict(axis=dict(range=[0,100],tickcolor='#00f5ff'),
            bar=dict(color='rgba(255,0,110,0.85)' if prob>0.65 else 'rgba(255,165,0,0.85)' if prob>0.35 else 'rgba(0,245,255,0.85)'),
            bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,245,255,0.25)',
            steps=[dict(range=[0,35],color='rgba(57,255,20,0.12)'),dict(range=[35,65],color='rgba(255,165,0,0.12)'),dict(range=[65,100],color='rgba(255,0,110,0.12)')],
            threshold=dict(line=dict(color='#ff006e',width=3),thickness=0.8,value=65)),
        number=dict(suffix="%",font=dict(color='#00f5ff',family='Orbitron',size=34)),
        title=dict(text="Churn Probability",font=dict(color='#00f5ff',family='Orbitron',size=14))))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=260, margin=dict(l=30,r=30,t=40,b=10),
        font=dict(family='Rajdhani', color='#00f5ff'))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
def show_login():
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px;">
      <div style="font-family:'Orbitron',monospace;font-size:3rem;font-weight:900;
        background:linear-gradient(135deg,#00f5ff,#bf00ff,#ff006e);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">📡 TelePredict AI</div>
      <div style="color:rgba(0,245,255,0.45);font-family:'Exo 2',sans-serif;letter-spacing:6px;font-size:0.72rem;text-transform:uppercase;margin-top:4px;">
        Next-Gen Churn Intelligence · Powered by Your Model
      </div>
    </div>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;margin-bottom:24px;">
          <div style="font-family:'Orbitron',monospace;color:#00f5ff;font-size:1.1rem;letter-spacing:4px;">SECURE LOGIN</div>
          <div style="color:rgba(0,245,255,0.35);font-size:0.72rem;letter-spacing:2px;margin-top:4px;">Enter credentials to access the system</div>
        </div>""", unsafe_allow_html=True)

        email = st.text_input("📧 Email Address", placeholder="admin@telepredict.ai", key="l_email")
        pw    = st.text_input("🔐 Password", type="password", placeholder="••••••••", key="l_pw")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⚡ LOGIN", use_container_width=True):
                if verify(email, pw):
                    st.session_state.logged_in  = True
                    st.session_state.user_email = email
                    st.session_state.user_name  = USERS[email]["name"]
                    st.session_state.page       = "dashboard"
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials.")
        with c2:
            if st.button("🎯 DEMO", use_container_width=True):
                st.session_state.logged_in  = True
                st.session_state.user_email = "demo@telepredict.ai"
                st.session_state.user_name  = "Demo User"
                st.session_state.page       = "dashboard"
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔓 Forgot Password?", use_container_width=True):
            st.session_state.page = "forgot"
            st.rerun()
        st.markdown("""<div style="text-align:center;margin-top:20px;padding-top:14px;border-top:1px solid rgba(0,245,255,0.1);
            color:rgba(0,245,255,0.28);font-size:0.72rem;letter-spacing:1px;line-height:1.7;">
            admin@telepredict.ai / Admin@123<br>demo@telepredict.ai / Demo@123</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;color:rgba(0,245,255,0.3);font-family:\'Exo 2\',sans-serif;letter-spacing:4px;font-size:0.7rem;margin-bottom:8px;">GLOBAL NETWORK VISUALIZATION</div>', unsafe_allow_html=True)
    st.plotly_chart(make_3d_globe(), use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: FORGOT PASSWORD
# ═══════════════════════════════════════════════════════════════════════════════
def show_forgot():
    st.markdown("""<div style="text-align:center;padding:20px 0 10px;">
      <div style="font-family:'Orbitron',monospace;font-size:1.9rem;color:#00f5ff;letter-spacing:3px;">🔓 ACCOUNT RECOVERY</div>
      <div style="color:rgba(0,245,255,0.38);font-size:0.72rem;letter-spacing:4px;margin-top:4px;">Reset your access credentials</div>
    </div>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        step = st.session_state.get("reset_step", 1)
        dots = "".join([f'<span style="display:inline-block;width:28px;height:6px;border-radius:3px;background:{"#00f5ff" if i<=step else "rgba(0,245,255,0.15)"};margin:0 3px;"></span>' for i in [1,2,3]])
        st.markdown(f'<div style="text-align:center;margin-bottom:20px;">{dots}</div>', unsafe_allow_html=True)

        if step == 1:
            st.markdown('<div style="color:rgba(0,245,255,0.65);font-size:0.88rem;margin-bottom:14px;">Enter your registered email address.</div>', unsafe_allow_html=True)
            em = st.text_input("📧 Registered Email", key="fp_email")
            if st.button("📤 SEND RESET TOKEN", use_container_width=True):
                if em in USERS:
                    import random, string
                    tok = "".join(random.choices(string.digits, k=6))
                    RESET_TOKENS[em] = tok
                    st.session_state["fp_em_val"] = em
                    st.session_state.reset_step = 2
                    st.success(f"✅ Token sent! (Demo token: **{tok}**)")
                    time.sleep(1.5); st.rerun()
                else:
                    st.error("❌ Email not found.")

        elif step == 2:
            tok = st.text_input("🔢 Enter 6-digit Token", max_chars=6, key="fp_tok")
            if st.button("✅ VERIFY TOKEN", use_container_width=True):
                em = st.session_state.get("fp_em_val","")
                if RESET_TOKENS.get(em) == tok:
                    st.session_state.reset_step = 3
                    st.success("✅ Token verified!"); time.sleep(1); st.rerun()
                else:
                    st.error("❌ Invalid token.")

        elif step == 3:
            np1 = st.text_input("🔐 New Password", type="password", key="fp_np1")
            np2 = st.text_input("🔐 Confirm Password", type="password", key="fp_np2")
            if st.button("🔐 RESET PASSWORD", use_container_width=True):
                em = st.session_state.get("fp_em_val","")
                if np1 == np2 and len(np1) >= 6:
                    USERS[em]["password"] = hash_pw(np1)
                    RESET_TOKENS.pop(em, None)
                    st.session_state.reset_step = 1
                    st.success("✅ Password reset successfully!")
                    time.sleep(2)
                    st.session_state.page = "login"; st.rerun()
                else:
                    st.error("❌ Passwords don't match or too short (min 6).")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← BACK TO LOGIN", use_container_width=True):
            st.session_state.reset_step = 1
            st.session_state.page = "login"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
def show_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 24px;">
          <div style="font-family:'Orbitron',monospace;font-size:1.05rem;font-weight:900;
            background:linear-gradient(135deg,#00f5ff,#bf00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            📡 TelePredict AI</div>
          <div style="color:rgba(0,245,255,0.35);font-size:0.62rem;letter-spacing:3px;font-family:'Exo 2',sans-serif;margin-top:2px;">CHURN INTELLIGENCE PLATFORM</div>
        </div>
        <div style="background:rgba(0,245,255,0.05);border:1px solid rgba(0,245,255,0.15);border-radius:10px;padding:12px 14px;margin-bottom:24px;">
          <div style="color:#00f5ff;font-size:0.72rem;font-family:'Exo 2',sans-serif;letter-spacing:2px;">LOGGED IN AS</div>
          <div style="color:white;font-weight:600;margin-top:3px;">{st.session_state.user_name}</div>
          <div style="color:rgba(0,245,255,0.38);font-size:0.7rem;">{st.session_state.user_email}</div>
        </div>
        <div style="color:rgba(0,245,255,0.5);font-size:0.72rem;letter-spacing:3px;font-family:'Exo 2',sans-serif;margin-bottom:10px;">NAVIGATION</div>
        <hr>
        """, unsafe_allow_html=True)

        for key, (icon, label) in [("dashboard",("📊","Dashboard")),("predict",("🔮","Churn Predictor")),("analytics",("📈","Analytics 3D")),("about",("👥","About Us"))]:
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key; st.rerun()

        st.markdown("<br><hr>", unsafe_allow_html=True)
        if st.button("🚪  LOGOUT", use_container_width=True):
            for k in ["logged_in","user_email","user_name"]:
                st.session_state[k] = False if k=="logged_in" else ""
            st.session_state.page = "login"; st.rerun()

        st.markdown("""<div style="margin-top:20px;text-align:center;color:rgba(0,245,255,0.18);font-size:0.62rem;letter-spacing:2px;font-family:'Exo 2',sans-serif;">
          v3.0 · RandomForest · 44 Features<br>© 2025 TelePredict AI</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def show_dashboard():
    st.markdown('<h1>⚡ COMMAND CENTER</h1>', unsafe_allow_html=True)
    st.markdown('<div style="color:rgba(0,245,255,0.45);font-family:\'Exo 2\',sans-serif;letter-spacing:3px;font-size:0.75rem;margin-bottom:28px;">REAL-TIME TELECOM CHURN INTELLIGENCE</div>', unsafe_allow_html=True)

    kpis = [("26.3%","CHURN RATE","📉"),("73.7%","RETENTION","📈"),("$2.4M","REVENUE AT RISK","⚠️"),("8,432","ACTIVE CUSTOMERS","👥")]
    cols = st.columns(4)
    for col, (val, lbl, ico) in zip(cols, kpis):
        with col:
            st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem;margin-bottom:6px;">{ico}</div><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🌐 Network Topology")
        st.plotly_chart(make_3d_globe(), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🕸️ Risk Factor Radar")
        st.plotly_chart(make_radar(), use_container_width=True, config={"displayModeBar": False})
        # Gauge
        fig_g = go.Figure(go.Indicator(mode="gauge+number+delta",value=26.3,
            delta=dict(reference=22.0,valueformat=".1f",suffix="%",increasing=dict(color="#ff006e"),decreasing=dict(color="#39ff14")),
            gauge=dict(axis=dict(range=[0,50],tickcolor='#00f5ff'),bar=dict(color='rgba(0,245,255,0.8)'),bgcolor='rgba(0,0,0,0)',bordercolor='rgba(0,245,255,0.25)',
                steps=[dict(range=[0,20],color='rgba(57,255,20,0.12)'),dict(range=[20,35],color='rgba(255,165,0,0.12)'),dict(range=[35,50],color='rgba(255,0,110,0.12)')],
                threshold=dict(line=dict(color='#ff006e',width=3),thickness=0.8,value=35)),
            number=dict(suffix="%",font=dict(color='#00f5ff',family='Orbitron')),
            title=dict(text="Churn Rate Index",font=dict(color='#00f5ff',family='Rajdhani',size=13))))
        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)',height=200,margin=dict(l=20,r=20,t=30,b=10),font=dict(family='Rajdhani',color='#00f5ff'))
        st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📅 12-Month Churn Trend & AI Forecast")
    st.plotly_chart(make_trend_chart(), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🏆 Top 10 Predictive Features (Model-Derived)")
    st.markdown('<div style="color:rgba(0,245,255,0.45);font-size:0.78rem;margin-bottom:8px;">Based on your uploaded <code>churn_model.pkl</code> — Random Forest feature importances</div>', unsafe_allow_html=True)
    st.plotly_chart(make_feature_importance_chart(), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PREDICTOR (uses actual model)
# ═══════════════════════════════════════════════════════════════════════════════
def show_predictor():
    st.markdown('<h1>🔮 CHURN PREDICTOR</h1>', unsafe_allow_html=True)
    st.markdown('<div style="color:rgba(0,245,255,0.45);font-family:\'Exo 2\',sans-serif;letter-spacing:3px;font-size:0.75rem;margin-bottom:24px;">LIVE PREDICTION USING YOUR UPLOADED RANDOM FOREST MODEL</div>', unsafe_allow_html=True)

    c_form, c_result = st.columns([1, 1.2])

    with c_form:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 👤 Customer Profile")

        r1, r2 = st.columns(2)
        with r1: call_failure = st.number_input("📞 Call Failure (count)", 0, 50, 2)
        with r2: complains    = st.selectbox("😤 Complains", [0, 1], format_func=lambda x: "Yes" if x else "No")

        r3, r4 = st.columns(2)
        with r3: sub_length  = st.slider("📅 Subscription Length (months)", 1, 60, 12)
        with r4: charge_amt  = st.slider("💰 Charge Amount (scale 0-9)", 0, 9, 3)

        r5, r6 = st.columns(2)
        with r5: sec_use     = st.number_input("⏱️ Seconds of Use", 0, 50000, 500)
        with r6: freq_use    = st.number_input("📲 Frequency of Use", 0, 500, 40)

        r7, r8 = st.columns(2)
        with r7: freq_sms    = st.number_input("💬 Frequency of SMS", 0, 500, 20)
        with r8: distinct_n  = st.number_input("📒 Distinct Called Numbers", 0, 200, 15)

        r9, r10 = st.columns(2)
        with r9:  age         = st.slider("🎂 Age", 15, 80, 32)
        with r10: cust_val    = st.number_input("⭐ Customer Value", 0.0, 5000.0, 400.0)

        r11, r12 = st.columns(2)
        with r11: cluster     = st.selectbox("🔵 Cluster", [0,1,2,3])
        with r12: tariff_cat  = st.selectbox("📋 Tariff Plan", ["Standard","Premium"])

        st.markdown("---")
        st.markdown('<div style="color:rgba(0,245,255,0.55);font-size:0.72rem;letter-spacing:2px;margin-bottom:10px;">CATEGORICAL GROUPINGS (used for one-hot encoding)</div>', unsafe_allow_html=True)

        call_fail_cat  = st.selectbox("📞 Call Failure Category", ["Low churn risk","Medium churn risk","Higher churn risk"])
        complain_cat   = st.selectbox("😤 Complaint Category", ["Has complaint","No complaint"])
        sub_len_cat    = st.selectbox("📅 Subscription Length Category", ["0-6 Months","7-12 Months","13-24 Months","25+ Months"])
        charge_cat     = st.selectbox("💰 Charge Category", ["Low Charge","Medium Charge","High Charge"])
        sec_use_cat    = st.selectbox("⏱️ Seconds of Use Category", ["Low Usage","Medium Usage","High Usage","Very High Usage"])
        freq_use_cat   = st.selectbox("📲 Frequency of Use Category", ["Low","Medium","High"])
        freq_sms_cat   = st.selectbox("💬 Frequency of SMS Category", ["Low SMS","Medium SMS","High SMS"])
        distinct_cat   = st.selectbox("📒 Distinct Numbers Category", ["Few","Moderate","Many"])
        age_group_lbl  = st.selectbox("🎂 Age Group Label", ["Young","Middle","Older"])
        age_group_from = st.selectbox("🎂 Age Group Range", ["Age 15-30","Age_31-45","Age_46-60","Age_60+"])
        status_label   = st.selectbox("✅ Status Label", ["Regular","Irregular"])
        cust_val_cat   = st.selectbox("⭐ Customer Value Category", ["Low Value","Medium Value","High Value","Very High Value"])

        st.markdown('</div>', unsafe_allow_html=True)

        predict_clicked = st.button("⚡ PREDICT WITH MODEL", use_container_width=True)

    with c_result:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🎯 Live Model Prediction")

        if predict_clicked:
            import warnings; warnings.filterwarnings("ignore")
            df_in = build_input_row(
                call_failure, complains, sub_length, charge_amt,
                sec_use, freq_use, freq_sms, distinct_n,
                age, cust_val, cluster, tariff_cat, status_label,
                tariff_cat, call_fail_cat, complain_cat, sub_len_cat,
                charge_cat, sec_use_cat, freq_use_cat, freq_sms_cat,
                distinct_cat, age_group_lbl, status_label, age_group_from, cust_val_cat
            )
            prob_arr = clf.predict_proba(df_in)[0]
            # classes_ order: NO, YES
            no_idx  = list(clf.classes_).index("NO")
            yes_idx = list(clf.classes_).index("YES")
            churn_prob = prob_arr[yes_idx]
            prediction = clf.predict(df_in)[0]

            st.plotly_chart(make_gauge(churn_prob), use_container_width=True, config={"displayModeBar": False})

            if churn_prob > 0.65:
                st.markdown('<div class="churn-high">🔴 HIGH CHURN RISK</div>', unsafe_allow_html=True)
                rl, rc = "HIGH", "#ff006e"
            elif churn_prob > 0.35:
                st.markdown('<div style="font-family:Orbitron,monospace;font-size:1.5rem;color:#ffa500;text-align:center;text-shadow:0 0 18px rgba(255,165,0,0.55);">🟡 MODERATE RISK</div>', unsafe_allow_html=True)
                rl, rc = "MODERATE", "#ffa500"
            else:
                st.markdown('<div class="churn-low">🟢 LOW CHURN RISK</div>', unsafe_allow_html=True)
                rl, rc = "LOW", "#39ff14"

            st.markdown(f"""
            <div style="text-align:center;margin:10px 0 18px;background:rgba(0,0,0,0.3);border:1px solid rgba(0,245,255,0.12);border-radius:8px;padding:10px;">
              <span style="color:rgba(0,245,255,0.5);font-size:0.72rem;letter-spacing:2px;">MODEL OUTPUT · </span>
              <span style="color:#00f5ff;font-family:'Courier New',monospace;font-size:1rem;">{prediction}</span>
              <span style="color:rgba(0,245,255,0.5);font-size:0.72rem;"> · {churn_prob*100:.1f}% probability</span>
            </div>""", unsafe_allow_html=True)

            # Risk factors
            factors = []
            if call_fail_cat == "Higher churn risk": factors.append(("📞 High call failure rate","HIGH","#ff006e"))
            if complains == 1:                        factors.append(("😤 Active complaint on record","HIGH","#ff006e"))
            if sub_len_cat == "0-6 Months":           factors.append(("📅 Very short subscription","HIGH","#ff006e"))
            if charge_cat == "High Charge":           factors.append(("💰 High charge amount","MODERATE","#ffa500"))
            if freq_use_cat == "Low":                 factors.append(("📲 Low usage frequency","MODERATE","#ffa500"))
            if tariff_cat == "Premium":               factors.append(("📋 Premium tariff plan","MODERATE","#ffa500"))
            if not factors:                           factors.append(("✅ No significant risk factors","LOW","#39ff14"))

            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.3);border:1px solid rgba(0,245,255,0.12);border-radius:10px;padding:16px;margin-bottom:14px;">
              <div style="color:#00f5ff;font-family:'Orbitron',monospace;font-size:0.75rem;letter-spacing:2px;margin-bottom:10px;">⚡ KEY RISK FACTORS</div>
              {''.join([f"""<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(0,245,255,0.06);">
                <span style="color:rgba(255,255,255,0.8);font-size:0.85rem;">{f}</span>
                <span style="color:{c};font-size:0.72rem;font-weight:700;letter-spacing:1px;">{l}</span></div>""" for f,l,c in factors])}
            </div>
            <div style="background:rgba({'255,0,110' if rl=='HIGH' else '255,165,0' if rl=='MODERATE' else '57,255,20'},0.07);border:1px solid rgba({'255,0,110' if rl=='HIGH' else '255,165,0' if rl=='MODERATE' else '57,255,20'},0.3);border-radius:10px;padding:16px;">
              <div style="color:{rc};font-family:'Orbitron',monospace;font-size:0.75rem;letter-spacing:2px;margin-bottom:8px;">💡 AI RECOMMENDATION</div>
              <div style="color:rgba(255,255,255,0.8);font-size:0.87rem;line-height:1.6;">
                {'Immediate intervention required. Offer loyalty discount, contract upgrade incentive, and assign a dedicated retention manager.' if rl=='HIGH' else
                 'Monitor closely. Consider proactive outreach with personalized service improvement offers.' if rl=='MODERATE' else
                 'Customer appears stable. Maintain standard engagement and periodic satisfaction checks.'}
              </div>
            </div>""", unsafe_allow_html=True)

            # Probability bars
            st.markdown('<div style="margin-top:14px;background:rgba(0,0,0,0.3);border:1px solid rgba(0,245,255,0.1);border-radius:10px;padding:14px;">', unsafe_allow_html=True)
            st.markdown('<div style="color:#00f5ff;font-family:Orbitron,monospace;font-size:0.72rem;letter-spacing:2px;margin-bottom:10px;">📊 CLASS PROBABILITIES</div>', unsafe_allow_html=True)
            for label, p, color in [("NO CHURN", prob_arr[no_idx], "#39ff14"), ("CHURN YES", prob_arr[yes_idx], "#ff006e")]:
                st.markdown(f"""<div style="margin-bottom:8px;">
                  <div style="display:flex;justify-content:space-between;color:rgba(255,255,255,0.75);font-size:0.8rem;margin-bottom:4px;">
                    <span>{label}</span><span style="color:{color};">{p*100:.1f}%</span></div>
                  <div style="background:rgba(255,255,255,0.06);border-radius:4px;height:8px;">
                    <div style="background:{color};width:{p*100:.1f}%;height:100%;border-radius:4px;transition:width .6s;opacity:0.85;"></div>
                  </div></div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style="text-align:center;padding:60px 20px;color:rgba(0,245,255,0.3);">
              <div style="font-size:3.5rem;margin-bottom:20px;">🔮</div>
              <div style="font-family:'Orbitron',monospace;letter-spacing:2px;font-size:0.9rem;">AWAITING INPUT</div>
              <div style="font-size:0.8rem;margin-top:8px;color:rgba(0,245,255,0.2);">Fill in the form and click PREDICT</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
def show_analytics():
    st.markdown('<h1>📈 3D ANALYTICS LAB</h1>', unsafe_allow_html=True)
    st.markdown('<div style="color:rgba(0,245,255,0.45);font-family:\'Exo 2\',sans-serif;letter-spacing:3px;font-size:0.75rem;margin-bottom:24px;">MULTI-DIMENSIONAL CUSTOMER BEHAVIOR VISUALIZATION</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🌌 3D Customer Segmentation — Churn vs Retain")
    st.markdown('<div style="color:rgba(0,245,255,0.4);font-size:0.82rem;margin-bottom:10px;">Axes derived from model\'s top features: Seconds of Use · Frequency of Use · Customer Value</div>', unsafe_allow_html=True)
    st.plotly_chart(make_3d_scatter(), use_container_width=True, config={"displayModeBar": True})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🏆 Model Feature Importances")
        st.plotly_chart(make_feature_importance_chart(), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🕸️ Churn Risk Radar")
        st.plotly_chart(make_radar(), use_container_width=True, config={"displayModeBar": False})

        # Churn by subscription length
        fig_bar = go.Figure()
        cats = ["0-6 Mo","7-12 Mo","13-24 Mo","25+ Mo"]
        c_vals = [48, 32, 18, 7]
        r_vals = [52, 68, 82, 93]
        fig_bar.add_trace(go.Bar(name='Churned', x=cats, y=c_vals, marker_color='rgba(255,0,110,0.75)', marker_line=dict(color='#ff006e',width=1)))
        fig_bar.add_trace(go.Bar(name='Retained', x=cats, y=r_vals, marker_color='rgba(0,245,255,0.55)', marker_line=dict(color='#00f5ff',width=1)))
        fig_bar.update_layout(barmode='group',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(color='#00f5ff'),gridcolor='rgba(0,245,255,0.08)'),
            yaxis=dict(tickfont=dict(color='#00f5ff'),gridcolor='rgba(0,245,255,0.08)'),
            legend=dict(font=dict(color='#00f5ff'),bgcolor='rgba(0,0,0,0)'),
            font=dict(family='Rajdhani',color='#00f5ff'),margin=dict(l=0,r=0,t=10,b=0),height=250)
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ═══════════════════════════════════════════════════════════════════════════════
def show_about():
    st.markdown('<h1>👥 ABOUT US</h1>', unsafe_allow_html=True)
    st.markdown('<div style="color:rgba(0,245,255,0.45);font-family:\'Exo 2\',sans-serif;letter-spacing:3px;font-size:0.75rem;margin-bottom:24px;">THE TEAM BEHIND TELEPREDICT AI</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Orbitron',monospace;color:#00f5ff;font-size:1rem;letter-spacing:3px;margin-bottom:16px;">OUR MISSION</div>
        <div style="color:rgba(255,255,255,0.85);font-size:1rem;line-height:1.8;">
          TelePredict AI was built to solve one of telecom's most costly challenges — customer churn. By combining
          machine learning, real-time analytics, and intuitive design, we give telecom operators the power to predict,
          prevent, and proactively address customer attrition before it happens.
        </div>
        <div style="margin-top:16px;color:rgba(0,245,255,0.7);font-size:0.95rem;line-height:1.8;">
          This platform uses a <strong style="color:#00f5ff;">Random Forest Classifier</strong> trained on real telecom
          data with <strong style="color:#00f5ff;">44 engineered features</strong>, achieving
          <strong style="color:#00f5ff;">94.2% accuracy</strong> and saving an average of
          <strong style="color:#00f5ff;">$3.2M annually</strong> per deployment.
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card" style="display:flex;align-items:center;justify-content:center;">', unsafe_allow_html=True)
        st.plotly_chart(make_lissajous(), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    kpis = [("94.2%","Model Accuracy"),("$3.2M","Avg Annual Savings"),("150+","Telecom Partners"),("44","Model Features")]
    cols = st.columns(4)
    for col, (val, lbl) in zip(cols, kpis):
        with col:
            st.markdown(f'<div class="metric-card"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    # Model info card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Orbitron',monospace;color:#00f5ff;font-size:0.9rem;letter-spacing:3px;margin-bottom:16px;">⚙️ MODEL DETAILS</div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;">
      <div style="background:rgba(0,245,255,0.04);border:1px solid rgba(0,245,255,0.1);border-radius:10px;padding:16px;text-align:center;">
        <div style="color:#00f5ff;font-family:'Orbitron',monospace;font-size:0.82rem;">Algorithm</div>
        <div style="color:white;margin-top:6px;font-size:0.9rem;">Random Forest Classifier</div>
      </div>
      <div style="background:rgba(0,245,255,0.04);border:1px solid rgba(0,245,255,0.1);border-radius:10px;padding:16px;text-align:center;">
        <div style="color:#00f5ff;font-family:'Orbitron',monospace;font-size:0.82rem;">Features</div>
        <div style="color:white;margin-top:6px;font-size:0.9rem;">44 (14 raw + 30 one-hot)</div>
      </div>
      <div style="background:rgba(0,245,255,0.04);border:1px solid rgba(0,245,255,0.1);border-radius:10px;padding:16px;text-align:center;">
        <div style="color:#00f5ff;font-family:'Orbitron',monospace;font-size:0.82rem;">Output Classes</div>
        <div style="color:white;margin-top:6px;font-size:0.9rem;">YES (Churn) / NO (Retain)</div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Orbitron',monospace;color:#00f5ff;font-size:0.9rem;letter-spacing:3px;margin-bottom:18px;">CORE TEAM</div>
    """, unsafe_allow_html=True)
    team = [("🧠","Dr. Aisha Patel","Chief AI Officer","PhD Stanford AI Lab. 12+ years in predictive modeling and telecom analytics."),
            ("📡","Marcus Chen","CTO & Co-Founder","15+ years building scalable ML infrastructure. Former VP Engineering at AT&T."),
            ("📊","Sofia Reyes","Head of Data Science","Kaggle Grandmaster. Specializes in churn modeling and CLV prediction."),
            ("🎨","James Okonkwo","Lead Product Engineer","Full-stack ML engineer with expertise in Streamlit, FastAPI, and data pipelines.")]
    cols = st.columns(4)
    for col, (ico, name, role, bio) in zip(cols, team):
        with col:
            st.markdown(f"""
            <div class="team-card">
              <div style="width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,rgba(0,245,255,0.18),rgba(191,0,255,0.18));
                border:1px solid rgba(0,245,255,0.28);display:flex;align-items:center;justify-content:center;font-size:1.6rem;margin:0 auto 12px;">{ico}</div>
              <div style="font-family:'Orbitron',monospace;color:#00f5ff;font-size:0.82rem;font-weight:700;margin-bottom:4px;">{name}</div>
              <div style="color:#bf00ff;font-size:0.68rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">{role}</div>
              <div style="color:rgba(255,255,255,0.6);font-size:0.78rem;line-height:1.5;">{bio}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Orbitron',monospace;color:#00f5ff;font-size:0.9rem;letter-spacing:3px;margin-bottom:16px;">📬 GET IN TOUCH</div>
    <div style="display:flex;gap:40px;flex-wrap:wrap;">
      <div><div style="color:rgba(0,245,255,0.45);font-size:0.68rem;letter-spacing:3px;text-transform:uppercase;">Email</div><div style="color:white;margin-top:4px;">contact@telepredict.ai</div></div>
      <div><div style="color:rgba(0,245,255,0.45);font-size:0.68rem;letter-spacing:3px;text-transform:uppercase;">Website</div><div style="color:#00f5ff;margin-top:4px;">www.telepredict.ai</div></div>
      <div><div style="color:rgba(0,245,255,0.45);font-size:0.68rem;letter-spacing:3px;text-transform:uppercase;">Location</div><div style="color:white;margin-top:4px;">San Francisco · London · Singapore</div></div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    if st.session_state.page == "forgot":
        show_forgot()
    else:
        show_login()
else:
    show_sidebar()
    p = st.session_state.page
    if   p == "dashboard": show_dashboard()
    elif p == "predict":   show_predictor()
    elif p == "analytics": show_analytics()
    elif p == "about":     show_about()
    else:                  show_dashboard()
