import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ---------- STATE ----------
if "page" not in st.session_state:
    st.session_state.page = 1

# ---------- CSS (PPT STYLE) ----------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background:#0D1B2A;
    color:white;
}
.card {
    background:#112233;
    padding:15px;
    border-radius:10px;
    border:1px solid #00C6FF;
    margin-bottom:10px;
}
.title {
    font-size:28px;
    font-weight:bold;
}
.btn {
    background: linear-gradient(90deg,#0072FF,#00C6FF);
    padding:10px;
    text-align:center;
    border-radius:8px;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 🔹 SLIDE 1 → LOGIN
# =========================================================
if st.session_state.page == 1:
    col1, col2 = st.columns([1,1])

    with col1:
        st.markdown("<div class='title'>TELECOM</div>", unsafe_allow_html=True)
        st.markdown("<div style='color:#00C6FF'>CHURN PREDICTOR</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>98.5% Network Uptime</div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>4.2M Subscribers</div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>AI Powered</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='title'>Welcome Back</div>", unsafe_allow_html=True)

        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        if st.button("SIGN IN"):
            st.session_state.page = 2
            st.rerun()

        st.write("— OR —")

        if st.button("CREATE ACCOUNT"):
            st.success("Account Created")

# =========================================================
# 🔹 SLIDE 2 → INPUT FORM
# =========================================================
elif st.session_state.page == 2:
    st.markdown("<div class='title'>Customer Information Input</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        call = st.slider("Call Failure",0,100)
        sub = st.slider("Subscription Length",1,60)
        sec = st.number_input("Seconds of Use",0,100000)
        age = st.slider("Age",18,80)
        value = st.number_input("Customer Value",0,1000)

    with c2:
        comp = st.selectbox("Complains",["Yes","No"])
        charge = st.number_input("Charge Amount",0,1000)
        freq = st.number_input("Frequency of Use",0,1000)
        sms = st.number_input("Frequency of SMS",0,1000)
        cluster = st.selectbox("Cluster",["Low","Mid","High"])

    tariff = st.selectbox("Tariff Plan",["Basic","Premium"])
    status = st.selectbox("Status",["Active","Inactive"])
    distinct = st.number_input("Distinct Called Numbers",0,200)

    if st.button("NEXT → PREDICT"):
        prob = (call + freq) % 100 / 100
        st.session_state.prob = prob
        st.session_state.page = 3
        st.rerun()

# =========================================================
# 🔹 SLIDE 3 → RESULT + AI
# =========================================================
elif st.session_state.page == 3:
    prob = st.session_state.prob

    col1, col2 = st.columns(2)

    with col1:
        if prob > 0.5:
            st.markdown(f"""
            <div class='card' style='border:2px solid red'>
            <h2 style='color:red'>CHURN PREDICTED</h2>
            <p>{prob*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='card' style='border:2px solid green'>
            <h2 style='color:green'>NO CHURN</h2>
            <p>{prob*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>Risk Analysis</div>", unsafe_allow_html=True)

        if prob > 0.7:
            st.error("HIGH RISK")
        elif prob > 0.4:
            st.warning("MEDIUM RISK")
        else:
            st.success("LOW RISK")

    # chart same like ppt
    df = pd.DataFrame({
        "Feature":["Call Failure","Complains","Sub Length","Value","Usage"],
        "Impact":[85,78,62,55,40]
    })

    fig = px.bar(df,x="Feature",y="Impact",color="Impact")
    st.plotly_chart(fig,use_container_width=True)

    fig2 = px.pie(values=[32,45,23],names=["High","Medium","Low"])
    st.plotly_chart(fig2,use_container_width=True)

    if st.button("NEXT → DOWNLOAD"):
        st.session_state.page = 4
        st.rerun()

# =========================================================
# 🔹 SLIDE 4 → DOWNLOAD
# =========================================================
elif st.session_state.page == 4:
    st.markdown("<div class='title'>Download Results</div>", unsafe_allow_html=True)

    df = pd.DataFrame({
        "Prediction":["Churn"],
        "Probability":[st.session_state.prob]
    })

    st.dataframe(df)

    st.download_button("DOWNLOAD CSV",df.to_csv(),"churn.csv")

    if st.button("NEXT → LOGOUT"):
        st.session_state.page = 5
        st.rerun()

# =========================================================
# 🔹 SLIDE 5 → LOGOUT
# =========================================================
elif st.session_state.page == 5:
    st.markdown("<div class='title'>Session Complete</div>", unsafe_allow_html=True)

    st.success("Your prediction results have been saved.")

    st.markdown("<div class='card'>Predictions Run: 1</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>Churn Probability: {st.session_state.prob:.2f}</div>", unsafe_allow_html=True)

    if st.button("LOGOUT"):
        st.session_state.page = 1
        st.rerun()
