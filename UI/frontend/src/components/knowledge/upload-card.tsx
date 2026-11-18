"use client";

import { CheckCircle2, Search, Upload } from "lucide-react";
import Link from "next/link";
import { useRef, useState, type DragEvent } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader } from "@/components/ui/card";
import { Field, Input } from "@/components/ui/fields";
import { ErrorState } from "@/components/ui/states";
import { api } from "@/lib/api";
import { cn, formatBytes } from "@/lib/format";
import type { IndexingJob } from "@/lib/types";

const ALLOWED = [".pdf", ".docx", ".txt", ".md"];
const MAX_BYTES = 20 * 1024 * 1024;

type Status =
  | { kind: "idle" }
  | { kind: "uploading" | "indexing"; message: string }
  | { kind: "ready"; message: string }
  | { kind: "error"; message: string };

// Backend upload'dan keyin o'zi index qiladi. Biz shu index tugashini kutamiz:
// tarixda upload boshlangandan KEYIN boshlangan my_documents job paydo bo'lishi kerak.
async function waitForIndexing(since: number): Promise<IndexingJob> {
  for (let i = 0; i < 600; i++) {
    const done = (await api.indexingHistory()).find(
      (job) => job.source === "my_documents" && new Date(job.started_at).getTime() >= since - 2000,
    );
    if (done) return done;
    await new Promise((resolve) => setTimeout(resolve, 1500));
  }
  throw new Error("Indexing is taking too long. Check the Indexing card below.");
}

// Fayl(lar) -> my_documents -> avtomatik index -> Investigate'da so'rash mumkin
export function UploadCard({ onUploaded }: { onUploaded: () => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [dragging, setDragging] = useState(false);
  const [meta, setMeta] = useState({ document_type: "", topic: "", language: "" });
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const busy = status.kind === "uploading" || status.kind === "indexing";

  function pick(list: FileList | null | undefined) {
    if (!list?.length) return;
    const chosen = Array.from(list);
    const bad = chosen.find((f) => !ALLOWED.includes(f.name.slice(f.name.lastIndexOf(".")).toLowerCase()));
    if (bad) return setStatus({ kind: "error", message: `${bad.name}: unsupported format. Allowed: ${ALLOWED.join(", ")}` });
    const big = chosen.find((f) => f.size > MAX_BYTES);
    if (big) return setStatus({ kind: "error", message: `${big.name} is larger than 20 MB.` });
    setFiles(chosen);
    setStatus({ kind: "idle" });
  }

  function onDrop(event: DragEvent) {
    event.preventDefault();
    setDragging(false);
    pick(event.dataTransfer.files);
  }

  async function upload() {
    if (!files.length) return;
    const since = Date.now();
    try {
      for (const [n, file] of files.entries()) {
        setStatus({ kind: "uploading", message: `Uploading ${file.name} (${n + 1}/${files.length})…` });
        await api.upload(file, meta, true); // bir xil nomli fayl yangilanadi
      }
      onUploaded();
      setStatus({ kind: "indexing", message: "Reading the text and saving it to the knowledge base… This can take a minute." });
      const job = await waitForIndexing(since);
      onUploaded();
      if (job.status === "failed") throw new Error(job.error ?? "Indexing failed");
      const names = files.map((f) => f.name).join(", ");
      setStatus({ kind: "ready", message: `${names} ${files.length > 1 ? "are" : "is"} ready. You can ask about ${files.length > 1 ? "them" : "it"} now.` });
      setFiles([]);
    } catch (err) {
      setStatus({ kind: "error", message: err instanceof Error ? err.message : String(err) });
    }
  }

  return (
    <Card>
      <CardHeader title="Add documents" description="PDF, DOCX, TXT or Markdown · max 20 MB each · indexed automatically" />
      <div className="space-y-4 p-5">
        <div
          role="button"
          tabIndex={0}
          onClick={() => input.current?.click()}
          onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && input.current?.click()}
          onDragOver={(e) => (e.preventDefault(), setDragging(true))}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          className={cn(
            "flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-8 text-center transition-colors",
            dragging ? "border-primary bg-primary-soft" : "border-line hover:border-primary/40 hover:bg-subtle",
          )}
        >
          <Upload className="mb-2 size-6 text-primary" aria-hidden />
          {files.length ? (
            <ul className="text-sm font-medium">
              {files.map((f) => <li key={f.name}>{f.name} <span className="text-muted">· {formatBytes(f.size)}</span></li>)}
            </ul>
          ) : (
            <p className="text-sm"><span className="font-medium text-primary">Choose files</span> or drag them here</p>
          )}
          <input ref={input} type="file" multiple accept={ALLOWED.join(",")} className="hidden" onChange={(e) => pick(e.target.files)} />
        </div>

        <details className="text-sm">
          <summary className="cursor-pointer text-muted">Optional details (type, topic, language)</summary>
          <div className="mt-3 grid gap-3 sm:grid-cols-3">
            <Field label="Document type"><Input placeholder="scouting_report" value={meta.document_type} onChange={(e) => setMeta({ ...meta, document_type: e.target.value })} /></Field>
            <Field label="Topic"><Input placeholder="new_players" value={meta.topic} onChange={(e) => setMeta({ ...meta, topic: e.target.value })} /></Field>
            <Field label="Language"><Input placeholder="en" value={meta.language} onChange={(e) => setMeta({ ...meta, language: e.target.value })} /></Field>
          </div>
          <p className="mt-2 text-xs text-muted">Leave blank if unknown. TACTIQ never guesses metadata.</p>
        </details>

        {status.kind === "error" && <ErrorState message={status.message} />}
        {busy && <p className="rounded-lg bg-subtle px-4 py-3 text-sm text-muted" aria-live="polite">{status.message}</p>}
        {status.kind === "ready" && (
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg bg-primary-soft px-4 py-3 text-sm text-primary" aria-live="polite">
            <span className="flex items-center gap-2"><CheckCircle2 className="size-4" /> {status.message}</span>
            <Link href="/investigate" className="inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-hover">
              <Search className="size-3.5" /> Ask a question
            </Link>
          </div>
        )}

        <Button onClick={upload} disabled={!files.length} loading={busy}>
          <Upload className="size-4" /> Upload and index
        </Button>
      </div>
    </Card>
  );
}
