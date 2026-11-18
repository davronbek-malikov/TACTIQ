"""Backend API testlari: vaqtinchalik papkalar + local Qdrant (Docker kerak emas), LLM soxta."""

import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Sozlamalar import paytida o'qiladi — shuning uchun env'ni oldin beramiz.
TMP = Path(tempfile.mkdtemp(prefix="tactiq_api_test_"))
os.environ["QDRANT_LOCAL_PATH"] = str(TMP / "qdrant")
os.environ["QDRANT_COLLECTION"] = "api_test"
os.environ["TACTIQ_CHUNK_SIZE"], os.environ["TACTIQ_CHUNK_OVERLAP"] = "500", "50"  # kutilgan chunk soni .env'ga bog'liq bo'lmasin
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # UI/backend

from fastapi.testclient import TestClient  # noqa: E402

import core  # noqa: E402
import documents  # noqa: E402
import investigate  # noqa: E402
from main import app  # noqa: E402

SAMPLE_DIR = core.PROJECT_ROOT / "Indexing" / "01_documents" / "sample_docs"


@pytest.fixture(scope="module")
def client():
    sample = TMP / "sample_docs"
    mine = TMP / "my_documents"
    shutil.copytree(SAMPLE_DIR, sample)
    mine.mkdir()
    documents.SOURCES = {"sample_docs": sample, "my_documents": mine}  # haqiqiy papkalarga tegmaymiz
    core.RUNTIME_DIR = TMP / "runtime"
    import indexing_jobs
    indexing_jobs.HISTORY_FILE = core.RUNTIME_DIR / "history.json"
    with TestClient(app) as test_client:
        yield test_client
    core.close()


def wait_for_job(client, job_id):
    for _ in range(300):
        job = client.get(f"/api/indexing/jobs/{job_id}").json()
        if job["status"] != "running":
            return job
        time.sleep(0.2)
    raise TimeoutError(job_id)


def wait_idle():
    """Avtomatik index (upload / metadata) tugashini kutadi."""
    import indexing_jobs
    for _ in range(300):
        if not indexing_jobs._running.locked() and not indexing_jobs._pending:
            return
        time.sleep(0.2)
    raise TimeoutError("auto-index")


def test_health_and_system_before_indexing(client):
    assert client.get("/api/health").json()["status"] == "ok"
    system = client.get("/api/system").json()
    assert system["qdrant"]["connected"] is True and system["qdrant"]["mode"] == "local"
    assert system["collection"]["exists"] is False
    assert system["indexed_documents"] == 0


def test_llms_never_expose_keys(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "secret-groq-key-123")
    response = client.get("/api/llms")
    assert [llm["id"] for llm in response.json()] == ["qwen", "groq", "gemini"]
    assert "secret-groq-key-123" not in response.text
    groq = next(llm for llm in response.json() if llm["id"] == "groq")
    assert groq["ready"] is True


def test_upload_validation(client):
    bad = client.post("/api/documents/upload", files={"file": ("notes.exe", b"x")})
    assert bad.status_code == 400
    clash = client.post("/api/documents/upload", files={"file": ("low_block.txt", b"x")})
    assert clash.status_code == 400
    empty = client.post("/api/documents/upload", files={"file": ("empty.txt", b"")})
    assert empty.status_code == 400
    traversal = client.get("/api/documents/my_documents/..%2F..%2Fsecret.txt")
    assert traversal.status_code == 404


