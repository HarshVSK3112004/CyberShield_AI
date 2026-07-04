import streamlit as st

from database.db import get_user_stats

st.set_page_config(page_title="Profile — CyberShield-AI", page_icon="👤")
st.title("👤 Profile")

if not st.session_state.get("logged_in"):
    st.warning("Please log in to view your profile.")
    st.stop()

user = st.session_state.user
stats = get_user_stats(user["id"])

st.subheader(user["username"])
st.write("**Email:**", user["email"])
st.write("**Member since:**", user["created_at"][:10])

st.markdown("---")
st.subheader("Your Activity")
col1, col2, col3 = st.columns(3)
col1.metric("Total scans", stats["total"])
col2.metric("Phishing flagged", stats["phishing"])
col3.metric("Legitimate flagged", stats["safe"])

if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()
