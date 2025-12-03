"""
db_skeleton.py
Task 1: DB schema + basic persistence for JD Interview Prep.
DEFAULT_MODEL set to the Gemini model you selected.
LLM stubs left as NotImplemented for Task 2+.
"""

# --- Imports ---
import sqlite3
import json
from typing import Any, List, Dict
from typing import List, Dict, Any
from datetime import datetime

# --- Constants & config ---
DB_PATH = "jd_prep.db"
DEFAULT_MODEL = "gemini-2.5-flash"  # your selected Gemini model for later tasks

# --- DB layer (Task 1 implemented) ---
def init_db(path: str = DB_PATH):
    """Create DB and tables if missing, return connection."""
    conn = sqlite3.connect(path, check_same_thread=False)
    # enforce foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS jds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        jd_text TEXT NOT NULL,
        domain TEXT,
        seniority TEXT,
        summary TEXT,
        created_at TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jd_id INTEGER NOT NULL,
        skill TEXT NOT NULL,
        FOREIGN KEY (jd_id) REFERENCES jds(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jd_id INTEGER NOT NULL,
        skill TEXT,
        qtype TEXT,
        prompt TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (jd_id) REFERENCES jds(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    return conn

def save_jd(conn, title: str, jd_text: str, skills: List[str], domain: str = "", seniority: str = "", summary: str = "") -> int:
    """Persist JD and skills; return jd_id."""
    cur = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO jds (title, jd_text, domain, seniority, summary, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (title, jd_text, domain, seniority, summary, created_at),
    )
    jd_id = cur.lastrowid

    # insert skills
    for s in skills:
        if s is None:
            continue
        s_clean = str(s).strip()
        if s_clean == "":
            continue
        cur.execute("INSERT INTO skills (jd_id, skill) VALUES (?, ?)", (jd_id, s_clean))

    conn.commit()
    return jd_id

def save_questions(conn, jd_id: int, questions: List[Dict[str, Any]]):
    """Persist generated questions for a JD."""
    cur = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    for q in questions:
        skill = (q.get("skill") or "").strip()
        qtype = (q.get("qtype") or "").strip()
        prompt = (q.get("prompt") or "").strip()
        if prompt == "":
            continue  # skip empty prompts
        cur.execute(
            "INSERT INTO questions (jd_id, skill, qtype, prompt, created_at) VALUES (?, ?, ?, ?, ?)",
            (jd_id, skill, qtype, prompt, created_at),
        )
    conn.commit()


# --- Read helpers (useful for tests / UI) ---
def get_jds(conn) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT id, title, jd_text, domain, seniority, summary, created_at FROM jds ORDER BY id DESC")
    rows = cur.fetchall()
    cols = ["id", "title", "jd_text", "domain", "seniority", "summary", "created_at"]
    return [dict(zip(cols, r)) for r in rows]

def get_skills_for_jd(conn, jd_id: int) -> List[str]:
    cur = conn.cursor()
    cur.execute("SELECT skill FROM skills WHERE jd_id = ? ORDER BY id ASC", (jd_id,))
    return [r[0] for r in cur.fetchall()]

def get_questions_for_jd(conn, jd_id: int) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT id, skill, qtype, prompt, created_at FROM questions WHERE jd_id = ? ORDER BY id ASC", (jd_id,))
    rows = cur.fetchall()
    cols = ["id", "skill", "qtype", "prompt", "created_at"]
    return [dict(zip(cols, r)) for r in rows]

def delete_jd(conn, jd_id: int):
    """Delete JD and cascade to skills/questions (uses FK ON DELETE CASCADE)."""
    cur = conn.cursor()
    cur.execute("DELETE FROM jds WHERE id = ?", (jd_id,))
    conn.commit()

# --- LLM / UI stubs (for future tasks) ---
def configure_llm(api_key: str = None, model: str = DEFAULT_MODEL, api_base: str = None):
    raise NotImplementedError("configure_llm not implemented. Implement Task 2 (Gemini wrapper).")

def call_llm_for_skills(jd_text: str, top_k: int = 6):
    raise NotImplementedError("call_llm_for_skills not implemented. Implement Task 3.")

def call_llm_for_questions(jd_title: str, skills: List[str]):
    raise NotImplementedError("call_llm_for_questions not implemented. Implement Task 4.")
