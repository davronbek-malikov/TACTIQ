"use client";

import { Upload } from "lucide-react";
import { useRef, useState, type DragEvent } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader } from "@/components/ui/card";
import { Field, Input } from "@/components/ui/fields";
import { ErrorState } from "@/components/ui/states";
import { api } from "@/lib/api";
import { cn, formatBytes } from "@/lib/format";

const ALLOWED = [".pdf", ".docx", ".txt", ".md"];
const MAX_BYTES = 20 * 1024 * 1024;

// Fayl -> my_documents (backend tekshiradi). Keyin "Index" bilan Qdrant'ga yoziladi.
export function UploadCard({ onUploaded }: { onUploaded: () => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [meta, setMeta] = useState({ document_type: "", topic: "", language: "" });
  const [status, setStatus] = useState<{ kind: "idle" | "uploading" | "done" | "error"; message?: string }>({ kind: "idle" });

  function pick(candidate: File | undefined) {
    if (!candidate) return;
    const ext = candidate.name.slice(candidate.name.lastIndexOf(".")).toLowerCase();
    if (!ALLOWED.includes(ext)) return setStatus({ kind: "error", message: `Unsupported format. Allowed: ${ALLOWED.join(", ")}` });
    if (candidate.size > MAX_BYTES) return setStatus({ kind: "error", message: "File is larger than 20 MB." });
    setFile(candidate);
    setStatus({ kind: "idle" });
  }

  function onDrop(event: DragEvent) {
    event.preventDefault();
    setDragging(false);
    pick(event.dataTransfer.files[0]);
  }

  async function upload() {
    if (!file) return;
    setStatus({ kind: "uploading" });
    try {
      const result = await api.upload(file, meta);
      setStatus({ kind: "done", message: `Saved ${result.filename} to my_documents. Index it to make it searchable.` });
      setFile(null);
      onUploaded();
    } catch (err) {
      setStatus({ kind: "error", message: err instanceof Error ? err.message : String(err) });
    }
  }

  return (
    <Card>
      <CardHeader title="Upload documents" description="PDF, DOCX, TXT or Markdown · max 20 MB · saved locally to my_documents" />
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
          {file ? (
            <p className="text-sm font-medium">{file.name} <span className="text-muted">· {formatBytes(file.size)}</span></p>
          ) : (
            <p className="text-sm"><span className="font-medium text-primary">Choose a file</span> or drag it here</p>
          )}
          <input ref={input} type="file" accept={ALLOWED.join(",")} className="hidden" onChange={(e) => pick(e.target.files?.[0])} />
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          <Field label="Document type"><Input placeholder="tactical_report" value={meta.document_type} onChange={(e) => setMeta({ ...meta, document_type: e.target.value })} /></Field>
          <Field label="Topic"><Input placeholder="high_pressing" value={meta.topic} onChange={(e) => setMeta({ ...meta, topic: e.target.value })} /></Field>
          <Field label="Language"><Input placeholder="en" value={meta.language} onChange={(e) => setMeta({ ...meta, language: e.target.value })} /></Field>
        </div>
        <p className="text-xs text-muted">Optional. Leave blank if unknown — TACTIQ never guesses metadata. Match, team and player IDs can be added later.</p>

        {status.kind === "error" && <ErrorState message={status.message!} />}
        {status.kind === "done" && <p className="rounded-lg bg-primary-soft px-4 py-3 text-sm text-primary">{status.message}</p>}

        <Button onClick={upload} disabled={!file} loading={status.kind === "uploading"}>
          <Upload className="size-4" /> Upload
        </Button>
      </div>
    </Card>
  );
}
