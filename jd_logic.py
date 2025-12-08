from typing import Any, List, Dict
from llm_core import configure_llm, _genai_generate, _parse_json_from_text, DEFAULT_MODEL
import prompts  # <--- Make sure to import your prompts file


def call_llm_for_skills(jd_text: str, top_k: int = 6):
    prompt = f"""
        Extract the top {top_k} skills, one-word domain, seniority, and 1–2 sentence summary
        from the following job description:

        {jd_text}

        Return ONLY JSON:
        {{
        "skills": [...],
        "domain": "...",
        "seniority": "...",
        "summary": "..."
        }}
        """
    raw = _genai_generate(prompt)

    try:
        parsed = _parse_json_from_text(raw)
        if isinstance(parsed, dict):
            return parsed
    except:
        pass

    # LAST-RESORT fallback (never breaks)
    return {
        "skills": ["Skill A", "Skill B", "Skill C"][:top_k],
        "domain": "general",
        "seniority": "mid",
        "summary": "Summary unavailable due to model error."
    }

def call_llm_for_questions(jd_title, skills):
    prompt = f"""
    Generate 40 interview questions for the role: {jd_title}
    The skills to target are: {", ".join(skills)}

    Return ONLY JSON list:
    [
    {{"skill": "...", "qtype": "...", "prompt": "..."}},
    ...
    ]
    """
    raw = _genai_generate(prompt)
    try:
        parsed = _parse_json_from_text(raw)
        if isinstance(parsed, list):
            return parsed
    except:
        pass

    # fallback
    out = []
    for s in skills[:5]:
        out.append({"skill": s, "qtype": "technical", "prompt": f"What is {s}?"})
        out.append({"skill": s, "qtype": "behavioral", "prompt": f"Describe a time you used {s}."})
    return out


def generate_answer(question_text: str) -> str:
    """Generates a sample answer for a specific question."""
    # This uses the new prompt we just added
    prompt = prompts.get_answer_prompt(question_text)
    
    # We reuse the existing generation function
    response = _genai_generate(prompt)
    print(response)
    return response