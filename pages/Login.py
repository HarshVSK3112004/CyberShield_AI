import streamlit as st

from database.db import verify_user

st.set_page_config(page_title="Login — CyberShield-AI", page_icon="🔐")
st.title("🔐 Login")

if st.session_state.get("logged_in"):
    st.success(f"You're already logged in as **{st.session_state.user['username']}**.")
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
else:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user = verify_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(f"Welcome back, {user['username']}!")
                st.info("Head to the **Dashboard** from the sidebar to check a URL.")
            else:
                st.error("Invalid username or password.")