def test_upload_index_and_details(client):
    uploaded = client.post(
        "/api/documents/upload",
        files={"file": ("rest_defence.txt", b"Rest defence means players who stay behind the ball while attacking.")},
        data={"topic": "rest_defence", "language": "en"},
    )
    assert uploaded.status_code == 200, uploaded.text
    auto_job = uploaded.json()["indexing_job"]  # upload'dan keyin index o'zi boshlanadi
    assert auto_job["source"] == "my_documents"
    assert wait_for_job(client, auto_job["id"])["status"] == "succeeded"
    assert client.post("/api/documents/upload", files={"file": ("rest_defence.txt", b"again")}).status_code == 409

    job = client.post("/api/indexing/jobs", json={"source": "sample_docs"}).json()
    assert wait_for_job(client, job["id"])["status"] == "succeeded"

    rows = {row["filename"]: row for row in client.get("/api/documents").json()}
    assert rows["counterpressing.pdf"]["chunks"] == 2
    assert rows["rest_defence.txt"]["indexed"] is True
    assert rows["rest_defence.txt"]["metadata"]["topic"] == "rest_defence"

    system = client.get("/api/system").json()
    assert system["collection"]["points"] == 8 and system["collection"]["vector_size"] == 384
    assert system["indexed_documents"] == 6
    assert system["last_indexing"]["status"] == "succeeded"

    detail = client.get("/api/documents/sample_docs/counterpressing.pdf").json()
    assert [page["page"] for page in detail["pages"]] == [1, 2]
    assert len(detail["chunks"]) == 2 and detail["metadata"]["topic"] == "counterpressing"
    assert detail["editable"] is False


def test_metadata_editing_rules(client):
    ok = client.put("/api/documents/my_documents/rest_defence.txt/metadata", json={"topic": "rest_defence_v2"})
    assert ok.status_code == 200 and ok.json()["topic"] == "rest_defence_v2" and ok.json()["team_id"] is None
    forbidden = client.put("/api/documents/sample_docs/low_block.txt/metadata", json={"topic": "x"})
    assert forbidden.status_code == 403
    wait_idle()  # metadata o'zgargach qayta index avtomatik ishladi


def test_investigate_answer_no_answer_and_llm_error(client, monkeypatch):
    monkeypatch.setattr(investigate, "generate_answer", lambda messages, llm: "Pressing right after losing the ball [1].")
    result = client.post("/api/investigate", json={"question": "What is counterpressing?", "llm": "groq"}).json()
    assert result["answered"] is True
    assert result["evidence"][0]["source"] == "counterpressing.pdf"
    assert result["evidence"][0]["category"] == "retrieved_document_evidence"
    assert [s["id"] for s in result["steps"]] == ["01", "02", "03", "04", "05", "06", "07"]
    assert all(s["status"] == "done" for s in result["steps"])

    filtered = client.post("/api/investigate", json={"question": "What is counterpressing?", "llm": "groq",
                                                     "topics": ["low_block"]}).json()
    assert all(e["metadata"]["topic"] == "low_block" for e in filtered["evidence"])

    unknown = client.post("/api/investigate", json={"question": "Who won the 2022 World Cup?", "llm": "groq"}).json()
    assert unknown["answered"] is False and unknown["evidence"] == []
    assert [s["status"] for s in unknown["steps"]][4:6] == ["skipped", "skipped"]

    def broken_llm(messages, llm):
        raise ValueError("GROQ_API_KEY topilmadi")

    monkeypatch.setattr(investigate, "generate_answer", broken_llm)
    failed = client.post("/api/investigate", json={"question": "What is a low block?", "llm": "groq"}).json()
    assert failed["answered"] is False and failed["answer"] is None
    assert "GROQ_API_KEY" in failed["error"] and failed["evidence"]
    assert failed["steps"][-1]["status"] == "failed"


def test_llm_only_mode_uses_no_documents(client, monkeypatch):
    sent = {}

    def fake_llm(messages, llm):
        sent["messages"] = messages
        return "Model's own answer."

    monkeypatch.setattr(investigate, "generate_answer", fake_llm)
    result = client.post("/api/investigate", json={"question": "What is counterpressing?", "llm": "gemini",
                                                   "mode": "llm_only"}).json()
    assert result["mode"] == "llm_only" and result["answered"] is True
    assert result["evidence"] == []
    assert [s["status"] for s in result["steps"]] == ["done", "skipped", "skipped", "skipped", "skipped", "done", "done"]
    assert "Context" not in sent["messages"][1]["content"]           # hujjat konteksti yuborilmagan
    assert sent["messages"][1]["content"] == "What is counterpressing?"


def test_delete_document(client):
    assert client.delete("/api/documents/sample_docs/low_block.txt").status_code == 403
    assert client.delete("/api/documents/my_documents/rest_defence.txt").status_code == 200
    rows = [row["filename"] for row in client.get("/api/documents").json()]
    assert "rest_defence.txt" not in rows
    assert client.get("/api/system").json()["collection"]["points"] == 7
