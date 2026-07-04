import streamlit as st

st.set_page_config(page_title="About — CyberShield-AI", page_icon="ℹ️")
st.title("ℹ️ About CyberShield-AI")

st.markdown(
    """
    **CyberShield-AI** is an educational project that demonstrates how multiple
    signals can be combined to assess whether a URL is likely to be a phishing
    attempt:

    1. **Machine learning model** — a TF-IDF + Random Forest classifier trained
       on labeled URL examples (`dataset/phishing.csv`, `models/train_model.py`).
    2. **Heuristic features** — structural red flags like IP-address hosts,
       suspicious keywords, excessive subdomains, and non-HTTPS links
       (`prediction/feature_extractor.py`).
    3. **SSL certificate check** — verifies the target site presents a valid,
       unexpired certificate (`security/ssl_checker.py`).
    4. **WHOIS lookup** — checks domain registration date and registrar, since
       phishing domains are often very recently registered (`security/whois_lookup.py`).
    5. **VirusTotal reputation** (optional) — cross-references community threat
       intelligence (`security/virustotal.py`).

    ### Tech Stack
    - **Frontend:** Streamlit (multipage app)
    - **ML:** scikit-learn, pandas
    - **Storage:** SQLite (users + scan history)
    - **Security checks:** Python `ssl`/`socket`, `python-whois`, VirusTotal API v3

    ### Disclaimer
    This tool is built for learning purposes and should **not** be relied on as
    your sole line of defense. Always verify suspicious links through official
    channels, keep software updated, and use multi-factor authentication.
    """
)
