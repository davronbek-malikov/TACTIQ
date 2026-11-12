import type { ReactNode } from "react";
import { cn } from "@/lib/format";

export type Tone = "neutral" | "success" | "warning" | "danger" | "info";

const tones: Record<Tone, string> = {
  neutral: "bg-subtle text-muted",
  success: "bg-primary-soft text-primary",
  warning: "bg-warning-soft text-warning",
  danger: "bg-danger-soft text-danger",
  info: "bg-info-soft text-info",
};

export function Badge({ tone = "neutral", children, className }: { tone?: Tone; children: ReactNode; className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium", tones[tone], className)}>
      {children}
    </span>
  );
}

// Holat nuqtasi: ulangan / ulanmagan
export function StatusDot({ ok, label }: { ok: boolean | null; label: string }) {
  const color = ok === null ? "bg-muted/40" : ok ? "bg-primary" : "bg-danger";
  return (
    <span className="inline-flex items-center gap-2 text-sm text-ink">
      <span className={cn("size-2 rounded-full", color)} aria-hidden />
      {label}
    </span>
  );
}
