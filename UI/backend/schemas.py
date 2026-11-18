"""
schemas — API kontraktlari (Pydantic). Frontend'dagi `src/lib/types.ts` bilan bir xil tuzilma.
"""

from typing import Literal, Optional  # Literal["qwen", "groq", "gemini"] — faqat shu qiymatlar

from pydantic import BaseModel, Field  # so'rov/javob shaklini tekshiradi (fastapi bilan keladi)

SourceName = Literal["sample_docs", "my_documents", "football_data"]
LlmName = Literal["qwen", "groq", "gemini"]
Mode = Literal["rag", "llm_only"]  # rag — hujjatlar asosida; llm_only — hujjatsiz (taqqoslash uchun)


class MetadataUpdate(BaseModel):
    """Sidecar (.meta.json) maydonlari. ID'lar faqat foydalanuvchi bilsa yoziladi — taxmin qilinmaydi."""

    document_type: Optional[str] = None
    topic: Optional[str] = None
    language: Optional[str] = None
    match_id: Optional[str] = None
    team_id: Optional[str] = None
    player_id: Optional[str] = None


class IndexRequest(BaseModel):
    source: SourceName = "my_documents"


class InvestigateRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    llm: LlmName = "qwen"
    mode: Mode = "rag"
    k: int = Field(default=5, ge=1, le=10)  # 5 — futbol datasida bitta o'yin bir necha chunk'ga bo'linadi
    collection: Optional[str] = None
    document_ids: list[str] = []   # bo'sh — barcha hujjatlar
    file_types: list[str] = []
    topics: list[str] = []
    languages: list[str] = []


class Evidence(BaseModel):
    """Modallikdan mustaqil dalil. Hozir faqat 'document'; keyinchalik 'video', 'statistic', 'image', 'audio'."""

    evidence_id: str
    kind: Literal["document", "statistic", "video", "image", "audio"] = "document"
    category: Literal[
        "verified_fact", "retrieved_document_evidence", "analytical_observation",
        "hypothesis", "recommendation", "cannot_be_verified",
    ] = "retrieved_document_evidence"
    title: str
    text: str
    score: Optional[float] = None
    document_id: Optional[str] = None
    source: Optional[str] = None
    page: Optional[int] = None
    chunk_index: Optional[int] = None
    metadata: dict = {}


class Step(BaseModel):
    id: str
    name: str
    status: Literal["done", "skipped", "failed"]
    duration_ms: Optional[float] = None
    detail: str = ""


class InvestigateResponse(BaseModel):
    question: str
    answer: Optional[str]
    answered: bool
    llm: str
    model: str
    mode: str = "rag"
    evidence: list[Evidence]
    steps: list[Step]
    error: Optional[str] = None
