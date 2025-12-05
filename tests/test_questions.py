# tests/test_questions.py
import jd_prep_skeleton as mod

def test_call_llm_for_questions_with_clean_json(monkeypatch):
    raw = '[{"skill":"python","qtype":"technical","prompt":"Explain list comprehensions."},{"skill":"sql","qtype":"behavioral","prompt":"Tell me about optimizing queries."}]'
    monkeypatch.setattr(mod, "_genai_generate", lambda prompt, **kwargs: raw)
    out = mod.call_llm_for_questions("Backend Engineer", ["python", "sql"])
    assert isinstance(out, list) and len(out) == 2
    assert out[0]["skill"] == "python"
    assert out[0]["qtype"] == "technical"

def test_call_llm_for_questions_with_wrapped_json(monkeypatch):
    raw = 'Note: below are questions\\n[{"skill":"react","qtype":"technical","prompt":"Explain the reconciliation algorithm."}]\\nend'
    monkeypatch.setattr(mod, "_genai_generate", lambda prompt, **kwargs: raw)
    out = mod.call_llm_for_questions("Frontend", ["react"])
    assert out and out[0]["skill"] == "react"

def test_call_llm_for_questions_fallback(monkeypatch):
    # malformed output to trigger fallback
    raw = "sorry cannot generate"
    monkeypatch.setattr(mod, "_genai_generate", lambda prompt, **kwargs: raw)
    out = mod.call_llm_for_questions("SRE", ["terraform", "prometheus"])
    assert isinstance(out, list)
    assert len(out) <= 12
    # ensure questions are about provided skills
    assert any("terraform" in q["prompt"] for q in out) or any("prometheus" in q["prompt"] for q in out)
