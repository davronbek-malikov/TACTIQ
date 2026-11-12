"use client";

import { CalendarDays } from "lucide-react";
import Link from "next/link";
import { Card, CardHeader, PageHeader } from "@/components/ui/card";
import { Select } from "@/components/ui/fields";
import { PlannedNotice } from "@/components/ui/planned";
import { EmptyState } from "@/components/ui/states";
import { VideoWorkspace } from "@/components/video/video-workspace";
import { api } from "@/lib/api";
import { useApi } from "@/lib/use-api";

export default function MatchesPage() {
  const documents = useApi(() => api.documents());
  const matchDocs = (documents.data ?? []).filter((doc) => doc.metadata.match_id);

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <PageHeader title="Matches" description="Explore matches, statistics, tactical reports and — later — video." />

      <PlannedNotice title="Match explorer" requires="structured match data (PostgreSQL + match/event ingestion). No match data is loaded yet, so nothing is shown.">
        <div className="grid gap-3 sm:grid-cols-3">
          {["Competition", "Season", "Team"].map((label) => (
            <Select key={label} disabled aria-label={label}><option>{label}</option></Select>
          ))}
        </div>
      </PlannedNotice>

      <Card>
        <CardHeader title="Match list" description="Date · competition · home vs away · score" />
        <EmptyState icon={CalendarDays} title="No matches yet" description="Matches will appear here once structured football data is ingested. TACTIQ never invents fixtures or scores." />
      </Card>

      <Card>
        <CardHeader title="Match-related documents" description="Documents whose metadata contains a match_id" />
        {matchDocs.length === 0 ? (
          <p className="px-5 py-6 text-sm text-muted">
            No documents are linked to a match. Add a <code className="font-mono">match_id</code> on the <Link className="font-medium text-primary" href="/knowledge">Knowledge</Link> page.
          </p>
        ) : (
          <ul className="divide-y divide-line">
            {matchDocs.map((doc) => (
              <li key={doc.document_id} className="flex justify-between px-5 py-3 text-sm">
                {doc.filename}<span className="font-mono text-xs text-muted">{doc.metadata.match_id}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card>
        <CardHeader title="Video workspace" description="Player, timeline, event markers, clips and AI observations" />
        <div className="p-5"><VideoWorkspace /></div>
      </Card>
    </div>
  );
}
