import streamlit as st
from database import authenticate_user, get_user_id

def show_signin_page():
    st.title("Sign In")
    
    # Center the form
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("signin_form", clear_on_submit=True):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            submitted = st.form_submit_button("Sign In")
            
            if submitted:
                if authenticate_user(username, password):
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = username
                    st.session_state['user_id'] = get_user_id(username)
                    st.success("Signed in successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password!") 