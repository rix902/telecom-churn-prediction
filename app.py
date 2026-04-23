import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
body {
    background-color: #0D1B2A;
}

.main {
    background-color: #0D1B2A;
}

.card {
    background-color: #112233;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #00C6FF;
    margin-bottom: 10px;
}

.title {
    color: white;
    font-size: 28px;
    font-weight: bold;
}

.subtitle {
    color: #00C6FF;
}

.stButton>button {
    background: linear-gradient(90deg, #0072FF, #00C6FF);
    color: white;
    border-radius: 8px;
    height: 45px;
    font-weight: bold;
}

input, select {
    background-color: #112233 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------- LOGIN ----------
if st.session_state.page == "login":
    col1, col2 = st.columns([1,1])

    with col1:
        st.markdown("<div class='title'>📡 TELECOM</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>CHURN PREDICTOR</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>98.5% Network Uptime</div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>4.2M Subscribers</div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>AI Powered</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='title'>Welcome Back</div>", unsafe_allow_html=True)

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("SIGN IN"):
            st.session_state.page = "input"
            st.rerun()

        st.write("— OR —")

        if st.button("CREATE ACCOUNT"):
            st.success("Account created!")

# ---------- INPUT ----------
elif st.session_state.page == "input":
    st.markdown("<div class='title'>Customer Information Input</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        call_failure = st.slider("📞 Call Failure", 0, 100)
        sub_length = st.slider("📅 Subscription Length", 1, 60)
        seconds = st.number_input("⏱ Seconds of Use", 0, 100000)
        age = st.slider("👤 Age", 18, 80)
        value = st.number_input("💰 Customer Value", 0, 1000)

    with col2:
        complains = st.selectbox("⚠️ Complains", ["Yes", "No"])
        charge = st.number_input("💳 Charge Amount", 0, 1000)
        freq = st.number_input("📱 Frequency of Use", 0, 1000)
        sms = st.number_input("💬 Frequency of SMS", 0, 1000)
        cluster = st.selectbox("📊 Cluster", ["Low", "Mid", "High"])

    tariff = st.selectbox("📡 Tariff Plan", ["Basic", "Premium"])
    status = st.selectbox("🔋 Status", ["Active", "Inactive"])
    distinct = st.number_input("🔢 Distinct Numbers", 0, 200)

    if st.button("🚀 Predict"):
        prob = (call_failure + freq) % 100 / 100

        st.session_state.result = prob
        st.session_state.page = "result"
        st.rerun()

# ---------- RESULT ----------
elif st.session_state.page == "result":
    st.markdown("<div class='title'>Prediction Result</div>", unsafe_allow_html=True)

    prob = st.session_state.result

    if prob > 0.5:
        st.error(f"⚠️ CHURN PREDICTED ({prob*100:.1f}%)")
    else:
        st.success(f"✅ NO CHURN ({prob*100:.1f}%)")

    st.subheader("Risk Level")

    if prob > 0.7:
        st.warning("HIGH RISK")
    elif prob > 0.4:
        st.info("MEDIUM RISK")
    else:
        st.success("LOW RISK")

    # chart
    st.bar_chart({"Impact":[85,78,62,55,40]})

    # CSV
    df = pd.DataFrame({"Probability":[prob]})
    st.download_button("📥 Download CSV", df.to_csv(), "result.csv")

    if st.button("Logout"):
        st.session_state.page = "login"
        st.rerun()
