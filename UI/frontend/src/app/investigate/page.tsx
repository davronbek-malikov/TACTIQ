"use client";

import { Bot, PanelLeftClose, PanelLeftOpen, PanelRightClose, PanelRightOpen, Plus, Save, SlidersHorizontal, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { EVIDENCE_CATEGORIES, EvidenceCard } from "@/components/evidence/evidence-card";
import { AnswerText } from "@/components/investigate/answer-text";
import { Composer } from "@/components/investigate/composer";
import { KnowledgePanel, type KnowledgeFilters } from "@/components/investigate/knowledge-panel";
import { ProgressSteps } from "@/components/investigate/progress-steps";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState, ErrorState } from "@/components/ui/states";
import { api } from "@/lib/api";
import { cn } from "@/lib/format";
import { saveReport } from "@/lib/reports";
import type { AnswerMode, InvestigateResponse, LlmId } from "@/lib/types";
import { useApi } from "@/lib/use-api";

interface Turn {
  id: string;
  question: string;
  llm: LlmId;
  mode: AnswerMode;
  status: "running" | "done" | "error";
  response?: InvestigateResponse;
  error?: string;
  saved?: boolean;
}

export default function InvestigatePage() {
  const documents = useApi(() => api.documents());
  const collections = useApi(() => api.collections().catch(() => []));
  const llms = useApi(() => api.llms());
  const system = useApi(() => api.system());

  const [filters, setFilters] = useState<KnowledgeFilters>({ collection: "", documentIds: [], fileTypes: [], topics: [], languages: [] });
  const [llm, setLlm] = useState<LlmId>("qwen");
  const [mode, setMode] = useState<AnswerMode>("rag");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [activeTurnId, setActiveTurnId] = useState<string | null>(null);
  const [activeEvidence, setActiveEvidence] = useState<string | null>(null);
  const [showSources, setShowSources] = useState(true);
  const [showEvidence, setShowEvidence] = useState(true);
  const [mobilePanel, setMobilePanel] = useState<"sources" | "evidence" | null>(null);
  const [prefill, setPrefill] = useState("");

  // Overview'dagi "suggested question" -> ?q=...
  useEffect(() => {
    const q = new URLSearchParams(window.location.search).get("q");
    if (q) setPrefill(q);
  }, []);

  // Birinchi tayyor LLM'ni tanlash
  useEffect(() => {
    const ready = llms.data?.find((item) => item.ready);
    if (ready) setLlm(ready.id);
  }, [llms.data]);

  const collection = filters.collection || system.data?.collection.name || "";
  const activeTurn = useMemo(
    () => turns.find((t) => t.id === activeTurnId) ?? [...turns].reverse().find((t) => t.response),
    [turns, activeTurnId],
  );
  const evidence = activeTurn?.response?.evidence ?? [];
  const busy = turns.some((t) => t.status === "running");

  async function ask(question: string, askMode: AnswerMode = mode) {
    const id = crypto.randomUUID();
    setTurns((prev) => [...prev, { id, question, llm, mode: askMode, status: "running" }]);
    try {
      const response = await api.investigate({
        question,
        llm,
        mode: askMode,
        collection: collection || undefined,
        document_ids: filters.documentIds,
        file_types: filters.fileTypes,
        topics: filters.topics,
        languages: filters.languages,
      });
      setTurns((prev) => prev.map((t) => (t.id === id ? { ...t, status: "done", response } : t)));
      setActiveTurnId(id);
      setActiveEvidence(null);
    } catch (err) {
      setTurns((prev) => prev.map((t) => (t.id === id ? { ...t, status: "error", error: err instanceof Error ? err.message : String(err) } : t)));
    }
  }

  function cite(turnId: string, evidenceId: string) {
    setActiveTurnId(turnId);
    setActiveEvidence(evidenceId);
    setShowEvidence(true);
    setMobilePanel("evidence");
    setTimeout(() => document.getElementById(`evidence-${evidenceId}`)?.scrollIntoView({ behavior: "smooth", block: "nearest" }), 50);
  }

  const sourcesPanel = (
    <KnowledgePanel
      documents={documents.data ?? []}
      collections={collections.data ?? []}
      filters={{ ...filters, collection }}
      onChange={setFilters}
      loading={documents.loading}
      error={documents.error}
      onRefresh={() => (documents.reload(), collections.reload())}
    />
  );

  const evidencePanel = (
    <div className="flex h-full flex-col">
      <div className="border-b border-line px-4 py-3">
        <h2 className="text-sm font-semibold">Evidence</h2>
        <p className="text-xs text-muted">{activeTurn ? `For: ${activeTurn.question}` : "Sources behind the answer appear here"}</p>
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto p-3">
        {evidence.length === 0 ? (
          <p className="px-1 py-6 text-center text-sm text-muted">No evidence yet.</p>
        ) : (
          evidence.map((item, index) => (
            <EvidenceCard
              key={item.evidence_id}
              evidence={item}
              number={index + 1}
              active={activeEvidence === item.evidence_id}
              expanded={activeEvidence === item.evidence_id}
              onSelect={() => setActiveEvidence(item.evidence_id)}
            />
          ))
        )}
      </div>
      <details className="border-t border-line px-4 py-3 text-xs text-muted">
        <summary className="cursor-pointer font-medium">Evidence categories</summary>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {Object.values(EVIDENCE_CATEGORIES).map((c) => (
            <Badge key={c.label} tone={c.tone}>{c.label}</Badge>
          ))}
        </div>
        <p className="mt-2">Today the engine returns document evidence. Statistics, video timestamps and validation labels arrive with later modules.</p>
      </details>
    </div>
  );

  return (
    <div className="-mx-4 -my-6 flex h-[calc(100dvh-4rem)] sm:-mx-6 lg:-mx-8">
      {/* LEFT — knowledge context */}
      {showSources && <aside className="hidden w-72 shrink-0 border-r border-line bg-card xl:block">{sourcesPanel}</aside>}

      {/* CENTER — conversation */}
      <section className="flex min-w-0 flex-1 flex-col">
        <div className="flex items-center gap-2 border-b border-line px-4 py-2">
          <button className="hidden rounded-md p-1.5 text-muted hover:bg-subtle xl:block" onClick={() => setShowSources(!showSources)} aria-label="Toggle sources panel">
            {showSources ? <PanelLeftClose className="size-4" /> : <PanelLeftOpen className="size-4" />}
          </button>
          <button className="rounded-md p-1.5 text-muted hover:bg-subtle xl:hidden" onClick={() => setMobilePanel("sources")} aria-label="Open sources">
            <SlidersHorizontal className="size-4" />
          </button>
          <h1 className="min-w-0 flex-1 truncate text-sm font-semibold">Investigation</h1>
          <Button variant="secondary" size="sm" onClick={() => (setTurns([]), setActiveTurnId(null), setActiveEvidence(null))} disabled={!turns.length || busy}>
            <Plus className="size-4" /> <span className="hidden sm:inline">New investigation</span>
          </Button>
          <button className="rounded-md p-1.5 text-muted hover:bg-subtle xl:hidden" onClick={() => setMobilePanel("evidence")} aria-label="Open evidence">
            <PanelRightOpen className="size-4" />
          </button>
          <button className="hidden rounded-md p-1.5 text-muted hover:bg-subtle xl:block" onClick={() => setShowEvidence(!showEvidence)} aria-label="Toggle evidence panel">
            {showEvidence ? <PanelRightClose className="size-4" /> : <PanelRightOpen className="size-4" />}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto flex max-w-3xl flex-col gap-6">
            {turns.length === 0 ? (
              <EmptyState
                icon={Bot}
                title="Start an investigation"
                description="Ask a question about your indexed documents. TACTIQ retrieves the most relevant passages and answers only from them, with numbered citations."
              />
            ) : (
              turns.map((turn) => <TurnView key={turn.id} turn={turn} busy={busy} onAskWithRag={() => ask(turn.question, "rag")} onCite={(eid) => cite(turn.id, eid)} onSave={() => {
                if (!turn.response) return;
                saveReport(turn.response);
                setTurns((prev) => prev.map((t) => (t.id === turn.id ? { ...t, saved: true } : t)));
              }} />)
            )}
          </div>
        </div>

        <div className="border-t border-line bg-canvas px-4 py-3">
          <div className="mx-auto max-w-3xl">
            {llms.error && <div className="mb-2"><ErrorState message={llms.error} /></div>}
            <Composer key={prefill} llms={llms.data ?? []} llm={llm} onLlmChange={setLlm} mode={mode} onModeChange={setMode} onSubmit={(q) => ask(q)} busy={busy} initialQuestion={prefill} />
          </div>
        </div>
      </section>

      {/* RIGHT — evidence */}
      {showEvidence && <aside className="hidden w-96 shrink-0 border-l border-line bg-card xl:block">{evidencePanel}</aside>}

      {/* Kichik ekranlar: panellar drawer ko'rinishida */}
      {mobilePanel && (
        <div className="fixed inset-0 z-40 xl:hidden">
          <button className="absolute inset-0 bg-ink/20" onClick={() => setMobilePanel(null)} aria-label="Close panel" />
          <div className={cn("absolute inset-y-0 w-[min(24rem,90vw)] bg-card shadow-xl", mobilePanel === "sources" ? "left-0" : "right-0")}>
            <button className="absolute right-3 top-3 z-10 rounded-md p-1 text-muted hover:bg-subtle" onClick={() => setMobilePanel(null)} aria-label="Close">
              <X className="size-4" />
            </button>
            {mobilePanel === "sources" ? sourcesPanel : evidencePanel}
          </div>
        </div>
      )}
    </div>
  );
}

