"use client";

import { Search, Users } from "lucide-react";
import Link from "next/link";
import { Card, CardHeader, PageHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/fields";
import { PlannedNotice } from "@/components/ui/planned";
import { EmptyState } from "@/components/ui/states";
import { api } from "@/lib/api";
import { useApi } from "@/lib/use-api";

// Kelajakdagi tuzilgan ma'lumot uchun profil maydonlari (hozir to'ldirilmaydi)
const PROFILE_FIELDS = ["Team", "Position", "Age", "Competition", "Statistics", "Related matches"];

export default function PlayersPage() {
  const documents = useApi(() => api.documents());
  const playerDocs = (documents.data ?? []).filter((doc) => doc.metadata.player_id);

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <PageHeader title="Players" description="Player profiles, comparisons, scouting reports and related evidence." />

      <PlannedNotice title="Player intelligence" requires="structured player data (canonical player IDs, statistics and match links). No player data is loaded, so no profile is shown.">
        <div className="relative max-w-md">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" />
          <Input disabled placeholder="Search players" className="pl-9" />
        </div>
      </PlannedNotice>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Player profile" />
          <EmptyState icon={Users} title="No player selected" description="Profiles will show the fields below — filled only from verified data." />
          <ul className="grid grid-cols-2 gap-2 border-t border-line p-5 text-sm text-muted">
            {PROFILE_FIELDS.map((field) => <li key={field} className="rounded-lg bg-subtle px-3 py-2">{field}</li>)}
          </ul>
        </Card>
        <Card>
          <CardHeader title="Scouting & tactical documents" description="Documents whose metadata contains a player_id" />
          {playerDocs.length === 0 ? (
            <p className="px-5 py-6 text-sm text-muted">
              No documents are linked to a player yet. Add a <code className="font-mono">player_id</code> on the <Link className="font-medium text-primary" href="/knowledge">Knowledge</Link> page.
            </p>
          ) : (
            <ul className="divide-y divide-line">
              {playerDocs.map((doc) => (
                <li key={doc.document_id} className="flex justify-between px-5 py-3 text-sm">
                  {doc.filename}<span className="font-mono text-xs text-muted">{doc.metadata.player_id}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
