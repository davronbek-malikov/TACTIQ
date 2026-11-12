"use client";

import { ArrowUp, Image as ImageIcon, Mic, Paperclip, Video } from "lucide-react";
import { useState, type KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/fields";
import { cn } from "@/lib/format";
import type { AnswerMode, LlmId, LlmInfo } from "@/lib/types";

const LLM_LABELS: Record<LlmId, string> = {
  qwen: "Qwen · local (offline)",
  groq: "Groq · cloud",
  gemini: "Gemini · cloud (free tier)",
};

// Kelajakdagi multimodal kirishlar — hozircha faqat interfeys (ishlayotgandek ko'rsatilmaydi)
const FUTURE_INPUTS = [
  { icon: Paperclip, label: "Attach document — use the Knowledge page to add documents for now" },
  { icon: ImageIcon, label: "Image input — coming soon" },
  { icon: Video, label: "Video clip — coming soon (V2)" },
  { icon: Mic, label: "Voice question — coming soon" },
];

export function Composer({
  llms,
  llm,
  onLlmChange,
  mode,
  onModeChange,
  onSubmit,
  busy,
  initialQuestion = "",
}: {
  llms: LlmInfo[];
  llm: LlmId;
  onLlmChange: (llm: LlmId) => void;
  mode: AnswerMode;
  onModeChange: (mode: AnswerMode) => void;
  onSubmit: (question: string) => void;
  busy: boolean;
  initialQuestion?: string;
}) {
  const [question, setQuestion] = useState(initialQuestion);
  const selected = llms.find((item) => item.id === llm);

  const submit = () => {
    if (!question.trim() || busy) return;
    onSubmit(question.trim());
    setQuestion("");
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <div className="rounded-xl border border-line bg-card shadow-sm focus-within:border-primary/50">
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={onKeyDown}
        rows={3}
        placeholder="Ask a football question, e.g. What is counterpressing?"
        aria-label="Question"
        className="w-full resize-none rounded-t-xl bg-transparent px-4 pt-3 text-[15px] placeholder:text-muted/70 focus:outline-none"
      />
      <div className="flex flex-wrap items-center gap-2 border-t border-line px-3 py-2">
        <div className="flex items-center">
          {FUTURE_INPUTS.map(({ icon: Icon, label }) => (
            <span key={label} title={label} className="rounded-md p-2 text-muted/50" aria-label={label} role="img">
              <Icon className="size-4" />
            </span>
          ))}
        </div>
        <div className="ml-auto flex w-full items-center gap-2 sm:w-auto">
          <Select
            aria-label="Answer mode"
            value={mode}
            onChange={(e) => onModeChange(e.target.value as AnswerMode)}
            className="h-9 min-w-0 flex-1 text-xs sm:w-auto sm:flex-none sm:min-w-44"
          >
            <option value="rag">RAG — from documents</option>
            <option value="llm_only">LLM only — no documents</option>
          </Select>
          <Select
            aria-label="LLM"
            value={llm}
            onChange={(e) => onLlmChange(e.target.value as LlmId)}
            className="h-9 min-w-0 flex-1 text-xs sm:w-auto sm:flex-none sm:min-w-52"
          >
            {(llms.length ? llms : (["qwen", "groq", "gemini"] as LlmId[]).map((id) => ({ id, ready: false }) as LlmInfo)).map((item) => (
              <option key={item.id} value={item.id}>
                {LLM_LABELS[item.id]} {item.ready ? "" : "— not configured"}
              </option>
            ))}
          </Select>
          <Button onClick={submit} disabled={!question.trim()} loading={busy} aria-label="Ask">
            {!busy && <ArrowUp className="size-4" />}
            Ask
          </Button>
        </div>
      </div>
      {selected && (
        <p className={cn("border-t border-line px-4 py-1.5 text-xs", selected.ready ? "text-muted" : "text-warning")}>
          {selected.model} · {selected.detail}
        </p>
      )}
    </div>
  );
}
