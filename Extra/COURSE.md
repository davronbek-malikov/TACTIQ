# COURSE.md — how we build this course (read first in every new session)

> Working context for Davronbek and Claude. Lesson scope lives in [1-oy/ROADMAP.md](1-oy/ROADMAP.md);
> progress lives in [1-oy/README.md](1-oy/README.md). This file holds the rules and decisions.

## Who and what

- **Teacher:** Davronbek Malikov (git user `Davronbek`). Teaches an LLM course to Uzbek students.
- **This repo:** `davronbek-malikov/TACTIQ` (GitHub, public; renamed from `RAG` on 2026-11-04). Local path `C:\Users\davro\OneDrive\Desktop\RAG`.
- **This phase:** Month 4 of the course = **"1-oy"** of the LLM Engineering + RAG phase (12 lessons).
  Month 5 (= "2-oy": Agents + Production + Career) comes after it.
- **We build each lesson together:** one lesson per working session. Claude prepares materials, Davronbek reviews,
  runs the notebooks and decides. Don't run ahead to the next lesson without being asked.

## What came before (Post-Training repo)

Full summary: `C:\Users\davro\OneDrive\Desktop\Post-Training\POST_TRAINING_LESSON.md`.

- Product: **TeachHelp** (earlier "Ustoz"), a short-answer Uzbek course assistant, behaviour in `MODEL_SPEC.md`.
- Final model: **Qwen2.5-1.5B + DPO v2 LoRA adapter, 44/68** on the 68-question held-out test
  (base 1.5B 15/68, SFT v3 41/68, best RLHF 41/68). 0.5B SFT adapters also exist (32/68).
- Key lesson that motivates this month: post-training fixed **behaviour**, not **knowledge** → RAG.
- Old RAG plan (written 2026-10-15, before DPO/RLHF; partly outdated):
  `Post-Training/docs/plans/2026-10-15-ustoz-1.5b-rag.md` (Qdrant hybrid, bge-m3, bge-reranker-v2-m3,
  LangGraph, LangSmith, GGUF/Ollama, RAFT-style grounded SFT). Reuse ideas, not its status table.

## Conventions (from the roadmap, apply to everything)

- **Language:** Uzbek (Latin) for explanations; **English for every technical term** (never translate tool/library/method names).
- **Lesson shape:** A. Theory → B. Coding (labs) → checkpoint list → "next lesson" → **10 interview questions**
  (Easy 3 / Medium 4 / Hard 3), full answers in speaker notes, not on slides.
- **Forward links:** say which later lesson uses what we build now.
- **Real numbers only:** never invent benchmark numbers; use placeholders like `[TTFT ms]` until a real run fills them.
- **Environment:** Colab free T4 (16 GB, fp16 only, no bf16, no FlashAttention-2) unless a lesson says otherwise;
  Kaggle 2×T4 for tensor parallel (L4). Teacher's laptop: Windows, no GPU.
- **Secrets:** Colab Secrets / `.env` only; `.env` is gitignored, `.env.example` is committed.
- **Pin versions** in a `requirements.txt` per lesson; test notebooks on a fresh runtime.

## Per-lesson deliverables (ask which ones are needed each time)

```
1-oy/lessons/LXX-<name>/
  notebook.ipynb     # labs in order, runs top to bottom on Colab T4
  slides.md          # theory sections + interview questions (answers in notes)
  homework.md        # deliverables + checklist
  requirements.txt   # pinned versions
```

## Git rules

- **Never add Claude as co-author / contributor**: no `Co-Authored-By: Claude` trailer, no Claude line in PR bodies.
  Davronbek must be the only contributor on GitHub.
- Conventional commit prefixes: `feat:`, `fix:`, `docs:`, `refactor:`, `results:`.
- Branch `main`. Ask before pushing.

## Open questions (to settle before / during Lesson 1)

1. **Which "own model"?** The roadmap says `my-llm-v2-dpo` (0.5B, merged fp16) + a 7B QLoRA adapter.
   The Post-Training repo's final model is **1.5B + DPO v2** (no 7B adapter). Which one do the lessons use?
2. **Worked example:** do we build the teacher's reference project inside this repo (following the
   `my-llm-project/` layout from the roadmap), or only lesson materials?
3. **Project domain** for the worked example (course materials / TeachHelp like before, or a Korean/Uzbek
   company-rules domain as in the roadmap examples)?
4. **API model** for "own model vs API model" comparisons (and the judge in L10)?

## Decisions log

| Date | Decision |
|---|---|
| 2026-10-24 | Repo created at `Desktop/RAG` as its own git repo (remote `davronbek-malikov/RAG`); roadmap copied to `1-oy/ROADMAP.md`. |
| 2026-11-04 | Repo renamed `RAG` → `TACTIQ`. Worked project lives in `rag_project/` (indexing_pipeline + retrieval_generation_pipeline), domain = fictitious OASIS company, embedder Qwen3-Embedding-0.6B, Qdrant local mode by default. |
