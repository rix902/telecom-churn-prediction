import streamlit as st
import pandas as pd
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Churn Predictor", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background-color: #0b0b0b;
    color: white;
}

.main {
    background-color: #0b0b0b;
}

h1, h2, h3 {
    color: white;
}

/* Navbar */
.navbar {
    display: flex;
    justify-content: space-between;
    padding: 15px;
    background-color: #141414;
    border-radius: 10px;
}

/* Cards */
.card {
    background: #141414;
    padding: 20px;
    border-radius: 15px;
    transition: 0.3s;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.5);
}

.card:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 20px rgba(229,9,20,0.6);
}

/* Buttons */
.stButton>button {
    background-color: #E50914;
    color: white;
    border-radius: 8px;
    height: 3em;
    width: 100%;
    font-size: 16px;
}

.stButton>button:hover {
    background-color: #ff1e1e;
}

/* Hero Section */
.hero {
    background-image: url("https://images.unsplash.com/photo-1550751827-4bd374c3f58b");
    background-size: cover;
    padding: 100px;
    border-radius: 15px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- NAVBAR ----------------
st.markdown('<div class="navbar"><h2>🔥 AI Churn</h2><h4>Home | Predict | Dashboard | Profile</h4></div>', unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
    <h1>Predict Customer Churn with AI</h1>
    <p>Smart insights. Better decisions.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------------- NETFLIX STYLE ROW ----------------
st.subheader("🎬 Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card"><h3>🔮 Prediction</h3><p>AI powered churn prediction</p></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><h3>📊 Analytics</h3><p>Interactive dashboards</p></div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card"><h3>🧠 AI Explain</h3><p>Understand model decisions</p></div>', unsafe_allow_html=True)

# ---------------- PREDICTION SECTION ----------------
st.subheader("🔮 Make Prediction")

col1, col2 = st.columns(2)

with col1:
    tenure = st.slider("Tenure", 0, 72)
    monthly = st.number_input("Monthly Charges", 0.0, 200.0)

    if st.button("Predict"):
        prediction = np.random.choice(["Churn", "No Churn"])
        prob = np.random.uniform(0.6, 0.95)

        st.session_state["result"] = (prediction, prob)

with col2:
    if "result" in st.session_state:
        pred, prob = st.session_state["result"]

        color = "#E50914" if pred == "Churn" else "#00ff99"

        st.markdown(f"""
        <div class="card">
            <h2 style="color:{color}">{pred}</h2>
            <p>Confidence: {prob:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- CHART ----------------
st.subheader("📊 Analytics")

chart_data = pd.DataFrame({
    "Churn": ["Yes", "No"],
    "Count": [200, 800]
})

st.bar_chart(chart_data.set_index("Churn"))

# ---------------- DOWNLOAD ----------------
st.subheader("⬇️ Download Predictions")

df = pd.DataFrame({
    "Prediction": ["Churn", "No Churn"],
    "Confidence": [0.85, 0.92]
})

st.dataframe(df)

st.download_button("Download CSV", df.to_csv(index=False), "predictions.csv")

# ---------------- FOOTER ----------------
st.markdown("<hr><center>🔥 Built like Netflix UI</center>", unsafe_allow_html=True)
