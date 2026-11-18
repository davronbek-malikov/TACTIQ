// Service layer: backend bilan barcha aloqa faqat shu fayl orqali.
// Brauzer Qdrant'ga to'g'ridan-to'g'ri ulanmaydi.

import type {
  CollectionInfo,
  DocumentDetail,
  DocumentMetadata,
  DocumentRow,
  IndexingJob,
  InvestigateRequest,
  InvestigateResponse,
  LlmInfo,
  SourceName,
  SystemInfo,
} from "./types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { cache: "no-store", ...init });
  } catch {
    throw new ApiError(`Backend is not reachable at ${API_URL}. Start it with: python UI/backend/main.py`, 0);
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : response.statusText;
    throw new ApiError(detail, response.status);
  }
  return response.json() as Promise<T>;
}

const json = (method: string, body: unknown): RequestInit => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

// football_data/statsbomb/... kabi ichki papkalar: har bir qism alohida kodlanadi, "/" qoladi
const docPath = (source: SourceName, filename: string) =>
  `/api/documents/${source}/${filename.split("/").map(encodeURIComponent).join("/")}`;

// Asl faylni yangi tabda ochish (PDF uchun sahifaga sakraydi)
export const rawDocumentUrl = (source: SourceName, filename: string, page?: number | null) =>
  `${API_URL}${docPath(source, filename)}/raw${page ? `#page=${page}` : ""}`;

// Hujjat sahifasi: barcha chunk'lar, keltirilgan chunk ajratib ko'rsatiladi
export const sourcePageUrl = (source: SourceName, filename: string, chunk?: number | null) =>
  `/source?source=${source}&file=${encodeURIComponent(filename)}${chunk != null ? `&chunk=${chunk}` : ""}`;

export const api = {
  system: () => request<SystemInfo>("/api/system"),
  collections: () => request<CollectionInfo[]>("/api/collections"),
  llms: () => request<LlmInfo[]>("/api/llms"),

  documents: () => request<DocumentRow[]>("/api/documents"),
  document: (source: SourceName, filename: string) => request<DocumentDetail>(docPath(source, filename)),
  updateMetadata: (source: SourceName, filename: string, metadata: DocumentMetadata) =>
    request<DocumentMetadata>(`${docPath(source, filename)}/metadata`, json("PUT", metadata)),
  deleteDocument: (source: SourceName, filename: string) =>
    request<{ deleted: string }>(docPath(source, filename), { method: "DELETE" }),
  upload: (file: File, metadata: Partial<DocumentMetadata>, overwrite = false) => {
    const form = new FormData();
    form.append("file", file);
    form.append("overwrite", String(overwrite));
    Object.entries(metadata).forEach(([key, value]) => form.append(key, value ?? ""));
    // indexing_job — avtomatik boshlangan index; index_queued — boshqa index tugagach boshlanadi
    return request<{ source: SourceName; filename: string; document_id: string; indexing_job: IndexingJob | null; index_queued: boolean }>("/api/documents/upload", {
      method: "POST",
      body: form,
    });
  },

  startIndexing: (source: SourceName) => request<IndexingJob>("/api/indexing/jobs", json("POST", { source })),
  indexingJob: (id: string) => request<IndexingJob>(`/api/indexing/jobs/${id}`),
  indexingHistory: () => request<IndexingJob[]>("/api/indexing/history"),

  investigate: (body: InvestigateRequest) => request<InvestigateResponse>("/api/investigate", json("POST", body)),
};
