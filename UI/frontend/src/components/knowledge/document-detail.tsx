"use client";

import { Pencil, Trash2, X } from "lucide-react";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Field, Input } from "@/components/ui/fields";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { api } from "@/lib/api";
import type { DocumentMetadata, DocumentRow } from "@/lib/types";
import { useApi } from "@/lib/use-api";

const EDITABLE_FIELDS: (keyof DocumentMetadata)[] = ["document_type", "topic", "language", "match_id", "team_id", "player_id"];

// Hujjat tafsilotlari: metadata, matn namunasi, Qdrant'dagi chunk'lar
export function DocumentDetailPanel({ row, onClose, onChanged }: { row: DocumentRow; onClose: () => void; onChanged: () => void }) {
  const detail = useApi(() => api.document(row.source, row.filename), [row.source, row.filename]);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<DocumentMetadata>(row.metadata);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function saveMetadata() {
    try {
      await api.updateMetadata(row.source, row.filename, form);
      setEditing(false);
      setMessage("Metadata saved. Qdrant is updated automatically in a few seconds.");
      onChanged();
      detail.reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  async function remove() {
    if (!confirm(`Delete ${row.filename} and its chunks from Qdrant?`)) return;
    try {
      await api.deleteDocument(row.source, row.filename);
      onChanged();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  const data = detail.data;
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-start justify-between gap-3 border-b border-line px-5 py-4">
        <div className="min-w-0">
          <h2 className="truncate text-base font-semibold">{row.filename}</h2>
          <p className="text-xs text-muted">{row.source.replace("_", " ")} · {row.file_type.toUpperCase()}</p>
        </div>
        <button onClick={onClose} className="rounded-md p-1 text-muted hover:bg-subtle" aria-label="Close details"><X className="size-4" /></button>
      </div>

      <div className="flex-1 space-y-5 overflow-y-auto p-5">
        {error && <ErrorState message={error} />}
        {message && <p className="rounded-lg bg-primary-soft px-3 py-2 text-sm text-primary">{message}</p>}
        {detail.loading && <LoadingState />}
        {detail.error && <ErrorState message={detail.error} />}

        {data && (
          <>
            <section>
              <div className="mb-2 flex items-center justify-between">
                <h3 className="text-sm font-semibold">Metadata</h3>
                {row.editable && !editing && (
                  <Button variant="ghost" size="sm" onClick={() => setEditing(true)}><Pencil className="size-3.5" /> Edit</Button>
                )}
              </div>
              {editing ? (
                <div className="space-y-3">
                  {EDITABLE_FIELDS.map((key) => (
                    <Field key={key} label={key}>
                      <Input value={form[key] ?? ""} onChange={(e) => setForm({ ...form, [key]: e.target.value || null })} placeholder="unknown" />
                    </Field>
                  ))}
                  <p className="text-xs text-muted">Only fill IDs you actually know. Empty means unknown.</p>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={saveMetadata}>Save</Button>
                    <Button size="sm" variant="secondary" onClick={() => (setEditing(false), setForm(row.metadata))}>Cancel</Button>
                  </div>
                </div>
              ) : (
                <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-sm">
                  {Object.entries(data.metadata).map(([key, value]) => (
                    <div key={key} className="contents">
                      <dt className="text-muted">{key}</dt>
                      <dd className="truncate font-mono text-xs leading-5" title={String(value ?? "")}>{value ?? <span className="text-muted">—</span>}</dd>
                    </div>
                  ))}
                  <dt className="text-muted">embedding_model</dt>
                  <dd className="truncate font-mono text-xs leading-5">{data.embedding_model ?? "not indexed"}</dd>
                </dl>
              )}
              {!row.editable && <p className="mt-2 text-xs text-muted">Sample documents are read-only.</p>}
            </section>

            <section>
              <h3 className="mb-2 text-sm font-semibold">Extracted text</h3>
              <div className="space-y-2">
                {data.pages.map((page, index) => (
                  <div key={index} className="rounded-lg bg-subtle p-3">
                    <p className="mb-1 text-xs text-muted">{page.page ? `Page ${page.page}` : "Full document"} · {page.characters} characters</p>
                    <p className="line-clamp-6 whitespace-pre-line text-sm">{page.preview}</p>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 className="mb-2 text-sm font-semibold">Chunks in Qdrant <Badge className="ml-1">{data.chunks.length}</Badge></h3>
              {data.chunks.length === 0 ? (
                <p className="text-sm text-muted">Not indexed yet.</p>
              ) : (
                <ol className="space-y-2">
                  {data.chunks.map((chunk) => (
                    <li key={`${chunk.page}-${chunk.chunk_index}`} className="rounded-lg border border-line p-3">
                      <p className="mb-1 text-xs text-muted">
                        chunk {chunk.chunk_index}{chunk.page ? ` · page ${chunk.page}` : ""} · {chunk.token_count} tokens
                      </p>
                      <p className="line-clamp-4 whitespace-pre-line text-sm">{chunk.text}</p>
                    </li>
                  ))}
                </ol>
              )}
            </section>
          </>
        )}
      </div>

      {row.editable && (
        <div className="border-t border-line p-4">
          <Button variant="danger" size="sm" onClick={remove}><Trash2 className="size-3.5" /> Delete document</Button>
        </div>
      )}
    </div>
  );
}
