import { useCallback, useRef } from "react";

import { streamQuery } from "../api/search";
import type { LanguageOption } from "../config/languages";
import { useQueryStore } from "../store/queryStore";
import type { QueryStreamEvent } from "../types/query.types";

export function useStreamingAnswer() {
  const abortRef = useRef<AbortController | null>(null);
  const {
    setSearching,
    setError,
    resetResults,
    setDetectedLanguage,
    setChunks,
    appendAnswer,
    setAnswer,
  } = useQueryStore();

  const handleEvent = useCallback(
    (event: QueryStreamEvent) => {
      if (event.type === "metadata" && event.detected_language) {
        setDetectedLanguage(event.detected_language);
      }
      if (event.type === "chunks" && event.chunks) {
        setChunks(event.chunks);
      }
      if (event.type === "token" && event.token) {
        appendAnswer(event.token);
      }
      if (event.type === "done" && event.answer) {
        setAnswer(event.answer);
      }
      if (event.type === "error") {
        setError(event.error ?? "Query failed");
      }
    },
    [appendAnswer, setAnswer, setChunks, setDetectedLanguage, setError],
  );

  const runQuery = useCallback(
    async (query: string, language: LanguageOption, topK: number) => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      resetResults();
      setSearching(true);
      setError(null);

      try {
        await streamQuery({ query, language, top_k: topK }, handleEvent, controller.signal);
      } catch (error) {
        if (controller.signal.aborted) {
          return;
        }
        const message = error instanceof Error ? error.message : "Query failed";
        setError(message);
      } finally {
        setSearching(false);
      }
    },
    [handleEvent, resetResults, setError, setSearching],
  );

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setSearching(false);
  }, [setSearching]);

  return { runQuery, cancel };
}
