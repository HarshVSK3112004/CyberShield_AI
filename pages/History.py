import pandas as pd
import streamlit as st

from database.db import get_history

st.set_page_config(page_title="History — CyberShield-AI", page_icon="📜")
st.title("📜 Scan History")

if not st.session_state.get("logged_in"):
    st.warning("Please log in to view your scan history.")
    st.stop()

history = get_history(st.session_state.user["id"])

if not history:
    st.info("No scans yet. Head to the Dashboard to check your first URL.")
else:
    df = pd.DataFrame(history)[["url", "verdict", "probability", "scanned_at"]]
    df["probability"] = (df["probability"] * 100).round(1).astype(str) + "%"
    df = df.rename(columns={
        "url": "URL",
        "verdict": "Verdict",
        "probability": "Phishing Probability",
        "scanned_at": "Scanned At (UTC)",
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

    phishing_count = sum(1 for h in history if h["verdict"] == "Phishing")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total scans", len(history))
    col2.metric("Flagged as phishing", phishing_count)
    col3.metric("Flagged as legitimate", len(history) - phishing_count)
