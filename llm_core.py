# llm_core.py
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ⚠️ Put YOUR API key here
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_MODEL = "gemini-2.5-flash"

# Global Client State
LLM_CLIENT = None
LLM_MODEL = DEFAULT_MODEL

def configure_llm(model="gemini-2.5-flash", api_base=None):
    global LLM_CLIENT, LLM_MODEL
    
    # 1. Try getting key from environment if not explicitly passed
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ CRITICAL: GEMINI_API_KEY is missing from environment variables.")
        return None

    try:
        # 2. Re-initialize the client
        LLM_CLIENT = genai.Client(api_key=api_key) 
        LLM_MODEL = model
        print(f"✅ LLM Client initialized with model: {model}")
    except Exception as e:
        print(f"❌ GENAI INIT ERROR: {e}")
        LLM_CLIENT = None
        
    return LLM_CLIENT

def _genai_generate(prompt, model=None, temperature=0.2, max_output_tokens=5000):
    global LLM_CLIENT
    
    if LLM_CLIENT is None:
        print("GENAI ERROR: LLM Client is not initialized. Cannot generate content.")
        return ""
        
    model = model or LLM_MODEL
    
    try:
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

def _parse_json_from_text(raw: str):
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