# ui_views.py
import streamlit as st
import docx, PyPDF2
import db_skeleton as db
import jd_logic as llm
from ui_components import render_question_card

def view_upload_jd(conn):
    st.header("Upload / Paste JD")

    col_left, spacer, col_right = st.columns([3, 0.2, 1])

    # --- Right Column: Saved JDs ---
    with col_right:
        st.subheader("Saved JDs")
        jds = db.get_jds(conn)
        selected_jd = None
        if not jds:
            st.info("No JDs saved yet.")
        else:
            options = {f"{r['id']}: {r['title']}": r for r in jds}
            sel = st.selectbox("Saved JDs", list(options.keys()))
            selected_jd = options.get(sel)

    # --- Left Column: Form ---
    with col_left:
        title = st.text_input("Role title", value="")
        uploaded_file = st.file_uploader("Upload JD file (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"])
        jd_text = st.text_area("Paste JD here", height=150)
        num_skills = st.slider("Top skills to extract", 4, 10, 6)

        # File Parsing Logic
        if uploaded_file:
            try:
                ext = uploaded_file.name.split(".")[-1].lower()
                if ext == "txt":
                    jd_text = uploaded_file.read().decode("utf-8", errors="ignore")
                elif ext == "pdf":
                    reader = PyPDF2.PdfReader(uploaded_file)
                    jd_text = "\n".join([page.extract_text() or "" for page in reader.pages])
                elif ext == "docx":
                    doc = docx.Document(uploaded_file)
                    jd_text = "\n".join([p.text for p in doc.paragraphs])
            except Exception as e:
                st.error(f"Failed to extract text: {e}")

        # Extraction Logic
        if st.button("Extract & Save", key="extract_save"):
            if not jd_text.strip():
                st.warning("Please paste a job description first.")
                return

            llm.configure_llm() # Ensure Client is ready

            try:
                with st.spinner("Extracting skills..."):
                    parsed = llm.call_llm_for_skills(jd_text, top_k=num_skills)
                
                jd_id = db.save_jd(
                    conn, 
                    title or "Untitled", 
                    jd_text, 
                    parsed.get("skills", []), 
                    parsed.get("domain", ""), 
                    parsed.get("seniority", ""), 
                    parsed.get("summary", "")
                )
                
                with st.spinner("Generating questions..."):
                    questions = llm.call_llm_for_questions(title or "Untitled", parsed.get("skills", []))
                
                db.save_questions(conn, jd_id, questions)
                st.success(f"Saved JD id={jd_id}")
                st.rerun()
                
            except Exception as e:
                st.error(f"Process failed: {e}")

        # View Logic (Saved JD)
        if selected_jd:
            st.markdown("---")
            st.subheader(f"Viewing Saved JD: {selected_jd['title']}")
            c1, c2, c3 = st.columns(3)
            with c1: st.write(f"**Domain:** {selected_jd.get('domain', 'N/A')}")
            with c2: st.write(f"**Seniority:** {selected_jd.get('seniority', 'N/A')}")
            with c3: st.write(f"**Date:** {selected_jd.get('created_at', '')[:10]}")
            st.write(f"**Summary:** {selected_jd.get('summary', '')}")

            qlist = db.get_questions_for_jd(conn, selected_jd["id"])
            if qlist:
                st.subheader(f"Questions ({len(qlist)})")
                for i, q in enumerate(qlist, 1):
                    render_question_card(q, i)

def view_practice(conn):
    st.header("Practice")
    st.info("Practice UI: TODO - implement session flow")

def view_dashboard(conn):
    st.header("Dashboard")
    st.info("Dashboard: TODO - implement metrics")