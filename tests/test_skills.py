# tests/test_skills.py
import jd_prep_skeleton as mod

def test_call_llm_for_skills_with_clean_json(monkeypatch):
    raw = '{"skills":["python","sql"],"domain":"Data","seniority":"mid","summary":"Do stuff"}'
    monkeypatch.setattr(mod, "_genai_generate", lambda prompt, **kwargs: raw)
    out = mod.call_llm_for_skills("irrelevant jd text", top_k=6)
    assert out["skills"] == ["python", "sql"]
    assert out["domain"] == "Data"
    assert out["seniority"] == "mid"
    assert "Do stuff" in out["summary"]

def test_call_llm_for_skills_with_wrapped_json(monkeypatch):
    # LLM often returns explanatory text before JSON
    raw = 'Explanation...\\n{"skills":["react","redux"],"domain":"Frontend","seniority":"senior","summary":"Build UIs."}\\nThanks'
    monkeypatch.setattr(mod, "_genai_generate", lambda prompt, **kwargs: raw)
    out = mod.call_llm_for_skills("jd text", top_k=6)
    assert out["skills"] == ["react", "redux"]
    assert out["domain"] == "Frontend"

def test_call_llm_for_skills_fallback_on_malformed(monkeypatch):
    # Return nonsense to trigger fallback path
    raw = "I cannot produce JSON right now."
    monkeypatch.setattr(mod, "_genai_generate", lambda prompt, **kwargs: raw)
    jd_text = "We need a backend engineer with experience in Python, Django, REST APIs and PostgreSQL."
    out = mod.call_llm_for_skills(jd_text, top_k=4)
    # fallback should pick up sensible tokens from first lines
    assert "Python" in " ".join(out["skills"]) or "Django" in " ".join(out["skills"])
    assert out["domain"] == "" and out["seniority"] == ""