function TurnView({ turn, busy, onAskWithRag, onCite, onSave }: { turn: Turn; busy: boolean; onAskWithRag: () => void; onCite: (evidenceId: string) => void; onSave: () => void }) {
  const response = turn.response;
  return (
    <div className="flex flex-col gap-3">
      <div className="self-end rounded-xl bg-primary-soft px-4 py-2.5 text-[15px] text-ink">{turn.question}</div>
      <div className="rounded-xl border border-line bg-card p-4">
        <div className="mb-3 flex items-center justify-between gap-2">
          <span className="flex items-center gap-2 text-xs font-medium text-muted">
            <Badge tone={turn.mode === "rag" ? "success" : "warning"}>{turn.mode === "rag" ? "RAG" : "LLM only"}</Badge>
            {turn.llm}{response ? ` (${response.model})` : ""}
          </span>
          {response?.answered && (
            <Button variant="ghost" size="sm" onClick={onSave} disabled={turn.saved}>
              <Save className="size-3.5" /> {turn.saved ? "Saved" : "Save to reports"}
            </Button>
          )}
        </div>

        {turn.status === "running" && <ProgressSteps running />}
        {turn.status === "error" && <ErrorState message={turn.error ?? "Request failed"} />}

        {response && (
          <div className="flex flex-col gap-3">
            {response.answer && <AnswerText text={response.answer} onCite={onCite} />}
            {response.mode === "llm_only" && response.answered && (
              <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-warning-soft px-3 py-2 text-xs text-warning">
                <span>Model&apos;s own knowledge — not checked against your documents, no sources. It may be wrong or out of date.</span>
                <Button variant="secondary" size="sm" onClick={onAskWithRag} disabled={busy}>Ask the same with RAG</Button>
              </div>
            )}
            {!response.answered && !response.error && (
              <p className="text-sm text-muted">No passage in the selected sources was relevant enough, so the LLM was not called. Nothing was invented.</p>
            )}
            {response.error && (
              <ErrorState message={`Evidence was retrieved, but the LLM could not answer: ${response.error}`} />
            )}
            <div className="border-t border-line pt-3">
              <ProgressSteps steps={response.steps} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
