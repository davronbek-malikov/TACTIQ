import {
  BookOpen,
  CalendarDays,
  FileText,
  LayoutDashboard,
  Search,
  Settings,
  Users,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  description: string;
}

export const MAIN_NAV: NavItem[] = [
  { href: "/", label: "Overview", icon: LayoutDashboard, description: "Workspace status and quick actions" },
  { href: "/investigate", label: "Investigate", icon: Search, description: "Ask questions and inspect evidence" },
  { href: "/knowledge", label: "Knowledge", icon: BookOpen, description: "Documents and indexing" },
  { href: "/matches", label: "Matches", icon: CalendarDays, description: "Match explorer" },
  { href: "/players", label: "Players", icon: Users, description: "Player intelligence" },
  { href: "/reports", label: "Reports", icon: FileText, description: "Saved investigations" },
];

export const BOTTOM_NAV: NavItem[] = [
  { href: "/settings", label: "Settings", icon: Settings, description: "Local services and configuration" },
];

export function findNavItem(pathname: string): NavItem | undefined {
  return [...MAIN_NAV, ...BOTTOM_NAV].find((item) =>
    item.href === "/" ? pathname === "/" : pathname.startsWith(item.href),
  );
}
