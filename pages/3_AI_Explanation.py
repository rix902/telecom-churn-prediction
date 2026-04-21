import streamlit as st

st.title("🤖 AI Explanation")

if "result" not in st.session_state:
    st.stop()

data = st.session_state["input_data"]
result = st.session_state["result"]

prob = result["probability"]

reasons = []

if data["Complains"] == 1:
    reasons.append("Customer has complaints")

if data["Subscription  Length"] < 12:
    reasons.append("Short subscription")

if data["Frequency of use"] < 10:
    reasons.append("Low usage")

if data["Customer Value"] < 200:
    reasons.append("Low value")

if data["Call  Failure"] > 5:
    reasons.append("High call failure")

# Risk
if prob > 0.7:
    risk = "🔴 High"
elif prob > 0.4:
    risk = "🟡 Medium"
else:
    risk = "🟢 Low"

st.subheader(f"Risk Level: {risk}")
st.write(f"Probability: {prob:.2f}")

st.subheader("Reasons:")
for r in reasons:
    st.write("-", r)

if st.button("Next ➡"):
    st.switch_page("pages/4_Download.py")
