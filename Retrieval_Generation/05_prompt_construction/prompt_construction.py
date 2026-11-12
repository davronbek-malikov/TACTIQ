"""
05 — Prompt Construction: savol + topilgan chunk'larni LLM uchun bitta xabarga birlashtiradi.

System prompt LLM'ga qoida beradi: FAQAT kontekst asosida javob ber, bo'lmasa "bilmayman" de, manbani [1] kabi ko'rsat.

    python Retrieval_Generation/05_prompt_construction/prompt_construction.py

Keyingi bosqich: 06 — LLM Generation
"""

SYSTEM_PROMPT = (
    "You are TACTIQ, a football analysis assistant. "
    "Answer ONLY using the context. If the context does not contain the answer, say that you don't know. "
    "Cite the sources you use as [1], [2]. Answer in the same language as the question."
)


def build_context(chunks: list) -> str:
    """Chunk'larni raqamlab bitta matnga yig'adi: [1] (manba, sahifa) + matn."""
    parts = []
    for number, chunk in enumerate(chunks, start=1):
        parts.append(f"[{number}] ({chunk.source}, page {chunk.page})\n{chunk.text}")
    return "\n\n".join(parts)


def build_messages(question: str, chunks: list) -> list[dict]:
    """LLM'ga yuboriladigan xabarlar: system (qoidalar) + user (kontekst + savol)."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{build_context(chunks)}\n\nQuestion: {question}"},
    ]


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import rag_paths  # noqa: F401
    from config.settings import get_settings
    from embedding_model import EmbeddingModel
    from query_embedding import embed_question
    from similarity_search import similarity_search
    from top_k_retrieval import select_top_k
    from user_question import SAMPLE_QUESTIONS
    from vector_database import create_qdrant_client

    settings = get_settings()
    model = EmbeddingModel(settings.embedding_model_name)
    client = create_qdrant_client(settings.qdrant_url, settings.qdrant_api_key, settings.qdrant_local_path)

    question = SAMPLE_QUESTIONS[0]
    chunks = select_top_k(similarity_search(client, settings.qdrant_collection, embed_question(question, model)))
    for message in build_messages(question, chunks):
        print(f"===== {message['role']} =====\n{message['content']}\n")
    client.close()
