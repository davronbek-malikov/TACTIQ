# Month 4 Roadmap — LLM Engineering + RAG — 12 lessons, theory + coding

*LLM Course · Davronbek Malikov · October 2026*

> Source of truth for lesson scope, order and deliverables (copied from `Practise_1_oy.md` / `1_oy_Roadmap.pdf`, 2026-10-24).
> Progress is tracked in [README.md](README.md); working rules are in [../COURSE.md](../COURSE.md).

## Overview

- **Where students are now.** Months 1–3 covered deep learning, pretraining a small LLM from scratch, and post-training (SFT, LoRA, QLoRA, DPO, RLHF/reward model) on the Qwen2.5 spine model. Students end Month 3 with `my-llm-v2-dpo` (0.5B) and a 7B QLoRA adapter.
- **Months 4–5 plan.** Based on Saramin and JobKorea postings (checked 24 Oct 2026), the remaining industry skills are split over two months: **Month 4 — LLM Engineering + RAG** (make it fast, make it correct) and **Month 5 — Agents + Production + Career** (make it capable, make it reliable, get hired).
- **Month 4 goal.** Serve and fine-tune the own model like a product, then build a measured RAG system on it: parsing (incl. OCR/VLM, HWP), vector DBs (Qdrant, Milvus), Elasticsearch hybrid search, rerankers, evaluation (RAGAS, DeepEval, LangSmith) and GraphRAG + Neo4j.
- **Lesson format.** Recorded lessons have a) Theory and b) Coding (practice) parts and end with 10 interview questions (Easy / Medium / Hard). Lessons 3 and 9 are face-to-face Q&A; Lesson 6 is the midterm and Lesson 12 the final.
- Week 1 = serving, Week 2 = sLLM + data, Week 3 = vector DBs + search, Week 4 = evaluation + GraphRAG.

## Instructions for the coding agent

You are helping the instructor (Davronbek Malikov) build the materials for this month of an LLM engineering course.
Use this file as the single source of truth for lesson scope, order and deliverables.

**Course context**
- Months 1–3 are done: deep learning basics, pretraining a small LLM from scratch, post-training (SFT, LoRA, QLoRA, DPO, RLHF/reward model) on the Qwen2.5 spine model.
- Students own `my-llm-v2-dpo` (Qwen2.5-0.5B based, merged fp16) and a 7B QLoRA adapter. Every lesson should use **the student's own model next to an API model** where possible.
- Months 4–5 were derived from Saramin / JobKorea / Jumpit / Remember postings checked on 2026-10-24 (sources at the end).

**Conventions (follow them for every artifact)**
- Language: Uzbek for narrative / explanations, **English for all technical terms** (never translate tool, library or method names).
- Recorded lessons have **a) Theory** and **b) Coding (practice)**; each ends with a checkpoint list, a "next lesson" statement and **10 interview questions** (Easy 3 / Medium 4 / Hard 3): recall → mechanism → open-ended trade-off. Put full expected answers in speaker notes, not on slides.
- Lessons 3 and 9 are face-to-face Q&A, Lesson 6 is the midterm, Lesson 12 the final.
- Forward-link concepts deliberately (say which later lesson uses what is built now).
- Ground everything in concrete models and numbers, not abstractions.
- Environment: Google Colab free **T4** (16 GB, fp16 only, no bf16, no FlashAttention-2) unless the lesson says otherwise. Secrets (HF token, API keys) only via Colab Secrets / `.env` — never hard-coded.
- **Pin library versions** in `requirements.txt` and test every notebook on a fresh runtime; the snippets below are starting points and APIs change often.
- Do not invent benchmark numbers in materials — leave placeholders (`[TTFT ms]`) to be filled from real runs.

**Typical deliverables per lesson (ask the instructor which ones are needed)**
1. `lessons/<month>-<lesson>/notebook.ipynb` — the labs in order, runnable top to bottom on Colab T4.
2. `lessons/<month>-<lesson>/slides.md` (or a deck outline) — theory sections in order + interview questions with answers in notes.
3. `lessons/<month>-<lesson>/homework.md` — deliverables and checklist.
4. `requirements.txt` per lesson with pinned versions.

**Suggested student project repo layout (grows over Months 4–5)**
```
my-llm-project/
  serving/        # vLLM / Ollama configs, Modelfile, benchmark scripts
  finetune/       # tool-calling dataset + LoRA training (M4 L4)
  ingest/         # parsers (PDF, HWP, OCR/VLM), chunkers, embedders
  retrieval/      # vector DB, Elasticsearch, reranker, GraphRAG (Neo4j)
  eval/           # dev/test sets, RAGAS / DeepEval tests, LangSmith experiments
  agents/         # LangGraph graphs, MCP servers, enterprise agents (M5)
  api/            # FastAPI app, LiteLLM config, Redis cache (M5)
  deploy/         # Dockerfile, docker-compose.yml, offline install guide, CI (M5)
  ui/             # Gradio / Streamlit demo
  README.md
```

## Month at a glance

| L | Type | Title | Core outputs |
|---|---|---|---|
| 1 | Lesson | LLM API & prompt engineering | Own model behind an OpenAI API; measured prompts; JSON, tool calling |
| 2 | Lesson | Serving & inference optimization | Merge → quantize → serve; vLLM vs AWQ vs GGUF; benchmark |
| 3 | Q&A | Face-to-face review 1 (L1–L2) | Quiz, clinic, serving gate check, project domain + tools chosen |
| 4 | Lesson | Domain sLLM & advanced serving | Tool-calling fine-tune, multi-LoRA, tensor parallel (2×T4) |
| 5 | Lesson | RAG core: parsing, chunking, embeddings | PDF, HWP, OCR/VLM; chunkers; Uzbek/Korean embeddings |
| 6 | Exam | Midterm exam (L1–L5) | Theory + Colab practical + written fine-tuning report |
| 7 | Lesson | Vector DBs & RAG frameworks | HNSW, Qdrant, Milvus, LangChain + LlamaIndex with citations |
| 8 | Lesson | Search quality | Elasticsearch (nori) hybrid, reranker, query transforms, latency |
| 9 | Q&A | Face-to-face review 2 (L7–L8 + midterm) | Retrieval clinic, pipeline checkpoint, test set written |
| 10 | Lesson | RAG evaluation & hallucination control | RAGAS, DeepEval, TruLens, LangSmith, RAG vs SFT |
| 11 | Lesson | GraphRAG + Neo4j + RAG app demo | Knowledge graph, Cypher, hybrid graph; Gradio demo |
| 12 | Exam | Final exam + RAG app defense | Theory + demo + eval report defense |

## To-do list → lesson map

| To-do item | Lesson |
|---|---|
| LLM API basics: OpenAI-compatible API, streaming, JSON output, function calling | L1 |
| Prompt engineering (templates, few-shot, versioning, measured comparison) | L1 |
| One interface for API model + own my-llm-v2-dpo (vLLM / Ollama) | L1 |
| vLLM: PagedAttention, continuous batching, KV cache; Linux / GPU basics | L2 |
| Inference quantization AWQ / GPTQ / GGUF; merge → quantize → serve; benchmarks | L2 |
| NEW · sLLM fine-tuning for tool calling / structured output (+ forgetting check) | L4 |
| NEW · Multi-LoRA serving; tensor parallel on 2×T4; TensorRT-LLM / ONNX overview | L4 |
| Document parsing: PDF, tables, HWP; OCR / VLM parsing | L5 |
| Chunking, metadata; embedding comparison on Uzbek / Korean | L5 |
| NEW · ANN internals (HNSW, IVF, PQ), sizing, filtering, multi-tenancy | L7 |
| Vector DBs: FAISS, Qdrant, Milvus (hands-on), pgvector overview | L7 |
| LangChain and LlamaIndex RAG pipelines with citations | L7 |
| Elasticsearch / OpenSearch (mapping, nori, BM25, kNN, hybrid) | L8 |
| Hybrid search (RRF) + reranker + query transforms; per-stage latency | L8 |
| Held-out eval set, RAGAS, DeepEval, TruLens, LLM-as-judge | L10 |
| LangSmith datasets and experiments | L10 |
| Hallucination control; RAG vs SFT vs SFT+RAG | L10 |
| THE CSR screening question | L10, L12 |
| GraphRAG + Neo4j (knowledge graph, Cypher, hybrid vector + graph) | L11 |
| RAG app demo (Gradio) + defense | L11, L12 |

---

## Lesson 1 — LLM API Engineering & Prompt Engineering — one interface for every model

**Goal:** Students put their own `my-llm-v2-dpo` behind an OpenAI-compatible API, call it with the same client code as an API model, and learn systematic prompt engineering with measured results — plus streaming, JSON output and tool calling.

