import streamlit as st

def set_bg():

    st.markdown("""
    <style>
    .stApp {
        background-image: 
        linear-gradient(rgba(15,32,39,0.85), rgba(44,83,100,0.85)),
        url("https://images.unsplash.com/photo-1581093588401-22f5b96a5c6d");
        
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    h1, h2, h3 {
        color: white !important;
        text-align: center;
    }

    label {
        color: white !important;
    }

    .stTextInput>div>div>input {
        background-color: white;
        color: black;
        border-radius: 10px;
    }

    .stNumberInput>div>div>input {
        background-color: white;
        color: black;
    }

    .stSelectbox>div {
        background-color: white;
        color: black;
    }

    .stButton>button {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: white;
        border-radius: 12px;
        height: 45px;
        width: 100%;
    }

    .stDownloadButton>button {
        background: linear-gradient(90deg, #ff512f, #dd2476);
        color: white;
        border-radius: 12px;
        height: 45px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
