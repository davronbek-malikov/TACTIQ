"use client";

import type { ReactNode } from "react";
import { Badge, StatusDot } from "@/components/ui/badge";
import { Card, CardHeader, PageHeader } from "@/components/ui/card";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { API_URL, api } from "@/lib/api";
import { useApi } from "@/lib/use-api";

export default function SettingsPage() {
  const system = useApi(() => api.system());
  const llms = useApi(() => api.llms());
  const info = system.data;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <PageHeader title="Settings" description="Local services and configuration. Values come from the project's .env file — edit it and restart the backend to change them." />

      {system.error && <ErrorState message={system.error} />}

      <Card>
        <CardHeader title="Local services" />
        {system.loading && !info ? <LoadingState /> : (
          <Rows>
            <Row label="FastAPI backend" value={<StatusDot ok={info ? true : system.error ? false : null} label={API_URL} />} />
            <Row label="Qdrant" value={info ? <StatusDot ok={info.qdrant.connected} label={info.qdrant.connected ? "Connected" : "Unreachable"} /> : "—"} />
            <Row label="Qdrant mode" value={info ? `${info.qdrant.mode} · ${info.qdrant.location}` : "—"} />
            {info?.qdrant.error && <Row label="Qdrant error" value={<span className="text-danger">{info.qdrant.error}</span>} />}
            <Row label="Collection" value={info ? `${info.collection.name} · ${info.collection.exists ? `${info.collection.points} points` : "not created yet"}` : "—"} />
          </Rows>
        )}
      </Card>

      <Card>
        <CardHeader title="AI configuration" description="API keys stay in .env on the server and are never sent to the browser." />
        <Rows>
          <Row label="Embedding model" value={info?.embedding_model ?? "—"} />
          <Row label="Chunking" value={info ? `${info.chunking.chunk_size} tokens · overlap ${info.chunking.chunk_overlap}` : "—"} />
          <Row label="Ollama endpoint" value="http://localhost:11434" />
          {(llms.data ?? []).map((llm) => (
            <Row
              key={llm.id}
              label={`LLM · ${llm.id}`}
              value={
                <span className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs">{llm.model}</span>
                  <Badge tone={llm.ready ? "success" : "warning"}>{llm.ready ? "ready" : "not configured"}</Badge>
                  <span className="text-xs text-muted">{llm.detail}</span>
                </span>
              }
            />
          ))}
        </Rows>
      </Card>

      <Card>
        <CardHeader title="Storage" />
        <Rows>
          <Row label="Sample documents" value={info?.document_dirs.sample_docs ?? "—"} mono />
          <Row label="My documents" value={info?.document_dirs.my_documents ?? "—"} mono />
          <Row label="Vector storage" value={info ? (info.qdrant.mode === "local" ? info.qdrant.location : "Docker volume qdrant_storage") : "—"} mono />
        </Rows>
      </Card>

      <Card>
        <CardHeader title="Application" />
        <Rows>
          <Row label="Theme" value="Light" />
          <Row label="Language" value="English" />
          <Row label="Version" value={info?.version ?? "—"} />
        </Rows>
      </Card>
    </div>
  );
}

function Rows({ children }: { children: ReactNode }) {
  return <dl className="divide-y divide-line">{children}</dl>;
}

function Row({ label, value, mono }: { label: string; value: ReactNode; mono?: boolean }) {
  return (
    <div className="grid gap-1 px-5 py-3 sm:grid-cols-[200px_1fr]">
      <dt className="text-sm text-muted">{label}</dt>
      <dd className={mono ? "break-all font-mono text-xs leading-5" : "text-sm"}>{value}</dd>
    </div>
  );
}
