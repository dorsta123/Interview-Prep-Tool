"""
jd_prep_skeleton.py
Minimal skeleton for an LLM-powered JD Interview Prep tool (Streamlit-style).

Replace TODOs with your implementation. Keep functions small and testable.
"""

# --- Imports ---
import streamlit as st
import sqlite3, json, time, docx, PyPDF2
import db_skeleton as db    
import jd_prep_skeleton as llm
from typing import List, Dict, Any
from datetime import datetime

# --- Constants & config ---
DB_PATH = "jd_prep.db"

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

def ui_sidebar_settings():
    st.sidebar.header("Settings")

    # Initialize default model one time only
    if "model_input" not in st.session_state:
        st.session_state.model_input = llm.DEFAULT_MODEL

    # Create the text input widget – it will manage session_state automatically
    model_input = st.sidebar.text_input(
        "Model",
        value=st.session_state.model_input,
        key="model_input"
    )

    # Configure button
    if st.sidebar.button("Configure LLM", key="sidebar_config_llm"):
        try:
            llm.configure_llm(model=model_input)
            st.sidebar.success(f"LLM configured using: {model_input}")
        except Exception as e:
            st.sidebar.error(f"Failed to configure LLM: {e}")

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

    # Wide middle area + narrower right sidebar
    col_left, spacer, col_right = st.columns([3, 0.2,1])

    # -------- LEFT COLUMN: main workflow --------
    with col_left:
        title = st.text_input("Role title", value="")

        # File uploader OR paste
        uploaded_file = st.file_uploader(
            "Upload JD file (PDF, TXT, DOCX)",
            type=["pdf", "txt", "docx"]
        )
        jd_text = ""

        # Slider for skills
        num_skills = st.slider("Top skills to extract", 4, 10, 6)

        # Read file if uploaded, else show textarea
        if uploaded_file:
            ext = uploaded_file.name.split(".")[-1].lower()
            try:
                if ext == "txt":
                    jd_text = uploaded_file.read().decode("utf-8", errors="ignore")
                elif ext == "pdf":
                    reader = PyPDF2.PdfReader(uploaded_file)
                    jd_text = "\n".join(
                        [page.extract_text() or "" for page in reader.pages]
                    )
                elif ext == "docx":
                    doc = docx.Document(uploaded_file)
                    jd_text = "\n".join([p.text for p in doc.paragraphs])
                else:
                    st.warning("Unsupported file type.")
            except Exception as e:
                st.error(f"Failed to extract text from file: {e}")
                return
        else:
            jd_text = st.text_area("Paste JD here", height=260)

        questions = []
        skills = []
        domain = seniority = summary = ""

        if st.button("Extract & Save", key="extract_save"):
            if not jd_text.strip():
                st.warning("Please paste a job description or upload a file first.")
                return

            # Check if LLM is configured (soft warning only)
            try:
                configured = getattr(llm, "LLM_CLIENT", None) is not None
            except Exception:
                configured = False

            if not configured:
                st.info(
                    "LLM not configured — configure it in the sidebar, "
                    "or continue and rely on fallback behavior."
                )

            # 1) Extract skills / metadata
            try:
                with st.spinner("Extracting skills..."):
                    parsed = llm.call_llm_for_skills(jd_text, top_k=num_skills)
            except Exception as e:
                st.error(f"Skill extraction failed: {e}")
                st.stop()

            skills = parsed.get("skills", []) if isinstance(parsed, dict) else []
            domain = parsed.get("domain", "") if isinstance(parsed, dict) else ""
            seniority = parsed.get("seniority", "") if isinstance(parsed, dict) else ""
            summary = parsed.get("summary", "") if isinstance(parsed, dict) else ""

            # 2) Save JD + skills
            try:
                jd_id = db.save_jd(
                    conn,
                    title or "Untitled",
                    jd_text,
                    skills,
                    domain=domain,
                    seniority=seniority,
                    summary=summary,
                )
                st.success(f"Saved JD id={jd_id}")
            except Exception as e:
                st.error(f"Failed to save JD: {e}")
                return

            # 3) Generate questions
            try:
                with st.spinner("Generating questions..."):
                    questions = llm.call_llm_for_questions(title or "Untitled", skills)
            except Exception as e:
                st.error(f"Question generation failed: {e}")
                questions = []

            # 4) Save questions
            try:
                db.save_questions(conn, jd_id, questions)
                st.success(f"Saved {len(questions)} questions for JD {jd_id}")
            except Exception as e:
                st.error(f"Failed to save questions: {e}")

            # 5) Show preview in the same wide left area
            if skills:
                st.subheader("Extracted skills")
                st.write(skills)

            if summary:
                st.subheader("Summary / metadata")
                st.write(f"**Domain:** {domain}  ·  **Seniority:** {seniority}")
                st.write(summary)

            if questions:
                st.subheader("Generated Questions")
                print(questions)

                # Single-column full-width cards (spanning entire left column)
                for q in questions:
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
                                {q.get('qtype','').upper() or 'QUESTION'}
                            </div>
                        </div>
                        <div style="margin-top:10px;line-height:1.4;color:#444;">
                            {q.get('prompt','')}
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

    # -------- RIGHT COLUMN: full sidebar for saved JDs --------
    with col_right:
        st.subheader("Preview saved JDs")
        selected = show_saved_jds(conn)
        if selected:
            st.write("**Title:**", selected["title"])
            st.write("**Summary:**", selected.get("summary", ""))
            st.write(
                "**Domain / Seniority:**",
                selected.get("domain", ""),
                "/",
                selected.get("seniority", ""),
            )

            qlist = db.get_questions_for_jd(conn, selected["id"])
            if qlist:
                st.markdown("**Questions (stored):**")
                for q in qlist[:10]:
                    st.markdown(
                        f"- **{q['qtype']}** — *{q['skill']}*: {q['prompt']}"
                    )
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
    st.set_page_config(
    page_title="JD Interview Prep - MVP",
    layout="wide"    # makes the central area span more horizontal space
    )
    st.markdown("""
        <style>

        /* Reduce top padding of the entire page */
        .block-container {
            padding-top: 1rem !important;   /* default is ~2.5rem */
        }

        /* Reduce margin above headers (h1, h2, etc.) */
        h1, h2, h3, h4, h5, h6 {
            margin-top: 0.4rem !important;
        }

        </style>
        """, unsafe_allow_html=True)

    ui_sidebar_settings()
    conn = db.init_db()
    # initialize DB and save into session_state once
    if "conn" not in st.session_state:
        st.session_state.conn = db.init_db()

    tab = st.sidebar.radio("Page", ["Upload JD", "Practice", "Dashboard"])
    if tab == "Upload JD":
        ui_upload_jd(conn)
    elif tab == "Practice":
        ui_practice(conn)
    else:
        ui_dashboard(conn)


if __name__ == "__main__":
    main()
