"use client";

import { Menu, PanelLeftClose, PanelLeftOpen, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { api } from "@/lib/api";
import { cn } from "@/lib/format";
import type { SystemInfo } from "@/lib/types";
import { BOTTOM_NAV, MAIN_NAV, findNavItem, type NavItem } from "./nav";

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const current = findNavItem(pathname);

  return (
    <div className="flex h-dvh overflow-hidden">
      {/* Mobil: sidebar ustidagi qoplama */}
      {mobileOpen && (
        <button
          aria-label="Close navigation"
          className="fixed inset-0 z-30 bg-ink/20 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex flex-col border-r border-line bg-card transition-all lg:static lg:h-full",
          collapsed ? "lg:w-[72px]" : "lg:w-60",
          mobileOpen ? "w-64 translate-x-0" : "w-64 -translate-x-full lg:translate-x-0",
        )}
      >
        <div className="flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2" onClick={() => setMobileOpen(false)}>
            <span className="grid size-8 place-items-center rounded-lg bg-primary text-sm font-bold text-white">T</span>
            {!collapsed && <span className="text-base font-semibold tracking-tight">TACTIQ</span>}
          </Link>
          <button className="rounded-md p-1 text-muted hover:bg-subtle lg:hidden" onClick={() => setMobileOpen(false)} aria-label="Close navigation">
            <X className="size-5" />
          </button>
        </div>

        <nav className="flex flex-1 flex-col gap-1 px-3 py-2" aria-label="Main">
          {MAIN_NAV.map((item) => (
            <NavLink key={item.href} item={item} active={current?.href === item.href} collapsed={collapsed} onNavigate={() => setMobileOpen(false)} />
          ))}
        </nav>

        <div className="flex flex-col gap-1 border-t border-line px-3 py-3">
          {BOTTOM_NAV.map((item) => (
            <NavLink key={item.href} item={item} active={current?.href === item.href} collapsed={collapsed} onNavigate={() => setMobileOpen(false)} />
          ))}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted hover:bg-subtle hover:text-ink lg:flex"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <PanelLeftOpen className="size-4" /> : <PanelLeftClose className="size-4" />}
            {!collapsed && "Collapse"}
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col overflow-y-auto">
        <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center gap-3 border-b border-line bg-canvas/95 px-4 backdrop-blur sm:px-6">
          <button className="rounded-md p-1.5 text-muted hover:bg-subtle lg:hidden" onClick={() => setMobileOpen(true)} aria-label="Open navigation">
            <Menu className="size-5" />
          </button>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm text-muted">
              Workspace <span className="mx-1">/</span>
              <span className="font-medium text-ink">{current?.label ?? "TACTIQ"}</span>
            </p>
          </div>
          <ConnectionStatus />
        </header>
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}

function NavLink({ item, active, collapsed, onNavigate }: { item: NavItem; active: boolean; collapsed: boolean; onNavigate: () => void }) {
  const Icon = item.icon;
  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      title={collapsed ? item.label : item.description}
      aria-current={active ? "page" : undefined}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
        active ? "bg-primary-soft text-primary" : "text-muted hover:bg-subtle hover:text-ink",
      )}
    >
      <Icon className="size-4 shrink-0" />
      {!collapsed && item.label}
    </Link>
  );
}

// Haqiqiy holat: backend va Qdrant (har 20 soniyada yangilanadi)
function ConnectionStatus() {
  const [system, setSystem] = useState<SystemInfo | null>(null);
  const [backendDown, setBackendDown] = useState(false);

  useEffect(() => {
    let alive = true;
    const check = () =>
      api
        .system()
        .then((info) => alive && (setSystem(info), setBackendDown(false)))
        .catch(() => alive && (setSystem(null), setBackendDown(true)));
    check();
    const timer = setInterval(check, 20000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  const [label, ok] = backendDown
    ? ["Backend offline", false]
    : !system
      ? ["Checking…", null]
      : system.qdrant.connected
        ? [`Qdrant connected · ${system.qdrant.mode}`, true]
        : ["Qdrant unreachable", false];

  return (
    <Link href="/settings" className="flex items-center gap-2 rounded-lg border border-line bg-card px-3 py-1.5 text-xs font-medium text-ink hover:bg-subtle">
      <span className={cn("size-2 rounded-full", ok === null ? "bg-muted/40" : ok ? "bg-primary" : "bg-danger")} aria-hidden />
      <span className="hidden sm:inline">{label}</span>
    </Link>
  );
}
