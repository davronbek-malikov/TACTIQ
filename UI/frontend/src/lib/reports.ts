// Saqlangan tekshiruvlar — brauzerning localStorage'ida (backend'da hisobot generatsiyasi hali yo'q).
import type { InvestigateResponse } from "./types";

export interface SavedReport {
  id: string;
  title: string;
  created_at: string;
  response: InvestigateResponse;
}

const KEY = "tactiq.reports";

export function loadReports(): SavedReport[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "[]");
  } catch {
    return [];
  }
}

export function saveReport(response: InvestigateResponse): SavedReport {
  const report: SavedReport = {
    id: crypto.randomUUID(),
    title: response.question,
    created_at: new Date().toISOString(),
    response,
  };
  localStorage.setItem(KEY, JSON.stringify([report, ...loadReports()]));
  return report;
}

export function deleteReport(id: string) {
  localStorage.setItem(KEY, JSON.stringify(loadReports().filter((r) => r.id !== id)));
}

export function reportToMarkdown(report: SavedReport): string {
  const { response } = report;
  const sources = response.evidence
    .map((e, i) => `${i + 1}. **${e.title}** (relevance ${e.score?.toFixed(2) ?? "—"})\n\n   > ${e.text.replace(/\n/g, " ").slice(0, 400)}`)
    .join("\n\n");
  return [
    `# ${report.title}`,
    `*Saved ${new Date(report.created_at).toLocaleString()} · LLM: ${response.llm} (${response.model})*`,
    "## Answer",
    response.answer ?? "_No answer_",
    "## Evidence",
    sources || "_No sources_",
  ].join("\n\n");
}
