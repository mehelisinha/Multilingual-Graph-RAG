import { apiClient } from "./client";

export interface UploadResponse {
  job_id: string;
  document_id: string;
  status: string;
}

export const uploadDocument = async (file: File, language?: string): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  if (language) {
    formData.append("language", language);
  }

  const response = await apiClient.post<UploadResponse>("/ingest", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const getJobStatus = async (jobId: string) => {
  const response = await apiClient.get(`/ingest/${jobId}`);
  return response.data;
};
