import { create } from "zustand";

import type { LanguageCode } from "../config/languages";
import type { ChunkResult } from "../types/query.types";

interface QueryState {
  query: string;
  answer: string;
  chunks: ChunkResult[];
  detectedLanguage: LanguageCode | null;
  isSearching: boolean;
  error: string | null;
  setQuery: (query: string) => void;
  setAnswer: (answer: string) => void;
  appendAnswer: (token: string) => void;
  setChunks: (chunks: ChunkResult[]) => void;
  setDetectedLanguage: (language: LanguageCode | null) => void;
  setSearching: (isSearching: boolean) => void;
  setError: (error: string | null) => void;
  resetResults: () => void;
}

export const useQueryStore = create<QueryState>((set) => ({
  query: "",
  answer: "",
  chunks: [],
  detectedLanguage: null,
  isSearching: false,
  error: null,
  setQuery: (query) => set({ query }),
  setAnswer: (answer) => set({ answer }),
  appendAnswer: (token) => set((state) => ({ answer: state.answer + token })),
  setChunks: (chunks) => set({ chunks }),
  setDetectedLanguage: (detectedLanguage) => set({ detectedLanguage }),
  setSearching: (isSearching) => set({ isSearching }),
  setError: (error) => set({ error }),
  resetResults: () =>
    set({ answer: "", chunks: [], detectedLanguage: null, error: null }),
}));
