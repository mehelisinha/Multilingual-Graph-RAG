import { useCallback, useState } from "react";

import type { LanguageOption } from "../config/languages";
import { useStreamingAnswer } from "./useStreamingAnswer";
import { useQueryStore } from "../store/queryStore";

export function useSearch() {
  const { query, isSearching, error } = useQueryStore();
  const { runQuery, cancel } = useStreamingAnswer();
  const [language, setLanguage] = useState<LanguageOption>("auto");
  const [topK, setTopK] = useState(10);

  const submit = useCallback(async () => {
    const trimmed = query.trim();
    if (!trimmed || isSearching) {
      return;
    }
    await runQuery(trimmed, language, topK);
  }, [query, isSearching, language, topK, runQuery]);

  return {
    query,
    language,
    topK,
    isSearching,
    error,
    setLanguage,
    setTopK,
    submit,
    cancel,
  };
}
