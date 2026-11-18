import { Save } from "lucide-react";
import { AnswerText } from "@/components/investigate/answer-text";
import { ProgressSteps } from "@/components/investigate/progress-steps";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/states";
import type { AnswerMode, InvestigateResponse, LlmId } from "@/lib/types";

// Suhbatdagi bitta savol-javob
export interface Turn {
  id: string;
  question: string;
  llm: LlmId;
  mode: AnswerMode;
  status: "running" | "done" | "error";
  response?: InvestigateResponse;
  error?: string;
  saved?: boolean;
  group?: string; // Compare rejimi: LLM only + RAG juftligi
}

// Savol (o'ngda) + javob kartasi: matn, [1] manbalar, ogohlantirishlar, 7 bosqich
export function TurnView({ turn, busy, compact = false, onAskWithRag, onCite, onSave }: {
  turn: Turn;
  busy: boolean;
  compact?: boolean; // Compare: savol ustida bir marta ko'rsatiladi, "Ask with RAG" tugmasi kerak emas
  onAskWithRag: () => void;
  onCite: (evidenceId: string) => void;
  onSave: () => void;
}) {
  const response = turn.response;
  return (
    <div className="flex flex-col gap-3">
      {!compact && <div className="self-end rounded-xl bg-primary-soft px-4 py-2.5 text-[15px] text-ink">{turn.question}</div>}
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
                {!compact && <Button variant="secondary" size="sm" onClick={onAskWithRag} disabled={busy}>Ask the same with RAG</Button>}
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
