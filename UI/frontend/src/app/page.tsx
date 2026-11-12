"use client";

import { ArrowUp, BookOpen, Database, Search, Upload } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import { Badge, StatusDot } from "@/components/ui/badge";
import { Card, CardHeader } from "@/components/ui/card";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/states";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/format";
import { useApi } from "@/lib/use-api";

const SUGGESTED_QUESTIONS = [
  "What is counterpressing?",
  "What are the weaknesses of a low block?",
  "How does a team build up from the back?",
  "What should players do right after losing the ball?",
];

export default function OverviewPage() {
  const system = useApi(() => api.system());
  const history = useApi(() => api.indexingHistory());
  const info = system.data;

  return (
    <div className="mx-auto max-w-6xl">
      <section className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">Your football intelligence workspace.</h1>
        <p className="mt-2 text-muted">Explore tactical knowledge, investigate matches and discover evidence.</p>
      </section>

      {system.error && <div className="mb-6"><ErrorState message={system.error} /></div>}

      <section className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3" aria-label="System overview">
        <StatCard label="Indexed documents" value={info ? info.indexed_documents : null} hint="Documents with chunks in Qdrant" />
        <StatCard label="Indexed chunks" value={info ? (info.collection.points ?? 0) : null} hint={info ? `Collection: ${info.collection.name}` : ""} />
        <StatCard
          label="Qdrant"
          value={info ? <StatusDot ok={info.qdrant.connected} label={info.qdrant.connected ? "Connected" : "Unreachable"} /> : null}
          hint={info ? `${info.qdrant.mode} · ${info.qdrant.location}` : ""}
        />
        <StatCard label="Embedding model" value={info?.embedding_model.split("/").pop() ?? null} hint={info ? `${info.collection.vector_size ?? "—"} dimensions · chunk ${info.chunking.chunk_size}/${info.chunking.chunk_overlap}` : ""} />
        <StatCard
          label="Last indexing"
          value={info ? (info.last_indexing ? formatDate(info.last_indexing.finished_at) : "Not yet run from UI") : null}
          hint={info?.last_indexing ? `${info.last_indexing.source} · ${info.last_indexing.status}` : "Run indexing from the Knowledge page"}
        />
        <StatCard label="Collections" value={info ? info.qdrant.collections.length : null} hint={info?.qdrant.collections.join(", ") || "No collections yet"} />
      </section>

      <div className="grid gap-6 lg:grid-cols-5 lg:items-start">
        <Card className="lg:col-span-3">
          <CardHeader title="Recent activity" description="Indexing operations started from this workspace" />
          {history.loading ? (
            <LoadingState />
          ) : history.error ? (
            <div className="p-5"><ErrorState message={history.error} /></div>
          ) : !history.data?.length ? (
            <EmptyState icon={Database} title="No activity yet" description="Indexing runs started from the Knowledge page will appear here." />
          ) : (
            <ul className="divide-y divide-line">
              {history.data.slice(0, 6).map((job) => (
                <li key={job.id} className="flex flex-wrap items-center justify-between gap-2 px-5 py-3 text-sm">
                  <div>
                    <p className="font-medium">Indexed {job.source.replace("_", " ")}</p>
                    <p className="text-muted">
                      {job.summary ? `${job.summary.loaded_files} files · ${job.summary.chunks_created} chunks` : job.error}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge tone={job.status === "succeeded" ? "success" : job.status === "failed" ? "danger" : "info"}>{job.status}</Badge>
                    <span className="text-xs text-muted">{formatDate(job.finished_at ?? job.started_at)}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <div className="flex flex-col gap-6 lg:col-span-2">
          <Card>
            <CardHeader title="Quick actions" />
            <div className="grid gap-2 p-4">
              <QuickAction href="/knowledge" icon={<Upload className="size-4" />} label="Upload documents" />
              <QuickAction href="/investigate" icon={<Search className="size-4" />} label="Start an investigation" />
              <QuickAction href="/knowledge" icon={<BookOpen className="size-4" />} label="Browse knowledge" />
              <QuickAction
                href={info?.qdrant.mode === "server" ? "http://localhost:6333/dashboard" : "/settings"}
                icon={<Database className="size-4" />}
                label="Inspect Qdrant"
                external={info?.qdrant.mode === "server"}
              />
            </div>
          </Card>

          <Card>
            <CardHeader title="Suggested questions" description="Answered from your indexed documents" />
            <ul className="p-2">
              {SUGGESTED_QUESTIONS.map((question) => (
                <li key={question}>
                  <Link
                    href={`/investigate?q=${encodeURIComponent(question)}`}
                    className="flex items-center justify-between gap-3 rounded-lg px-3 py-2.5 text-sm hover:bg-subtle"
                  >
                    {question}
                    <ArrowUp className="size-4 rotate-45 text-muted" />
                  </Link>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, hint }: { label: string; value: ReactNode | null; hint?: string }) {
  return (
    <Card className="p-5">
      <p className="text-sm text-muted">{label}</p>
      <div className="mt-2 min-h-8 text-2xl font-semibold tracking-tight">
        {value === null ? <span className="inline-block h-7 w-20 animate-pulse rounded bg-subtle" /> : value}
      </div>
      {hint && <p className="mt-1 truncate text-xs text-muted" title={hint}>{hint}</p>}
    </Card>
  );
}

function QuickAction({ href, icon, label, external }: { href: string; icon: ReactNode; label: string; external?: boolean }) {
  const className = "flex items-center gap-3 rounded-lg border border-line px-3 py-2.5 text-sm font-medium hover:border-primary/40 hover:bg-primary-soft";
  return external ? (
    <a href={href} target="_blank" rel="noreferrer" className={className}>{icon}{label}</a>
  ) : (
    <Link href={href} className={className}>{icon}{label}</Link>
  );
}
