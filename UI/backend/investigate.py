"""
investigate — Retrieval & Generation'ning 7 bosqichini ishga tushiradi va har bir bosqich vaqtini qaytaradi.

Bosqich funksiyalari Retrieval_Generation papkasidan olinadi (qayta yozilmagan).
UI'dagi progress faqat HAQIQATDA bajarilgan bosqichlarni ko'rsatadi.
"""

import time  # time.perf_counter() — har bir bosqich vaqti (ms)

from qdrant_client.models import FieldCondition, Filter, MatchAny  # UI filter: "topic IN [...]"

from user_question import prepare_question                 # 01
from query_embedding import embed_question                  # 02
from similarity_search import similarity_search             # 03
from top_k_retrieval import select_top_k                    # 04
from prompt_construction import build_messages              # 05
from llm_generation import generate_answer, get_model_name  # 06
from rag_pipeline import NO_ANSWER                          # 07 (mos chunk yo'q bo'lganda)

import core
from schemas import Evidence, InvestigateRequest, InvestigateResponse, Step

STEP_NAMES = {
    "01": "User Question", "02": "Query Embedding", "03": "Similarity Search", "04": "Top-k Retrieval",
    "05": "Prompt Construction", "06": "LLM Generation", "07": "Answer + Sources",
}


# LLM only rejimi: hujjat yo'q, kontekst qoidalari yo'q — model faqat o'z bilimi bilan javob beradi.
LLM_ONLY_SYSTEM_PROMPT = "You are a football analysis assistant. Answer the question. Answer in the same language as the question."


def run_llm_only(request: InvestigateRequest) -> InvestigateResponse:
    """RAG'siz: savol to'g'ridan-to'g'ri LLM'ga. 02–05 bosqichlar ishlamaydi, manba bo'lmaydi."""
    model_name = get_model_name(request.llm)
    start = time.perf_counter()
    question = prepare_question(request.question)
    steps = [Step(id="01", name=STEP_NAMES["01"], status="done", duration_ms=round((time.perf_counter() - start) * 1000, 1))]
    for step_id in ("02", "03", "04", "05"):
        steps.append(Step(id=step_id, name=STEP_NAMES[step_id], status="skipped", detail="RAG o'chirilgan"))

    messages = [{"role": "system", "content": LLM_ONLY_SYSTEM_PROMPT}, {"role": "user", "content": question}]
    start = time.perf_counter()
    try:
        answer = generate_answer(messages, request.llm)
    except Exception as error:
        steps.append(Step(id="06", name=STEP_NAMES["06"], status="failed", detail=type(error).__name__))
        return InvestigateResponse(question=question, answer=None, answered=False, llm=request.llm, model=model_name,
                                   mode="llm_only", evidence=[], steps=steps, error=f"{type(error).__name__}: {error}")
    steps.append(Step(id="06", name=STEP_NAMES["06"], status="done",
                      duration_ms=round((time.perf_counter() - start) * 1000, 1), detail=model_name))
    steps.append(Step(id="07", name=STEP_NAMES["07"], status="done", detail="manba yo'q — modelning o'z bilimi"))
    return InvestigateResponse(question=question, answer=answer, answered=True, llm=request.llm, model=model_name,
                               mode="llm_only", evidence=[], steps=steps)


def build_filter(request: InvestigateRequest):
    """UI'dagi tanlovlardan Qdrant filter yasaydi (hech narsa tanlanmagan bo'lsa — None)."""
    conditions = []
    for key, values in [("document_id", request.document_ids), ("file_type", request.file_types),
                        ("topic", request.topics), ("language", request.languages)]:
        if values:
            conditions.append(FieldCondition(key=key, match=MatchAny(any=values)))
    return Filter(must=conditions) if conditions else None


def run(request: InvestigateRequest) -> InvestigateResponse:
    if request.mode == "llm_only":
        return run_llm_only(request)
    steps: list[Step] = []

    def timed(step_id: str, func, detail=lambda result: ""):
        start = time.perf_counter()
        result = func()
        steps.append(Step(id=step_id, name=STEP_NAMES[step_id], status="done",
                          duration_ms=round((time.perf_counter() - start) * 1000, 1), detail=detail(result)))
        return result

    collection = request.collection or core.settings.qdrant_collection
    model_name = get_model_name(request.llm)

    question = timed("01", lambda: prepare_question(request.question))
    model = core.get_embedding_model()
    vector = timed("02", lambda: embed_question(question, model), lambda v: f"{len(v)} ta son")
    with core.qdrant_lock:
        points = timed("03", lambda: similarity_search(core.get_qdrant_client(), collection, vector,
                                                       query_filter=build_filter(request)),
                       lambda p: f"{len(p)} ta chunk solishtirildi")
    chunks = timed("04", lambda: select_top_k(points, k=request.k), lambda c: f"{len(c)} ta mos chunk")

    evidence = [
        Evidence(evidence_id=str(n), title=f"{c.source}" + (f" · page {c.page}" if c.page else ""), text=c.text,
                 score=round(c.score, 4), source=c.source, page=c.page,
                 document_id=p.payload.get("document_id"), chunk_index=p.payload.get("chunk_index"),
                 metadata={k: p.payload.get(k) for k in ("file_type", "topic", "language", "document_type")})
        for n, (c, p) in enumerate(zip(chunks, points), start=1)
    ]

    if not chunks:  # mos dalil yo'q — LLM chaqirilmaydi, javob o'ylab topilmaydi
        for step_id in ("05", "06"):
            steps.append(Step(id=step_id, name=STEP_NAMES[step_id], status="skipped", detail="mos chunk yo'q"))
        steps.append(Step(id="07", name=STEP_NAMES["07"], status="done", detail="manba yo'q"))
        return InvestigateResponse(question=question, answer=NO_ANSWER, answered=False, llm=request.llm,
                                   model=model_name, evidence=[], steps=steps)

    messages = timed("05", lambda: build_messages(question, chunks), lambda m: f"{len(m)} ta xabar")
    try:
        answer = timed("06", lambda: generate_answer(messages, request.llm), lambda a: model_name)
    except Exception as error:  # LLM sozlanmagan yoki ishlamayapti — halol xato
        steps.append(Step(id="06", name=STEP_NAMES["06"], status="failed", detail=type(error).__name__))
        return InvestigateResponse(question=question, answer=None, answered=False, llm=request.llm,
                                   model=model_name, evidence=evidence, steps=steps,
                                   error=f"{type(error).__name__}: {error}")

    steps.append(Step(id="07", name=STEP_NAMES["07"], status="done", detail=f"{len(evidence)} ta manba"))
    return InvestigateResponse(question=question, answer=answer, answered=True, llm=request.llm,
                               model=model_name, evidence=evidence, steps=steps)
