import streamlit as st
import pandas as pd
import joblib

# -------------------------------
# Load Model and Columns
# -------------------------------
model = joblib.load("churn_model.pkl")
model_columns = joblib.load("model_columns.pkl")

st.title("📊 Telecom Customer Churn Prediction")
st.write("Enter customer details to predict churn.")

# -------------------------------
# User Inputs
# -------------------------------

call_failure = st.number_input("Call Failure", 0, 100)
complains = st.selectbox("Complains", [0,1])
subscription_length = st.number_input("Subscription Length (Months)",1,60)
charge_amount = st.number_input("Charge Amount",0,1000)

seconds_of_use = st.number_input("Seconds of Use",0,100000)
frequency_of_use = st.number_input("Frequency of Use",0,1000)
frequency_sms = st.number_input("Frequency of SMS",0,1000)
distinct_numbers = st.number_input("Distinct Called Numbers",0,200)

age = st.number_input("Customer Age",18,80)
tariff_plan = st.selectbox("Tariff Plan",[0,1])
status = st.selectbox("Customer Status",[0,1])
customer_value = st.number_input("Customer Value",0,1000)

cluster = st.number_input("Cluster",0,5)

# -------------------------------
# Prediction Button
# -------------------------------

if st.button("Predict Churn"):

    input_data = {
        'Call  Failure': call_failure,
        'Complains': complains,
        'Subscription  Length': subscription_length,
        'Charge  Amount': charge_amount,
        'Seconds of Use': seconds_of_use,
        'Frequency of use': frequency_of_use,
        'Frequency of SMS': frequency_sms,
        'Distinct Called Numbers': distinct_numbers,
        'Age': age,
        'Tariff Plan': tariff_plan,
        'Status': status,
        'Customer Value': customer_value,
        'Cluster': cluster
    }

    # Convert to dataframe
    input_df = pd.DataFrame([input_data])

    # Create full dataframe with training columns
    final_df = pd.DataFrame(columns=model_columns)

    for col in final_df.columns:
        final_df[col] = 0

    for col in input_df.columns:
        if col in final_df.columns:
            final_df[col] = input_df[col]

    # Prediction
    prediction = model.predict(final_df)

    if prediction[0] == 1:
        st.error("⚠ Customer will CHURN")
    else:
        st.success("✅ Customer will NOT churn")
