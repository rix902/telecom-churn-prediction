import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import time
import hashlib

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TelePredict AI",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── User Database (in-memory) ───────────────────────────────────────────────
USERS = {
    "admin@telepredict.ai": {"password": hashlib.sha256("Admin@123".encode()).hexdigest(), "name": "Admin User"},
    "demo@telepredict.ai": {"password": hashlib.sha256("Demo@123".encode()).hexdigest(), "name": "Demo User"},
}
RESET_TOKENS = {}

def hash_password(pw): return hashlib.sha256(pw.encode()).hexdigest()
def verify(email, pw): return email in USERS and USERS[email]["password"] == hash_password(pw)

# ─── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&family=Exo+2:wght@300;400;600&display=swap');

:root {
    --neon-cyan: #00f5ff;
    --neon-purple: #bf00ff;
    --neon-pink: #ff006e;
    --neon-green: #39ff14;
    --dark-bg: #020b18;
    --card-bg: rgba(0,20,40,0.85);
    --glass: rgba(0,245,255,0.05);
    --border: rgba(0,245,255,0.2);
}

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
}

/* Dark background */
.stApp {
    background: var(--dark-bg);
    background-image:
        radial-gradient(ellipse at 10% 20%, rgba(0,245,255,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(191,0,255,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(255,0,110,0.04) 0%, transparent 60%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020b18 0%, #030d20 100%) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple), var(--neon-pink));
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }

/* Headings */
h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: var(--neon-cyan) !important;
    text-shadow: 0 0 20px rgba(0,245,255,0.5), 0 0 40px rgba(0,245,255,0.2);
    letter-spacing: 2px;
}

/* Cards */
.glass-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 4px 30px rgba(0,0,0,0.5), inset 0 1px 0 rgba(0,245,255,0.1);
}
.glass-card::before {
    content: '';
    position: absolute;
    top: -2px; left: -2px; right: -2px; bottom: -2px;
    background: linear-gradient(135deg, rgba(0,245,255,0.15), transparent, rgba(191,0,255,0.15));
    border-radius: 18px;
    z-index: -1;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(0,20,40,0.9), rgba(0,10,25,0.95));
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.metric-card .value {
    font-family: 'Orbitron', monospace;
    font-size: 2.4rem;
    font-weight: 900;
    background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-card .label {
    font-family: 'Exo 2', sans-serif;
    color: rgba(0,245,255,0.6);
    font-size: 0.85rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 6px;
}

/* Neon button */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,245,255,0.1), rgba(191,0,255,0.1));
    color: var(--neon-cyan) !important;
    border: 1px solid var(--neon-cyan) !important;
    border-radius: 8px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 2px !important;
    padding: 12px 28px !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 15px rgba(0,245,255,0.2) !important;
}
.stButton > button:hover {
    background: rgba(0,245,255,0.15) !important;
    box-shadow: 0 0 30px rgba(0,245,255,0.5), 0 0 60px rgba(0,245,255,0.2) !important;
    transform: translateY(-2px) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: rgba(0,20,40,0.8) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--neon-cyan) !important;
    font-family: 'Rajdhani', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--neon-cyan) !important;
    box-shadow: 0 0 15px rgba(0,245,255,0.3) !important;
}

/* Labels */
label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stSlider label {
    color: rgba(0,245,255,0.7) !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* Sliders */
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple)) !important;
}

/* Alert boxes */
.stSuccess { background: rgba(57,255,20,0.1) !important; border-left: 4px solid var(--neon-green) !important; }
.stError { background: rgba(255,0,110,0.1) !important; border-left: 4px solid var(--neon-pink) !important; }
.stWarning { background: rgba(255,165,0,0.1) !important; border-left: 4px solid #ffa500 !important; }
.stInfo { background: rgba(0,245,255,0.1) !important; border-left: 4px solid var(--neon-cyan) !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--dark-bg); }
::-webkit-scrollbar-thumb { background: var(--neon-cyan); border-radius: 3px; }

/* Login page */
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
}
.login-card {
    background: rgba(0,20,40,0.9);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 48px;
    max-width: 480px;
    width: 100%;
    backdrop-filter: blur(20px);
    box-shadow: 0 0 60px rgba(0,245,255,0.1), 0 20px 60px rgba(0,0,0,0.8);
    position: relative;
}
.login-card::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px; right: -1px; bottom: -1px;
    background: linear-gradient(135deg, var(--neon-cyan), transparent, var(--neon-purple), transparent, var(--neon-pink));
    border-radius: 21px;
    z-index: -1;
    opacity: 0.5;
}
.logo-title {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 900;
    background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 8px;
}
.logo-sub {
    text-align: center;
    color: rgba(0,245,255,0.5);
    font-family: 'Exo 2', sans-serif;
    font-size: 0.8rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 32px;
}

/* Sidebar nav */
.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 6px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 1px;
    color: rgba(0,245,255,0.6);
}
.nav-item:hover, .nav-item.active {
    background: rgba(0,245,255,0.08);
    color: var(--neon-cyan);
    border-left: 3px solid var(--neon-cyan);
}

/* Team cards */
.team-card {
    background: linear-gradient(135deg, rgba(0,20,40,0.9), rgba(0,10,25,0.95));
    border: 1px solid rgba(0,245,255,0.15);
    border-radius: 16px;
    padding: 32px 24px;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.team-card:hover {
    border-color: var(--neon-cyan);
    box-shadow: 0 0 40px rgba(0,245,255,0.15);
    transform: translateY(-4px);
}
.avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin: 0 auto 16px;
    box-shadow: 0 0 20px rgba(0,245,255,0.3);
}

