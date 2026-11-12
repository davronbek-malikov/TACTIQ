"use client";

import { Download, FileText, Trash2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { EvidenceCard } from "@/components/evidence/evidence-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, PageHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/states";
import { formatDate } from "@/lib/format";
import { deleteReport, loadReports, reportToMarkdown, type SavedReport } from "@/lib/reports";

export default function ReportsPage() {
  const [reports, setReports] = useState<SavedReport[]>([]);
  const [selected, setSelected] = useState<SavedReport | null>(null);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setReports(loadReports());
  }, []);

  function exportMarkdown(report: SavedReport) {
    const blob = new Blob([reportToMarkdown(report)], { type: "text/markdown" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `tactiq-report-${report.created_at.slice(0, 10)}.md`;
    link.click();
    URL.revokeObjectURL(link.href);
  }

  function remove(id: string) {
    deleteReport(id);
    setReports(loadReports());
    if (selected?.id === id) setSelected(null);
  }

  return (
    <div className="mx-auto max-w-7xl">
      <PageHeader title="Reports" description="Investigations you saved, with their answers and evidence. Stored locally in this browser." />

      {reports.length === 0 ? (
        <Card>
          <EmptyState
            icon={FileText}
            title="No saved investigations"
            description={<>Ask a question on the <Link href="/investigate" className="font-medium text-primary">Investigate</Link> page and choose “Save to reports”.</>}
          />
        </Card>
      ) : (
        <div className="grid gap-6 lg:grid-cols-5">
          <Card className="lg:col-span-2">
            <CardHeader title="Saved investigations" description={`${reports.length} saved`} />
            <ul className="divide-y divide-line">
              {reports.map((report) => (
                <li key={report.id}>
                  <button onClick={() => setSelected(report)} className={`w-full px-5 py-3 text-left hover:bg-subtle ${selected?.id === report.id ? "bg-primary-soft/60" : ""}`}>
                    <p className="line-clamp-2 text-sm font-medium">{report.title}</p>
                    <p className="mt-0.5 text-xs text-muted">{formatDate(report.created_at)} · {report.response.evidence.length} sources · {report.response.llm}</p>
                  </button>
                </li>
              ))}
            </ul>
          </Card>

          <Card className="lg:col-span-3">
            {!selected ? (
              <EmptyState icon={FileText} title="Select a report" description="Choose a saved investigation to view it." />
            ) : (
              <div>
                <CardHeader
                  title={selected.title}
                  description={`${formatDate(selected.created_at)} · ${selected.response.llm} (${selected.response.model})`}
                  action={
                    <div className="flex gap-2">
                      <Button variant="secondary" size="sm" onClick={() => exportMarkdown(selected)}><Download className="size-3.5" /> Markdown</Button>
                      <Button variant="secondary" size="sm" disabled title="PDF export — coming soon">PDF</Button>
                      <Button variant="danger" size="sm" onClick={() => remove(selected.id)} aria-label="Delete report"><Trash2 className="size-3.5" /></Button>
                    </div>
                  }
                />
                <div className="space-y-4 p-5">
                  <section>
                    <h3 className="mb-1 text-sm font-semibold">Summary</h3>
                    <p className="whitespace-pre-line text-sm leading-relaxed">{selected.response.answer}</p>
                  </section>
                  <section>
                    <h3 className="mb-2 text-sm font-semibold">Evidence <Badge className="ml-1">{selected.response.evidence.length}</Badge></h3>
                    <div className="space-y-2">
                      {selected.response.evidence.map((item, index) => <EvidenceCard key={item.evidence_id} evidence={item} number={index + 1} />)}
                    </div>
                  </section>
                </div>
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}
