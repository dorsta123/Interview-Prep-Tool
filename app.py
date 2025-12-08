# app.py
import streamlit as st
import db_skeleton as db
from ui_components import render_sidebar
from ui_views import view_upload_jd, view_practice, view_dashboard

def main():
    st.set_page_config(page_title="JD Interview Prep", layout="wide")
    
    # CSS Tweaks
    st.markdown("""
        <style>
        .block-container { padding-top: 1rem !important; }
        h1, h2, h3 { margin-top: 0.4rem !important; }
        </style>
        """, unsafe_allow_html=True)

    # Init
    render_sidebar()
    if "conn" not in st.session_state:
        st.session_state.conn = db.init_db()

    # Routing
    tab = st.sidebar.radio("Navigation", ["Upload JD", "Practice", "Dashboard"])
    
    if tab == "Upload JD":
        view_upload_jd(st.session_state.conn)
    elif tab == "Practice":
        view_practice(st.session_state.conn)
    else:
        view_dashboard(st.session_state.conn)

if __name__ == "__main__":
    main()