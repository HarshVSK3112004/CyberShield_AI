import streamlit as st

from database.db import add_scan_history
from prediction.predictor import predict
from security.ssl_checker import check_ssl
from security.whois_lookup import get_whois
from security.virustotal import check_virustotal
from chatbot.chatbot import get_response
from utils.helper import risk_label, is_valid_url

st.set_page_config(page_title="Dashboard — CyberShield-AI", page_icon="📊", layout="wide")
st.title("📊 Dashboard")

if not st.session_state.get("logged_in"):
    st.warning("Please log in to use the Dashboard.")
    st.stop()

st.markdown(f"Logged in as **{st.session_state.user['username']}**")

col_main, col_chat = st.columns([2, 1])

with col_main:
    st.subheader("🔎 Check a URL")
    url_input = st.text_input("Enter a URL to analyze", placeholder="e.g. http://example.com/login")
    run_vt = st.checkbox("Also check VirusTotal (requires API key in .env)", value=False)
    analyze = st.button("Analyze", type="primary")

    if analyze:
        if not url_input or not is_valid_url(url_input):
            st.error("Please enter a valid URL.")
        else:
            with st.spinner("Analyzing URL..."):
                pred = predict(url_input)
                ssl_result = check_ssl(url_input)
                whois_result = get_whois(url_input)
                vt_result = check_virustotal(url_input) if run_vt else None

            verdict = pred["verdict"]
            proba = pred["probability"]
            label = risk_label(proba)

            st.markdown("### Result")
            if verdict == "Phishing":
                st.error(f"{label} — Model verdict: **{verdict}** (probability: {proba:.0%})")
            else:
                st.success(f"{label} — Model verdict: **{verdict}** (probability: {proba:.0%})")

            tabs = st.tabs(["🧠 Model Details", "🔒 SSL", "🌐 WHOIS", "🦠 VirusTotal"])

            with tabs[0]:
                st.write(f"Prediction source: `{pred['source']}`")
                feats = pred["features"]
                fcol1, fcol2 = st.columns(2)
                with fcol1:
                    st.metric("URL length", feats["url_length"])
                    st.metric("Subdomain count", feats["count_subdomains"])
                    st.write("Uses HTTPS:", "✅" if feats["uses_https"] else "❌")
                    st.write("Has IP address as host:", "⚠️ Yes" if feats["has_ip_address"] else "No")
                with fcol2:
                    st.write("Contains '@' symbol:", "⚠️ Yes" if feats["has_at_symbol"] else "No")
                    st.write("Suspicious TLD:", "⚠️ Yes" if feats["has_suspicious_tld"] else "No")
                    st.write(
                        "Suspicious keywords found:",
                        ", ".join(feats["suspicious_words_found"]) if feats["suspicious_words_found"] else "None",
                    )

            with tabs[1]:
                if ssl_result["error"]:
                    st.warning(ssl_result["error"])
                else:
                    st.write("Valid certificate:", "✅" if ssl_result["valid"] else "❌")
                    st.write("Issued to:", ssl_result["subject"])
                    st.write("Issued by:", ssl_result["issuer"])
                    st.write("Expires on:", ssl_result["expires_on"])
                    st.write("Days remaining:", ssl_result["days_remaining"])

            with tabs[2]:
                if whois_result["error"]:
                    st.warning(whois_result["error"])
                else:
                    st.write("Registrar:", whois_result["registrar"] or "Unknown")
                    st.write("Created on:", whois_result["created_on"] or "Unknown")
                    st.write("Expires on:", whois_result["expires_on"] or "Unknown")
                    st.write("Domain age (days):", whois_result["domain_age_days"] or "Unknown")

            with tabs[3]:
                if vt_result is None:
                    st.info("VirusTotal check was not run. Enable the checkbox above to run it.")
                elif vt_result["error"]:
                    st.warning(vt_result["error"])
                else:
                    st.write("Verdict:", vt_result["verdict"])
                    st.write("Malicious detections:", vt_result["malicious"])
                    st.write("Suspicious detections:", vt_result["suspicious"])
                    st.write("Harmless detections:", vt_result["harmless"])

            add_scan_history(st.session_state.user["id"], pred["url"], verdict, proba)
            st.caption("This result has been saved to your History.")

with col_chat:
    st.subheader("🤖 Ask the Assistant")
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []

    for role, msg in st.session_state.chat_log:
        with st.chat_message(role):
            st.write(msg)

    user_msg = st.chat_input("Ask about phishing or online safety...")
    if user_msg:
        st.session_state.chat_log.append(("user", user_msg))
        bot_reply = get_response(user_msg)
        st.session_state.chat_log.append(("assistant", bot_reply))
        st.rerun()
