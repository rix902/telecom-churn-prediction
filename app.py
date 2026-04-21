import streamlit as st
def set_bg():
    import streamlit as st
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(15,32,39,0.85), rgba(44,83,100,0.85)),
        url("https://images.unsplash.com/photo-1518779578993-ec3579fee39f");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
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
        border-radius: 10px;
    }

    div[data-baseweb="select"] {
        background-color: white !important;
        color: black !important;
    }

    .stButton>button {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: white;
        border-radius: 12px;
        height: 45px;
        width: 100%;
        font-size: 16px;
    }

    .stDownloadButton>button {
        background: linear-gradient(90deg, #ff512f, #dd2476);
        color: white;
        border-radius: 12px;
        height: 45px;
        width: 100%;
    }

    .css-1d391kg {
        background-color: rgba(0,0,0,0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Login")

st.title("🔐 Login / Signup")

# Session me users store (temporary DB)
if "users" not in st.session_state:
    st.session_state["users"] = {}

username = st.text_input("Username")
password = st.text_input("Password", type="password")

col1, col2 = st.columns(2)

# ---------------- LOGIN ----------------
with col1:
    if st.button("Login"):
        users = st.session_state["users"]

        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.success(f"Welcome {username} ✅")
            st.switch_page("pages/1_Information.py")
        else:
            st.error("User not found ❌ (Signup first)")

# ---------------- SIGNUP ----------------
with col2:
    if st.button("Signup"):
        users = st.session_state["users"]

        if username in users:
            st.warning("User already exists ⚠")
        else:
            users[username] = password
            st.success("Account created ✅ Now login")
