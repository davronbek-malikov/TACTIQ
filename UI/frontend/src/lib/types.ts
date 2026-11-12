// API kontraktlari — UI/backend/schemas.py va main.py javoblari bilan bir xil.

export type SourceName = "sample_docs" | "my_documents";
export type LlmId = "qwen" | "groq" | "gemini";
export type AnswerMode = "rag" | "llm_only"; // rag — hujjatlar asosida; llm_only — hujjatsiz (taqqoslash)

export interface QdrantStatus {
  mode: "server" | "local";
  location: string;
  connected: boolean;
  collections: string[];
  error: string | null;
}

export interface IndexingSummary {
  data_dir: string;
  discovered_files: number;
  loaded_files: number;
  failed_files: Record<string, string>;
  unsupported_files: string[];
  text_sections: number;
  empty_sections_skipped: number;
  chunks_created: number;
  vectors_stored: number;
  collection_total_points: number;
  embedding_model: string;
  vector_dimension: number;
  collection_name: string;
  collection_created: boolean;
  warnings: string[];
}

export interface IndexingJob {
  id: string;
  source: SourceName;
  status: "running" | "succeeded" | "failed";
  started_at: string;
  finished_at: string | null;
  summary: IndexingSummary | null;
  error: string | null;
}

export interface SystemInfo {
  version: string;
  qdrant: QdrantStatus;
  collection: { name: string; exists: boolean; points: number | null; vector_size: number | null };
  indexed_documents: number;
  embedding_model: string;
  chunking: { chunk_size: number; chunk_overlap: number };
  last_indexing: IndexingJob | null;
  document_dirs: Record<SourceName, string>;
}

export interface CollectionInfo {
  name: string;
  points: number;
}

export interface LlmInfo {
  id: LlmId;
  model: string;
  local: boolean;
  ready: boolean;
  detail: string;
}

export interface DocumentMetadata {
  document_type: string | null;
  topic: string | null;
  language: string | null;
  match_id: string | null;
  team_id: string | null;
  player_id: string | null;
}

export interface DocumentRow {
  source: SourceName;
  filename: string;
  document_id: string;
  file_type: string;
  size_bytes: number;
  metadata: DocumentMetadata;
  chunks: number;
  indexed: boolean;
  editable: boolean;
}

export interface DocumentDetail {
  source: SourceName;
  filename: string;
  metadata: Record<string, string | number | null>;
  pages: { page: number | null; characters: number; preview: string }[];
  chunks: { chunk_index: number; page: number | null; token_count: number; text: string }[];
  embedding_model: string | null;
  editable: boolean;
}

// ---------- Evidence: modallikdan mustaqil (hujjat, statistika, video, rasm, audio) ----------

export type EvidenceKind = "document" | "statistic" | "video" | "image" | "audio";

export type EvidenceCategory =
  | "verified_fact"
  | "retrieved_document_evidence"
  | "analytical_observation"
  | "hypothesis"
  | "recommendation"
  | "cannot_be_verified";

export interface Evidence {
  evidence_id: string;
  kind: EvidenceKind;
  category: EvidenceCategory;
  title: string;
  text: string;
  score: number | null;
  // document
  document_id?: string | null;
  source?: string | null;
  page?: number | null;
  chunk_index?: number | null;
  // video (V2): match + timestamp + clip/frame
  video?: { match_label: string; timestamp_seconds: number; clip_id?: string; frame?: number };
  metadata: Record<string, string | number | null>;
}

export interface InvestigationStep {
  id: string;
  name: string;
  status: "done" | "skipped" | "failed";
  duration_ms: number | null;
  detail: string;
}

export interface InvestigateRequest {
  question: string;
  llm: LlmId;
  mode?: AnswerMode;
  k?: number;
  collection?: string;
  document_ids?: string[];
  file_types?: string[];
  topics?: string[];
  languages?: string[];
}

export interface InvestigateResponse {
  question: string;
  answer: string | null;
  answered: boolean;
  llm: LlmId;
  model: string;
  mode: AnswerMode;
  evidence: Evidence[];
  steps: InvestigationStep[];
  error: string | null;
}
