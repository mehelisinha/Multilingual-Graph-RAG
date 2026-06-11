import { apiClient } from "./client";
import { DocumentRecord } from "../types/document.types";

export const listDocuments = async (): Promise<DocumentRecord[]> => {
  const response = await apiClient.get<DocumentRecord[]>("/documents");
  return response.data;
};

export const deleteDocument = async (documentId: string): Promise<void> => {
  await apiClient.delete(`/documents/${documentId}`);
};