/* Churn result */
.churn-high {
    font-family: 'Orbitron', monospace;
    font-size: 1.8rem;
    color: var(--neon-pink);
    text-shadow: 0 0 20px rgba(255,0,110,0.6);
    text-align: center;
}
.churn-low {
    font-family: 'Orbitron', monospace;
    font-size: 1.8rem;
    color: var(--neon-green);
    text-shadow: 0 0 20px rgba(57,255,20,0.6);
    text-align: center;
}

/* Particle canvas */
#particles { position: fixed; top: 0; left: 0; z-index: -1; }

/* Pulse animation */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
.pulse { animation: pulse 2s infinite; }

/* Glow scan line */
@keyframes scan {
    0% { top: -10%; }
    100% { top: 110%; }
}
</style>
""", unsafe_allow_html=True)

# ─── Session State ───────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "page" not in st.session_state:
    st.session_state.page = "login"

# ─── 3D Globe Helper ─────────────────────────────────────────────────────────
def make_3d_globe():
    theta = np.linspace(0, 2*np.pi, 100)
    phi = np.linspace(0, np.pi, 80)
    THETA, PHI = np.meshgrid(theta, phi)
    x = np.sin(PHI)*np.cos(THETA)
    y = np.sin(PHI)*np.sin(THETA)
    z = np.cos(PHI)

    # Network points
    np.random.seed(42)
    n = 120
    lat = np.random.uniform(-1, 1, n)
    lon = np.random.uniform(0, 2*np.pi, n)
    px = np.sqrt(1-lat**2)*np.cos(lon)
    py = np.sqrt(1-lat**2)*np.sin(lon)
    pz = lat

    fig = go.Figure()

    # Sphere surface
    fig.add_trace(go.Surface(
        x=x, y=y, z=z,
        colorscale=[[0, 'rgba(0,20,40,0.8)'], [1, 'rgba(0,50,100,0.6)']],
        showscale=False,
        opacity=0.4,
        lighting=dict(ambient=0.8, diffuse=0.5, specular=0.8),
    ))

    # Network nodes
    fig.add_trace(go.Scatter3d(
        x=px, y=py, z=pz,
        mode='markers',
        marker=dict(size=4, color=np.random.uniform(0, 1, n),
                    colorscale=[[0,'#00f5ff'],[0.5,'#bf00ff'],[1,'#ff006e']],
                    opacity=0.9),
        hoverinfo='none'
    ))

    # Network edges (random connections)
    edge_x, edge_y, edge_z = [], [], []
    for _ in range(60):
        i, j = np.random.choice(n, 2, replace=False)
        edge_x += [px[i], px[j], None]
        edge_y += [py[i], py[j], None]
        edge_z += [pz[i], pz[j], None]

    fig.add_trace(go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(width=1.5, color='rgba(0,245,255,0.3)'),
        hoverinfo='none'
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor='rgba(0,0,0,0)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=420,
    )
    return fig


def make_3d_churn_scatter(n=300):
    np.random.seed(7)
    tenure = np.random.exponential(30, n)
    monthly = np.random.normal(65, 30, n)
    usage = np.random.normal(500, 200, n)
    churn = ((tenure < 15) & (monthly > 70)).astype(int)

    fig = go.Figure(data=go.Scatter3d(
        x=tenure, y=monthly, z=usage,
        mode='markers',
        marker=dict(
            size=5,
            color=churn,
            colorscale=[[0,'#39ff14'],[1,'#ff006e']],
            opacity=0.8,
            showscale=True,
            colorbar=dict(title='Churn', tickfont=dict(color='#00f5ff'), title_font=dict(color='#00f5ff'))
        ),
        hovertemplate='<b>Tenure</b>: %{x:.0f}mo<br><b>Monthly</b>: $%{y:.0f}<br><b>Usage</b>: %{z:.0f}MB<extra></extra>',
    ))
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Tenure (months)', title_font=dict(color='#00f5ff'), tickfont=dict(color='#00f5ff'), gridcolor='rgba(0,245,255,0.15)', backgroundcolor='rgba(0,0,0,0)'),
            yaxis=dict(title='Monthly Charges ($)', title_font=dict(color='#00f5ff'), tickfont=dict(color='#00f5ff'), gridcolor='rgba(0,245,255,0.15)', backgroundcolor='rgba(0,0,0,0)'),
            zaxis=dict(title='Data Usage (MB)', title_font=dict(color='#00f5ff'), tickfont=dict(color='#00f5ff'), gridcolor='rgba(0,245,255,0.15)', backgroundcolor='rgba(0,0,0,0)'),
            bgcolor='rgba(0,0,0,0)',
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0),
        height=440,
        font=dict(family='Rajdhani'),
    )
    return fig


def make_3d_bar_chart():
    categories = ['Contract', 'Internet', 'Payment', 'Support', 'Tenure']
    churn_rates = [45, 38, 28, 22, 15]
    retain_rates = [55, 62, 72, 78, 85]

    fig = go.Figure()
    for i, (cat, churn, retain) in enumerate(zip(categories, churn_rates, retain_rates)):
        fig.add_trace(go.Bar(
            name=f'{cat} - Churn',
            x=[cat], y=[churn],
            marker_color='rgba(255,0,110,0.8)',
            marker_line=dict(color='#ff006e', width=1.5),
        ))
        fig.add_trace(go.Bar(
            name=f'{cat} - Retain',
            x=[cat], y=[retain],
            marker_color='rgba(0,245,255,0.6)',
            marker_line=dict(color='#00f5ff', width=1.5),
        ))

    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Rajdhani', color='#00f5ff'),
        xaxis=dict(gridcolor='rgba(0,245,255,0.1)', title='Category'),
        yaxis=dict(gridcolor='rgba(0,245,255,0.1)', title='Percentage (%)'),
        legend=dict(font=dict(color='#00f5ff', size=10), bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0, r=0, t=20, b=0),
        height=360,
    )
    return fig


# ─── Train Model ─────────────────────────────────────────────────────────────
@st.cache_resource
def train_model():
    np.random.seed(42)
    n = 2000
    df = pd.DataFrame({
        'gender': np.random.choice(['Male','Female'], n),
        'SeniorCitizen': np.random.choice([0,1], n, p=[0.84,0.16]),
        'Partner': np.random.choice(['Yes','No'], n),
        'Dependents': np.random.choice(['Yes','No'], n),
        'tenure': np.random.randint(0, 72, n),
        'PhoneService': np.random.choice(['Yes','No'], n, p=[0.9,0.1]),
        'MultipleLines': np.random.choice(['Yes','No','No phone'], n),
        'InternetService': np.random.choice(['DSL','Fiber optic','No'], n, p=[0.35,0.44,0.21]),
        'Contract': np.random.choice(['Month-to-month','One year','Two year'], n, p=[0.55,0.24,0.21]),
        'PaperlessBilling': np.random.choice(['Yes','No'], n),
        'PaymentMethod': np.random.choice(['Electronic check','Mailed check','Bank transfer','Credit card'], n),
        'MonthlyCharges': np.random.normal(65, 30, n).clip(18, 120),
        'TotalCharges': np.random.normal(2200, 2000, n).clip(0, 8900),
    })
    # Churn logic
    p_churn = (
        0.5*(df['Contract']=='Month-to-month').astype(float) +
        0.2*(df['InternetService']=='Fiber optic').astype(float) +
        0.2*(df['tenure']<12).astype(float) +
        0.1*(df['SeniorCitizen']==1).astype(float) - 0.2
    ).clip(0.05, 0.85)
    df['Churn'] = (np.random.rand(n) < p_churn).astype(int)

    le = LabelEncoder()
    cat_cols = ['gender','Partner','Dependents','PhoneService','MultipleLines',
                'InternetService','Contract','PaperlessBilling','PaymentMethod']
    for col in cat_cols:
        df[col] = le.fit_transform(df[col])

    X = df.drop('Churn', axis=1)
    y = df['Churn']
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    return clf, X.columns.tolist()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
def show_login():
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px;">
        <div style="font-family:'Orbitron',monospace; font-size:3rem; font-weight:900;
            background:linear-gradient(135deg,#00f5ff,#bf00ff,#ff006e);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:6px;">
            📡 TelePredict AI
        </div>
        <div style="color:rgba(0,245,255,0.5); font-family:'Exo 2',sans-serif;
            letter-spacing:6px; font-size:0.75rem; text-transform:uppercase;">
            Next-Gen Churn Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)

            st.markdown("""
            <div style="text-align:center; margin-bottom:24px;">
                <div style="font-family:'Orbitron',monospace; color:#00f5ff; font-size:1.3rem; font-weight:700; letter-spacing:3px;">
                    SECURE LOGIN
                </div>
                <div style="color:rgba(0,245,255,0.4); font-size:0.75rem; letter-spacing:2px; margin-top:4px;">
                    Enter your credentials to access the system
                </div>
            </div>
            """, unsafe_allow_html=True)

            email = st.text_input("📧 Email Address", placeholder="admin@telepredict.ai", key="login_email")
            password = st.text_input("🔐 Password", type="password", placeholder="••••••••", key="login_pw")

            st.markdown("<br>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("⚡ LOGIN", use_container_width=True):
                    if verify(email, password):
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.user_name = USERS[email]["name"]
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Try admin@telepredict.ai / Admin@123")
            with col_b:
                if st.button("🔑 DEMO", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.user_email = "demo@telepredict.ai"
                    st.session_state.user_name = "Demo User"
                    st.session_state.page = "dashboard"
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔓 Forgot Password?", use_container_width=True):
                st.session_state.page = "forgot_password"
                st.rerun()

            st.markdown("""
            <div style="text-align:center; margin-top:20px; padding-top:16px; border-top:1px solid rgba(0,245,255,0.1);">
                <span style="color:rgba(0,245,255,0.3); font-size:0.75rem; font-family:'Exo 2',sans-serif; letter-spacing:2px;">
                    DEMO: admin@telepredict.ai / Admin@123
                </span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 3D Globe below login
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:rgba(0,245,255,0.4); font-family:\'Exo 2\',sans-serif; letter-spacing:4px; font-size:0.75rem; margin-bottom:8px;">GLOBAL TELECOM NETWORK VISUALIZATION</div>', unsafe_allow_html=True)
    st.plotly_chart(make_3d_globe(), use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: FORGOT PASSWORD
# ═══════════════════════════════════════════════════════════════════════════════
def show_forgot_password():
    st.markdown("""
    <div style="text-align:center; padding:20px 0 10px;">
        <div style="font-family:'Orbitron',monospace; font-size:2rem; font-weight:900; color:#00f5ff;
            text-shadow: 0 0 20px rgba(0,245,255,0.5); letter-spacing:3px;">
            🔓 ACCOUNT RECOVERY
        </div>
        <div style="color:rgba(0,245,255,0.4); font-size:0.8rem; letter-spacing:4px; margin-top:4px;">
            Reset your access credentials
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        step = st.session_state.get("reset_step", 1)

        if step == 1:
            st.markdown("""
            <div style="color:rgba(0,245,255,0.7); font-family:'Exo 2',sans-serif; font-size:0.9rem; margin-bottom:16px;">
                Enter your registered email address to receive a reset token.
            </div>""", unsafe_allow_html=True)
            reset_email = st.text_input("📧 Registered Email", placeholder="your@email.com", key="reset_email")
            if st.button("📤 SEND RESET TOKEN", use_container_width=True):
                if reset_email in USERS:
                    import random, string
                    token = ''.join(random.choices(string.digits, k=6))
                    RESET_TOKENS[reset_email] = token
                    st.session_state.reset_email_val = reset_email
                    st.session_state.reset_step = 2
                    st.success(f"✅ Token sent! (Demo token: **{token}**)")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ Email not found in our system.")

        elif step == 2:
            token_input = st.text_input("🔢 Enter 6-digit Token", placeholder="123456", key="token_input")
            new_pw = st.text_input("🔐 New Password", type="password", key="new_pw")
            confirm_pw = st.text_input("🔐 Confirm Password", type="password", key="confirm_pw")

            if st.button("✅ RESET PASSWORD", use_container_width=True):
                email_val = st.session_state.get("reset_email_val", "")
                if RESET_TOKENS.get(email_val) == token_input:
                    if new_pw == confirm_pw and len(new_pw) >= 6:
                        USERS[email_val]["password"] = hash_password(new_pw)
                        del RESET_TOKENS[email_val]
                        st.session_state.reset_step = 1
                        st.success("✅ Password reset successfully! Please login.")
                        time.sleep(2)
                        st.session_state.page = "login"
                        st.rerun()
                    else:
                        st.error("❌ Passwords don't match or too short (min 6 chars).")
                else:
                    st.error("❌ Invalid token. Please try again.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← BACK TO LOGIN", use_container_width=True):
            st.session_state.reset_step = 1
            st.session_state.page = "login"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
def show_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 16px 0 24px;">
            <div style="font-family:'Orbitron',monospace; font-size:1.1rem; font-weight:900;
                background:linear-gradient(135deg,#00f5ff,#bf00ff);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:4px;">
                📡 TelePredict AI
            </div>
            <div style="color:rgba(0,245,255,0.4); font-size:0.65rem; letter-spacing:3px; font-family:'Exo 2',sans-serif;">
                CHURN INTELLIGENCE PLATFORM
            </div>
        </div>
        <div style="background:rgba(0,245,255,0.05); border:1px solid rgba(0,245,255,0.15);
            border-radius:10px; padding:12px 14px; margin-bottom:24px;">
            <div style="color:#00f5ff; font-size:0.75rem; font-family:'Exo 2',sans-serif; letter-spacing:2px;">
                LOGGED IN AS
            </div>
            <div style="color:white; font-weight:600; margin-top:4px; font-size:0.9rem;">
                {st.session_state.user_name}
            </div>
            <div style="color:rgba(0,245,255,0.4); font-size:0.7rem; margin-top:2px;">
                {st.session_state.user_email}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**NAVIGATION**", )
        st.markdown('<div style="border-bottom:1px solid rgba(0,245,255,0.15); margin-bottom:12px;"></div>', unsafe_allow_html=True)

        pages = {
            "dashboard": ("📊", "Dashboard"),
            "predict": ("🔮", "Churn Predictor"),
            "analytics": ("📈", "Analytics 3D"),
            "about": ("👥", "About Us"),
        }

        for page_key, (icon, label) in pages.items():
            active = "active" if st.session_state.page == page_key else ""
            if st.button(f"{icon}  {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div style="border-top:1px solid rgba(0,245,255,0.15); padding-top:16px;"></div>', unsafe_allow_html=True)
        if st.button("🚪  LOGOUT", use_container_width=True, key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_name = ""
            st.session_state.page = "login"
            st.rerun()

        st.markdown("""
        <div style="margin-top:24px; text-align:center;">
            <div style="color:rgba(0,245,255,0.2); font-size:0.65rem; letter-spacing:2px; font-family:'Exo 2',sans-serif;">
                v2.5.0 · © 2025 TelePredict AI
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def show_dashboard():
    st.markdown("""
    <div style="margin-bottom:32px;">
        <h1 style="margin-bottom:4px;">⚡ COMMAND CENTER</h1>
        <div style="color:rgba(0,245,255,0.5); font-family:'Exo 2',sans-serif; letter-spacing:3px; font-size:0.8rem;">
            REAL-TIME TELECOM CHURN INTELLIGENCE OVERVIEW
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI Cards
    kpis = [
        ("26.3%", "CHURN RATE", "📉"),
        ("73.7%", "RETENTION", "📈"),
        ("$2.4M", "REVENUE AT RISK", "⚠️"),
        ("8,432", "ACTIVE CUSTOMERS", "👥"),
    ]
    cols = st.columns(4)
    for col, (value, label, icon) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:2rem; margin-bottom:8px;">{icon}</div>
                <div class="value">{value}</div>
                <div class="label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Globe + Bar chart
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🌐 Network Topology")
        st.plotly_chart(make_3d_globe(), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Churn by Category")
        st.plotly_chart(make_3d_bar_chart(), use_container_width=True, config={"displayModeBar": False})

        st.markdown("<br>", unsafe_allow_html=True)
        # Risk gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=26.3,
            delta=dict(reference=22.0, valueformat=".1f", suffix="%",
                       increasing=dict(color="#ff006e"), decreasing=dict(color="#39ff14")),
            gauge=dict(
                axis=dict(range=[0, 50], tickcolor="#00f5ff"),
                bar=dict(color="rgba(0,245,255,0.8)"),
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,245,255,0.3)",
                steps=[
                    dict(range=[0,20], color="rgba(57,255,20,0.15)"),
                    dict(range=[20,35], color="rgba(255,165,0,0.15)"),
                    dict(range=[35,50], color="rgba(255,0,110,0.15)"),
                ],
                threshold=dict(line=dict(color="#ff006e", width=3), thickness=0.8, value=35)
            ),
            number=dict(suffix="%", font=dict(color="#00f5ff", family="Orbitron")),
            title=dict(text="Churn Rate Index", font=dict(color="#00f5ff", family="Rajdhani", size=14)),
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=200, margin=dict(l=20,r=20,t=30,b=10),
            font=dict(family='Rajdhani', color='#00f5ff'),
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Trend line
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📅 Churn Trend — Last 12 Months")
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    churn_vals = [24.1, 25.3, 23.8, 26.7, 28.1, 27.4, 25.9, 26.3, 24.8, 25.6, 26.1, 26.3]
    predict_vals = [None]*9 + [24.5, 23.1, 21.8]

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=months, y=churn_vals, name='Actual Churn',
        line=dict(color='#00f5ff', width=3),
        fill='tozeroy', fillcolor='rgba(0,245,255,0.05)',
        mode='lines+markers', marker=dict(size=8, color='#00f5ff'),
    ))
    fig_trend.add_trace(go.Scatter(
        x=months, y=predict_vals, name='AI Forecast',
        line=dict(color='#bf00ff', width=3, dash='dot'),
        mode='lines+markers', marker=dict(size=8, color='#bf00ff', symbol='diamond'),
    ))
    fig_trend.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(0,245,255,0.1)', tickfont=dict(color='#00f5ff')),
        yaxis=dict(gridcolor='rgba(0,245,255,0.1)', tickfont=dict(color='#00f5ff'), title='Churn Rate (%)'),
        legend=dict(font=dict(color='#00f5ff'), bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0,r=0,t=10,b=0), height=300,
        hovermode='x unified',
        font=dict(family='Rajdhani', color='#00f5ff'),
    )
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PREDICTOR
# ═══════════════════════════════════════════════════════════════════════════════
def show_predictor():
    clf, feature_cols = train_model()

    st.markdown("""
    <h1>🔮 CHURN PREDICTOR</h1>
    <div style="color:rgba(0,245,255,0.5); font-family:'Exo 2',sans-serif; letter-spacing:3px; font-size:0.8rem; margin-bottom:28px;">
        AI-POWERED CUSTOMER CHURN RISK ASSESSMENT ENGINE
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 👤 Customer Profile")

        gender = st.selectbox("Gender", ["Male", "Female"])
        senior = st.selectbox("Senior Citizen", [0, 1], format_func=lambda x: "Yes" if x==1 else "No")
        partner = st.selectbox("Has Partner", ["Yes", "No"])
        dependents = st.selectbox("Has Dependents", ["Yes", "No"])
        tenure = st.slider("Tenure (months)", 0, 72, 12)
        phone = st.selectbox("Phone Service", ["Yes", "No"])
        multiline = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"])
        internet = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
        billing = st.selectbox("Paperless Billing", ["Yes", "No"])
        payment = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
        monthly = st.slider("Monthly Charges ($)", 18.0, 120.0, 65.0)
        total = st.slider("Total Charges ($)", 0.0, 9000.0, float(monthly * tenure))

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        le = LabelEncoder()

        def encode(col, vals, val):
            le.fit(vals)
            return le.transform([val])[0]

        input_data = {
            'gender': encode('gender', ['Female','Male'], gender),
            'SeniorCitizen': senior,
            'Partner': encode('Partner', ['No','Yes'], partner),
            'Dependents': encode('Dependents', ['No','Yes'], dependents),
            'tenure': tenure,
            'PhoneService': encode('PhoneService', ['No','Yes'], phone),
            'MultipleLines': encode('MultipleLines', ['No','No phone service','Yes'], multiline),
            'InternetService': encode('InternetService', ['DSL','Fiber optic','No'], internet),
            'Contract': encode('Contract', ['Month-to-month','One year','Two year'], contract),
            'PaperlessBilling': encode('PB', ['No','Yes'], billing),
            'PaymentMethod': encode('PM', ['Bank transfer (automatic)','Credit card (automatic)','Electronic check','Mailed check'], payment),
            'MonthlyCharges': monthly,
            'TotalCharges': total,
        }

        df_input = pd.DataFrame([input_data])
        proba = clf.predict_proba(df_input)[0]
        churn_prob = proba[1] * 100

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🎯 Prediction Result")

        # Gauge
        fig_pred = go.Figure(go.Indicator(
            mode="gauge+number",
            value=churn_prob,
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor="#00f5ff"),
                bar=dict(color="rgba(255,0,110,0.9)" if churn_prob > 50 else "rgba(0,245,255,0.9)"),
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,245,255,0.3)",
                steps=[
                    dict(range=[0,30], color="rgba(57,255,20,0.15)"),
                    dict(range=[30,60], color="rgba(255,165,0,0.15)"),
                    dict(range=[60,100], color="rgba(255,0,110,0.15)"),
                ],
            ),
            number=dict(suffix="%", font=dict(color="#00f5ff", family="Orbitron", size=36)),
            title=dict(text="Churn Probability", font=dict(color="#00f5ff", family="Orbitron", size=16)),
        ))
        fig_pred.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=280, margin=dict(l=30,r=30,t=40,b=10),
            font=dict(family='Rajdhani', color='#00f5ff'),
        )
        st.plotly_chart(fig_pred, use_container_width=True, config={"displayModeBar": False})

        if churn_prob > 65:
            st.markdown(f'<div class="churn-high">🔴 HIGH CHURN RISK</div>', unsafe_allow_html=True)
            risk_level, risk_color = "HIGH", "#ff006e"
        elif churn_prob > 35:
            st.markdown(f'<div style="font-family:Orbitron,monospace;font-size:1.6rem;color:#ffa500;text-align:center;text-shadow:0 0 20px rgba(255,165,0,0.6);">🟡 MODERATE RISK</div>', unsafe_allow_html=True)
            risk_level, risk_color = "MODERATE", "#ffa500"
        else:
            st.markdown(f'<div class="churn-low">🟢 LOW CHURN RISK</div>', unsafe_allow_html=True)
            risk_level, risk_color = "LOW", "#39ff14"

        st.markdown("<br>", unsafe_allow_html=True)

        # Risk factors
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,245,255,0.15); border-radius:10px; padding:16px; margin-top:12px;">
            <div style="color:#00f5ff; font-family:'Orbitron',monospace; font-size:0.85rem; letter-spacing:2px; margin-bottom:12px;">
                ⚡ KEY RISK FACTORS
            </div>
        """, unsafe_allow_html=True)

        risks = []
        if contract == "Month-to-month": risks.append(("📋 Month-to-month contract", "HIGH"))
        if internet == "Fiber optic": risks.append(("🌐 Fiber optic service", "MODERATE"))
        if tenure < 12: risks.append(("⏱️ Short tenure (<12mo)", "HIGH"))
        if monthly > 80: risks.append(("💰 High monthly charges", "MODERATE"))
        if not risks: risks.append(("✅ No significant risk factors", "LOW"))

        for factor, level in risks:
            color = "#ff006e" if level=="HIGH" else "#ffa500" if level=="MODERATE" else "#39ff14"
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid rgba(0,245,255,0.08);">
                <span style="color:rgba(255,255,255,0.8); font-size:0.85rem;">{factor}</span>
                <span style="color:{color}; font-size:0.75rem; font-weight:700;">{level}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Recommendation
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba({','.join(['255,0,110' if risk_level=='HIGH' else '255,165,0' if risk_level=='MODERATE' else '57,255,20'])},0.08);
            border:1px solid rgba({','.join(['255,0,110' if risk_level=='HIGH' else '255,165,0' if risk_level=='MODERATE' else '57,255,20'])},0.3);
            border-radius:10px; padding:16px;">
            <div style="color:{risk_color}; font-family:'Orbitron',monospace; font-size:0.8rem; letter-spacing:2px; margin-bottom:8px;">
                💡 AI RECOMMENDATION
            </div>
            <div style="color:rgba(255,255,255,0.8); font-size:0.88rem; line-height:1.6;">
                {'Immediate intervention required. Offer loyalty discount, contract upgrade incentive, and dedicated account manager.' if risk_level=='HIGH' else
                'Monitor closely. Consider proactive outreach with personalized offers and service improvement plans.' if risk_level=='MODERATE' else
                'Customer appears stable. Continue standard engagement and periodic satisfaction surveys.'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS 3D
# ═══════════════════════════════════════════════════════════════════════════════
def show_analytics():
    st.markdown("""
    <h1>📈 3D ANALYTICS LAB</h1>
    <div style="color:rgba(0,245,255,0.5); font-family:'Exo 2',sans-serif; letter-spacing:3px; font-size:0.8rem; margin-bottom:28px;">
        MULTI-DIMENSIONAL CUSTOMER BEHAVIOR VISUALIZATION
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🌌 3D Customer Segmentation — Churn vs Retain")
    st.markdown('<div style="color:rgba(0,245,255,0.5); font-size:0.85rem; margin-bottom:12px;">Rotate · Zoom · Hover for details</div>', unsafe_allow_html=True)
    st.plotly_chart(make_3d_churn_scatter(), use_container_width=True, config={"displayModeBar": True})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🕸️ Churn Factor Radar")
        categories = ['Contract Risk', 'Service Issues', 'Billing', 'Usage Patterns', 'Support Tickets', 'Tenure Risk']
        vals = [85, 62, 48, 38, 71, 55]
        vals += vals[:1]
        cats = categories + [categories[0]]
        fig_radar = go.Figure(go.Scatterpolar(
            r=vals, theta=cats, fill='toself',
            fillcolor='rgba(0,245,255,0.12)',
            line=dict(color='#00f5ff', width=2),
            marker=dict(size=8, color='#00f5ff'),
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,100], gridcolor='rgba(0,245,255,0.2)', tickfont=dict(color='#00f5ff')),
                angularaxis=dict(gridcolor='rgba(0,245,255,0.2)', tickfont=dict(color='#00f5ff')),
                bgcolor='rgba(0,0,0,0)',
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Rajdhani', color='#00f5ff'),
            margin=dict(l=20,r=20,t=20,b=20), height=320,
            showlegend=False,
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Churn by Contract Type")
        contracts = ['Month-to-Month', 'One Year', 'Two Year']
        churned = [42.7, 11.3, 2.8]
        retained = [57.3, 88.7, 97.2]
        fig_pie = go.Figure()
        fig_pie.add_trace(go.Bar(name='Churned', x=contracts, y=churned, marker_color='#ff006e', marker_opacity=0.85))
        fig_pie.add_trace(go.Bar(name='Retained', x=contracts, y=retained, marker_color='#00f5ff', marker_opacity=0.65))
        fig_pie.update_layout(
            barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(color='#00f5ff'), gridcolor='rgba(0,245,255,0.1)'),
            yaxis=dict(tickfont=dict(color='#00f5ff'), gridcolor='rgba(0,245,255,0.1)', title='%'),
            legend=dict(font=dict(color='#00f5ff'), bgcolor='rgba(0,0,0,0)'),
            font=dict(family='Rajdhani', color='#00f5ff'),
            margin=dict(l=0,r=0,t=10,b=0), height=320,
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Heatmap
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🔥 Churn Heatmap — Tenure × Monthly Charges")
    np.random.seed(99)
    tenure_bins = list(range(0, 73, 12))
    charge_bins = [18, 35, 50, 65, 80, 95, 120]
    z = np.array([
        [55, 42, 35, 28, 20, 12],
        [48, 38, 28, 22, 16, 10],
        [38, 30, 22, 16, 12, 8],
        [28, 22, 16, 11, 8, 5],
        [20, 16, 11, 8, 5, 3],
        [14, 10, 8, 5, 3, 2],
    ])
    fig_heat = go.Figure(data=go.Heatmap(
        z=z,
        x=['$18-35','$35-50','$50-65','$65-80','$80-95','$95-120'],
        y=['0-12mo','12-24mo','24-36mo','36-48mo','48-60mo','60-72mo'],
        colorscale=[[0,'rgba(57,255,20,0.6)'],[0.5,'rgba(255,165,0,0.8)'],[1,'rgba(255,0,110,0.95)']],
        showscale=True,
        colorbar=dict(title='Churn %', tickfont=dict(color='#00f5ff'), title_font=dict(color='#00f5ff')),
        hovertemplate='Tenure: %{y}<br>Charges: %{x}<br>Churn Rate: %{z}%<extra></extra>',
    ))
    fig_heat.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Monthly Charges', tickfont=dict(color='#00f5ff'), title_font=dict(color='#00f5ff')),
        yaxis=dict(title='Tenure', tickfont=dict(color='#00f5ff'), title_font=dict(color='#00f5ff')),
        font=dict(family='Rajdhani', color='#00f5ff'),
        margin=dict(l=0,r=0,t=10,b=0), height=340,
    )
    st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT US
