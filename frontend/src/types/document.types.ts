export interface DocumentRecord {
  id: string;
  filename: string;
  title?: string;
  language?: string;
  size_bytes: number;
  chunk_count: number;
  status: string;
  created_at: string;
}

export interface IngestionJob {
  job_id: string;
  document_id: string;
  status: string;
  current_stage: string;
  progress: number;
  error_message?: string;
}
