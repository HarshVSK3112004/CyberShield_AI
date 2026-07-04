"""
CyberShield-AI — main entry point.

Run with:  streamlit run app.py
Streamlit auto-discovers the pages/ folder and lists them in the sidebar.
"""
import streamlit as st

from database.db import init_db

st.set_page_config(
    page_title="CyberShield-AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure DB tables exist before any page tries to use them
init_db()

# Shared session state defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

st.title("🛡️ CyberShield-AI")
st.subheader("AI-Powered Phishing URL Detection & Cyber Risk Assessment")

st.markdown(
    """
    Welcome to **CyberShield-AI** — a tool that combines machine learning,
    URL heuristics, SSL certificate checks, WHOIS domain lookups, and
    VirusTotal reputation data to help you assess whether a link is safe.

    ### Get started
    - 👉 Use the sidebar to **Register** or **Login**.
    - Once logged in, head to the **Dashboard** to check a URL.
    - View your past checks under **History**.
    - Have a question? Chat with the assistant on the Dashboard page.

    ### Why this matters
    Phishing remains one of the most common ways attackers steal credentials
    and financial information. A quick automated check before you click can
    catch many of the obvious red flags — though it's never a substitute for
    good judgment and multi-factor authentication.
    """
)

if st.session_state.logged_in and st.session_state.user:
    st.success(f"You're logged in as **{st.session_state.user['username']}**. Head to the Dashboard from the sidebar.")
else:
    st.info("You're not logged in yet. Go to **Login** or **Register** in the sidebar to get started.")
