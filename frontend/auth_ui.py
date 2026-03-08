import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")

def login_ui():
    st.markdown("<h1 style='text-align: center; color: #007bff;'>LensFlow 访问权限</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d;'>请验证您的身份以继续。</p>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("用户名", placeholder="请输入用户名")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("登录")
        with col2:
            register = st.form_submit_button("注册")

    if submit:
        if not username or not password:
            st.error("Credentials required.")
            return

        try:
            res = requests.post(f"{BACKEND_URL}/auth/token", data={"username": username, "password": password})
            if res.status_code == 200:
                token = res.json()["access_token"]
                st.session_state["token"] = token
                st.session_state["username"] = username
                st.success("Access Granted.")
                st.rerun()
            else:
                st.error("Access Denied: Invalid credentials.")
        except Exception as e:
            st.error(f"Connection Error: {e}")

    if register:
        if not username or not password:
            st.error("Credentials required.")
            return
            
        try:
            res = requests.post(f"{BACKEND_URL}/auth/register", json={"username": username, "password": password})
            if res.status_code == 200:
                st.success("Registration Successful. Please Login.")
            elif res.status_code == 400:
                st.warning("Username already exists.")
            else:
                st.error(f"Error: {res.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")
