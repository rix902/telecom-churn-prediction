import streamlit as st
from utils import set_bg

set_bg()
import pandas as pd
import joblib

st.title("🤖 Prediction")

if "logged_in" not in st.session_state:
    st.stop()

model = joblib.load("churn_model.pkl")
model_columns = joblib.load("model_columns.pkl")

data = st.session_state.get("input_data", {})

if st.button("Predict 🔍"):

    df = pd.DataFrame([data])

    final_df = pd.DataFrame(columns=model_columns)
    for col in final_df.columns:
        final_df[col] = 0

    for col in df.columns:
        if col in final_df.columns:
            final_df[col] = df[col]

    prediction = model.predict(final_df)[0]
    probability = model.predict_proba(final_df)[0][1]

    st.session_state["result"] = {
        "prediction": prediction,
        "probability": probability
    }

    st.success("Prediction Done ✅")
    st.switch_page("pages/3_AI_Explanation.py")
