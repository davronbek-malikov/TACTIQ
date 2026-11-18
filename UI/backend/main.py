"""
TACTIQ backend (FastAPI) — UI va ikki pipeline o'rtasidagi ko'prik.

Brauzer Qdrant'ga to'g'ridan-to'g'ri ulanmaydi: hammasi shu API orqali.

    python UI/backend/main.py            # http://localhost:8000  (hujjatlar: http://localhost:8000/docs)
"""

import os                # os.getenv — port, CORS manzillari, API kalitlar bormi
import urllib.request    # Ollama ishlayaptimi — oddiy HTTP so'rov

from fastapi import FastAPI, File, Form, HTTPException, UploadFile  # web API (pip install fastapi)
from fastapi.middleware.cors import CORSMiddleware  # brauzer :3000 dan :8000 ga so'rov yubora olsin

import core
import documents
from config.settings import is_offline
import indexing_jobs
import investigate
from llm_generation import LLM_PROVIDERS, get_model_name
from schemas import IndexRequest, InvestigateRequest, InvestigateResponse, MetadataUpdate

app = FastAPI(title="TACTIQ API", version=core.APP_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("TACTIQ_UI_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


def http_error(error: Exception) -> HTTPException:
    """Python xatosini mos HTTP javobga aylantiradi."""
    status = {FileNotFoundError: 404, KeyError: 404, PermissionError: 403, FileExistsError: 409,
              RuntimeError: 409, ValueError: 400}.get(type(error), 500)
    return HTTPException(status_code=status, detail=str(error))


# ---------- Tizim holati ----------

@app.get("/api/health")
def health():
    return {"status": "ok", "version": core.APP_VERSION}


@app.get("/api/system")
def system():
    """Overview va Settings sahifalari uchun haqiqiy holat (taxminiy son yo'q)."""
    qdrant = core.check_qdrant()
    collection = {"name": core.settings.qdrant_collection, "exists": False, "points": None, "vector_size": None}
    if qdrant["connected"] and collection["name"] in qdrant["collections"]:
        with core.qdrant_lock:
            store = core.get_store()
            collection.update(exists=True, points=store.count(), vector_size=store.get_vector_dimension())
    history = indexing_jobs.load_history()
    return {
        "version": core.APP_VERSION,
        "offline": is_offline(),  # TACTIQ_OFFLINE=1 — internetsiz rejim
        "qdrant": qdrant,
        "collection": collection,
        "indexed_documents": len(documents.chunk_counts()) if collection["exists"] else 0,
        "embedding_model": core.settings.embedding_model_name,
        "chunking": {"chunk_size": core.settings.chunk_size, "chunk_overlap": core.settings.chunk_overlap},
        "last_indexing": history[-1] if history else None,
        "document_dirs": {name: str(path) for name, path in documents.SOURCES.items()},
    }


@app.get("/api/collections")
def collections():
    qdrant = core.check_qdrant()
    if not qdrant["connected"]:
        raise HTTPException(503, f"Qdrant ulanmagan: {qdrant['error']}")
    with core.qdrant_lock:
        client = core.get_qdrant_client()
        return [{"name": name, "points": client.count(name, exact=True).count} for name in qdrant["collections"]]


@app.get("/api/llms")
def llms():
    """LLM'lar va ular sozlanganmi (API kalitlarning o'zi hech qachon qaytarilmaydi)."""
    result = []
    for name, provider in LLM_PROVIDERS.items():
        if provider["key_env"] and is_offline():
            ready, detail = False, "Offline rejim — cloud LLM o'chirilgan"
        elif provider["key_env"]:
            ready = bool(os.getenv(provider["key_env"]))
            detail = "API kalit sozlangan" if ready else f"{provider['key_env']} .env faylida yo'q"
        else:
            try:
                urllib.request.urlopen(provider["base_url"].replace("/v1", "/api/tags"), timeout=1)
                ready, detail = True, "Ollama ishlayapti"
            except Exception:
                ready, detail = False, "Ollama ishlamayapti (ollama serve)"
        result.append({"id": name, "model": get_model_name(name), "local": provider["key_env"] is None,
                       "ready": ready, "detail": detail})
    return result


# ---------- Hujjatlar (Knowledge) ----------

@app.get("/api/documents")
def list_documents():
    return documents.list_documents()


@app.get("/api/documents/{source}/{filename}")
def document_detail(source: str, filename: str):
    try:
        return documents.document_detail(source, filename)
    except Exception as error:
        raise http_error(error)


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    overwrite: bool = Form(False),
    document_type: str = Form(""), topic: str = Form(""), language: str = Form(""),
    match_id: str = Form(""), team_id: str = Form(""), player_id: str = Form(""),
):
    content = await file.read(documents.MAX_UPLOAD_BYTES + 1)
    metadata = {"document_type": document_type, "topic": topic, "language": language,
                "match_id": match_id, "team_id": team_id, "player_id": player_id}
    try:
        return documents.save_upload(file.filename, content, metadata, overwrite)
    except Exception as error:
        raise http_error(error)


@app.put("/api/documents/{source}/{filename}/metadata")
def update_metadata(source: str, filename: str, body: MetadataUpdate):
    try:
        return documents.update_metadata(source, filename, body.model_dump())
    except Exception as error:
        raise http_error(error)


@app.delete("/api/documents/{source}/{filename}")
def delete_document(source: str, filename: str):
    try:
        documents.delete_document(source, filename)
        return {"deleted": filename}
    except Exception as error:
        raise http_error(error)


# ---------- Indexing ----------

@app.post("/api/indexing/jobs")
def start_indexing(body: IndexRequest):
    try:
        return indexing_jobs.start_job(body.source)
    except Exception as error:
        raise http_error(error)


@app.get("/api/indexing/jobs/{job_id}")
def indexing_job(job_id: str):
    try:
        return indexing_jobs.get_job(job_id)
    except Exception as error:
        raise http_error(error)


@app.get("/api/indexing/history")
def indexing_history():
    return list(reversed(indexing_jobs.load_history()))


# ---------- Investigate (Retrieval & Generation) ----------

@app.post("/api/investigate", response_model=InvestigateResponse)
def run_investigation(body: InvestigateRequest):
    qdrant = core.check_qdrant()
    if body.mode == "rag" and not qdrant["connected"]:  # LLM only rejimiga Qdrant kerak emas
        raise HTTPException(503, f"Qdrant ulanmagan: {qdrant['error']}")
    try:
        return investigate.run(body)
    except Exception as error:
        raise http_error(error)


@app.on_event("shutdown")
def shutdown():
    core.close()


if __name__ == "__main__":
    import uvicorn  # FastAPI ilovasini ishga tushiradigan server (pip install uvicorn)

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("TACTIQ_API_PORT", "8000")))
