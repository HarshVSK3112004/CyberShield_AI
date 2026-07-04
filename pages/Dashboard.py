import streamlit as st

from database.db import add_scan_history
from prediction.predictor import predict
from chatbot.chatbot import get_response

# Optional Security Modules
try:
    from security.ssl_checker import check_ssl
except:
    check_ssl = None

try:
    from security.whois_lookup import get_whois
except:
    get_whois = None

try:
    from security.virustotal import check_virustotal
except:
    check_virustotal = None


# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="Dashboard",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ CyberShield AI Dashboard")

# ----------------------------
# LOGIN CHECK
# ----------------------------

if not st.session_state.get("logged_in"):

    st.warning("Please login first.")

    st.stop()

user = st.session_state["user"]

st.success(f"Welcome **{user['username']}**")

st.divider()

# ----------------------------
# URL INPUT
# ----------------------------

st.subheader("🔍 Phishing Website Detection")

url = st.text_input(
    "Enter Website URL",
    placeholder="https://example.com"
)

run_ssl = st.checkbox("Check SSL Certificate")

run_whois = st.checkbox("WHOIS Lookup")

run_vt = st.checkbox("VirusTotal Scan")

# ----------------------------
# ANALYZE BUTTON
# ----------------------------

if st.button("Analyze Website", use_container_width=True):

    if url == "":

        st.error("Please enter a URL.")

    else:

        with st.spinner("Analyzing..."):

            result = predict(url)

        verdict = result["verdict"]

        probability = result["probability"]

        if verdict == "Phishing":

            st.error(
                f"⚠️ Phishing Website Detected\n\nConfidence : {probability:.2%}"
            )

        else:

            st.success(
                f"✅ Legitimate Website\n\nConfidence : {probability:.2%}"
            )

        # ----------------------------
        # SAVE HISTORY
        # ----------------------------

        add_scan_history(

            user["id"],

            url,

            verdict,

            probability

        )

        st.success("Prediction saved to History.")

        st.divider()

        # ----------------------------
        # MODEL DETAILS
        # ----------------------------

        st.subheader("📊 Prediction Details")

        st.write(result)

        # ----------------------------
        # SSL
        # ----------------------------

        if run_ssl and check_ssl:

            st.subheader("🔒 SSL Information")

            ssl_data = check_ssl(url)

            st.json(ssl_data)

        # ----------------------------
        # WHOIS
        # ----------------------------

        if run_whois and get_whois:

            st.subheader("🌐 WHOIS Information")

            whois_data = get_whois(url)

            st.json(whois_data)

        # ----------------------------
        # VirusTotal
        # ----------------------------

        if run_vt and check_virustotal:

            st.subheader("🦠 VirusTotal Report")

            vt = check_virustotal(url)

            st.json(vt)

st.divider()

# ----------------------------
# CHATBOT
# ----------------------------

st.subheader("🤖 Cyber Assistant")

if "messages" not in st.session_state:

    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.write(msg["content"])

prompt = st.chat_input("Ask me anything about Cyber Security")

if prompt:

    st.session_state.messages.append(

        {

            "role": "user",

            "content": prompt

        }

    )

    reply = get_response(prompt)

    st.session_state.messages.append(

        {

            "role": "assistant",

            "content": reply

        }

    )

    st.rerun()