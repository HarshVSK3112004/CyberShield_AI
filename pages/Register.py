import streamlit as st

from database.db import register_user

st.set_page_config(page_title="Register — CyberShield-AI", page_icon="📝")
st.title("📝 Create an Account")

with st.form("register_form"):
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Register")

    if submitted:
        if not username or not email or not password:
            st.error("Please fill in all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters long.")
        else:
            success, message = register_user(username, email, password)
            if success:
                st.success(message)
                st.info("Go to the **Login** page from the sidebar to sign in.")
            else:
                st.error(message)
