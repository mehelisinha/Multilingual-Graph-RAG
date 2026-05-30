// Graph type definitions.

export interface GraphNode {
  id: string;
  name: string;
  type: string;
  label: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphEdge[];
}

export {};
