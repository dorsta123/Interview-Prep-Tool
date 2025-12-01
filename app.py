"""
jd_prep_skeleton.py
Minimal skeleton for an LLM-powered JD Interview Prep tool (Streamlit-style).

Replace TODOs with your implementation. Keep functions small and testable.
"""

# --- Imports ---
import streamlit as st
import sqlite3
import json
import time
from typing import List, Dict, Any
from datetime import datetime

# Optional LLM client import (install when ready)
# import openai

# --- Constants & config ---
DB_PATH = "jd_prep.db"
DEFAULT_MODEL = "gpt-4o-mini"  # replace with chosen model

# --- DB layer (very small) ---
def init_db(path: str = DB_PATH):
    """Create DB and tables if missing, return connection."""
    conn = sqlite3.connect(path, check_same_thread=False)
    cur = conn.cursor()
    # TODO: create tables jds, skills, questions, sessions, answers
    return conn

def save_jd(conn, title: str, jd_text: str, skills: List[str]) -> int:
    """Persist JD and skills; return jd_id."""
    # TODO: insert into jds and skills tables
    return 1

def save_questions(conn, jd_id: int, questions: List[Dict[str, Any]]):
    """Persist generated questions for a JD."""
    # TODO: insert into questions table
    pass

# --- LLM wrapper (abstract) ---
def configure_llm(api_key: str = None, model: str = DEFAULT_MODEL, api_base: str = None):
    """Set up LLM client without requiring API key input."""
    # Example stub – adapt based on your LLM provider
    # openai.api_key = FIXED_SYSTEM_KEY or environment variable
    # openai.base_url = api_base or default
    pass

def call_llm_for_skills(jd_text: str, top_k: int = 6) -> Dict[str, Any]:
    """
    Call LLM to extract top skills, domain, seniority, summary.
    Return structured dict: {'skills': [...], 'domain': '...', 'seniority':'...', 'summary':'...'}
    """
    # TODO: craft prompt, call LLM, parse JSON
    return {"skills": [], "domain": "", "seniority": "", "summary": ""}

def call_llm_for_questions(jd_title: str, skills: List[str]) -> List[Dict[str, str]]:
    """
    Return list of question dicts: [{'skill':..., 'qtype': 'technical'|'behavioral'|'product', 'prompt':...}, ...]
    """
    # TODO: LLM call -> generate questions
    return []

def call_llm_for_answer_review(jd_text: str, question: str, answer: str) -> Dict[str, Any]:
    """
    Return review containing strengths, weaknesses, missing_points, suggested_answer, score
    """
    # TODO: LLM call -> parse JSON
    return {"strengths": [], "weaknesses": [], "missing_points": [], "suggested_answer": "", "score": 3}

# --- Domain logic helpers ---
def build_question_pack(jd_title: str, skills: List[str]) -> List[Dict[str,str]]:
    """Either template-generate or call LLM; wrapper for generating question pack."""
    # For MVP use call_llm_for_questions
    return call_llm_for_questions(jd_title, skills)

def compute_skill_readiness(conn, jd_id: int) -> Dict[str, float]:
    """Aggregate scores per skill (naive average)."""
    # TODO: query DB and compute averages
    return {}

# --- Streamlit UI --- 
def ui_sidebar_settings():
    st.sidebar.header("Settings")
    # Removed API key field (users do NOT need to enter key)
    model = st.sidebar.text_input("Model", value=DEFAULT_MODEL)
    if st.sidebar.button("Configure LLM"):
        # Call without API key
        configure_llm(api_key=None, model=model)
        st.sidebar.success("LLM configured")

    st.sidebar.markdown("---")


def ui_upload_jd(conn):
    st.header("Upload / Paste JD")
    title = st.text_input("Role title")
    jd_text = st.text_area("Paste JD here", height=200)
    num_skills = st.slider("Top skills to extract", 4, 10, 6)
    if st.button("Extract & Save"):
        if not jd_text.strip():
            st.warning("Paste a JD first")
            return
        parsed = call_llm_for_skills(jd_text, top_k=num_skills)
        skills = parsed.get("skills", [])
        jd_id = save_jd(conn, title or "Untitled", jd_text, skills)
        questions = build_question_pack(title or "Untitled", skills)
        save_questions(conn, jd_id, questions)
        st.success(f"Saved JD id={jd_id} with {len(skills)} skills and {len(questions)} questions")

def ui_practice(conn):
    st.header("Practice")
    # TODO: list saved JDs, start session, load questions, accept answers and call LLM review, save answers
    st.info("Practice UI: TODO - implement session flow")

def ui_dashboard(conn):
    st.header("Dashboard")
    # TODO: show saved JDs, skills readiness, recent sessions
    st.info("Dashboard: TODO - implement metrics and readiness visualization")

# --- App entrypoint ---
def main():
    st.set_page_config(page_title="JD Interview Prep - MVP")
    ui_sidebar_settings()
    conn = init_db()
    tab = st.sidebar.radio("Page", ["Upload JD", "Practice", "Dashboard"])
    if tab == "Upload JD":
        ui_upload_jd(conn)
    elif tab == "Practice":
        ui_practice(conn)
    else:
        ui_dashboard(conn)

if __name__ == "__main__":
    main()
