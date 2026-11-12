"""
06 — LLM Generation: LLM kontekst asosida javob yozadi.

3 ta LLM — bitta `openai` kutubxonasi orqali (hammasi OpenAI-compatible API, faqat manzil farq qiladi):
    qwen   — o'z kompyuterimizda (Ollama): internetsiz, ma'lumot tashqariga chiqmaydi
    groq   — cloud, juda tez (GROQ_API_KEY kerak)
    gemini — cloud, free tier (GEMINI_API_KEY kerak)

    python Retrieval_Generation/06_llm_generation/llm_generation.py --llm groq

Keyingi bosqich: 07 — Answer + Sources
"""

import os
import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # Retrieval_Generation/
import rag_paths  # noqa: E402,F401
import config.settings  # noqa: E402,F401  — .env faylini yuklaydi (API kalitlar shu yerda)

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
    return response.choices[0].message.content


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", choices=list(LLM_PROVIDERS), default="qwen")
    args = parser.parse_args()

    test_messages = [{"role": "user", "content": "In one sentence: what is counterpressing in football?"}]
    print(f"LLM: {args.llm} ({get_model_name(args.llm)})")
    print(generate_answer(test_messages, args.llm))
