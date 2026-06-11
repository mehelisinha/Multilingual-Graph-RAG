import { useState, useCallback, useEffect } from "react";
import { uploadDocument } from "../api/ingest";
import { IngestionJob } from "../types/document.types";
import { getWsBaseUrl } from "../config/env";
import toast from "react-hot-toast";

export const useIngest = () => {
  const [activeJob, setActiveJob] = useState<IngestionJob | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const upload = useCallback(async (file: File, language?: string) => {
    setIsUploading(true);
    try {
      const response = await uploadDocument(file, language);

      const newJob: IngestionJob = {
        job_id: response.job_id,
        document_id: response.document_id,
        status: response.status,
        current_stage: "UPLOADED",
        progress: 0,
      };
      setActiveJob(newJob);
      toast.success("Document uploaded. Processing started...");

      // Setup websocket (same host/prefix as the REST API).
      const socket = new WebSocket(`${getWsBaseUrl()}/ingest/ws/${response.job_id}`);

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setActiveJob((prev) => ({ ...prev, ...data }));

        if (data.status === "COMPLETED") {
          toast.success("Document processing completed!");
          socket.close();
        } else if (data.status === "FAILED") {
          toast.error(`Processing failed: ${data.error_message}`);
          socket.close();
        }
      };

      socket.onerror = () => {
        console.error("WebSocket error");
        toast.error("Connection to job tracker lost");
      };

      setWs(socket);
    } catch (error) {
      console.error(error);
      toast.error("Failed to upload document");
    } finally {
      setIsUploading(false);
    }
  }, []);

  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  return { upload, isUploading, activeJob };
};
