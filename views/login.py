import streamlit as st
import hashlib

def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username, password):
    """Check if the credentials are valid."""
    # This is a simple example. In a real application, you would:
    # 1. Store credentials securely in a database
    # 2. Use proper password hashing (like bcrypt)
    # 3. Implement proper session management
    valid_credentials = {
        "admin": hash_password("admin123"),
        "user": hash_password("user123")
    }
    return username in valid_credentials and valid_credentials[username] == hash_password(password)

def show():
    st.title("Login")
    
    # Create a form for login
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if check_credentials(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password") 