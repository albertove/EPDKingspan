import streamlit as st

def load_css(path="assets/style.css"):
    with open(path) as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)
