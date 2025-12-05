# tests/test_llm.py
import types
import jd_prep_skeleton as mod

# Fake response shapes used by different SDK versions:
class FakeRespText:
    def __init__(self, text):
        self.text = text

class FakeCandidate:
    def __init__(self, text):
        self.content = types.SimpleNamespace(parts=[types.SimpleNamespace(text=text)])

class FakeRespCandidates:
    def __init__(self, text):
        self.candidates = [FakeCandidate(text)]

def test_genai_generate_with_text_shape(monkeypatch):
    # Build a fake client exposing .models.generate_content
    fake_client = types.SimpleNamespace()
    def fake_generate_content(model, contents, **kwargs):
        return FakeRespText("hello from .text")
    fake_client.models = types.SimpleNamespace(generate_content=fake_generate_content)

    # Inject into module and call helper
    mod.LLM_CLIENT = fake_client
    mod.LLM_MODEL = "fake-model"
    out = mod._genai_generate("prompt")
    assert "hello from .text" in out

def test_genai_generate_with_candidates_shape(monkeypatch):
    fake_client = types.SimpleNamespace()
    def fake_generate_content(model, contents, **kwargs):
        return FakeRespCandidates("hello from candidates")
    fake_client.models = types.SimpleNamespace(generate_content=fake_generate_content)

    mod.LLM_CLIENT = fake_client
    mod.LLM_MODEL = "fake-model"
    out = mod._genai_generate("prompt")
    assert "hello from candidates" in out

def test_generate_raises_if_not_configured():
    # Ensure LLM_CLIENT is None to simulate not configured
    mod.LLM_CLIENT = None
    try:
        mod._genai_generate("prompt")
        assert False, "Expected RuntimeError when LLM client not configured"
    except RuntimeError as e:
        assert "not configured" in str(e)
