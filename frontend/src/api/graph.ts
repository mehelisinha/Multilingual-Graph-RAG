// Graph API client.

import { apiClient } from './client';
import { GraphData } from '../types/graph.types';

export const graphApi = {
  getSubgraph: async (entityId: string): Promise<GraphData> => {
    const response = await apiClient.get<GraphData>(`/graph/subgraph/${encodeURIComponent(entityId)}`);
    return response.data;
  },
  getEntities: async (): Promise<{ id: string; name: string; type: string; degree: number }[]> => {
    const response = await apiClient.get(`/graph/entities`);
    return response.data;
  },
};

export {};
