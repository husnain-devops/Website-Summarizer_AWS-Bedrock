import streamlit as st
from database import create_user, init_db

def show_signup_page():
    st.title("Sign Up")
    
    # Center the form
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("signup_form", clear_on_submit=True):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submitted = st.form_submit_button("Sign Up")
            
            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match!")
                    return
                
                if len(password) < 8:
                    st.error("Password must be at least 8 characters long!")
                    return
                
                if create_user(username, email, password):
                    st.success("Account created successfully! Please sign in.")
                    st.session_state['show_signup'] = False
                else:
                    st.error("Username or email already exists!") 