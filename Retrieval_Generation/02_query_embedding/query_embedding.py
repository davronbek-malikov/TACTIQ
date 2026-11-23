import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # Retrieval_Generation/
import rag_paths  # noqa: E402,F401

from embedding_model import EmbeddingModel  # noqa: E402  — Indexing/04 dan (ko'chirilmaydi, import qilinadi)


def embed_question(question: str, model: EmbeddingModel) -> list[float]:
    """Savol -> vector (oddiy Python list)."""
    return model.embed([question])[0].tolist()


if __name__ == "__main__":
    from config.settings import get_settings
    from user_question import SAMPLE_QUESTIONS

    model = EmbeddingModel(get_settings().embedding_model_name)
    question = SAMPLE_QUESTIONS[0]
    vector = embed_question(question, model)
    print(f"Savol:  {question}")
    print(f"Vector: {len(vector)} ta son -> {[round(x, 3) for x in vector[:6]]} ...")
