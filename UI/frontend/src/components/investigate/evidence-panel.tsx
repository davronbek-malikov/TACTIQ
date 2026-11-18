import { EVIDENCE_CATEGORIES, EvidenceCard } from "@/components/evidence/evidence-card";
import { Badge } from "@/components/ui/badge";
import type { Evidence } from "@/lib/types";

// O'ng panel: javob ortidagi dalillar (Qdrant'dan topilgan chunk'lar)
export function EvidencePanel({ question, evidence, activeId, onSelect }: {
  question?: string;
  evidence: Evidence[];
  activeId: string | null;
  onSelect: (evidenceId: string) => void;
}) {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-line px-4 py-3">
        <h2 className="text-sm font-semibold">Evidence</h2>
        <p className="text-xs text-muted">{question ? `For: ${question}` : "Sources behind the answer appear here"}</p>
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
              active={activeId === item.evidence_id}
              expanded={activeId === item.evidence_id}
              onSelect={() => onSelect(item.evidence_id)}
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
}
