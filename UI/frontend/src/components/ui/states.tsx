import { LoaderCircle, TriangleAlert } from "lucide-react";
import type { ComponentType, ReactNode } from "react";

// Bo'sh holat: nima yo'qligini va qaysi backend imkoniyati kerakligini tushuntiradi
export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  badge,
}: {
  icon?: ComponentType<{ className?: string }>;
  title: string;
  description: ReactNode;
  action?: ReactNode;
  badge?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-14 text-center">
      {Icon && (
        <div className="mb-4 rounded-xl bg-primary-soft p-3">
          <Icon className="size-6 text-primary" />
        </div>
      )}
      {badge && <div className="mb-2">{badge}</div>}
      <h3 className="text-base font-semibold text-ink">{title}</h3>
      <div className="mt-1 max-w-md text-sm text-muted">{description}</div>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 px-5 py-8 text-sm text-muted" role="status">
      <LoaderCircle className="size-4 animate-spin" aria-hidden />
      {label}
    </div>
  );
}

export function ErrorState({ message, action }: { message: string; action?: ReactNode }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-danger/20 bg-danger-soft px-4 py-3 text-sm text-danger" role="alert">
      <TriangleAlert className="mt-0.5 size-4 shrink-0" aria-hidden />
      <div className="flex-1">{message}</div>
      {action}
    </div>
  );
}
