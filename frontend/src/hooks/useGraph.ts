// Graph fetch hook.

import { useCallback } from "react";
import { useGraphStore } from "../store/graphStore";
import { graphApi } from "../api/graph";
import toast from "react-hot-toast";

export function useGraph() {
  const {
    data,
    selectedEntity,
    isLoading,
    error,
    setData,
    setSelectedEntity,
    setLoading,
    setError,
  } = useGraphStore();

  const fetchSubgraph = useCallback(
    async (entityId: string) => {
      setLoading(true);
      setError(null);
      try {
        const graphData = await graphApi.getSubgraph(entityId);
        setData(graphData);
      } catch (error: unknown) {
        const msg = (error as any).response?.data?.detail || (error as any).message || "Failed to fetch subgraph";
        setError(msg);
        toast.error(msg);
      } finally {
        setLoading(false);
      }
    },
    [setData, setError, setLoading],
  );

  return {
    data,
    selectedEntity,
    isLoading,
    error,
    fetchSubgraph,
    setSelectedEntity,
  };
}

export {};