- **Builds on:** Month 3 L2 (chat template, EOS, loss masking) and L5 (adapter switching).
- **Leads to:** L2 makes this server fast and small; L4 fine-tunes the model for tool calling; L5 starts RAG.
- **Job postings:** 퍼즐에이아이: Structured Output, Tool Calling, LLM API · 지티원/더아이엠씨: LLM API, prompt engineering · Samsung DS: OpenAI API integration. · 지티원/더아이엠씨/Jumpit: prompt engineering.

### A. Theory

#### 1. From model to product — what an LLM engineer does
- Three job types seen in postings: Applied LLM Engineer (fine-tune → quantize → serve), RAG/Agent Engineer, LLM Research/Training Engineer. Month 4 targets the first two.
- The product stack: model → inference server → API → application logic (RAG, agents) → UI. Months 1–3 built the bottom layer; Month 4 builds everything above it.

#### 2. Anatomy of the Chat Completions API
- Request: `model, messages[role, content], temperature, top_p, max_tokens, stop, seed`.
- Response: `choices[].message, finish_reason, usage (prompt/completion tokens)`.
- "OpenAI-compatible" is the de-facto standard: vLLM, Ollama, LiteLLM, many cloud vendors all expose `/v1/chat/completions`. Changing providers = changing `base_url`.
- Sampling recap: temperature/top_p ↔ Month 2 generation lesson; why temperature=0 for evaluation.

#### **[NEW]** 3. Prompt engineering as an engineering skill
- Anatomy of a good prompt: role/system message, task, context, constraints, output format, examples.
- Techniques: clear instructions, delimiters / XML tags for context, few-shot examples, step-by-step reasoning (and when reasoning models make it unnecessary), self-check instructions, output templates.
- Prompts are code: templates with variables, versioning in Git, a small test set to compare versions — never "it looks better".
- Model-specific behavior: small fine-tuned models need shorter, more explicit prompts and few-shot examples; chat-template roles must match training (Month 3).
- Prompt injection awareness: user or document text can contain instructions — keep instructions and data separate.

#### 4. Streaming
- Server-Sent Events (SSE): the server sends token chunks as they are generated.
- Improves perceived latency: **TTFT** (time to first token) matters more for UX than total time.
- Client side: iterate chunks, accumulate `delta.content`, handle the final chunk and errors.

#### 5. Structured output
- Three levels: prompt-only ("answer in JSON"), JSON mode (valid JSON, any shape), JSON-schema / constrained decoding (valid AND matches the schema).
- Constrained (guided) decoding: at each step the sampler masks tokens that would break the grammar — vLLM supports this through `response_format` with a JSON schema.
- Always validate with Pydantic; on failure retry with the error message appended.

#### 6. Function / tool calling
- Tool = name + description + JSON-schema parameters. The model does not execute anything — it returns `tool_calls`; the application executes and sends back a `role='tool'` message.
- Round trip: user → model (tool_calls) → app runs tool → model (final answer). Parallel tool calls.
- Tool descriptions are prompts: clear names, few parameters, enums instead of free text.

