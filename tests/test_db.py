# tests/test_db.py
import pytest
from db_skeleton import init_db, save_jd, save_questions, get_jds, get_skills_for_jd, get_questions_for_jd, delete_jd

def test_init_db_and_tables():
    conn = init_db(":memory:")
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cur.fetchall()}
    assert {"jds", "skills", "questions"}.issubset(tables)

def test_save_jd_and_skills():
    conn = init_db(":memory:")
    jd_id = save_jd(conn, "Test Role", "Some job description", ["python", "sql"])
    assert jd_id > 0
    skills = get_skills_for_jd(conn, jd_id)
    assert skills == ["python", "sql"]

def test_save_questions_and_query():
    conn = init_db(":memory:")
    jd_id = save_jd(conn, "Role", "JD text", ["a"])
    questions = [
        {"skill": "a", "qtype": "technical", "prompt": "Explain X."},
        {"skill": "a", "qtype": "behavioral", "prompt": "Tell me about Y."}
    ]
    save_questions(conn, jd_id, questions)
    fetched = get_questions_for_jd(conn, jd_id)
    assert len(fetched) == 2
    assert fetched[0]["prompt"] == "Explain X."

def test_delete_jd_cascades():
    conn = init_db(":memory:")
    jd_id = save_jd(conn, "Role", "JD text", ["s"])
    save_questions(conn, jd_id, [{"skill":"s", "qtype":"t", "prompt":"P"}])
    delete_jd(conn, jd_id)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM jds WHERE id = ?", (jd_id,))
    (c_jd,) = cur.fetchone()
    cur.execute("SELECT count(*) FROM skills WHERE jd_id = ?", (jd_id,))
    (c_sk,) = cur.fetchone()
    cur.execute("SELECT count(*) FROM questions WHERE jd_id = ?", (jd_id,))
    (c_q,) = cur.fetchone()
    assert c_jd == 0 and c_sk == 0 and c_q == 0
