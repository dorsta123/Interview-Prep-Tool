# jd_prep_skeleton.py
"""
LLM + App logic for JD Interview Prep.
This file contains Gemini integration and functions that call LLMs,
as well as the Streamlit UI (if you want to add it later).
"""

# --- Imports ---
from typing import Any, List, Dict
import os, json
from dotenv import load_dotenv

from google import genai 
from google.genai import types # Import types for configuration objects (if you used the suggested code)

# ⚠️ Put YOUR API key here
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_MODEL="gemini-2.5-flash"

# jd_prep_skeleton.py (configure_llm function)

def configure_llm(model="gemini-2.5-flash", api_base=None):
    global LLM_CLIENT, LLM_MODEL
    
    # ❌ REMOVE THIS LINE (Causes the AttributeError)
    # genai.configure(api_key=GEMINI_API_KEY) 
    
    try:
        # ✅ NEW SDK: Instantiate the client directly.
        # It automatically picks up the API key from the GEMINI_API_KEY environment variable.
        LLM_CLIENT = genai.Client() 
        LLM_MODEL = model
        print("LLM Client initialized successfully.")
    except Exception as e:
        print(f"GENAI ERROR: Client initialization failed. Check your API key or environment: {e}")
        LLM_CLIENT = None
        
    return LLM_CLIENT

# jd_prep_skeleton.py (_genai_generate function)

def _genai_generate(prompt, model=None, temperature=0.2, max_output_tokens=5000):
    global LLM_CLIENT
    
    if LLM_CLIENT is None:
        print("GENAI ERROR: LLM Client is not initialized. Cannot generate content.")
        return ""
        
    model = model or LLM_MODEL
    
    try:
        # ❌ OLD (Error): LLM_CLIENT.generate_content(...) 
        # ✅ CORRECTED: Use the .models attribute on the Client object
        response = LLM_CLIENT.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig( 
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
        )
        return response.text

    except Exception as e:
        print("GENAI ERROR:", e)
        return ""


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
    print(raw)

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
    Generate 25 interview questions for the role: {jd_title}
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


# (optional) you can add Streamlit UI functions here or in another module that imports db_skeleton

#only for testing purposes
'''configure_llm()
print(_genai_generate("hi"))
'''