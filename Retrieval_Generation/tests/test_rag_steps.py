"""Retrieval & Generation testlari: har bir bosqich + to'liq pipeline (local Qdrant, soxta LLM)."""

from types import SimpleNamespace

import pytest

import llm_generation
from answer_sources import RagAnswer, format_sources
from prompt_construction import SYSTEM_PROMPT, build_messages
from top_k_retrieval import RetrievedChunk, select_top_k
from user_question import prepare_question


def fake_point(score, source="a.pdf", page=1, text="some text"):
    return SimpleNamespace(score=score, payload={"chunk_text": text, "source": source, "page": page})


# ---------- 01 User Question ----------

def test_prepare_question_strips_and_rejects_empty():
    assert prepare_question("  What is a low block?  ") == "What is a low block?"
    with pytest.raises(ValueError):
        prepare_question("   ")


# ---------- 04 Top-k Retrieval ----------

def test_select_top_k_keeps_order_and_limit():
    points = [fake_point(0.9, "a.pdf"), fake_point(0.8, "b.md"), fake_point(0.7, "c.txt"), fake_point(0.6, "d.md")]
    chunks = select_top_k(points, k=3)
    assert [c.source for c in chunks] == ["a.pdf", "b.md", "c.txt"]
    assert chunks[0] == RetrievedChunk(text="some text", source="a.pdf", page=1, score=0.9)


def test_select_top_k_drops_low_scores():
    points = [fake_point(0.5), fake_point(0.2), fake_point(0.1)]
    assert len(select_top_k(points, k=3, min_score=0.3)) == 1
    assert select_top_k([fake_point(0.1)], min_score=0.3) == []


# ---------- 05 Prompt Construction ----------

def test_build_messages_contains_rules_context_and_question():
    chunks = [RetrievedChunk("Press high.", "press.docx", None, 0.8), RetrievedChunk("Win it back.", "cp.pdf", 2, 0.7)]
    system, user = build_messages("What is pressing?", chunks)
    assert system == {"role": "system", "content": SYSTEM_PROMPT}
    assert "ONLY" in system["content"]
    assert "[1] (press.docx, page None)\nPress high." in user["content"]
    assert "[2] (cp.pdf, page 2)\nWin it back." in user["content"]
    assert user["content"].endswith("Question: What is pressing?")


# ---------- 06 LLM Generation ----------

def test_three_llms_are_configured():
    assert set(llm_generation.LLM_PROVIDERS) == {"qwen", "groq", "gemini"}


def test_missing_api_key_gives_clear_error(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        llm_generation.generate_answer([{"role": "user", "content": "hi"}], "groq")


def test_generate_answer_calls_openai_compatible_api(monkeypatch):
    calls = {}

    class FakeOpenAI:
        def __init__(self, base_url, api_key):
            calls["base_url"], calls["api_key"] = base_url, api_key
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

        def create(self, model, messages, temperature):
            calls["model"] = model
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="answer [1]"))])

    monkeypatch.setattr(llm_generation, "OpenAI", FakeOpenAI)
    monkeypatch.setenv("TACTIQ_OFFLINE", "0")  # .env'da offline yoqilgan bo'lsa ham test online rejimda
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "my-gemini")

    assert llm_generation.generate_answer([{"role": "user", "content": "hi"}], "gemini") == "answer [1]"
    assert calls == {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                     "api_key": "test-key", "model": "my-gemini"}


def test_offline_mode_blocks_cloud_llms(monkeypatch):
    monkeypatch.setenv("TACTIQ_OFFLINE", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    with pytest.raises(RuntimeError, match="Offline"):
        llm_generation.generate_answer([{"role": "user", "content": "hi"}], "gemini")


def test_offline_mode_allows_local_qwen(monkeypatch):
    monkeypatch.setenv("TACTIQ_OFFLINE", "1")
    fake = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
        create=lambda **_: SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="local"))]))))
    monkeypatch.setattr(llm_generation, "OpenAI", lambda base_url, api_key: fake)
    assert llm_generation.generate_answer([{"role": "user", "content": "hi"}], "qwen") == "local"


def test_offline_mode_rejects_qdrant_cloud(monkeypatch):
    from config.settings import get_settings

    monkeypatch.setenv("TACTIQ_OFFLINE", "1")
    monkeypatch.setenv("QDRANT_URL", "https://xxxx.cloud.qdrant.io:6333")
    monkeypatch.delenv("QDRANT_LOCAL_PATH", raising=False)
    with pytest.raises(ValueError, match="Offline"):
        get_settings()


# ---------- 07 Answer + Sources ----------

def test_format_sources():
    chunks = [RetrievedChunk("t", "cp.pdf", 1, 0.712), RetrievedChunk("t", "low_block.txt", None, 0.5)]
    assert format_sources(chunks) == ["[1] cp.pdf, page 1 (score 0.71)", "[2] low_block.txt (score 0.50)"]


# ---------- To'liq pipeline: haqiqiy embedding + haqiqiy Qdrant (local mode, Docker'siz), LLM soxta ----------

@pytest.fixture
def indexed_settings(tmp_path):
    """Namunaviy hujjatlarni vaqtinchalik local Qdrant'ga index qiladi."""
    from config.settings import Settings
    from indexing_pipeline import run_indexing_pipeline

    settings = Settings(qdrant_local_path=str(tmp_path / "qdrant"), qdrant_collection="rag_test")
    run_indexing_pipeline(settings, save_chunks=False)
    return settings


@pytest.mark.slow
def test_rag_pipeline_end_to_end(indexed_settings, monkeypatch):
    import rag_pipeline

    sent = {}

    def fake_llm(messages, llm):
        sent["messages"], sent["llm"] = messages, llm
        return "Counterpressing means pressing right after losing the ball [1]."

    monkeypatch.setattr(rag_pipeline, "generate_answer", fake_llm)
    pipeline = rag_pipeline.RagPipeline(indexed_settings)
    try:
        result = pipeline.ask("What is counterpressing?", llm="groq")
        assert isinstance(result, RagAnswer)
        assert result.sources[0].source == "counterpressing.pdf"        # to'g'ri hujjat birinchi topildi
        assert len(result.sources) <= 3
        assert "counterpressing.pdf" in sent["messages"][1]["content"]   # kontekst LLM'ga yuborildi
        assert sent["llm"] == "groq"

        unrelated = pipeline.ask("Who won the 2022 World Cup?", llm="groq")
        assert unrelated.answer == rag_pipeline.NO_ANSWER                # mos chunk yo'q -> LLM chaqirilmaydi
        assert unrelated.sources == []
    finally:
        pipeline.close()
