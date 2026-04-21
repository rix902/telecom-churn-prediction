import streamlit as st
import pandas as pd

st.title("📥 Download Result")

if "result" not in st.session_state:
    st.warning("No result found")
    st.stop()

result = st.session_state["result"]

st.write("Prediction:", result["prediction"])
st.write("Probability:", result["probability"])

df = pd.DataFrame([result])

csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    "Download CSV",
    data=csv,
    file_name="result.csv",
    mime="text/csv"
)

if st.button("Logout ➡"):
    st.switch_page("pages/4_Logout.py")
