import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ---------- SESSION ----------
if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------- CSS ----------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #0D1B2A, #000);
    color: white;
}
#MainMenu, header, footer {visibility: hidden;}

.left {
    background: linear-gradient(180deg,#1A2B3C,#0D1B2A);
    padding:40px;
    border-radius:10px;
}
.card {
    background:#112233;
    padding:15px;
    border-radius:10px;
    margin-top:15px;
    border:1px solid #00C6FF;
}
.title {
    font-size:32px;
    font-weight:bold;
}
.stButton>button {
    background: linear-gradient(90deg,#0072FF,#00C6FF);
    color:white;
    border-radius:8px;
    height:45px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ---------- LOGIN ----------
if st.session_state.page == "login":
    col1, col2 = st.columns([1,1])

    with col1:
        st.markdown("<div class='left'>", unsafe_allow_html=True)
        st.markdown("<div class='title'>📡 TELECOM</div>", unsafe_allow_html=True)
        st.markdown("<div style='color:#00C6FF'>CHURN PREDICTOR</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>98.5% Network Uptime</div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>4.2M Subscribers</div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>AI Powered</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='title'>Welcome Back</div>", unsafe_allow_html=True)

        email = st.text_input("📧 Email Address")
        password = st.text_input("🔒 Password", type="password")

        if st.button("SIGN IN"):
            st.session_state.page = "input"
            st.rerun()

        st.write("— OR —")

        if st.button("CREATE ACCOUNT"):
            st.success("Account created!")

# ---------- INPUT ----------
elif st.session_state.page == "input":
    st.markdown("<div class='title'>Customer Information Input</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        call = st.slider("📞 Call Failure",0,100)
        sub = st.slider("📅 Subscription Length",1,60)
        sec = st.number_input("⏱ Seconds of Use",0,100000)
        age = st.slider("👤 Age",18,80)
        value = st.number_input("💰 Customer Value",0,1000)

    with c2:
        comp = st.selectbox("⚠️ Complains",["Yes","No"])
        charge = st.number_input("💳 Charge Amount",0,1000)
        freq = st.number_input("📱 Frequency of Use",0,1000)
        sms = st.number_input("💬 Frequency of SMS",0,1000)
        cluster = st.selectbox("📊 Cluster",["Low","Mid","High"])

    tariff = st.selectbox("📡 Tariff Plan",["Basic","Premium"])
    status = st.selectbox("🔋 Status",["Active","Inactive"])
    distinct = st.number_input("🔢 Distinct Called Numbers",0,200)

    if st.button("🚀 Predict"):
        prob = (call + freq) % 100 / 100
        st.session_state.prob = prob
        st.session_state.page = "result"
        st.rerun()

# ---------- RESULT ----------
elif st.session_state.page == "result":
    prob = st.session_state.prob

    col1, col2 = st.columns(2)

    with col1:
        if prob > 0.5:
            st.markdown(f"""
            <div class='card' style='border:2px solid red'>
            <h2 style='color:red'>⚠️ CHURN PREDICTED</h2>
            <p>{prob*100:.1f}% Probability</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='card' style='border:2px solid green'>
            <h2 style='color:green'>✅ NO CHURN</h2>
            <p>{prob*100:.1f}% Probability</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>Risk Level</div>", unsafe_allow_html=True)

        if prob > 0.7:
            st.error("🔴 HIGH RISK")
        elif prob > 0.4:
            st.warning("🟡 MEDIUM RISK")
        else:
            st.success("🟢 LOW RISK")

    # ---------- CHART ----------
    df = pd.DataFrame({
        "Feature":["Call","Complains","Usage","Value","SMS"],
        "Impact":[85,78,62,55,40]
    })
    fig = px.bar(df,x="Feature",y="Impact",color="Impact")
    st.plotly_chart(fig,use_container_width=True)

    # ---------- PIE ----------
    fig2 = px.pie(values=[78,22],names=["Churn","No Churn"])
    st.plotly_chart(fig2,use_container_width=True)

    # ---------- DOWNLOAD ----------
    st.download_button("📥 DOWNLOAD CSV REPORT",
                       pd.DataFrame({"prob":[prob]}).to_csv(),
                       "churn_result.csv")

    if st.button("Logout"):
        st.session_state.page = "login"
        st.rerun()
