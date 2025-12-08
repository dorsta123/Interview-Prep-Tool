# ui_components.py
import streamlit as st
import jd_logic as llm

def render_sidebar():
    """Renders the settings sidebar."""
    st.sidebar.header("Settings")

    if "model_input" not in st.session_state:
        st.session_state.model_input = llm.DEFAULT_MODEL

    model_input = st.sidebar.text_input(
        "Model",
        value=st.session_state.model_input,
        key="model_input"
    )

    if st.sidebar.button("Configure LLM", key="sidebar_config_llm"):
        try:
            llm.configure_llm(model=model_input)
            st.sidebar.success(f"LLM configured using: {model_input}")
        except Exception as e:
            st.sidebar.error(f"Failed to configure LLM: {e}")

    st.sidebar.markdown("---")

def render_question_card(q, index):
    """Renders a single question card."""
    card_html = f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e6e6e6;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    ">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div style="font-weight:600;font-size:14px;color:#333;">
                <span style="color:#888; margin-right:8px; font-weight:normal;">#{index}</span>
                {q.get('skill','').title() or 'General'}
            </div>
            <div style="
                font-size:11px;
                padding:4px 8px;
                border-radius:999px;
                background:#eef2ff;
                color:#3b4cca;
                font-weight:600;
            ">
                {str(q.get('qtype','')).upper() or 'QUESTION'}
            </div>
        </div>
        <div style="margin-top:10px;line-height:1.4;color:#444;">
            {q.get('prompt','')}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)