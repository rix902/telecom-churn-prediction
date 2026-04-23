import streamlit as st
import pandas as pd

st.set_page_config(page_title="Telecom Churn", layout="wide")

# ---------- SESSION ----------
if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------- LOGIN PAGE ----------
if st.session_state.page == "login":
    st.title("📡 Telecom Churn Predictor")
    st.subheader("Login / Register")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email and password:
            st.session_state.page = "input"
            st.rerun()
        else:
            st.error("Enter credentials")

    st.markdown("---")

    if st.button("Create Account"):
        st.success("Dummy account created (for demo)")

# ---------- INPUT PAGE ----------
elif st.session_state.page == "input":
    st.title("📋 Customer Information Input")

    col1, col2 = st.columns(2)

    with col1:
        call_failure = st.slider("Call Failure", 0, 100)
        sub_length = st.slider("Subscription Length", 1, 60)
        seconds = st.number_input("Seconds of Use", 0, 100000)
        age = st.slider("Age", 18, 80)
        customer_value = st.number_input("Customer Value", 0, 1000)

    with col2:
        complains = st.selectbox("Complains", ["Yes", "No"])
        charge = st.number_input("Charge Amount", 0, 1000)
        freq_use = st.number_input("Frequency of Use", 0, 1000)
        freq_sms = st.number_input("Frequency of SMS", 0, 1000)
        cluster = st.selectbox("Cluster", ["Low", "Mid", "High"])

    tariff = st.selectbox("Tariff Plan", ["Basic", "Premium"])
    status = st.selectbox("Status", ["Active", "Inactive"])
    distinct = st.number_input("Distinct Called Numbers", 0, 200)

    if st.button("Predict"):
        # Dummy prediction logic
        prob = (call_failure + freq_use) % 100 / 100

        st.session_state.result = {
            "prob": prob,
            "prediction": "CHURN" if prob > 0.5 else "NO CHURN"
        }

        st.session_state.data = {
            "Call Failure": call_failure,
            "Subscription Length": sub_length,
            "Seconds": seconds,
            "Age": age,
            "Customer Value": customer_value,
            "Complains": complains,
            "Charge": charge,
            "Frequency": freq_use,
            "SMS": freq_sms,
            "Cluster": cluster,
            "Tariff": tariff,
            "Status": status,
            "Distinct": distinct
        }

        st.session_state.page = "result"
        st.rerun()

# ---------- RESULT PAGE ----------
elif st.session_state.page == "result":
    st.title("📊 Prediction Result")

    prob = st.session_state.result["prob"]
    prediction = st.session_state.result["prediction"]

    if prediction == "CHURN":
        st.error(f"⚠️ CHURN PREDICTED ({prob*100:.1f}%)")
    else:
        st.success(f"✅ NO CHURN ({prob*100:.1f}%)")

    st.subheader("Risk Level")
    if prob > 0.7:
        st.warning("High Risk")
    elif prob > 0.4:
        st.info("Medium Risk")
    else:
        st.success("Low Risk")

    st.subheader("Input Summary")
    df = pd.DataFrame([st.session_state.data])
    st.dataframe(df)

    # ---------- CSV DOWNLOAD ----------
    csv = df.to_csv(index=False)

    st.download_button(
        "Download CSV",
        csv,
        "churn_result.csv",
        "text/csv"
    )

    if st.button("Logout"):
        st.session_state.page = "login"
        st.rerun()
