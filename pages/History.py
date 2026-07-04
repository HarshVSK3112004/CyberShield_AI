import streamlit as st
import pandas as pd

from database.db import get_history

# ---------------------------------
# PAGE CONFIG
# ---------------------------------

st.set_page_config(
    page_title="History",
    page_icon="📜",
    layout="wide"
)

st.title("📜 Scan History")

# ---------------------------------
# LOGIN CHECK
# ---------------------------------

if not st.session_state.get("logged_in"):
    st.warning("Please login first.")
    st.stop()

user = st.session_state["user"]

st.success(f"Logged in as **{user['username']}**")

st.divider()

# ---------------------------------
# LOAD HISTORY
# ---------------------------------

history = get_history(user["id"])

if len(history) == 0:

    st.info("No scan history available.")

    st.stop()

# ---------------------------------
# CREATE DATAFRAME
# ---------------------------------

rows = []

for item in history:

    rows.append({

        "URL": item["url"],

        "Prediction": item["prediction"],

        "Confidence (%)": round(item["probability"] * 100, 2),

        "Date": item["created_at"]

    })

df = pd.DataFrame(rows)

# ---------------------------------
# FILTERS
# ---------------------------------

st.subheader("🔍 Filter Records")

col1, col2 = st.columns(2)

with col1:

    prediction_filter = st.selectbox(

        "Prediction",

        [

            "All",

            "Phishing",

            "Legitimate"

        ]

    )

with col2:

    search = st.text_input(

        "Search URL"

    )

# ---------------------------------
# APPLY FILTER
# ---------------------------------

filtered = df.copy()

if prediction_filter != "All":

    filtered = filtered[
        filtered["Prediction"] == prediction_filter
    ]

if search:

    filtered = filtered[
        filtered["URL"].str.contains(search, case=False)
    ]

# ---------------------------------
# METRICS
# ---------------------------------

st.divider()

c1, c2, c3 = st.columns(3)

c1.metric(

    "Total Scans",

    len(df)

)

c2.metric(

    "Phishing",

    len(df[df["Prediction"] == "Phishing"])

)

c3.metric(

    "Legitimate",

    len(df[df["Prediction"] == "Legitimate"])

)

st.divider()

# ---------------------------------
# TABLE
# ---------------------------------

st.subheader("📋 Scan Records")

st.dataframe(

    filtered,

    use_container_width=True,

    hide_index=True

)

# ---------------------------------
# DOWNLOAD CSV
# ---------------------------------

csv = filtered.to_csv(index=False)

st.download_button(

    "⬇ Download History",

    csv,

    "scan_history.csv",

    "text/csv"

)

# ---------------------------------
# CHART
# ---------------------------------

st.divider()

st.subheader("📊 Scan Summary")

chart = df["Prediction"].value_counts()

st.bar_chart(chart)

# ---------------------------------
# FOOTER
# ---------------------------------

st.caption(

    "CyberShield AI • History Module"

)