import { getApiBaseUrl } from "../config/env";
import { useAuthStore } from "../store/authStore";
import type { QueryRequest, QueryStreamEvent } from "../types/query.types";

function parseSsePayload(raw: string): QueryStreamEvent | null {
  const trimmed = raw.trim();
  if (!trimmed || trimmed === "[DONE]") {
    return null;
  }
  try {
    return JSON.parse(trimmed) as QueryStreamEvent;
  } catch {
    return null;
  }
}

export async function streamQuery(
  request: QueryRequest,
  onEvent: (event: QueryStreamEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const token = useAuthStore.getState().accessToken;
  const response = await fetch(`${getApiBaseUrl()}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      query: request.query,
      language: request.language ?? "auto",
      top_k: request.top_k ?? 10,
      use_graph: request.use_graph ?? false,
    }),
    signal,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Query failed (${response.status})`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Streaming is not supported in this browser");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";

    for (const part of parts) {
      const dataLine = part
        .split("\n")
        .find((line) => line.startsWith("data:"));
      if (!dataLine) {
        continue;
      }
      const payload = dataLine.replace(/^data:\s*/, "");
      const event = parseSsePayload(payload);
      if (event) {
        onEvent(event);
      }
    }
  }
}