#### 7. Chat templates and why your own model may fail
- Tool calling only works if the model was trained on a tool format (e.g. Qwen's Hermes-style `<tool_call>` tags) and the server uses the matching parser.
- `my-llm-v2-dpo` never saw tool data in SFT → expect failures. This is a real finding, not a bug — and a motivation for tool-calling fine-tuning in Lesson 4.

#### 8. Local servers: vLLM and Ollama (overview)
- vLLM: GPU-first, high throughput, OpenAI server out of the box. Ollama: easy local/offline use, GGUF models, CPU or GPU. Details and benchmarks in L2.

### B. Coding (Practice)

#### Lab 1 — Serve your own model with vLLM on Colab
- Install vLLM (pin the version you tested), start the OpenAI server in the background, wait for the port.
- Use the merged fp16 `my-llm-v2-dpo` from Month 3 (push to HF Hub first).

```bash
!pip install -q vllm openai
!nohup vllm serve <user>/my-llm-v2-dpo --dtype half \
    --max-model-len 2048 --gpu-memory-utilization 0.85 \
    --port 8000 > vllm.log 2>&1 &
# wait until: curl localhost:8000/v1/models
```

#### Lab 2 — One client, two models
- Write `llm_client.py`: one function `chat(messages, model, **kw)`; provider chosen by config (local vLLM, Ollama, API model).
- Run the same 5 eval questions from Month 3 on both and compare.

```python
from openai import OpenAI
BACKENDS = {
  'local': dict(base_url='http://localhost:8000/v1', api_key='x'),
  'api':   dict(base_url=None, api_key=API_KEY),  # any OpenAI-compatible API
}
def chat(messages, backend='local', model=None, **kw):
    c = OpenAI(**BACKENDS[backend])
    return c.chat.completions.create(model=model, messages=messages, **kw)
```

#### **[NEW]** Lab 3 — Prompt engineering with numbers
- 20 test inputs (e.g. classify Uzbek/Korean support messages). Compare v1 zero-shot, v2 clear instructions + format, v3 few-shot, v4 few-shot + XML-delimited context — on the API model and on the own model.
- Score with exact match or a simple rubric; keep prompts as versioned templates (`prompts/v1.txt` …).

```python
PROMPT_V3 = '''You are a support classifier.
Categories: billing, technical, account, other.
<examples>{examples}</examples>
<message>{message}</message>
Answer with only the category.'''
```

#### Lab 4 — Streaming + measuring TTFT
- Stream a long answer; record time of first chunk and total time; print tokens/sec.

```python
t0 = time.perf_counter(); first = None; n = 0
for ch in c.chat.completions.create(model=m, messages=msgs, stream=True):
    if ch.choices and ch.choices[0].delta.content:
        first = first or time.perf_counter(); n += 1
print('TTFT', first - t0, 'tok/s', n / (time.perf_counter() - first))
```

#### Lab 5 — Structured output with a schema
- Define a Pydantic model (e.g. `Ticket(category, priority, summary)`); request it with `response_format` json_schema; validate; count failures over 20 inputs for prompt-only vs schema-constrained.

#### Lab 6 — Tool calling and the small-model reality check
- Restart vLLM with `--enable-auto-tool-choice --tool-call-parser hermes`.
- Two tools: `get_weather(city)`, `calculator(expr)`. Implement the full round trip.
- Compare tool-call validity on 20 prompts: own 0.5B model vs Qwen2.5-0.5B-Instruct vs Qwen2.5-1.5B-Instruct vs API model.

### Deliverables / homework

- [ ] `llm_client.py` that works for local + API backends (used all month).
- [ ] Prompt comparison table (v1–v4 × 2 models) with the winning template committed to Git.
- [ ] Table: TTFT, tokens/sec, JSON validity %, tool-call validity % per backend.
- [ ] One paragraph: "Why does my own model fail/succeed at tool calling?"

### Environment notes

- T4 has no bf16 → always `--dtype half`. Install vLLM before class; pin the version that works on T4.
- If vLLM install fails on Colab, fall back to Ollama for this lesson (same client code, port 11434/v1).
- Never paste API keys in notebooks — use Colab Secrets (same as Month 2 HF token).

### Interview questions

**Easy**

1. What does "OpenAI-compatible API" mean and why does it matter for switching models?
2. What is streaming and which latency metric does it improve?
3. Name four parts of a well-structured prompt.

**Medium**

4. Walk through a complete function-calling round trip, message by message.
5. Why can your own 0.5B SFT model fail at tool calling while Qwen2.5-Instruct succeeds?
6. How does constrained (guided) decoding guarantee valid JSON?
7. How do you prove that prompt v2 is better than v1? Describe the test setup.

**Hard**

8. Design an LLM client layer for 3 providers with retries, fallbacks and streaming.
9. An agent produces malformed tool arguments 5% of the time. Fix it at the decoding, prompt and training levels.
10. Why must the serving chat template match the one used in fine-tuning? What breaks if it does not?

---

## Lesson 2 — Serving & Inference Optimization — merge → quantize → serve → benchmark

**Goal:** Students understand where inference time and memory go, serve their model in three formats (fp16 vLLM, AWQ vLLM, GGUF Ollama), and write a benchmark report with real numbers.

- **Builds on:** Month 3 L5 (QLoRA: NF4, merge trap, adapter switching).
- **Leads to:** L4 adds multi-GPU and multi-LoRA serving; every RAG lesson runs on this server.
- **Job postings:** 다비치: LoRA/QLoRA + quantization + serving · 퍼즐에이아이: vLLM, quantization, tensor parallel, GPU memory / latency / throughput · NexIn: vLLM, Ollama, TPS/latency.

### A. Theory

#### 1. Inference in two phases
- **Prefill**: the whole prompt in one forward pass (compute-bound). **Decode**: one token at a time (memory-bandwidth-bound) → why generation is slow and why batching helps.

#### 2. KV cache — the hidden memory cost
- Per token: 2 (K and V) × layers × kv_heads × head_dim × bytes.
- Worked example, Qwen2.5-7B (28 layers, 4 KV heads with GQA, head_dim 128, fp16): 2×28×4×128×2 B ≈ 56 KB per token → 4,096 tokens × 8 requests ≈ 1.9 GB.
- Link to Month 1/2: why GQA (grouped-query attention) exists.

#### 3. Why vLLM is fast
- **PagedAttention**: KV cache stored in fixed-size blocks, like OS virtual-memory pages → no fragmentation, more concurrent requests.
- **Continuous batching**: new requests join the batch at every decode step instead of waiting.
- Prefix caching (shared system prompts), multi-LoRA serving (one base, many adapters — Month 3 slide 34).

#### 4. Metrics that postings name
- TTFT, TPOT / inter-token latency, tokens/sec per request, total throughput, p50 / p95 latency, GPU memory.
- Trade-off: more concurrency → higher throughput but worse per-user latency. Plot it.

#### 5. Inference quantization (different from QLoRA training)
- bitsandbytes NF4: great for training (QLoRA), slow for serving.
- **GPTQ**: layer-wise, second-order error correction with calibration data.
- **AWQ**: protects "salient" weight channels found from activations; W4A16 (4-bit weights, 16-bit activations).
- **GGUF** (llama.cpp): Q4_K_M / Q5_K_M / Q8_0; CPU + GPU; Ollama format; ideal for laptops and on-prem.
- Quality check after quantizing: perplexity + the Month 3 eval questions.

#### 6. The full chain: merge → quantize → serve
- Merge the LoRA adapter into an fp16 base first, then quantize (quantizing first and merging later breaks).
- RAM trap: merging 7B needs ≈15 GB of CPU RAM (free Colab ≈12 GB) → do the full chain on 0.5B; for 7B use an official AWQ checkpoint or serve the adapter with vLLM multi-LoRA.

#### 7. Linux / GPU survival kit
- `nvidia-smi`, driver vs CUDA version, compute capability (T4 = 7.5: no bf16, no FlashAttention-2).
- OOM checklist: max-model-len ↓, gpu-memory-utilization, batch size, quantize, kill zombie processes.
- Background processes: nohup / tmux, ports, logs (`tail -f vllm.log`).

### B. Coding (Practice)

#### Lab 1 — Merge and push
- Merge the 0.5B adapter (if not already merged) and push fp16 weights to HF Hub.

```python
base = AutoModelForCausalLM.from_pretrained(base_id, torch_dtype=torch.float16)
merged = PeftModel.from_pretrained(base, adapter_id).merge_and_unload()
merged.push_to_hub('<user>/my-llm-v2-dpo-merged'); tok.push_to_hub(...)
```

#### Lab 2 — GGUF + Ollama
- Convert with llama.cpp, quantize to Q8_0 and Q4_K_M, create an Ollama model with a Modelfile (include the correct chat template and stop token `<|im_end|>`).

```bash
python llama.cpp/convert_hf_to_gguf.py my-llm-v2-dpo-merged --outtype f16 \
    --outfile my-llm-f16.gguf
./llama.cpp/build/bin/llama-quantize my-llm-f16.gguf my-llm-q4.gguf Q4_K_M
ollama create my-llm -f Modelfile   # FROM ./my-llm-q4.gguf
```

#### Lab 3 — AWQ (W4A16) + vLLM
- Quantize the merged model with llm-compressor (AWQ / W4A16 recipe, ~128 calibration samples) and serve it with vLLM. Compare memory and answers with fp16.

#### Lab 4 — A 7B model on a 16 GB T4
- Serve `Qwen/Qwen2.5-7B-Instruct-AWQ` with vLLM (max-model-len 4096).
- Multi-LoRA demo on 0.5B: `vllm serve Qwen/Qwen2.5-0.5B --enable-lora --lora-modules general=... uzbek=...` and switch adapters per request with the `model` field.

#### Lab 5 — Benchmark script
- Async client, concurrency 1 / 4 / 16 / 32, 100 prompts; record TTFT, tokens/sec, p50/p95, GPU memory.
- Compare: HF generate vs vLLM fp16 vs vLLM AWQ vs Ollama GGUF. Plot throughput vs p95 latency.

```python
async def one(prompt):
    t0 = time.perf_counter(); first = None; n = 0
    async for ch in await ac.chat.completions.create(
            model=M, messages=[{'role':'user','content':prompt}], stream=True):
        if ch.choices and ch.choices[0].delta.content:
            first = first or time.perf_counter(); n += 1
    return first - t0, n, time.perf_counter() - t0
sem = asyncio.Semaphore(CONC)  # wrap one() to limit concurrency
```

### Deliverables / homework

- [ ] Benchmark report (1 page): table + throughput-vs-latency chart + quality check per format.
- [ ] Model on HF Hub in fp16, AWQ and GGUF; Ollama Modelfile in the repo.

### Environment notes

- Run one server at a time on T4 (stop vLLM before starting another).
- llama.cpp build takes several minutes — prebuild or use the released binaries; test the night before.
- Library APIs change quickly (AutoAWQ → llm-compressor); pin versions in requirements.txt.

### Interview questions

**Easy**

1. What is the difference between prefill and decode?
2. What do TTFT and tokens/sec measure?
3. When would you use GGUF and when AWQ?

**Medium**

4. Compute the KV cache size for Qwen2.5-7B at 4k context and batch 8. Show the formula.
5. Explain PagedAttention and continuous batching in your own words.
6. Why merge the LoRA adapter before quantizing?
7. Why does throughput rise but per-user latency get worse as concurrency grows?

**Hard**

8. You have one 24 GB GPU and must serve a 7B model to 50 concurrent users. Plan it with numbers.
9. Why not serve the QLoRA NF4 model directly in production? What would you serve instead?
10. Design multi-LoRA serving for 50 enterprise clients on one base model.

---

## Lesson 3 — Face-to-face Q&A and Review 1 — Lessons 1–2

**Type:** face-to-face Q&A

**Purpose:** Close gaps in API, prompting and serving before fine-tuning and RAG start, and make sure every student has a working server.

### Session plan (~2.5 h)

| Time | Activity |
|---|---|
| 0:00–0:15 | Warm-up quiz (10 questions below, paper or Kahoot). |
| 0:15–0:45 | Whiteboard: KV-cache calculation and VRAM budget for 0.5B fp16, 7B AWQ, 7B fp16 on a T4. |
| 0:45–1:30 | Debugging clinic: students bring errors (vLLM OOM, wrong tool parser, GGUF conversion, missing stop token, port already in use). Solve live on the projector. |
| 1:30–2:10 | Benchmark reports: 3 minutes per student/team; class discusses surprising numbers. |
| 2:10–2:30 | Project kick-off: choose a domain (e.g. Korean company rules, Uzbek law, medical FAQ), define 4–6 tools for L4, and start collecting 30–100 documents for L5. |

### Review quiz

1. Name four parts of a well-structured prompt, and how you would compare two prompt versions.
2. What is TTFT and why does streaming improve it?
3. JSON mode vs JSON schema — which guarantees the fields?
4. Who executes a tool: the model or the application?
5. Prefill vs decode — which is memory-bound?
6. Write the KV-cache-per-token formula.
7. What do PagedAttention and continuous batching solve?
8. AWQ, GPTQ, GGUF — one sentence each.
9. Why merge before quantizing?
10. Why do we use --dtype half on a T4?

### Gate check — every student must have

- [ ] Own model served behind an OpenAI-compatible endpoint (vLLM or Ollama).
- [ ] llm_client.py works for local + API backends.
- [ ] Benchmark report submitted.
- [ ] Project domain chosen; document collection started.

---

## Lesson 4 — Domain sLLM & Advanced Serving — fine-tune for tool calling, multi-LoRA, multi-GPU

**Goal:** Students fine-tune their own small model for a service task (tool calling / JSON output), prove the gain with numbers without breaking general ability, and serve it with multi-LoRA and tensor parallelism.

- **Builds on:** Month 3 SFT/LoRA/DPO; L1 tool-calling reality check (own model failed); L2 serving.
- **Leads to:** L5–L11 can use the improved own model as the RAG generator; Month 5 uses it inside agents.
- **Job postings:** 지티원: sLLM fine-tuning · NexIn: domain sLLM LoRA, TensorRT, ONNX · 다비치: fine-tuning practical assignment, quantized serving · 퍼즐에이아이: service-specific fine-tuning, tensor parallel, multi-GPU.

### A. Theory

#### 1. Prompt, RAG or fine-tune? A decision guide
- Prompting: fastest, no training. RAG: new or changing facts. Fine-tuning: behavior, format, style, tool use, latency/cost (a small tuned model replacing a big prompted one).
- Typical sLLM project: a 0.5B–7B model tuned for one service task, served on-prem.

#### 2. Tool-calling and structured-output training data
- Format: chat messages with a `tools` list rendered by the model's own chat template (Qwen uses Hermes-style `<tool_call>` tags) — same template at train and serve time.
- Sources: synthetic generation with a teacher model (API or 7B), public function-calling datasets (check the license), hand-written edge cases.
- Must include: no-tool examples (model should answer directly), multi-tool and parallel calls, invalid requests, Uzbek/Korean prompts. Filter: valid JSON, arguments match schema, de-duplicate.

#### 3. Training recipe
- LoRA SFT on the own model (Month 3 setup), loss only on assistant/tool-call tokens (completion-only).
- Optional DPO pairs: correct call vs wrong tool / wrong arguments.

#### 4. Evaluating a tool-calling model
- Tool-call validity %, correct tool %, argument exact-match %, end-to-end task success, false tool calls on no-tool prompts.
- Forgetting check: Month 3 eval questions before and after (general ability must not collapse).

#### 5. Multi-LoRA serving in production
- One base model + many adapters (one per customer or task); vLLM `--enable-lora`, `--max-loras`; routing by the `model` field; adapter versioning.

#### 6. Multi-GPU serving
- Tensor parallel (split each layer across GPUs, needs fast interconnect) vs pipeline parallel (split layers) vs data parallel replicas behind a load balancer.
- When a model does not fit one GPU → tensor parallel; when traffic grows → replicas.

#### 7. Other inference engines (overview)
- TensorRT-LLM (NVIDIA, compiled engines, highest throughput, more setup), ONNX Runtime (portable, CPU/edge), SGLang (fast serving, structured generation), llama.cpp (CPU, laptops). vLLM remains the default to learn first.

### B. Coding (Practice)

#### Lab 1 — Build a tool-calling dataset
- Define 4–6 tools for the project domain. Generate 500–1,000 examples with a teacher model; add no-tool and edge cases; validate every example with JSON schema; split train/dev/test.

```python
msgs = [{'role': 'user', 'content': q},
        {'role': 'assistant', 'tool_calls': [{'type': 'function',
          'function': {'name': 'get_leave_days', 'arguments': {'year': 2026}}}]}]
text = tok.apply_chat_template(msgs, tools=TOOLS, tokenize=False)
assert valid_call(msgs[-1], TOOLS)   # schema check before training
```

#### Lab 2 — LoRA SFT on the own model
- Train a LoRA adapter on my-llm-v2-dpo with completion-only loss (Month 3 config, T4 fp16). Push the adapter.

#### Lab 3 — Before / after evaluation
- On the test split: validity %, correct tool %, argument match %, false-call rate on no-tool prompts — base vs tuned vs Qwen2.5-0.5B-Instruct. Run the Month 3 eval questions to check forgetting.

#### Lab 4 — Serve with multi-LoRA
- vLLM with the base model + two adapters (general SFT and tool-calling); call each through the L1 client and run the L1 tool round trip again.

```bash
vllm serve <user>/my-llm-v2-dpo-merged --dtype half --enable-lora \
    --lora-modules general=<user>/sft-lora tools=<user>/tools-lora \
    --max-loras 2 --enable-auto-tool-choice --tool-call-parser hermes
```

#### Lab 5 — Tensor parallel on Kaggle 2×T4
- Serve Qwen2.5-7B-Instruct in fp16 with `--tensor-parallel-size 2`; compare with 7B-AWQ on one T4: TTFT, tokens/sec, max concurrency (reuse the L2 benchmark script).

#### Lab 6 — ONNX Runtime on CPU
- Export the 0.5B model with Optimum to ONNX and run it on CPU; compare speed with GGUF in Ollama.

### Deliverables / homework

- [ ] Tool-calling dataset card (size, sources, license, splits) + adapter on HF Hub.
- [ ] Before/after table + forgetting check; tensor-parallel vs AWQ benchmark table.

### Environment notes

- Tensor parallel needs 2 GPUs: use Kaggle (2×T4, free weekly quota). Colab has one GPU.
- Generate the dataset with the API model to keep the T4 free for training.

### Interview questions

**Easy**

1. When should you fine-tune instead of using RAG or prompting?
2. What is tensor parallelism?
3. What is multi-LoRA serving?

**Medium**

4. What must a good tool-calling dataset contain besides correct calls?
5. Which metrics show that tool-calling fine-tuning worked?
6. How do you check that fine-tuning did not damage general ability?
7. Tensor parallel vs replicas — when do you use each?

**Hard**

8. Design an sLLM project for a bank: data, training, evaluation, on-prem serving, cost.
9. Your tuned model calls tools when it should not (false calls 20%). Fix it at data, training and decoding level.
10. Compare vLLM, TensorRT-LLM, ONNX Runtime and llama.cpp for three deployment targets: GPU server, CPU server, laptop.

---

## Lesson 5 — RAG Core — parsing (PDF, HWP, OCR/VLM), chunking and embeddings

**Goal:** Students turn real documents — digital PDFs, tables, scanned pages and HWP — into clean, well-chunked, well-embedded data, and measure which chunker and embedding model work best for Uzbek and Korean.

- **Builds on:** Month 2 (cleaning, dedup, PII, tokenizer fertility); Month 3 "SFT teaches behavior, not knowledge"; L4 decision guide.
- **Leads to:** L7 stores these chunks in vector DBs and builds the first full RAG pipelines.
- **Job postings:** NexIn: parsing, chunking, embedding, Vector DB, PDF/HWP/tables, VLM, Milvus/Chroma/FAISS · THE CSR: LangChain/LlamaIndex RAG · 인포유앤컴퍼니: chunking, metadata, HF embeddings.

### A. Theory

#### 1. Why RAG
- Knowledge cutoff, private data, changing documents, citations and auditability.
- RAG vs fine-tuning: fine-tuning changes behavior/style; RAG supplies facts at query time. Often both.

#### 2. Pipeline anatomy
- **Ingestion** (offline): parse → clean → chunk → embed → index (+ metadata).
- **Query** (online): embed query → retrieve top-k → (rerank, L5) → build prompt → generate → cite.

#### 3. Document parsing — the quality ceiling
- Digital PDF text vs scanned PDF; tables (pdfplumber), layout-aware parsers (docling, unstructured, marker).
- **HWP / HWPX** (Korean public and enterprise documents): HWP5 is a binary OLE file (pyhwp `hwp5txt`); HWPX is a zip of XML files (parse with zipfile + XML).
- Bad parsing cannot be fixed later — inspect parsed output by eye.

#### **[NEW]** 4. OCR and VLM document parsing
- When text extraction returns nothing: scanned PDFs, photos, stamped forms, screenshots.
- **OCR pipeline**: page → image → layout detection → text recognition → reading order. Engines: PaddleOCR (strong Korean support), EasyOCR, Tesseract (kor/eng). Docling can call OCR automatically.
- **VLM parsing**: a vision-language model (e.g. Qwen2.5-VL-3B) reads the page image and outputs Markdown — better for tables, charts and complex layouts; slower and can hallucinate.
- Choose by document: digital → direct text; scanned text → OCR; tables/charts/forms → VLM. Always compare on 5 pages.
- Quality checks: character error rate on a hand-typed sample, table structure preserved, Korean/Uzbek characters correct.

#### 5. Chunking
- Fixed-size with overlap; recursive by separators (headings → paragraphs → sentences); semantic (split where embedding similarity drops); structure-aware (one table = one chunk); parent–child (retrieve small, return big).
- Measure size in **tokens of the generator's tokenizer** — Uzbek text has higher fertility (Month 2 L5).
- Trade-off: small chunks = precise but lose context; large chunks = context but noisy and expensive.

#### 6. Metadata design
- source, page, section/heading, date/version, language, doc_type, access level.
- Used for citations, filtering ("only 2026 regulations"), access control and index updates.

#### 7. Embeddings
- Bi-encoder trained contrastively; cosine similarity; normalize vectors.
- Multilingual options: multilingual-e5 (needs `query: ` / `passage: ` prefixes), bge-m3 (dense + sparse + multi-vector, long inputs). Leaderboards (MTEB) are a start — always test on your own Uzbek/Korean data.
- Dimension vs storage vs speed.

### B. Coding (Practice)

#### Lab 1 — Parsers to one Document format
- pdfplumber for text + tables; hwp5txt for HWP; zipfile/XML for HWPX. Output `Document(text, metadata)` JSONL.

```python
import pdfplumber
with pdfplumber.open(path) as pdf:
    for i, p in enumerate(pdf.pages):
        docs.append({'text': p.extract_text() or '',
                     'meta': {'source': path, 'page': i + 1}})
        for t in p.extract_tables(): docs.append(table_to_markdown(t, path, i))
```

#### **[NEW]** Lab 2 — Scanned documents: OCR vs VLM
- Take 5 scanned pages (one with a table). Run PaddleOCR (Korean + English) and a VLM (Qwen2.5-VL-3B-Instruct, fp16 on T4) that outputs Markdown. Compare text accuracy, table structure and time per page.

```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='korean')
result = ocr.ocr('scan_page1.png')
# VLM: prompt = 'Convert this page to Markdown. Keep tables as Markdown tables.'
```

#### Lab 3 — Chunking experiment
- Same corpus, three chunkers (fixed 512 tokens / recursive / semantic). Report chunk count, mean and max tokens using the Qwen tokenizer; eyeball 5 chunks each.

#### Lab 4 — Embedding comparison on Uzbek / Korean
- Write 20 query → correct-passage pairs. Compare 2–3 models (multilingual-e5-base, bge-m3, one small model) by Hit@1 and Hit@5.

#### Lab 5 — Baseline retrieval with FAISS
- Flat FAISS index over the chunks; for 20 test queries print the top-5 chunks and check them by eye — the first end-to-end retrieval before L7.

### Deliverables / homework

- [ ] Domain corpus (30–100 documents, incl. at least 5 scanned pages) parsed into JSONL with metadata.
- [ ] OCR vs VLM table; chunking statistics; embedding comparison (Hit@1/Hit@5) with the chosen model and why.

### Environment notes

- Load the VLM only for the OCR/VLM lab, then free GPU memory (del model; torch.cuda.empty_cache()).
- Keep parsed outputs on Google Drive / HF Hub — parsing is slow, do it once.

### Interview questions

**Easy**

1. Why use RAG instead of fine-tuning to add new facts?
2. What is chunk overlap for?
3. When do you need OCR or a VLM instead of normal PDF text extraction?

**Medium**

4. How do you choose a chunk size? Why measure it in tokens of your generator's tokenizer, especially for Uzbek?
5. OCR vs VLM parsing — compare accuracy on tables, speed and failure modes.
6. Why does multilingual-e5 need "query:" and "passage:" prefixes?
7. Design metadata that supports citations, filtering and access control.

**Hard**

8. Design an ingestion pipeline for 10,000 Korean HWP files plus scanned PDFs.
9. Design retrieval for a corpus mixing Uzbek, Korean and English documents.
10. Documents change weekly. How do you update chunks and embeddings without full re-processing?

---

## Lesson 6 — Midterm Exam — Lessons 1–5

**Type:** exam

### Part A — Theory (40%)
- 10 short questions from the L1, L2, L4, L5 interview questions.
- 2 calculations: KV cache for a given model/context/batch; VRAM to serve a 7B model in fp16 vs AWQ vs 2×T4 tensor parallel.
- 1 design question, e.g. "Prompt, RAG or fine-tune? Decide for a given company case and justify."

### Part B — Practical in Colab (45%)
- Given: a small document set (incl. 2 scanned pages) prepared by the instructor.
- Task 1: serve a model behind the OpenAI API and call it with structured JSON output.
- Task 2: parse all documents (OCR for the scanned pages), chunk them, embed them.
- Task 3: FAISS baseline retrieval for 10 given queries; report Hit@5 with gold IDs provided.

### Part C — Written (15%)
- 300–500 words: your L4 fine-tuning result — dataset, metrics before/after, forgetting check, and one thing that did not work.

### Grading rubric

| Criterion | Excellent | Acceptable | Weak |
|---|---|---|---|
| Correct concepts | Precise, uses terms correctly | Mostly correct | Confused terms |
| Working pipeline | Runs end to end, citations correct | Runs with small issues | Does not run |
| Measurement | Correct metrics, dev/test separated | Metrics computed | No numbers |
| Improvement | Clear before/after, reasoned | Change made, weak evidence | No change |
| Written report | Honest, specific, includes failure | Generic | Missing |

---

## Lesson 7 — Vector Databases & RAG Frameworks — FAISS, Qdrant, Milvus, pgvector, LangChain, LlamaIndex

**Goal:** Students understand how vector search works inside, choose and operate a vector DB (Qdrant and Milvus hands-on), and build complete RAG pipelines with citations in LangChain and LlamaIndex on their own served model.

- **Builds on:** L5 chunks and embeddings; L1 client and own-model server.
- **Leads to:** L8 adds keyword search, hybrid and reranking on top of these pipelines.
- **Job postings:** NexIn: Vector DB (Milvus, ChromaDB, FAISS), LangChain/LlamaIndex · PwC: Pinecone, Weaviate, Qdrant, pgvector · THE CSR: LangChain/LlamaIndex RAG, Vector DB optimization · 지티원: Vector DB hands-on.

### A. Theory

#### 1. How approximate nearest-neighbor search works
- Exact (flat) search cost grows with N. ANN trades a little recall for big speed.
- **HNSW**: layered graph; parameters M, ef_construction (build quality), ef_search (query recall vs speed).
- **IVF**: cluster vectors (nlist), search only nprobe clusters. **PQ**: compress vectors to save memory.
- Distance metrics: cosine / dot / L2; normalize embeddings for cosine.

#### 2. Sizing and filtering
- Memory ≈ N × dim × 4 bytes (fp32): 1M chunks × 1024 dims ≈ 4 GB before index overhead.
- Metadata filters: pre-filter vs post-filter; payload / scalar indexes; multi-tenancy (one collection per tenant vs tenant field).
- Updates and deletes, re-embedding when the model changes, collection versioning and aliases.

#### 3. Choosing a vector store
- FAISS: library, fastest to start, no server. Chroma: embedded, prototyping. **Qdrant**: Rust server, strong filtering, easy ops. **Milvus**: distributed, very large scale, many index types (Milvus Lite for laptops). **pgvector**: vectors in Postgres — simplest when Postgres already exists. Pinecone/Weaviate: managed/cloud options.
- Decide by: data size, filter needs, on-prem requirement, team skills.

#### 4. LangChain for RAG
- Document loaders, text splitters, embeddings, vector-store wrappers, retrievers, LCEL chains (`retriever | prompt | llm | parser`), returning sources with the answer.

#### 5. LlamaIndex for RAG
- Documents → nodes, VectorStoreIndex over an external store, query engine, node postprocessors, response synthesis with source nodes.
- LangChain vs LlamaIndex vs raw code: know what each hides; postings name both.

#### 6. Citations and the RAG prompt
- Context formatting with chunk IDs, "answer only from context", cite as [source, page], return structured output {answer, citations} (L1 structured output).

### B. Coding (Practice)

#### Lab 1 — HNSW parameter sweep
- FAISS flat vs HNSW on 50k–100k vectors: recall@10 vs latency for several ef_search values; one chart.

#### Lab 2 — Qdrant with filters and tenants
- Qdrant (local mode): payload metadata, payload index, filtered search, two tenants in one collection.

```python
from qdrant_client import QdrantClient, models
qc = QdrantClient(path='qdrant_db')
qc.create_collection('docs', vectors_config=models.VectorParams(
    size=dim, distance=models.Distance.COSINE))
hits = qc.query_points('docs', query=qv, limit=5, query_filter=models.Filter(
    must=[models.FieldCondition(key='dept', match=models.MatchValue(value='HR'))]))
```

#### Lab 3 — Milvus hands-on
- Same data in Milvus Lite: collection schema, HNSW index, filtered search; compare results and latency with Qdrant.

```python
from pymilvus import MilvusClient
mc = MilvusClient('milvus_demo.db')          # Milvus Lite, one local file
mc.create_collection('docs', dimension=dim)
mc.insert('docs', rows)                      # [{'id', 'vector', 'text', 'source'}]
hits = mc.search('docs', data=[qv], limit=5, filter="source like 'hr_%'",
                 output_fields=['text', 'source'])
```

#### Lab 4 — RAG with LangChain
- Retriever over Qdrant | prompt with chunk IDs | ChatOpenAI(base_url = own vLLM) | structured output with citations.

```python
chain = ({'context': retriever | format_docs, 'question': RunnablePassthrough()}
         | prompt | llm.with_structured_output(AnswerWithCitations))
chain.invoke('How many days of annual leave do new employees get?')
```

#### Lab 5 — RAG with LlamaIndex
- VectorStoreIndex over the same Qdrant collection; query engine with source nodes; compare answers with LangChain.

#### Lab 6 — Vector store decision memo
- For the project domain: expected size, filters, on-prem needs → which store and why (half a page, with the lab numbers).

### Deliverables / homework

- [ ] Two working RAG pipelines (LangChain + LlamaIndex) with citations on the project corpus.
- [ ] HNSW recall/latency chart; Qdrant vs Milvus table; vector store decision memo.

### Environment notes

- Qdrant local mode and Milvus Lite both run on Colab without Docker.
- Keep the generator at gpu-memory-utilization ≈0.6 so embeddings fit on the same T4.

### Interview questions

**Easy**

1. What is approximate nearest-neighbor search and why is it needed?
2. What do HNSW parameters M and ef_search control?
3. What is the difference between FAISS and a vector database?

**Medium**

4. Estimate the memory for 2 million 768-dimensional fp32 vectors.
5. Pre-filtering vs post-filtering — what goes wrong with each?
6. Qdrant vs Milvus vs pgvector — when would you choose each?
7. What does LangChain hide that you should still understand?

**Hard**

8. Design multi-tenant vector search for 50 enterprise customers with strict data separation.
9. The embedding model must change. How do you migrate 10M vectors with no downtime?
10. Recall is high in tests but users complain answers miss documents from one department. Debug it.

---

## Lesson 8 — Search Quality — Elasticsearch / OpenSearch, hybrid search, rerankers, query transforms

**Goal:** Students build production keyword search with Elasticsearch (Korean nori analyzer), combine it with vector search, add a reranker and query transformations — and prove each step with retrieval metrics.

- **Builds on:** L7 vector pipelines.
- **Leads to:** L10 evaluates the full system end to end; L11 adds graph retrieval.
- **Job postings:** Elastic Stack search role (Saramin) · 인포유앤컴퍼니: search-engine schema, index tuning, ingestion · PwC: Hybrid RAG · NexIn: retrieval accuracy tuning.

### A. Theory

#### 1. Retrieval metrics first
- Hit@k, Recall@k, MRR = mean(1 / rank of first relevant), nDCG (brief). A 30-question dev set with gold doc IDs is enough to steer this lesson; the full eval set comes in L10.

#### **[NEW]** 2. Elasticsearch / OpenSearch — production lexical search
- Inverted index, analyzers (tokenizer + filters), BM25 scoring with k1 and b parameters.
- **Korean text**: the `nori` analyzer (morphological analysis); why a whitespace tokenizer fails for Korean particles.
- **Index design**: mapping (text vs keyword fields, metadata fields for filters), shards/replicas basics, re-indexing when the mapping changes, index tuning (analyzer choice, field boosts).
- Vectors inside the same engine: dense_vector field + kNN search → hybrid search in one system. OpenSearch = open-source fork with a hybrid-search pipeline.
- When to use: large document collections, many filters, existing company search infrastructure.

#### 3. Hybrid search and fusion
- BM25 (exact names, codes, numbers) + dense (meaning, paraphrase). Reciprocal Rank Fusion: score(d) = Σ 1 / (k + rank_i(d)), k ≈ 60; or weighted score fusion.

#### 4. Rerankers
- Bi-encoder (fast, independent) vs cross-encoder (query + passage together, accurate, slower).
- Pattern: retrieve 30–50 → rerank → keep 3–5. Example model: bge-reranker-v2-m3 (multilingual).

#### 5. Query transformation
- Rewrite conversational follow-ups into standalone questions; multi-query (several paraphrases, union); HyDE (embed a hypothetical answer); decomposition of multi-hop questions into sub-questions.

#### 6. Latency budget
- Each stage adds time: BM25 + kNN + rerank + rewrite. Measure p95 per stage; rerank fewer candidates or cache rewrites when the budget is tight.

### B. Coding (Practice)

#### Lab 1 — Retrieval dev set + harness
- 30 questions with gold doc IDs; Hit@k, Recall@k, MRR and RRF functions; dense-only baseline numbers.

```python
def mrr(ranked_ids, gold):
    for r, d in enumerate(ranked_ids, 1):
        if d in gold: return 1 / r
    return 0.0
def rrf(*rankings, k=60):
    s = defaultdict(float)
    for rk in rankings:
        for r, d in enumerate(rk, 1): s[d] += 1 / (k + r)
    return sorted(s, key=s.get, reverse=True)
```

#### **[NEW]** Lab 2 — Elasticsearch BM25 + hybrid
- Run Elasticsearch (local install on Colab, or a free cloud trial) with the `analysis-nori` plugin installed; create an index with a mapping: text field with the `nori` analyzer for Korean, keyword fields for metadata, dense_vector field.
- Compare on dev: standard analyzer vs nori; BM25 only vs dense only vs hybrid (RRF).

```python
es.indices.create(index='docs', mappings={'properties': {
    'text':   {'type': 'text', 'analyzer': 'nori'},
    'source': {'type': 'keyword'},
    'vec':    {'type': 'dense_vector', 'dims': 1024, 'similarity': 'cosine'}}})
bm25 = es.search(index='docs', query={'match': {'text': q}}, size=30)
knn  = es.search(index='docs', knn={'field': 'vec', 'query_vector': qv,
                 'k': 30, 'num_candidates': 100})
# fuse the two rankings with rrf()
```

#### **[NEW]** Lab 3 — OpenSearch hybrid pipeline (optional)
- Same index in OpenSearch with a hybrid-search pipeline (normalization + combination); compare with the ES + RRF result.

#### Lab 4 — Reranker before/after
- Hybrid top-30 → cross-encoder → top-5. Report MRR and Hit@5 change and added latency.

#### Lab 5 — Query transforms (dev set only)
- Rewrite, multi-query, HyDE, decomposition — keep only what improves dev metrics; record the added latency.

#### Lab 6 — Per-stage latency report
- p50/p95 for BM25, kNN, fusion, rerank, rewrite; choose the final configuration for the project.

### Deliverables / homework

- [ ] Retrieval table: dense / BM25 standard / BM25 nori / hybrid / + reranker / + query transform (Hit@5, MRR, p95).
- [ ] Elasticsearch index mapping in the repo; chosen configuration with reasons.

### Environment notes

- Elasticsearch needs ~2 GB RAM and the analysis-nori plugin; start it before loading models. Test the Colab install the day before, or use a free cloud trial.

### Interview questions

**Easy**

1. What is the difference between Hit@k and MRR?
2. What does BM25 score, and what is an analyzer?
3. What is HyDE?

**Medium**

4. Why does Korean text need the nori analyzer?
5. Explain Reciprocal Rank Fusion and why it works without score normalization.
6. Compare bi-encoders and cross-encoders in accuracy and cost.
7. Which query transformation would you use for conversational follow-up questions, and why?

**Hard**

8. Design an Elasticsearch index (mapping, analyzers, fields) for 1M Korean and English documents with department and date filters.
9. Your hybrid + reranker pipeline is accurate but p95 is 4 s. Bring it under 1.5 s.
10. When would you choose Elasticsearch hybrid search over a vector DB + separate BM25?

---

## Lesson 9 — Face-to-face Q&A and Review 2 — Lessons 7–8 + midterm feedback

**Type:** face-to-face Q&A

**Purpose:** Fix the most common midterm mistakes, review vector databases and search, and check every student's retrieval pipeline before evaluation and GraphRAG.

### Session plan (~2.5 h)

| Time | Activity |
|---|---|
| 0:00–0:25 | Midterm feedback: top 5 mistakes, best answers shown anonymously. |
| 0:25–0:40 | Quiz (10 questions below). |
| 0:40–1:30 | Retrieval clinic: each team shows one query that fails; the class diagnoses it (chunking, embedding, analyzer, filter, fusion, reranker). |
| 1:30–2:10 | Pipeline checkpoint: retrieval table (dense → hybrid → reranker), 5 minutes per team. |
| 2:10–2:30 | Prep for L10–L11: write 50 held-out test questions; create AuraDB Free accounts. |

### Review quiz

1. What do HNSW parameters M and ef_search control?
2. Memory estimate for 1M × 1024-dim fp32 vectors?
3. Qdrant vs Milvus vs pgvector — one sentence each.
4. What does an Elasticsearch mapping define?
5. Why the nori analyzer for Korean?
6. Write the RRF formula.
7. Bi-encoder vs cross-encoder?
8. Name three query transformations.
9. Which is better for exact product codes: BM25 or dense? Why?
10. Hit@5 vs MRR?

### Gate check — every student must have

- [ ] LangChain and LlamaIndex pipelines with citations on the project corpus.
- [ ] Elasticsearch hybrid + reranker results table.
- [ ] 50 held-out test questions written.
- [ ] Neo4j AuraDB (or local) account ready.

---

## Lesson 10 — RAG Evaluation & Hallucination Control — RAGAS, DeepEval, TruLens, LangSmith

**Goal:** Students build a held-out eval set, measure retrieval and generation with RAGAS, DeepEval and LLM-as-judge, run LangSmith experiments, control hallucination, and run the RAG vs SFT vs SFT+RAG experiment.

- **Builds on:** L8 retrieval harness; Month 3 evaluation habits.
- **Leads to:** L11 reports these numbers in the RAG app demo; Month 5 L10 puts DeepEval into CI.
- **Job postings:** PwC: faithfulness / relevance / groundedness, RAGAS, DeepEval, TruLens · THE CSR: held-out eval set, regression, hallucination control · 인포유앤컴퍼니: RAG evaluation frameworks · Agent Engineer (Bundang): LangSmith eval cycle · eZar: evaluation datasets, RAG vs SFT.

### A. Theory

#### 1. RAG failure taxonomy
- Retrieval miss (gold chunk not in top-k), ranking miss, context overflow / lost-in-the-middle, generation hallucination, wrong refusal.
- Rule: evaluate **retrieval** and **generation** separately, or you cannot tell which one to fix.

#### 2. Building an eval set (the part interviewers ask about)
- Human-written questions + reference answers + gold document IDs; types: easy, hard, multi-hop, **unanswerable (10–20%)**.
- Split **dev** (tune on it) and **test / held-out** (report on it, never tune). Record who wrote answers and who judges.

#### 3. Generation metrics: RAGAS, DeepEval, TruLens
- **RAGAS**: faithfulness, answer relevancy, context precision, context recall.
- **[NEW]** **DeepEval**: pytest-style LLM tests (faithfulness, answer relevancy, G-Eval custom criteria) — runs in CI (L11).
- **[NEW]** **TruLens**: the "RAG triad" — context relevance, groundedness, answer relevance — with a dashboard.
- Same idea, different tooling: know one deeply (RAGAS), use a second (DeepEval), recognize the third.

#### 4. LLM-as-judge
- Pointwise rubric vs pairwise comparison. Known biases: position, verbosity, self-preference.
- Calibrate: label 20–30 items by hand, report judge–human agreement.

#### **[NEW]** 5. LangSmith datasets and experiments
- Dataset = the eval set stored in LangSmith; experiment = one run of a pipeline version over the dataset with evaluators; compare experiments side by side (chunk size A vs B, with vs without reranker).
- The tracing–eval–improve cycle: trace a failure → add it to the dataset → change the system → run a new experiment.
- Langfuse offers the same (datasets, experiments) and can be self-hosted for on-prem (L11).

#### 6. Hallucination control
- Grounded prompt ("answer only from the context"), mandatory citations, "I don't know" when the best rerank score is below a threshold, post-hoc citation check, refusal precision on unanswerable questions.

#### 7. RAG vs SFT vs SFT+RAG
- Same questions, three systems: base + RAG, SFT model without RAG, SFT model + RAG.
- Expected story: SFT gives format/behavior, RAG gives facts, both together are best — prove it with numbers.

### B. Coding (Practice)

#### Lab 1 — Full eval set
- JSONL `{id, question, reference, gold_doc_ids, type}`: 30 dev (from L8) + 50 held-out test, incl. multi-hop and 10–20% unanswerable.

#### Lab 2 — RAGAS on the test set
- Faithfulness, answer relevancy, context precision/recall with an API judge model. Pin the RAGAS version.

#### **[NEW]** Lab 3 — DeepEval tests
- Write 5 pytest tests with DeepEval metrics (faithfulness, answer relevancy, one G-Eval rule such as "answer must cite a source"). These become the CI gate in L11.

```python
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase
def test_leave_policy():
    out, ctx = rag('How many days of annual leave?')
    tc = LLMTestCase(input='How many days of annual leave?',
                     actual_output=out, retrieval_context=ctx)
    assert_test(tc, [FaithfulnessMetric(threshold=0.8)])
```

#### **[NEW]** Lab 4 — TruLens RAG triad (short)
- Instrument the pipeline with TruLens; view context relevance, groundedness and answer relevance in its dashboard.

#### Lab 5 — LLM-as-judge + human agreement
- Rubric 1–5 for correctness and groundedness; label 20 by hand; compute agreement.

#### **[NEW]** Lab 6 — LangSmith datasets and experiments
- Upload the dev set as a LangSmith dataset; run experiments for 3 versions (dense / hybrid / hybrid + reranker) with custom evaluators; compare them in the LangSmith UI; take one failure from a trace and add it to the dataset.

```python
from langsmith import Client, evaluate
ls = Client()
ds = ls.create_dataset('rag-dev')
ls.create_examples(dataset_id=ds.id, inputs=[{'question': q} for q in qs],
                   outputs=[{'answer': a} for a in refs])
evaluate(rag_hybrid_rerank, data='rag-dev',
         evaluators=[correctness, hit_at_5], experiment_prefix='hybrid-rerank')
```

#### Lab 7 — Hallucination control
- Citation requirement + rerank-score threshold for refusal; measure refusal precision on unanswerables.

#### Lab 8 — RAG vs SFT vs SFT+RAG
- Run the three systems on 30 test questions with the same judge; one table, one paragraph of conclusions.

### Deliverables / homework

- [ ] Eval report: dataset card (size, authors, held-out), retrieval + RAGAS/DeepEval tables, LangSmith experiment link, before/after for each change, **one experiment that did not help and why**.
- [ ] DeepEval test file in the repo; RAG vs SFT vs SFT+RAG table.

### Environment notes

- Use an API model as judge; cache judge results to disk. LangSmith and DeepEval keys go in Colab Secrets.

### Interview questions

**Easy**

1. What does RAGAS faithfulness measure?
2. Why must the test set be held out?
3. What is an unanswerable question in an eval set and why include it?

**Medium**

4. Compare RAGAS, DeepEval and TruLens: what does each give you?
5. Which biases does LLM-as-judge have and how do you calibrate it?
6. How do LangSmith datasets and experiments support the tracing–eval–improve cycle?
7. How do you set the threshold for "I don't know" answers?

**Hard**

8. Answer THE CSR screening question for your own system: metric, eval set size, author, held-out?, judge, and one failed attempt.
9. Recall@5 is 0.9 but faithfulness is 0.6. Diagnose and fix.
10. A company has 5,000 internal documents that change weekly. RAG, fine-tuning or both? Justify with your experiment.

---

## Lesson 11 — GraphRAG + Neo4j and the Month 4 RAG App Demo

**Goal:** Students build a knowledge-graph retriever in Neo4j for relationship and multi-hop questions, compare it with vector and hybrid retrieval, and present a working RAG app with measured quality.

- **Builds on:** L5–L10 pipeline and eval set.
- **Leads to:** Month 5 turns the retrievers (vector, search, graph) into tools for agents.
- **Job postings:** PwC: Graph RAG / Hybrid RAG (vector + graph), ontology & knowledge-graph modeling · 메타펫: LLM·RAG·GraphRAG · SkyWorldwide: knowledge graph, GraphRAG, Neo4j.

### A. Theory

#### **[NEW]** 1. Why GraphRAG: limits of vector search
- Vector search finds similar chunks; it struggles with relationships ("which suppliers of product X are in Busan?"), multi-hop chains and whole-corpus questions ("main themes across all reports?").
- A knowledge graph stores entities and relationships explicitly — the retriever can follow them.

#### **[NEW]** 2. Knowledge graph basics
- Nodes (entities), relationships (typed, directed), properties; schema / ontology (allowed node and relationship types). Example: (Employee)-[:WORKS_IN]->(Department)-[:FOLLOWS]->(Policy).
- Building a graph from text: LLM-based entity and relationship extraction with a fixed schema, entity resolution (merge duplicates), keeping a link from every node to its source chunk for citations.

#### **[NEW]** 3. Neo4j and Cypher
- Neo4j: the most common graph database in postings. Cypher basics: MATCH, WHERE, RETURN, MERGE, path patterns `(a)-[:REL*1..3]->(b)`.
- Neo4j vector index: embeddings stored on nodes → vector search and graph traversal in one database.

#### **[NEW]** 4. GraphRAG retrieval patterns
- **Text-to-Cypher**: the LLM writes a Cypher query from the question (validate it; read-only user).
- **Entity + neighborhood**: find entities in the question → expand 1–2 hops → send the subgraph as context.
- **Hybrid (vector + graph)**: vector search finds chunks → follow their entities in the graph → merge.
- **Community summaries** (Microsoft GraphRAG idea): cluster the graph, summarize clusters, answer global questions.
- Cost: extraction is expensive and imperfect — use GraphRAG where relationships matter, not everywhere.

#### 5. Presenting a RAG system
- Demo story: problem → data → architecture → live questions (easy, multi-hop, unanswerable) → numbers → limits → next steps. Show citations and the eval table, not only nice answers.

#### 6. Month 4 recap
- Walk the to-do list and the job postings: which line of which posting each part of the RAG app answers.

### B. Coding (Practice)

#### **[NEW]** Lab 1 — Build a knowledge graph in Neo4j
- Neo4j AuraDB Free (cloud) or Neo4j in Docker on a laptop. Define a small schema for the project domain; extract entities and relationships from 20–30 documents with an LLM; MERGE them into Neo4j with links to source chunks.

```python
from langchain_neo4j import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
graph = Neo4jGraph(url=NEO4J_URI, username='neo4j', password=NEO4J_PW)
tr = LLMGraphTransformer(llm=llm,
        allowed_nodes=['Employee', 'Department', 'Policy'],
        allowed_relationships=['WORKS_IN', 'FOLLOWS', 'APPROVES'])
graph.add_graph_documents(tr.convert_to_graph_documents(chunks),
                          include_source=True)
```

#### **[NEW]** Lab 2 — Cypher and graph retrieval
- Write 5 Cypher queries by hand (lookups, 2-hop paths). Then text-to-Cypher with a read-only user and query validation, and an entity-neighborhood retriever.

```
MATCH (e:Employee)-[:WORKS_IN]->(d:Department)-[:FOLLOWS]->(p:Policy)
WHERE p.name CONTAINS 'leave'
RETURN d.name, collect(e.name) AS employees, p.name
```

#### **[NEW]** Lab 3 — Vector vs GraphRAG vs hybrid
- Add 10 multi-hop / relationship questions to the dev set. Compare vector RAG, GraphRAG and hybrid (vector + graph) as LangSmith experiments: accuracy, latency, cost of building the graph.

#### Lab 4 — RAG app with a simple UI
- Gradio app on top of the pipeline: question box, answer with clickable citations, retrieval mode (vector / hybrid / graph / hybrid + graph) and backend (API / 7B-AWQ / own model) dropdowns.

```python
with gr.Blocks() as demo:
    q = gr.Textbox(label='Question')
    mode = gr.Dropdown(['vector', 'hybrid', 'graph', 'hybrid+graph'], label='Retrieval')
    out = gr.Markdown()
    q.submit(answer_with_citations, [q, mode], out)
demo.launch(share=True)
```

#### Lab 5 — LIVE DEMO
- 5 minutes per student: three live questions, the eval table, one failure and what you would do next.

### Deliverables / homework

- [ ] Neo4j graph + 5 Cypher queries; vector vs GraphRAG vs hybrid table.
- [ ] Month 4 RAG app (repo + Gradio link) and the final eval report.

### Environment notes

- Neo4j does not run on Colab: use AuraDB Free (cloud) or Docker on a laptop. Credentials in Colab Secrets.
- Graph extraction calls the LLM once per chunk — use the API model or 7B-AWQ and start with 20–30 documents.

### Interview questions

**Easy**

1. What are nodes, relationships and properties in a knowledge graph?
2. What does a Cypher MATCH query do?
3. Name two questions vector RAG answers poorly.

**Medium**

4. How do you build a knowledge graph from text, and what goes wrong (entity resolution, schema drift)?
5. Compare text-to-Cypher, entity-neighborhood and hybrid graph retrieval.
6. How do you keep citations when the answer comes from the graph?
7. What would you show in a 5-minute RAG demo to convince an interviewer?

**Hard**

8. Design a vector + graph hybrid RAG for an accounting firm's regulations — schema, ingestion, retrieval, evaluation.
9. Text-to-Cypher can run dangerous or wrong queries. How do you make it safe and reliable?
10. When is GraphRAG not worth its cost? Argue with numbers from your experiment.

---

## Lesson 12 — Final Exam + RAG App Defense — Month 4

**Type:** exam

### Part A — Theory (30%)
- 15 short questions across L1–L11 + 1 system-design question, e.g. "On-prem RAG for 500,000 Korean regulation documents, 2 GPUs, 300 users."

### Part B — RAG app demo (50%)
- 10-minute demo + 5 minutes of questions: own (or tuned) model served, parsing incl. OCR, vector DB, Elasticsearch hybrid + reranker, GraphRAG module, citations, refusal on unanswerables.

### Part C — Eval report defense (20%)
- The instructor picks two numbers from the eval report; the student explains how they were measured and what would change them.

### Grading rubric

| Criterion | Weight | What "excellent" looks like |
|---|---|---|
| Model & serving | 15% | Own model (incl. L4 adapter) quantized and served; benchmark numbers |
| Parsing & indexing | 15% | OCR/VLM for scans, good chunking, vector DB choice justified |
| Retrieval | 20% | Elasticsearch hybrid + reranker, GraphRAG + Neo4j, measured per stage |
| Evaluation | 25% | Held-out set, RAGAS/DeepEval, LangSmith experiments, RAG vs SFT, failure reported |
| App & communication | 25% | Working UI with citations; clear demo; answers with numbers; knows limits |

---

## Month 4 Project — "RAG on my own model"

Built step by step from L1 to L11 and defended in L12. It becomes the retrieval core of the Month 5 agent system.

### Model & serving (L1–L4)
- [ ] Own model served behind an OpenAI-compatible API (fp16 / AWQ / GGUF), benchmark report.
- [ ] Versioned, measured prompt templates.
- [ ] Tool-calling LoRA adapter with before/after metrics; multi-LoRA serving.

### Data & retrieval (L5–L8)
- [ ] Corpus incl. PDF tables, scanned pages (OCR/VLM) and HWP if Korean domain.
- [ ] Vector DB (Qdrant or Milvus) with metadata filters; LangChain and LlamaIndex pipelines.
- [ ] Elasticsearch hybrid + reranker; per-stage latency.

### Quality (L10–L11)
- [ ] Held-out eval set, RAGAS + DeepEval, LangSmith experiments, refusal on unanswerables.
- [ ] GraphRAG + Neo4j module; vector vs graph vs hybrid table.
- [ ] RAG vs SFT vs SFT+RAG experiment.
- [ ] Gradio RAG app with citations; README with architecture and results.

---

## Environment & tooling

### Compute
- Google Colab T4 (16 GB, fp16 only, no FlashAttention-2) for all lessons.
- Kaggle 2×T4 for L4 tensor parallel. Neo4j: AuraDB Free or Docker on a laptop. Elasticsearch: local install on Colab or a free cloud trial.

### Models
- Own: my-llm-v2-dpo (0.5B, merged fp16 / AWQ / GGUF) and the 7B QLoRA adapter.
- Reference: Qwen2.5-0.5B/1.5B-Instruct (tool-calling comparison), Qwen2.5-7B-Instruct-AWQ (7B on T4), one API model.
- Embeddings: multilingual-e5-base, bge-m3. Reranker: bge-reranker-v2-m3. VLM: Qwen2.5-VL-3B-Instruct. OCR: PaddleOCR.

### Libraries (pin versions in requirements.txt)
- openai, vllm, llama.cpp, ollama, llm-compressor, transformers, peft, trl, optimum, onnxruntime
- pdfplumber, pyhwp, docling, paddleocr, sentence-transformers, faiss-cpu, qdrant-client, pymilvus
- langchain, langchain-openai, llama-index, elasticsearch (or opensearch-py)
- ragas, deepeval, trulens, langsmith, neo4j, langchain-neo4j, langchain-experimental, gradio

### Before each lesson (instructor checklist)
- Run every notebook on a fresh Colab runtime the day before; libraries in this stack change monthly.
- Upload the needed models to HF Hub in advance; large downloads should start before class.
- Keep API keys in Colab Secrets / .env; never in notebooks or Git.

## Job postings used (checked 2026-10-24)

- [Saramin — search "LLM 엔지니어" (≈590)](https://www.saramin.co.kr/zf_user/search/recruit?searchword=LLM%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4)
- [Saramin — search "RAG" (≈650)](https://www.saramin.co.kr/zf_user/search/recruit?searchword=RAG)
- [Saramin — 다비치 LLM Engineer (private LLM·RAG)](https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=55177736)
- [Saramin — eZar LLM Training Engineer](https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=54841110)
- [Saramin — Deloitte Anjin AI Engineer](https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=55341231)
- [Saramin — Agent Engineer, RAG/Agent company (Bundang)](https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=55380325)
- [Saramin — 더아이엠씨 AI Agent Engineer](https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=55377603)
- [Saramin — Samsung DS LLM project (freelance)](https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=55377333)
- [Saramin — 지티원 AI Enabled Developer (LLM/Fine-tuning)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=53657436)
- [JobKorea — search "LLM 엔지니어" (≈540)](https://www.jobkorea.co.kr/Search/?stext=LLM%20%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&tabType=recruit)
- [JobKorea — 퍼즐에이아이 LLM Engineer](https://www.jobkorea.co.kr/Recruit/GI_Read/50147800)
- [JobKorea — LLM Research Engineer (Post-training)](https://www.jobkorea.co.kr/Recruit/GI_Read/50222981)
- [JobKorea — LLM Research Engineer (Pre-training)](https://www.jobkorea.co.kr/Recruit/GI_Read/50223021)
- [JobKorea — NexIn AI Core Engineer (RAG & LLM)](https://www.jobkorea.co.kr/Recruit/GI_Read/50110162)
- [JobKorea — THE CSR AI Engineer (LLM·RAG)](https://www.jobkorea.co.kr/Recruit/GI_Read/50167851)
- [JobKorea — 메타펫 AI Engineer](https://www.jobkorea.co.kr/Recruit/GI_Read/50149241)
- [PwC Korea — AI Engineer (Agent, GraphRAG, MCP)](https://www.pwc.com/kr/ko/career/experienced/r260519.html)
- [Remember — 인포유앤컴퍼니 AI Data Engineer (RAG/Retrieval)](https://career.rememberapp.co.kr/job/posting/326847)
- [Jumpit — SkyWorldwide Knowledge Graph & Ontology Engineer](https://jumpit.saramin.co.kr/position/52967506)
- [Jumpit — 생성형 AI/LLM 엔지니어 (prompt engineering, LangGraph, MCP)](https://jumpit.saramin.co.kr/position/50533504)

*LinkedIn could not be read (page access was blocked).*
