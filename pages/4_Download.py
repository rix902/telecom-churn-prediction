import streamlit as st
import pandas as pd

st.title("📥 Download Result")

result = st.session_state.get("result")

if not result:
    st.stop()

df = pd.DataFrame([result])

csv = df.to_csv(index=False).encode('utf-8')

st.download_button("Download CSV", data=csv, file_name="result.csv")

if st.button("Logout ➡"):
    st.switch_page("pages/5_Logout.py")
