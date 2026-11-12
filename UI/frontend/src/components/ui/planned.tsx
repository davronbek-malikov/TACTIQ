import type { ReactNode } from "react";
import { Badge } from "./badge";

// Rejadagi imkoniyat: nima kerakligini halol tushuntiradi
export function PlannedNotice({ title, requires, children }: { title: string; requires: string; children?: ReactNode }) {
  return (
    <div className="rounded-xl border border-line bg-card p-5">
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <h2 className="text-base font-semibold">{title}</h2>
        <Badge tone="warning">Coming soon</Badge>
      </div>
      <p className="text-sm text-muted">
        <span className="font-medium text-ink">Requires:</span> {requires}
      </p>
      {children && <div className="mt-4">{children}</div>}
    </div>
  );
}
