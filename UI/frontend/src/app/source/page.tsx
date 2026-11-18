"use client";

import { ArrowLeft, ExternalLink } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, PageHeader } from "@/components/ui/card";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { api, rawDocumentUrl } from "@/lib/api";
import { cn } from "@/lib/format";
import type { SourceName } from "@/lib/types";
import { useApi } from "@/lib/use-api";

// useSearchParams URL'ni o'qiydi -> Next.js talabi: Suspense ichida bo'lishi kerak
export default function SourcePage() {
  return (
    <Suspense fallback={<LoadingState />}>
      <SourceView />
    </Suspense>
  );
}

// Evidence'dagi "View in document": butun hujjat (Qdrant'dagi chunk'lar) + keltirilgan chunk ajratilgan
function SourceView() {
  const params = useSearchParams();
  const source = params.get("source") as SourceName | null;
  const file = params.get("file");
  const chunkParam = params.get("chunk");
  const query = source && file ? { source, file, chunk: chunkParam === null ? null : Number(chunkParam) } : null;
  const result = useApi(() => (query ? api.document(query.source, query.file) : Promise.reject(new Error("Missing document in the link."))), [source, file]);
  const detail = result.data;
  const error = result.error;

  // Keltirilgan chunk'ga avtomatik scroll
  useEffect(() => {
    if (detail && query?.chunk != null) {
      document.getElementById(`chunk-${query.chunk}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [detail, query?.chunk]);

  return (
    <div className="mx-auto max-w-4xl">
      <Link href="/investigate" className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink">
        <ArrowLeft className="size-4" /> Back to investigation
      </Link>
      <PageHeader
        title={query?.file.split("/").pop() ?? "Document"}
        description={query ? `${query.source} / ${query.file}` : ""}
        action={query && (
          <a href={rawDocumentUrl(query.source, query.file)} target="_blank" rel="noreferrer"
             className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-card px-3 py-2 text-sm font-medium hover:bg-subtle">
            <ExternalLink className="size-4" /> Open original file
          </a>
        )}
      />

      {error && <ErrorState message={error} />}
      {!error && !detail && <LoadingState />}

      {detail && (
        <Card>
          <CardHeader
            title="Indexed passages"
            description={`${detail.chunks.length} chunks in Qdrant · the highlighted one was used as evidence`}
          />
          <div className="space-y-3 p-5">
            {detail.chunks.length === 0 && <p className="text-sm text-muted">This document is not indexed yet.</p>}
            {detail.chunks.map((chunk) => {
              const cited = chunk.chunk_index === query?.chunk;
              return (
                <section
                  key={`${chunk.page}-${chunk.chunk_index}`}
                  id={`chunk-${chunk.chunk_index}`}
                  className={cn("rounded-lg border p-4", cited ? "border-primary bg-primary-soft/60 ring-1 ring-primary/30" : "border-line")}
                >
                  <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-muted">
                    <span className="font-medium text-ink">Chunk {chunk.chunk_index}</span>
                    {chunk.page && <span>page {chunk.page}</span>}
                    <span>{chunk.token_count} tokens</span>
                    {cited && <Badge tone="success">Cited as evidence</Badge>}
                  </div>
                  <p className="whitespace-pre-line text-sm leading-relaxed">{chunk.text}</p>
                </section>
              );
            })}
          </div>
        </Card>
      )}
    </div>
  );
}
