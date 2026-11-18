"use client";

import { BookOpen, RefreshCw } from "lucide-react";
import { useState } from "react";
import { DocumentDetailPanel } from "@/components/knowledge/document-detail";
import { IndexingCard } from "@/components/knowledge/indexing-card";
import { UploadCard } from "@/components/knowledge/upload-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, PageHeader } from "@/components/ui/card";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/states";
import { api } from "@/lib/api";
import { cn, formatBytes } from "@/lib/format";
import type { DocumentRow } from "@/lib/types";
import { useApi } from "@/lib/use-api";

export default function KnowledgePage() {
  const documents = useApi(() => api.documents());
  const [selected, setSelected] = useState<DocumentRow | null>(null);
  const refresh = documents.reload; // barqaror funksiya (useApi ichida useCallback)

  const rows = documents.data ?? [];
  return (
    <div className="mx-auto max-w-7xl">
      <PageHeader
        title="Knowledge"
        description="Documents TACTIQ answers from. Upload, index and inspect what is stored in Qdrant."
        action={<Button variant="secondary" onClick={refresh}><RefreshCw className="size-4" /> Refresh</Button>}
      />

      <div className="mb-6 grid gap-6 lg:grid-cols-2">
        <UploadCard onUploaded={refresh} />
        <IndexingCard onFinished={refresh} />
      </div>

      <div className="flex gap-6">
        <Card className="min-w-0 flex-1">
          <CardHeader title="Documents" description={`${rows.length} documents · ${rows.filter((r) => r.indexed).length} indexed`} />
          {documents.loading && !documents.data ? (
            <LoadingState />
          ) : documents.error ? (
            <div className="p-5"><ErrorState message={documents.error} /></div>
          ) : rows.length === 0 ? (
            <EmptyState icon={BookOpen} title="No documents" description="Upload a PDF, DOCX, TXT or Markdown file to get started." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[720px] text-left text-sm">
                <thead className="border-b border-line bg-subtle text-xs text-muted">
                  <tr>
                    {["Document", "Type", "Topic", "Language", "Chunks", "Status", "Source"].map((h) => (
                      <th key={h} className="px-4 py-2.5 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {rows.map((row) => (
                    <tr
                      key={`${row.source}/${row.filename}`}
                      onClick={() => setSelected(row)}
                      className={cn("cursor-pointer hover:bg-subtle", selected?.document_id === row.document_id && selected.source === row.source && "bg-primary-soft/60")}
                    >
                      <td className="px-4 py-3">
                        <p className="font-medium">{row.filename}</p>
                        <p className="text-xs text-muted">{formatBytes(row.size_bytes)}</p>
                      </td>
                      <td className="px-4 py-3 uppercase text-muted">{row.file_type}</td>
                      <td className="px-4 py-3">{row.metadata.topic ?? <span className="text-muted">—</span>}</td>
                      <td className="px-4 py-3">{row.metadata.language ?? <span className="text-muted">—</span>}</td>
                      <td className="px-4 py-3">{row.chunks}</td>
                      <td className="px-4 py-3">
                        <Badge tone={row.indexed ? "success" : "warning"}>{row.indexed ? "Indexed" : "Not indexed"}</Badge>
                      </td>
                      <td className="px-4 py-3 text-muted">{{ sample_docs: "Sample", my_documents: "Mine", football_data: "Football data" }[row.source]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {selected && (
          <Card className="fixed inset-0 z-40 overflow-hidden rounded-none lg:static lg:inset-auto lg:z-auto lg:w-[420px] lg:shrink-0 lg:rounded-xl">
            <DocumentDetailPanel key={`${selected.source}/${selected.filename}`} row={selected} onClose={() => setSelected(null)} onChanged={refresh} />
          </Card>
        )}
      </div>
    </div>
  );
}
