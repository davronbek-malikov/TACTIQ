
import os
import re
import sys
from pathlib import Path

from openai import OpenAI  # bitta client — Qwen (Ollama), Groq, Gemini (pip install openai)
from openai import APIError  # barcha API xatolari: 429 limit, 400/401 kalit, tarmoq, 5xx server

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # Retrieval_Generation/
import rag_paths  # noqa: E402,F401
from config.settings import is_offline  # noqa: E402  — .env faylini yuklaydi (API kalitlar shu yerda)

LLM_PROVIDERS = {
    "qwen": {
        "base_url": "http://localhost:11434/v1",
        "key_env": None,                       # Ollama kalit talab qilmaydi
        "model_env": "QWEN_MODEL",
        "default_model": "qwen2.5:1.5b",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "model_env": "GROQ_MODEL",
        "default_model": "openai/gpt-oss-120b",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_env": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "default_model": "gemini-3.5-flash-lite",
    },
}


def get_model_name(llm: str) -> str:
    """Model nomi: .env'dan (masalan GROQ_MODEL), bo'lmasa default."""
    provider = LLM_PROVIDERS[llm]
    return os.getenv(provider["model_env"]) or provider["default_model"]


def generate_answer(messages: list[dict], llm: str = "qwen") -> str:
    """Xabarlarni tanlangan LLM'ga yuboradi va javob matnini qaytaradi."""
    provider = LLM_PROVIDERS[llm]
    if is_offline() and provider["key_env"]:  # cloud LLM = internet kerak
        raise RuntimeError(f"Offline rejim (TACTIQ_OFFLINE=1): '{llm}' cloud LLM. Faqat 'qwen' ishlaydi.")

    api_key = "ollama"  # Ollama uchun istalgan matn
    if provider["key_env"]:
        api_key = os.getenv(provider["key_env"])
        if not api_key:
            raise ValueError(f"{provider['key_env']} topilmadi. Uni .env fayliga yozing.")

    client = OpenAI(base_url=provider["base_url"], api_key=api_key)
    response = client.chat.completions.create(
        model=get_model_name(llm),
        messages=messages,
        temperature=0,  # 0 — har safar bir xil, eng ishonchli javob
    )
    return normalize_citations(response.choices[0].message.content)


def normalize_citations(text: str) -> str:
    """Groq modeli manbani 【1†L13-L15】 deb yozadi -> bizning formatimiz [1] (UI'da bosiladigan)."""
    return re.sub(r"【(\d+)†[^】]*】", r"[\1]", text or "")


# Zaxira: bir cloud LLM ishlamasa (limit tugadi, kalit yo'q/eskirgan, server javob bermadi) — ikkinchisi.
# qwen'ga zaxira yo'q: u ataylab local (ma'lumot internetga chiqmasligi kerak).
FALLBACK = {"gemini": "groq", "groq": "gemini"}
FALLBACK_ERRORS = (APIError, ValueError)  # ValueError — .env'da kalit yo'q


def generate_answer_with_fallback(messages: list[dict], llm: str = "qwen") -> tuple[str, str]:
    """(javob, qaysi LLM javob berdi). Asosiy LLM xato bersa — zaxira LLM bilan qayta urinadi."""
    try:
        return generate_answer(messages, llm), llm
    except FALLBACK_ERRORS as error:
        backup = FALLBACK.get(llm)
        if not backup or is_offline():
            raise
        print(f"[06] {llm} ishlamadi ({type(error).__name__}) -> {backup} bilan qayta urinilmoqda")
        return generate_answer(messages, backup), backup


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", choices=list(LLM_PROVIDERS), default="qwen")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")  # Windows konsoli "‑" kabi belgilarda yiqilmasin
    test_messages = [{"role": "user", "content": "In one sentence: what is counterpressing in football?"}]
    print(f"Rejim: {'OFFLINE (internetsiz)' if is_offline() else 'ONLINE'}")
    answer, used = generate_answer_with_fallback(test_messages, args.llm)
    print(f"LLM: {used} ({get_model_name(used)})")
    print(answer)
