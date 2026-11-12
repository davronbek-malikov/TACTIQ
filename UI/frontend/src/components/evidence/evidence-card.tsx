import { BarChart3, FileText, Image as ImageIcon, Mic, PlayCircle } from "lucide-react";
import { Badge, type Tone } from "@/components/ui/badge";
import { cn, formatTimestamp } from "@/lib/format";
import type { Evidence, EvidenceCategory, EvidenceKind } from "@/lib/types";

// 6 ta dalil turi — TACTIQ'ning aniqlik tamoyili
export const EVIDENCE_CATEGORIES: Record<EvidenceCategory, { label: string; tone: Tone }> = {
  verified_fact: { label: "Verified fact", tone: "success" },
  retrieved_document_evidence: { label: "Document evidence", tone: "info" },
  analytical_observation: { label: "Analytical observation", tone: "neutral" },
  hypothesis: { label: "Hypothesis", tone: "warning" },
  recommendation: { label: "Recommendation", tone: "success" },
  cannot_be_verified: { label: "Cannot be verified", tone: "danger" },
};

const KIND_ICON: Record<EvidenceKind, typeof FileText> = {
  document: FileText,
  statistic: BarChart3,
  video: PlayCircle,
  image: ImageIcon,
  audio: Mic,
};

export function EvidenceCategoryBadge({ category }: { category: EvidenceCategory }) {
  const { label, tone } = EVIDENCE_CATEGORIES[category];
  return <Badge tone={tone}>{label}</Badge>;
}

// Bitta dalil: hujjat (sahifa), statistika, video (vaqt belgisi), rasm yoki audio
export function EvidenceCard({
  evidence,
  number,
  active,
  onSelect,
  expanded,
}: {
  evidence: Evidence;
  number: number;
  active?: boolean;
  onSelect?: () => void;
  expanded?: boolean;
}) {
  const Icon = KIND_ICON[evidence.kind];
  return (
    <article
      id={`evidence-${evidence.evidence_id}`}
      className={cn(
        "rounded-lg border bg-card p-3 transition-colors",
        active ? "border-primary ring-1 ring-primary/30" : "border-line",
        onSelect && "cursor-pointer hover:border-primary/40",
      )}
      onClick={onSelect}
    >
      <header className="flex items-start gap-2">
        <span className="grid size-6 shrink-0 place-items-center rounded-md bg-primary-soft text-xs font-semibold text-primary">
          {number}
        </span>
        <div className="min-w-0 flex-1">
          <p className="flex items-center gap-1.5 truncate text-sm font-medium">
            <Icon className="size-3.5 shrink-0 text-muted" aria-hidden />
            {evidence.title}
          </p>
          <div className="mt-1 flex flex-wrap items-center gap-1.5">
            <EvidenceCategoryBadge category={evidence.category} />
            {evidence.score !== null && <span className="text-xs text-muted">relevance {evidence.score.toFixed(2)}</span>}
            {evidence.video && (
              <span className="text-xs text-muted">
                {evidence.video.match_label} · {formatTimestamp(evidence.video.timestamp_seconds)}
              </span>
            )}
          </div>
        </div>
      </header>
      <p className={cn("mt-2 whitespace-pre-line text-sm leading-relaxed text-ink/90", !expanded && "line-clamp-4")}>
        {evidence.text}
      </p>
      {expanded && Object.values(evidence.metadata).some(Boolean) && (
        <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-1 border-t border-line pt-2 text-xs">
          {Object.entries(evidence.metadata).map(([key, value]) =>
            value ? (
              <div key={key} className="contents">
                <dt className="text-muted">{key.replace("_", " ")}</dt>
                <dd className="truncate">{String(value)}</dd>
              </div>
            ) : null,
          )}
        </dl>
      )}
    </article>
  );
}
