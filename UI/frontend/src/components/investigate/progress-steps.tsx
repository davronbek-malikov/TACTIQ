import { CircleCheck, CircleMinus, CircleX, LoaderCircle } from "lucide-react";
import { cn } from "@/lib/format";
import type { InvestigationStep } from "@/lib/types";

// Retrieval & Generation'ning 7 bosqichi. Faqat backend qaytargan HAQIQIY holat ko'rsatiladi.
export const PIPELINE_STEPS = [
  "User Question",
  "Query Embedding",
  "Similarity Search",
  "Top-k Retrieval",
  "Prompt Construction",
  "LLM Generation",
  "Answer + Sources",
];

export function ProgressSteps({ steps, running }: { steps?: InvestigationStep[]; running?: boolean }) {
  if (running) {
    return (
      <p className="flex items-center gap-2 text-sm text-muted" role="status">
        <LoaderCircle className="size-4 animate-spin" aria-hidden />
        Running the 7-step pipeline: retrieving evidence and generating the answer…
      </p>
    );
  }
  if (!steps?.length) return null;

  return (
    <ol className="flex flex-wrap gap-x-4 gap-y-1.5" aria-label="Pipeline steps">
      {steps.map((step) => {
        const Icon = step.status === "done" ? CircleCheck : step.status === "failed" ? CircleX : CircleMinus;
        return (
          <li
            key={step.id}
            className={cn(
              "flex items-center gap-1.5 text-xs",
              step.status === "done" ? "text-ink" : step.status === "failed" ? "text-danger" : "text-muted",
            )}
            title={step.detail}
          >
            <Icon className={cn("size-3.5", step.status === "done" && "text-primary")} aria-hidden />
            <span className="font-medium">{step.id}</span> {step.name}
            {step.duration_ms !== null && <span className="text-muted">{step.duration_ms} ms</span>}
          </li>
        );
      })}
    </ol>
  );
}