# ═══════════════════════════════════════════════════════════════════════════════
def show_about():
    st.markdown("""
    <h1>👥 ABOUT US</h1>
    <div style="color:rgba(0,245,255,0.5); font-family:'Exo 2',sans-serif; letter-spacing:3px; font-size:0.8rem; margin-bottom:28px;">
        THE TEAM BEHIND TELEPREDICT AI
    </div>
    """, unsafe_allow_html=True)

    # Mission
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown("""
        <div style="font-family:'Orbitron',monospace; font-size:1.4rem; color:#00f5ff; margin-bottom:16px; letter-spacing:2px;">
            OUR MISSION
        </div>
        <div style="color:rgba(255,255,255,0.85); font-size:1.05rem; line-height:1.8; font-family:'Rajdhani',sans-serif;">
            TelePredict AI was built to solve one of telecom's most costly challenges — customer churn.
            By combining machine learning, real-time analytics, and intuitive design, we give telecom operators
            the power to predict, prevent, and proactively address customer attrition before it happens.
        </div>
        <div style="margin-top:20px; color:rgba(0,245,255,0.7); font-size:0.95rem; line-height:1.8;">
            Our platform processes millions of data points to identify at-risk customers with 94.2% accuracy,
            enabling targeted retention campaigns that save an average of <strong style="color:#00f5ff;">$3.2M annually</strong> per deployment.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        # 3D sphere animation for about page
        theta = np.linspace(0, 4*np.pi, 200)
        r = np.sin(3*theta)
        x = r*np.cos(theta)
        y = r*np.sin(theta)
        z = np.cos(3*theta)
        fig_about = go.Figure(go.Scatter3d(
            x=x, y=y, z=z, mode='lines',
            line=dict(color=np.linspace(0,1,200), colorscale=[[0,'#00f5ff'],[0.5,'#bf00ff'],[1,'#ff006e']], width=4),
        ))
        fig_about.update_layout(
            scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='rgba(0,0,0,0)'),
            paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=0,b=0), height=260,
        )
        st.plotly_chart(fig_about, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats
    st.markdown("""
    <div style="font-family:'Orbitron',monospace; color:#00f5ff; font-size:1.1rem; letter-spacing:3px; margin-bottom:16px;">
        PLATFORM IMPACT
    </div>
    """, unsafe_allow_html=True)
    stats = [("94.2%", "Model Accuracy"), ("$3.2M", "Avg Annual Savings"), ("150+", "Telecom Partners"), ("8.4M", "Customers Protected")]
    cols = st.columns(4)
    for col, (val, lbl) in zip(cols, stats):
        with col:
            st.markdown(f'<div class="metric-card"><div class="value">{val}</div><div class="label">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Team
    st.markdown("""
    <div style="font-family:'Orbitron',monospace; color:#00f5ff; font-size:1.1rem; letter-spacing:3px; margin-bottom:20px;">
        CORE TEAM
    </div>
    """, unsafe_allow_html=True)

    team = [
        ("🧠", "Dr. Aisha Patel", "Chief AI Officer", "PhD Stanford AI Lab. 12+ years in predictive modeling and telecom analytics. Ex-Google Brain researcher."),
        ("📡", "Marcus Chen", "CTO & Co-Founder", "15+ years building scalable ML infrastructure. Former VP Engineering at AT&T Data Science division."),
        ("📊", "Sofia Reyes", "Head of Data Science", "Kaggle Grandmaster. Specializes in churn modeling, NLP, and customer lifetime value prediction."),
        ("🎨", "James Okonkwo", "Lead Product Engineer", "Full-stack ML engineer with expertise in Streamlit, FastAPI, and real-time data pipelines."),
    ]

    cols = st.columns(4)
    for col, (icon, name, role, bio) in zip(cols, team):
        with col:
            st.markdown(f"""
            <div class="team-card">
                <div class="avatar">{icon}</div>
                <div style="font-family:'Orbitron',monospace; color:#00f5ff; font-size:0.85rem; font-weight:700; margin-bottom:6px;">{name}</div>
                <div style="color:#bf00ff; font-size:0.75rem; font-family:'Exo 2',sans-serif; letter-spacing:2px; text-transform:uppercase; margin-bottom:12px;">{role}</div>
                <div style="color:rgba(255,255,255,0.7); font-size:0.8rem; line-height:1.6;">{bio}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tech Stack
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Orbitron',monospace; color:#00f5ff; font-size:1.1rem; letter-spacing:3px; margin-bottom:20px;">
        ⚙️ TECHNOLOGY STACK
    </div>
    """, unsafe_allow_html=True)

    tech = [
        ("🐍", "Python 3.11", "Core Language"),
        ("🎯", "Streamlit", "UI Framework"),
        ("🤖", "Scikit-learn", "ML Engine"),
        ("📊", "Plotly", "3D Visualization"),
        ("🐼", "Pandas", "Data Processing"),
        ("☁️", "AWS", "Cloud Infrastructure"),
    ]
    cols = st.columns(6)
    for col, (icon, name, desc) in zip(cols, tech):
        with col:
            st.markdown(f"""
            <div style="text-align:center; padding:16px 8px; background:rgba(0,245,255,0.04);
                border:1px solid rgba(0,245,255,0.12); border-radius:10px;">
                <div style="font-size:1.8rem; margin-bottom:8px;">{icon}</div>
                <div style="color:#00f5ff; font-size:0.8rem; font-weight:700; font-family:'Orbitron',monospace;">{name}</div>
                <div style="color:rgba(0,245,255,0.4); font-size:0.7rem; margin-top:4px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    # Contact
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Orbitron',monospace; color:#00f5ff; font-size:1.1rem; letter-spacing:3px; margin-bottom:16px;">
        📬 GET IN TOUCH
    </div>
    <div style="display:flex; gap:32px; flex-wrap:wrap;">
        <div>
            <div style="color:rgba(0,245,255,0.5); font-size:0.7rem; letter-spacing:3px; font-family:'Exo 2',sans-serif;">EMAIL</div>
            <div style="color:white; margin-top:4px;">contact@telepredict.ai</div>
        </div>
        <div>
            <div style="color:rgba(0,245,255,0.5); font-size:0.7rem; letter-spacing:3px; font-family:'Exo 2',sans-serif;">WEBSITE</div>
            <div style="color:#00f5ff; margin-top:4px;">www.telepredict.ai</div>
        </div>
        <div>
            <div style="color:rgba(0,245,255,0.5); font-size:0.7rem; letter-spacing:3px; font-family:'Exo 2',sans-serif;">LOCATION</div>
            <div style="color:white; margin-top:4px;">San Francisco, CA · London, UK · Singapore</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    if st.session_state.page == "forgot_password":
        show_forgot_password()
    else:
        show_login()
else:
    show_sidebar()
    page = st.session_state.page
    if page == "dashboard":
        show_dashboard()
    elif page == "predict":
        show_predictor()
    elif page == "analytics":
        show_analytics()
    elif page == "about":
        show_about()
    else:
        show_dashboard()
           if st.button("Register"):
    users[username] = password   # ✔ correct indent
            st.success("Account created ✅ Now login")
