"""Retrieval & Generation pipeline (keyingi dars).

Foydalanuvchi savol berganda ishlaydi:
  question -> embed_query -> Qdrant search (+ metadata filter) -> prompt (context + question) -> LLM -> answer + citations

Qayta ishlatiladi: config.py, indexing_pipeline.embedding.Embedder, indexing_pipeline.storing.get_client
"""
