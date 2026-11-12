"use client";

import { RefreshCw } from "lucide-react";
import Link from "next/link";
import { Select } from "@/components/ui/fields";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { cn } from "@/lib/format";
import type { CollectionInfo, DocumentRow } from "@/lib/types";

export interface KnowledgeFilters {
  collection: string;
  documentIds: string[]; // bo'sh = barcha hujjatlar
  fileTypes: string[];
  topics: string[];
  languages: string[];
}

function toggle(list: string[], value: string) {
  return list.includes(value) ? list.filter((item) => item !== value) : [...list, value];
}

export function KnowledgePanel({
  documents,
  collections,
  filters,
  onChange,
  loading,
  error,
  onRefresh,
}: {
  documents: DocumentRow[];
  collections: CollectionInfo[];
  filters: KnowledgeFilters;
  onChange: (filters: KnowledgeFilters) => void;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}) {
  const indexed = documents.filter((doc) => doc.indexed);
  const unique = (values: (string | null)[]) => [...new Set(values.filter(Boolean) as string[])].sort();
  const fileTypes = unique(indexed.map((d) => d.file_type));
  const topics = unique(indexed.map((d) => d.metadata.topic));
  const languages = unique(indexed.map((d) => d.metadata.language));

  return (
    <div className="flex h-full flex-col gap-5 overflow-y-auto p-4">
      <section>
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-sm font-semibold">Knowledge context</h2>
          <button onClick={onRefresh} className="rounded p-1 text-muted hover:bg-subtle" aria-label="Refresh sources">
            <RefreshCw className="size-3.5" />
          </button>
        </div>
        <Select
          aria-label="Qdrant collection"
          value={filters.collection}
          onChange={(e) => onChange({ ...filters, collection: e.target.value })}
        >
          {collections.length === 0 && <option value={filters.collection}>{filters.collection}</option>}
          {collections.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name} ({c.points} chunks)
            </option>
          ))}
        </Select>
      </section>

      {loading ? (
        <LoadingState label="Loading sources…" />
      ) : error ? (
        <ErrorState message={error} />
      ) : indexed.length === 0 ? (
        <p className="text-sm text-muted">
          No indexed documents. <Link href="/knowledge" className="font-medium text-primary">Index documents</Link> first.
        </p>
      ) : (
        <>
          <section>
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-muted">Sources</h3>
              <span className="text-xs text-muted">
                {filters.documentIds.length ? `${filters.documentIds.length} selected` : "All"}
              </span>
            </div>
            <ul className="flex flex-col gap-1">
              {indexed.map((doc) => {
                const checked = filters.documentIds.length === 0 || filters.documentIds.includes(doc.document_id);
                return (
                  <li key={doc.document_id}>
                    <label className="flex cursor-pointer items-start gap-2 rounded-lg px-2 py-1.5 hover:bg-subtle">
                      <input
                        type="checkbox"
                        className="mt-1 accent-primary"
                        checked={checked}
                        onChange={() => {
                          const base = filters.documentIds.length ? filters.documentIds : indexed.map((d) => d.document_id);
                          const next = toggle(base, doc.document_id);
                          onChange({ ...filters, documentIds: next.length === indexed.length ? [] : next });
                        }}
                      />
                      <span className="min-w-0">
                        <span className="block truncate text-sm">{doc.filename}</span>
                        <span className="text-xs text-muted">
                          {doc.file_type.toUpperCase()} · {doc.chunks} {doc.chunks === 1 ? "chunk" : "chunks"}{doc.metadata.topic ? ` · ${doc.metadata.topic}` : ""}
                        </span>
                      </span>
                    </label>
                  </li>
                );
              })}
            </ul>
          </section>

          <ChipGroup title="Document type" values={fileTypes} selected={filters.fileTypes} onToggle={(v) => onChange({ ...filters, fileTypes: toggle(filters.fileTypes, v) })} />
          <ChipGroup title="Topic" values={topics} selected={filters.topics} onToggle={(v) => onChange({ ...filters, topics: toggle(filters.topics, v) })} />
          <ChipGroup title="Language" values={languages} selected={filters.languages} onToggle={(v) => onChange({ ...filters, languages: toggle(filters.languages, v) })} />
          <p className="text-xs text-muted">Team, player and match filters appear once documents carry those IDs in their metadata.</p>
        </>
      )}
    </div>
  );
}

function ChipGroup({ title, values, selected, onToggle }: { title: string; values: string[]; selected: string[]; onToggle: (value: string) => void }) {
  if (!values.length) return null;
  return (
    <section>
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">{title}</h3>
      <div className="flex flex-wrap gap-1.5">
        {values.map((value) => (
          <button
            key={value}
            onClick={() => onToggle(value)}
            aria-pressed={selected.includes(value)}
            className={cn(
              "rounded-md border px-2 py-1 text-xs",
              selected.includes(value) ? "border-primary bg-primary-soft text-primary" : "border-line text-muted hover:bg-subtle",
            )}
          >
            {value}
          </button>
        ))}
      </div>
    </section>
  );
}
