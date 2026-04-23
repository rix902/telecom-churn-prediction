import streamlit as st
import pandas as pd
import joblib

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Churn Predictor", layout="centered")

# -------------------------------
# CSS THEME (FIXED + READABLE)
# -------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

h1, h2, h3 {
    color: white;
    text-align: center;
}

label {
    color: white !important;
}

input, textarea {
    background-color: white !important;
    color: black !important;
    border-radius: 8px;
}

div[data-baseweb="select"] {
    background-color: white !important;
}

div[data-baseweb="select"] * {
    color: black !important;
}

.stButton>button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 10px;
    height: 45px;
    width: 100%;
}

.stDownloadButton>button {
    background: linear-gradient(90deg, #ff512f, #dd2476);
    color: white;
    border-radius: 10px;
    height: 45px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Load Model
# -------------------------------
model = joblib.load("churn_model.pkl")
model_columns = joblib.load("model_columns.pkl")

# -------------------------------
# Title
# -------------------------------
st.title("📊 Telecom Customer Churn Prediction")

st.markdown("""
<div style='text-align:center;'>
<h3>📡 Smart Telecom Analytics System</h3>
<p>AI-powered churn prediction</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# -------------------------------
# AI Explanation Function
# -------------------------------
def generate_explanation(input_df, probability):

    reasons = []

    if input_df['Complains'].values[0] == 1:
        reasons.append("Customer has raised complaints")

    if input_df['Subscription  Length'].values[0] < 12:
        reasons.append("Short subscription duration")

    if input_df['Frequency of use'].values[0] < 10:
        reasons.append("Low usage frequency")

    if input_df['Customer Value'].values[0] < 200:
        reasons.append("Low customer value")

    if input_df['Call  Failure'].values[0] > 5:
        reasons.append("High call failure rate")

    if probability > 0.7:
        risk = "🔴 High Risk"
    elif probability > 0.4:
        risk = "🟡 Medium Risk"
    else:
        risk = "🟢 Low Risk"

    return reasons, risk

# -------------------------------
# Input Form
# -------------------------------
with st.form("form"):

    col1, col2 = st.columns(2)

    with col1:
        call_failure = st.number_input("Call Failure", 0, 100)
        subscription_length = st.number_input("Subscription Length", 1, 60)
        seconds_of_use = st.number_input("Seconds of Use", 0, 100000)
        age = st.number_input("Age", 18, 80)
        customer_value = st.number_input("Customer Value", 0, 1000)

    with col2:
        complains = st.selectbox("Complains", ["No", "Yes"])
        charge_amount = st.number_input("Charge Amount", 0, 1000)
        frequency_of_use = st.number_input("Frequency of Use", 0, 1000)
        frequency_sms = st.number_input("Frequency of SMS", 0, 1000)
        cluster = st.selectbox("Cluster", ["Low", "Medium", "High"])

    tariff_plan = st.selectbox("Tariff Plan", ["Basic", "Premium"])
    status = st.selectbox("Status", ["Inactive", "Active"])
    distinct_numbers = st.number_input("Distinct Called Numbers", 0, 200)

    submit = st.form_submit_button("🔍 Predict")

# -------------------------------
# Prediction
# -------------------------------
if submit:

    # Convert text → numeric
    complains_val = 1 if complains == "Yes" else 0
    tariff_val = 1 if tariff_plan == "Premium" else 0
    status_val = 1 if status == "Active" else 0

    cluster_map = {"Low": 0, "Medium": 1, "High": 2}
    cluster_val = cluster_map[cluster]

    input_data = {
        'Call  Failure': call_failure,
        'Complains': complains_val,
        'Subscription  Length': subscription_length,
        'Charge  Amount': charge_amount,
        'Seconds of Use': seconds_of_use,
        'Frequency of use': frequency_of_use,
        'Frequency of SMS': frequency_sms,
        'Distinct Called Numbers': distinct_numbers,
        'Age': age,
        'Tariff Plan': tariff_val,
        'Status': status_val,
        'Customer Value': customer_value,
        'Cluster': cluster_val
    }

    input_df = pd.DataFrame([input_data])

    final_df = pd.DataFrame(columns=model_columns)

    for col in final_df.columns:
        final_df[col] = 0

    for col in input_df.columns:
        if col in final_df.columns:
            final_df[col] = input_df[col]

    prediction = model.predict(final_df)[0]
    probability = model.predict_proba(final_df)[0][1]

    # -------------------------------
    # Result
    # -------------------------------
    st.markdown("---")
    st.subheader("🎯 Prediction Result")

    if prediction == 1:
        st.error("⚠ Customer will CHURN")
        result_text = "Churn"
    else:
        st.success("✅ Customer will NOT churn")
        result_text = "Not Churn"

    st.write(f"**Churn Probability:** {probability:.2f}")

    # -------------------------------
    # AI Explanation
    # -------------------------------
    st.markdown("---")
    st.subheader("🤖 AI Explanation")

    reasons, risk = generate_explanation(input_df, probability)

    st.write(f"### 📊 Risk Level: {risk}")

    if len(reasons) > 0:
        st.write("### 🔍 Key Reasons:")
        for r in reasons:
            st.write(f"- {r}")
    else:
        st.write("Customer behavior looks stable")

    # -------------------------------
    # Download Result
    # -------------------------------
    result_df = input_df.copy()
    result_df["Prediction"] = result_text
    result_df["Probability"] = probability

    csv = result_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "📥 Download Result",
        data=csv,
        file_name="churn_result.csv",
        mime="text/csv"
    )

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("🚀 Telecom Churn Prediction | BCA Project")== "about":     show_about()
    else:                  show_dashboard()
