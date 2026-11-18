import { BarChart3, Database, ExternalLink, FileSearch, FileText, Image as ImageIcon, Mic, PlayCircle } from "lucide-react";
import type { ReactNode } from "react";
import { Badge, type Tone } from "@/components/ui/badge";
import { rawDocumentUrl, sourcePageUrl } from "@/lib/api";
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

// Matndagi http(s) manzillarni bosiladigan havolaga aylantiradi
function linkify(text: string): ReactNode[] {
  return text.split(/(https?:\/\/[^\s)]+)/g).map((part, i) =>
    /^https?:\/\//.test(part) ? (
      <a key={i} href={part} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()} className="break-all text-primary underline underline-offset-2">
        {part}
      </a>
    ) : (
      part
    ),
  );
}

const linkClass = "inline-flex items-center gap-1 rounded-md border border-line px-2 py-1 text-xs font-medium text-ink hover:border-primary/40 hover:text-primary";

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
        {linkify(evidence.text)}
      </p>
      {evidence.source_name && evidence.filename && (
        <div className="mt-2 flex flex-wrap gap-1.5" onClick={(e) => e.stopPropagation()}>
          {/* yangi tab: Investigate'dagi suhbat yo'qolmasin */}
          <a href={sourcePageUrl(evidence.source_name, evidence.filename, evidence.chunk_index)} target="_blank" rel="noreferrer" className={linkClass} title="Open the full document with this passage highlighted">
            <FileSearch className="size-3.5" /> View in document
          </a>
          <a href={rawDocumentUrl(evidence.source_name, evidence.filename, evidence.page)} target="_blank" rel="noreferrer" className={linkClass} title="Open the original file in a new tab">
            <ExternalLink className="size-3.5" /> Open file
          </a>
          {evidence.provider_url && (
            <a href={evidence.provider_url} target="_blank" rel="noreferrer" className={linkClass} title="Original data provider">
              <Database className="size-3.5" /> Data source
            </a>
          )}
        </div>
      )}
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
