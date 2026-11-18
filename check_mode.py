"""
check_mode — RAG internetsiz (offline) yoki internetli (online) ishlashga tayyormi?

    python check_mode.py

Rejim .env dagi bitta kalit bilan: TACTIQ_OFFLINE=1 (internetsiz) yoki 0 (internetli).
"""

import os
import sys
import urllib.request  # Ollama'ga oddiy HTTP so'rov (localhost)
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "Retrieval_Generation"))
import rag_paths  # noqa: E402,F401  — config/ + .env + Indexing va RG bosqichlari

from huggingface_hub import try_to_load_from_cache  # noqa: E402  — model keshda bormi (internetsiz)

from config.settings import get_settings, is_offline  # noqa: E402
from llm_generation import LLM_PROVIDERS, get_model_name  # noqa: E402

settings = get_settings()
results = []
llm_ready = []  # tayyor LLM'lar


def check(name: str, ok: bool, detail: str) -> None:
    results.append(ok)
    print(f"  {'OK  ' if ok else 'XATO'}  {name:<18} {detail}")


print(f"\nRejim: {'OFFLINE - internetsiz, on-premise' if is_offline() else 'ONLINE - internetli'}\n")

# 1. Embedding model keshda bormi (internetsiz yuklash uchun)
cached = try_to_load_from_cache(settings.embedding_model_name, "config.json")
check("Embedding model", isinstance(cached, str), "keshda" if isinstance(cached, str) else "keshda yo'q - bir marta internet bilan ishga tushiring")

# 2. Qdrant: local papka yoki localhost
if settings.qdrant_local_path:
    has_data = (Path(settings.qdrant_local_path) / "meta.json").exists() or (Path(__file__).parent / settings.qdrant_local_path / "meta.json").exists()
    check("Qdrant", has_data, f"local: {settings.qdrant_local_path}" + ("" if has_data else " - avval Indexing"))
else:
    local = settings.qdrant_url.startswith(("http://localhost", "http://127.0.0.1"))
    check("Qdrant", local or not is_offline(), f"server: {settings.qdrant_url}" + ("" if local else " (cloud - internet kerak)"))

# 3. Qwen (Ollama) - internetsiz rejimdagi yagona LLM
try:
    with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as response:
        models = response.read().decode()
    model = get_model_name("qwen")
    ok = model in models
    llm_ready.append(ok)
    detail = model if ok else f"Ollama bor, lekin model yo'q: ollama pull {model}"
    print(f"  {'OK  ' if ok else 'XATO'}  {'Qwen (Ollama)':<18} {detail}")
except Exception:
    llm_ready.append(False)
    print(f"  {'XATO' if is_offline() else '--  '}  {'Qwen (Ollama)':<18} Ollama ishlamayapti - https://ollama.com o'rnating")

# 4. Cloud LLM'lar - faqat online rejimda
for name, provider in LLM_PROVIDERS.items():
    if provider["key_env"] is None:
        continue
    if is_offline():
        print(f"  --    {name:<18} offline rejimda o'chirilgan")
    else:
        has_key = bool(os.getenv(provider["key_env"]))
        llm_ready.append(has_key)
        detail = "kalit bor" if has_key else f"{provider['key_env']} .env da yo'q"
        print(f"  {'OK  ' if has_key else '--  '}  {name:<18} {detail}")

# Offline: Qwen shart (u ro'yxatda birinchi). Online: kamida bitta LLM yetadi.
check("LLM", llm_ready[0] if is_offline() else any(llm_ready), "qwen tayyor" if llm_ready[0] else ("cloud LLM tayyor" if any(llm_ready) and not is_offline() else "LLM yo'q"))
ready = all(results)
print(f"\n{'TAYYOR' if ready else 'TAYYOR EMAS'}: {'offline' if is_offline() else 'online'} rejim.\n")
sys.exit(0 if ready else 1)
