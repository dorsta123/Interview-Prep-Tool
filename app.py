"""
jd_prep_skeleton.py
Minimal skeleton for an LLM-powered JD Interview Prep tool (Streamlit-style).

Replace TODOs with your implementation. Keep functions small and testable.
"""

# --- Imports ---
import streamlit as st
import sqlite3, json, time
import db_skeleton as db         
import jd_prep_skeleton as llm
from typing import List, Dict, Any
from datetime import datetime

# Globals for Gemini client
LLM_CLIENT = None
LLM_MODEL = None


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
def configure_llm(api_key: str = None, model: str = None):
    """
    Initialize the Google GenAI (Gemini) client.
    If api_key is provided it will be set to GEMINI_API_KEY env var.
    model defaults to DEFAULT_MODEL when not provided.
    """
    global LLM_CLIENT, LLM_MODEL
    # Lazy import so the module can be used/tested without the package installed.
    try:
        from google import genai
    except Exception as e:
        raise RuntimeError("google-genai package not installed. Run: pip install google-genai") from e

    import os
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    LLM_MODEL = model or DEFAULT_MODEL
    # Initialize the client (it will read GEMINI_API_KEY from env)
    LLM_CLIENT = genai.Client()


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

# Helpers (ensure this appears before ui_upload_jd)
def show_saved_jds(conn):
    """
    Return selected JD dict or None.
    This helper renders the selectbox and returns the selected JD row.
    """
    jds = db.get_jds(conn)
    if not jds:
        st.info("No JDs saved yet.")
        return None
    options = {f"{r['id']}: {r['title']}": r for r in jds}
    sel = st.selectbox("Saved JDs", list(options.keys()))
    return options.get(sel)


def ui_upload_jd(conn):
    st.header("Upload / Paste JD")
    title = st.text_input("Role title", value="")

    # --- File uploader OR paste ---
    uploaded_file = st.file_uploader("Upload JD file (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"])
    jd_text = ""

    # Always define the slider at top-level (avoid scoping issues)
    num_skills = st.slider("Top skills to extract", 4, 10, 6)

    # Read file if uploaded, else show textarea
    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].lower()
        try:
            if ext == "txt":
                jd_text = uploaded_file.read().decode("utf-8", errors="ignore")
            elif ext == "pdf":
                # PyPDF2 required
                import PyPDF2
                reader = PyPDF2.PdfReader(uploaded_file)
                jd_text = "\n".join([page.extract_text() or "" for page in reader.pages])
            elif ext == "docx":
                import docx
                doc = docx.Document(uploaded_file)
                jd_text = "\n".join([p.text for p in doc.paragraphs])
            else:
                st.warning("Unsupported file type.")
        except Exception as e:
            st.error(f"Failed to extract text from file: {e}")
            return  # abort early if file extraction fails
    else:
        jd_text = st.text_area("Paste JD here", height=260)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Extract & Save"):
            if not jd_text.strip():
                st.warning("Please paste a job description or upload a file first.")
                return

            # Optional: warn if LLM not configured
            try:
                # Try a quick check if configure_llm was called (LLM wrapper sets LLM_CLIENT)
                configured = getattr(llm, "LLM_CLIENT", None) is not None
            except Exception:
                configured = False

            if not configured:
                st.info("LLM not configured — you can configure it in the sidebar or continue and use fallback behavior.")

            # call LLM for skills (stop on failure)
            try:
                with st.spinner("Extracting skills..."):
                    parsed = llm.call_llm_for_skills(jd_text, top_k=num_skills)
            except Exception as e:
                st.error(f"Skill extraction failed: {e}")
                st.stop()  # abort to avoid partial saves / undefined variables

            # normalize parsed
            skills = parsed.get("skills", []) if isinstance(parsed, dict) else []
            domain = parsed.get("domain", "") if isinstance(parsed, dict) else ""
            seniority = parsed.get("seniority", "") if isinstance(parsed, dict) else ""
            summary = parsed.get("summary", "") if isinstance(parsed, dict) else ""

            # Save JD & skills
            try:
                jd_id = db.save_jd(conn, title or "Untitled", jd_text, skills, domain=domain, seniority=seniority, summary=summary)
                st.success(f"Saved JD id={jd_id}")
            except Exception as e:
                st.error(f"Failed to save JD: {e}")
                return

            # Generate questions
            try:
                with st.spinner("Generating questions..."):
                    questions = llm.call_llm_for_questions(title or "Untitled", skills)
            except Exception as e:
                st.error(f"Question generation failed: {e}")
                questions = []

            # Save questions
            try:
                db.save_questions(conn, jd_id, questions)
                st.success(f"Saved {len(questions)} questions for JD {jd_id}")
            except Exception as e:
                st.error(f"Failed to save questions: {e}")

            # Show preview
            if skills:
                st.subheader("Extracted skills")
                st.write(skills)
            if summary:
                st.subheader("Summary / metadata")
                st.write(f"**Domain:** {domain}  ·  **Seniority:** {seniority}")
                st.write(summary)
            if questions:
                st.subheader("Generated questions (first 8)")
                for q in questions[:8]:
                    st.markdown(f"- **{q.get('qtype','')}** — *{q.get('skill','')}*: {q.get('prompt','')}")
    with col2:
        st.subheader("Preview saved JDs")
        selected = show_saved_jds(conn)
        if selected:
            st.write("**Title:**", selected["title"])
            st.write("**Summary:**", selected.get("summary", ""))
            st.write("**Domain / Seniority:**", selected.get("domain", ""), "/", selected.get("seniority", ""))
            qlist = db.get_questions_for_jd(conn, selected["id"])
            if qlist:
                st.markdown("**Questions (stored):**")
                for q in qlist[:10]:
                    st.markdown(f"- **{q['qtype']}** — *{q['skill']}*: {q['prompt']}")
            else:
                st.info("No questions stored for this JD yet.")


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
