# jd_prep_skeleton.py
"""
LLM + App logic for JD Interview Prep.
This file contains Gemini integration and functions that call LLMs,
as well as the Streamlit UI (if you want to add it later).
"""

# --- Imports ---
import os
import json
from typing import Any, List, Dict
import google.generativeai as genai
from google.generativeai import GenerativeModel
# import streamlit as st  # uncomment when you add UI
# from google import genai  # import inside configure_llm to keep tests offline

# ⚠️ Put YOUR API key here
GEMINI_API_KEY = "AIzaSyBzjCPGCpW8R8i9XUewpvRA0ptvQU7QCNI"
DEFAULT_MODEL="gemini-2.5-flash"

def configure_llm(model="gemini-2.5-flash", api_base=None):
    global LLM_CLIENT, LLM_MODEL
    genai.configure(api_key=GEMINI_API_KEY)
    LLM_CLIENT = genai
    LLM_MODEL = model


def _genai_generate(prompt: str, model: str = None, temperature: float = 0.1, max_output_tokens: int = 512):
    use_model = model or LLM_MODEL or DEFAULT_MODEL
    gen_model = GenerativeModel(use_model)
    resp = gen_model.generate_content(
        prompt,
        generation_config={"temperature": temperature, "max_output_tokens": max_output_tokens}
    )
    return getattr(resp, "text", str(resp))


def _parse_json_from_text(raw: str) -> Any:
    """
    Robust JSON extraction from raw LLM output.
    """
    text = (raw or "").strip()
    if not text:
        raise ValueError("Empty input")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start_obj = text.find("{")
    end_obj = text.rfind("}") + 1
    if start_obj != -1 and end_obj > start_obj:
        cand = text[start_obj:end_obj]
        try:
            return json.loads(cand)
        except json.JSONDecodeError:
            pass
    start_arr = text.find("[")
    end_arr = text.rfind("]") + 1
    if start_arr != -1 and end_arr > start_arr:
        cand = text[start_arr:end_arr]
        try:
            return json.loads(cand)
        except json.JSONDecodeError:
            pass
    if "'" in text and '"' not in text:
        try:
            return json.loads(text.replace("'", '"'))
        except Exception:
            pass
    raise ValueError("Could not parse JSON from LLM output")

def call_llm_for_skills(jd_text: str, top_k: int = 6) -> Dict[str, Any]:
    """
    Extract top skills, domain, seniority, and summary from JD text.
    """
    prompt = f"""
You are an expert recruiter assistant. Given the job description delimited by triple backticks,
extract the TOP {top_k} skills (short phrases), one-word or short 'domain' (e.g., Data Engineering),
an approximate 'seniority' (one of: junior, mid, senior, lead, manager), and a concise 1-2 sentence 'summary'
of the role.

Return ONLY valid JSON in this exact format (no extra commentary):
{{"skills": ["skill1","skill2",...], "domain":"...", "seniority":"...", "summary":"..."}}

Job Description:
"""
    raw = _genai_generate(prompt, model=LLM_MODEL, temperature=0.0, max_output_tokens=400)
    try:
        parsed = _parse_json_from_text(raw)
        if not isinstance(parsed, dict):
            raise ValueError("Parsed JSON not an object")
        skills = parsed.get("skills") or []
        skills = [str(s).strip() for s in skills if str(s).strip()][:top_k]
        domain = str(parsed.get("domain") or "").strip()
        seniority = str(parsed.get("seniority") or "").strip()
        summary = str(parsed.get("summary") or "").strip()
        return {"skills": skills, "domain": domain, "seniority": seniority, "summary": summary}
    except Exception:
        # fallback: simple heuristic
        fallback_skills = []
        try:
            head = " ".join(jd_text.strip().splitlines()[:3])
            candidates = [p.strip() for p in head.replace("/", ",").split(",") if len(p.strip()) > 2]
            for c in candidates:
                if len(fallback_skills) >= top_k:
                    break
                token = c.split("(")[0].strip()
                if 3 <= len(token) <= 80:
                    fallback_skills.append(token)
        except Exception:
            pass
        return {"skills": fallback_skills, "domain": "", "seniority": "", "summary": ""}

def call_llm_for_questions(jd_title: str, skills: List[str]) -> List[Dict[str,str]]:
    """
    Stub for question generation; keep simple or replace with actual prompt later.
    """
    # simple template fallback if LLM not ready yet
    try:
        skill_list = ", ".join(skills)
        prompt = f"Generate interview questions for role {jd_title} covering skills: {skill_list}. Return JSON array of objects {{'skill','qtype','prompt'}}"
        raw = _genai_generate(prompt, model=LLM_MODEL, temperature=0.15, max_output_tokens=700)
        parsed = _parse_json_from_text(raw)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    # fallback: return simple templated questions
    out = []
    for s in (skills[:6] if skills else ["general"]):
        out.append({"skill": s, "qtype": "technical", "prompt": f"Explain a core concept related to {s}."})
        out.append({"skill": s, "qtype": "behavioral", "prompt": f"Tell me about a time you used {s}."})
    # limit to 12
    return out[:12]

# (optional) you can add Streamlit UI functions here or in another module that imports db_skeleton
