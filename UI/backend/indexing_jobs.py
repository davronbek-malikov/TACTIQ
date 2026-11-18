"""
indexing_jobs — mavjud Indexing pipeline'ni (run_indexing_pipeline) fonda ishga tushiradi.

Yangi indexing yozilmagan: aynan Indexing/indexing_pipeline.py chaqiriladi.
Bir vaqtda faqat bitta job. Tarix runtime/indexing_history.json da saqlanadi.
"""

import json
import threading  # indexing fonda (alohida thread) ishlaydi
import uuid       # job id
from dataclasses import asdict
from datetime import datetime, timezone

from indexing_pipeline import run_indexing_pipeline

import core
from documents import source_dir

HISTORY_FILE = core.RUNTIME_DIR / "indexing_history.json"
_jobs: dict[str, dict] = {}
_running = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))


def _save_history(job: dict) -> None:
    core.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    history = (load_history() + [job])[-50:]  # oxirgi 50 ta
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def start_job(source: str) -> dict:
    """Yangi indexing job. Boshqa job ishlayotgan bo'lsa — RuntimeError."""
    folder = source_dir(source)
    if not _running.acquire(blocking=False):
        raise RuntimeError("Boshqa indexing jarayoni ishlayapti. Tugashini kuting.")
    job = {"id": uuid.uuid4().hex[:12], "source": source, "status": "running", "started_at": _now(),
           "finished_at": None, "summary": None, "error": None}
    _jobs[job["id"]] = job
    threading.Thread(target=_run, args=(job, folder), daemon=True).start()
    return job


def _run(job: dict, folder) -> None:
    try:
        model = core.get_embedding_model()
        with core.qdrant_lock:
            summary = run_indexing_pipeline(core.settings, data_dir=folder, qdrant_store=core.get_store(),
                                            embedding_model=model, save_chunks=False)
        job["summary"] = asdict(summary)
        job["status"] = "failed" if summary.failed_files else "succeeded"
        if summary.failed_files:
            job["error"] = f"{len(summary.failed_files)} ta fayl o'qilmadi"
    except Exception as error:
        job["status"], job["error"] = "failed", f"{type(error).__name__}: {error}"
    finally:
        job["finished_at"] = _now()
        _save_history(job)
        _running.release()


def get_job(job_id: str) -> dict:
    if job_id not in _jobs:
        raise KeyError(job_id)
    return _jobs[job_id]
