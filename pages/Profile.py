import streamlit as st
from database.db import get_user_stats

# ---------------------------------
# PAGE CONFIG
# ---------------------------------

st.set_page_config(
    page_title="Profile",
    page_icon="👤",
    layout="wide"
)

st.title("👤 User Profile")

# ---------------------------------
# LOGIN CHECK
# ---------------------------------

if not st.session_state.get("logged_in"):
    st.warning("Please login first.")
    st.stop()

user = st.session_state["user"]

# ---------------------------------
# USER INFO
# ---------------------------------

st.subheader("Personal Information")

col1, col2 = st.columns(2)

with col1:
    st.text_input(
        "Username",
        value=user["username"],
        disabled=True
    )

with col2:
    st.text_input(
        "Email",
        value=user["email"],
        disabled=True
    )

st.divider()

# ---------------------------------
# USER STATISTICS
# ---------------------------------

stats = get_user_stats(user["id"])

st.subheader("📊 Security Statistics")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Total Scans",
    stats["total"]
)

c2.metric(
    "Phishing Detected",
    stats["phishing"]
)

c3.metric(
    "Legitimate Websites",
    stats["safe"]
)

st.divider()

# ---------------------------------
# PIE CHART
# ---------------------------------

st.subheader("Prediction Distribution")

chart_data = {
    "Phishing": stats["phishing"],
    "Legitimate": stats["safe"]
}

st.bar_chart(chart_data)

st.divider()

# ---------------------------------
# ACCOUNT STATUS
# ---------------------------------

st.subheader("Account Status")

st.success("🟢 Account Active")

st.info(f"""
**User ID:** {user['id']}

**Username:** {user['username']}

**Email:** {user['email']}

Your CyberShield AI account is active and functioning correctly.
""")

st.divider()

# ---------------------------------
# SECURITY TIPS
# ---------------------------------

st.subheader("🛡 Cyber Safety Tips")

tips = [
    "Use strong and unique passwords.",
    "Enable Two-Factor Authentication (2FA).",
    "Avoid clicking unknown links.",
    "Verify website URLs before entering credentials.",
    "Keep your browser and operating system updated.",
    "Never download attachments from unknown emails.",
    "Check SSL certificates before making online payments.",
    "Use a password manager for better security."
]

for tip in tips:
    st.write("✅", tip)

st.divider()

# ---------------------------------
# LOGOUT
# ---------------------------------

if st.button("🚪 Logout", use_container_width=True):

    st.session_state.logged_in = False
    st.session_state.user = None

    st.success("Logged out successfully.")

    st.rerun()

st.caption("CyberShield AI • User Profile")