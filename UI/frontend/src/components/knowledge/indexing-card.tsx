"use client";

import { Database, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader } from "@/components/ui/card";
import { ErrorState } from "@/components/ui/states";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { IndexingJob, SourceName } from "@/lib/types";

const SOURCES: { id: SourceName; label: string; description: string }[] = [
  { id: "my_documents", label: "My documents", description: "Your uploaded documents" },
  { id: "sample_docs", label: "Sample documents", description: "Educational samples (read-only)" },
  { id: "football_data", label: "Football data", description: "StatsBomb, Wyscout and SkillCorner open data (read-only)" },
];

// Mavjud Indexing pipeline'ni backend orqali ishga tushiradi va natijasini kuzatadi.
export function IndexingCard({ onFinished }: { onFinished: () => void }) {
  const [job, setJob] = useState<IndexingJob | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (job?.status !== "running") return;
    const timer = setInterval(async () => {
      try {
        const next = await api.indexingJob(job.id);
        setJob(next);
        if (next.status !== "running") onFinished();
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [job, onFinished]);

  async function start(source: SourceName) {
    setError(null);
    try {
      setJob(await api.startIndexing(source));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  const running = job?.status === "running";
  const summary = job?.summary;

  return (
    <Card>
      <CardHeader
        title="Indexing"
        description="Runs the Indexing pipeline: load → metadata → clean → chunk → embed → Qdrant. Re-running is safe: no duplicates."
      />
      <div className="space-y-4 p-5">
        <div className="grid gap-2">
          {SOURCES.map((source) => (
            <div key={source.id} className="flex items-center justify-between gap-3 rounded-lg border border-line px-4 py-3">
              <div>
                <p className="text-sm font-medium">{source.label}</p>
                <p className="text-xs text-muted">{source.description}</p>
              </div>
              <Button variant="secondary" size="sm" onClick={() => start(source.id)} disabled={running}>
                <RefreshCw className="size-3.5" /> Index
              </Button>
            </div>
          ))}
        </div>

        {error && <ErrorState message={error} />}

        {job && (
          <div className="rounded-lg bg-subtle p-4 text-sm" aria-live="polite">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <Database className="size-4 text-primary" aria-hidden />
              <span className="font-medium">{job.source.replace("_", " ")}</span>
              <Badge tone={job.status === "succeeded" ? "success" : job.status === "failed" ? "danger" : "info"}>
                {running ? "running…" : job.status}
              </Badge>
              <span className="text-xs text-muted">{formatDate(job.finished_at ?? job.started_at)}</span>
            </div>
            {running && <p className="text-muted">Loading the embedding model and indexing documents. The first run can take a minute.</p>}
            {summary && (
              <dl className="grid grid-cols-2 gap-x-6 gap-y-1 sm:grid-cols-4">
                <Stat label="Files loaded" value={`${summary.loaded_files}/${summary.discovered_files}`} />
                <Stat label="Chunks" value={summary.chunks_created} />
                <Stat label="Vectors stored" value={summary.vectors_stored} />
                <Stat label="Collection total" value={summary.collection_total_points} />
              </dl>
            )}
            {summary && Object.entries(summary.failed_files).map(([file, err]) => (
              <p key={file} className="mt-2 text-xs text-danger">Failed: {file} — {err}</p>
            ))}
            {summary?.warnings.map((warning) => (
              <p key={warning} className="mt-2 text-xs text-warning">{warning}</p>
            ))}
            {job.error && !summary && <p className="text-danger">{job.error}</p>}
          </div>
        )}
      </div>
    </Card>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="font-semibold">{value}</dd>
    </div>
  );
}
