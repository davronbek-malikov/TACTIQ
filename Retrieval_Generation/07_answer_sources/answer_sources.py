"""
07 — Answer + Sources: javob va manbalarni foydalanuvchiga qaytaradi.

Manba ko'rsatish — RAG'ning asosiy afzalligi: javobni tekshirish mumkin.

    python Retrieval_Generation/07_answer_sources/answer_sources.py
"""

from dataclasses import dataclass, field


@dataclass
class RagAnswer:
    question: str
    answer: str
    llm: str
    sources: list = field(default_factory=list)  # RetrievedChunk'lar (04-bosqichdan)


def format_sources(chunks: list) -> list[str]:
    """[1] counterpressing.pdf, page 1 (score 0.71)"""
    lines = []
    for number, chunk in enumerate(chunks, start=1):
        page = f", page {chunk.page}" if chunk.page else ""
        lines.append(f"[{number}] {chunk.source}{page} (score {chunk.score:.2f})")
    return lines


def print_answer(result: RagAnswer) -> None:
    print(f"\nSavol:  {result.question}")
    print(f"LLM:    {result.llm}")
    print(f"\nJavob:\n{result.answer}")
    print("\nManbalar:")
    for line in format_sources(result.sources) or ["(manba topilmadi)"]:
        print(f"  {line}")


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from rag_pipeline import main

    sys.exit(main())  # 07 — oxirgi bosqich, shuning uchun butun pipeline ishlaydi
