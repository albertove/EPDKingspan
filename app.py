import streamlit as st
from views import comparison, calculator, login, transport
from config.settings import APP_TITLE
from utils.helpers import load_css

st.set_page_config(page_title=APP_TITLE, layout="wide")
load_css()

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Show login page if not authenticated
if not st.session_state.authenticated:
    login.show()
else:
    # Add logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    
    # Show username in sidebar
    st.sidebar.write(f"Welcome, {st.session_state.username}!")
    
    # Main app navigation
    page = st.sidebar.radio("Select Page", ["Comparison Tool", "Project Calculator (A1-A3)", "Transport Calculator (A5)"])

    if page == "Comparison Tool":
        comparison.show()
    elif page == "Transport Calculator (A5)":
        transport.show()
    else:
        calculator.show()
