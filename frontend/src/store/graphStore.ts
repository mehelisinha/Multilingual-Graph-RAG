// Zustand graph store.

import { create } from "zustand";
import { GraphData, GraphNode } from "../types/graph.types";

interface GraphState {
  data: GraphData | null;
  selectedEntity: GraphNode | null;
  isLoading: boolean;
  error: string | null;
  setData: (data: GraphData | null) => void;
  setSelectedEntity: (entity: GraphNode | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useGraphStore = create<GraphState>((set) => ({
  data: null,
  selectedEntity: null,
  isLoading: false,
  error: null,
  setData: (data) => set({ data }),
  setSelectedEntity: (entity) => set({ selectedEntity: entity }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));

export {};
