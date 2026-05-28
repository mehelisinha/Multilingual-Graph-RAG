import type { LanguageCode, LanguageOption } from "../config/languages";

export type StreamEventType = "metadata" | "chunks" | "token" | "done" | "error";

export interface QueryRequest {
  query: string;
  language?: LanguageOption | null;
  top_k?: number;
  use_graph?: boolean;
}

export interface ChunkResult {
  id: string;
  document_id: string;
  chunk_index: number;
  text: string;
  language: string;
  title: string;
  score: number;
}

export interface QueryStreamEvent {
  type: StreamEventType;
  detected_language?: LanguageCode | null;
  chunks?: ChunkResult[] | null;
  token?: string | null;
  answer?: string | null;
  error?: string | null;
}
