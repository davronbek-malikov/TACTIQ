"""
RAG Pipeline — Retrieval & Generation: 7 bosqichni ketma-ket ishga tushiradi.

    01 Savol -> 02 Embedding -> 03 Similarity Search -> 04 Top-k -> 05 Prompt -> 06 LLM -> 07 Javob + Manbalar

    python Retrieval_Generation/rag_pipeline.py --llm qwen
    python Retrieval_Generation/rag_pipeline.py --llm groq --question "What is a low block?"
"""

import argparse
import sys

import rag_paths  # noqa: F401

from config.settings import Settings, get_settings
from embedding_model import EmbeddingModel
from vector_database import create_qdrant_client

from user_question import SAMPLE_QUESTIONS, prepare_question   # 01
from query_embedding import embed_question                      # 02
from similarity_search import similarity_search                 # 03
from top_k_retrieval import select_top_k                        # 04
from prompt_construction import build_messages                  # 05
from llm_generation import LLM_PROVIDERS, generate_answer_with_fallback  # 06
from answer_sources import RagAnswer, print_answer              # 07

NO_ANSWER = "Hujjatlarda bu savolga javob topilmadi."


class RagPipeline:
    """Embedding model va Qdrant ulanishi bir marta ochiladi, keyin istalgancha savol berish mumkin."""

    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        self.model = EmbeddingModel(self.settings.embedding_model_name)
        self.client = create_qdrant_client(
            self.settings.qdrant_url, self.settings.qdrant_api_key, self.settings.qdrant_local_path
        )

    def ask(self, question: str, llm: str = "qwen", k: int = 3) -> RagAnswer:
        question = prepare_question(question)                                                # 01
        query_vector = embed_question(question, self.model)                                  # 02
        points = similarity_search(self.client, self.settings.qdrant_collection, query_vector)  # 03
        chunks = select_top_k(points, k=k)                                                   # 04

        if not chunks:  # mos chunk yo'q — LLM'ni chaqirmaymiz, javobni o'ylab topmaymiz
            return RagAnswer(question=question, answer=NO_ANSWER, llm=llm)

        messages = build_messages(question, chunks)                                          # 05
        answer, used = generate_answer_with_fallback(messages, llm)                          # 06 (+ zaxira LLM)
        return RagAnswer(question=question, answer=answer, llm=used, sources=chunks)         # 07

    def close(self) -> None:
        self.client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="TACTIQ RAG: savol -> javob + manbalar")
    parser.add_argument("--question", default=SAMPLE_QUESTIONS[0])
    parser.add_argument("--llm", choices=list(LLM_PROVIDERS), default="qwen")
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # Windows konsoli maxsus belgilarda yiqilmasin

    pipeline = RagPipeline()
    try:
        print_answer(pipeline.ask(args.question, args.llm, args.k))
    except Exception as error:
        print(f"\nXATO ({args.llm}): {type(error).__name__}: {error}")
        if args.llm == "qwen":
            print("Ollama ishlayotganini tekshiring: ollama pull qwen2.5:1.5b")
        return 1
    finally:
        pipeline.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
