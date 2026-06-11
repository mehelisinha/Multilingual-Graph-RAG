// Shared node color palette for the graph viewer and legend.
// The graph only contains Document, Chunk and Entity labels; Entity nodes
// are differentiated by their NER type (ORG, PER, LOC, LAW, MISC).

export const SELECTED_COLOR = "#ef4444";
export const DEFAULT_COLOR = "#6b7280";

const LABEL_COLORS: Record<string, string> = {
  Document: "#3b82f6",
  Chunk: "#9ca3af",
};

const ENTITY_TYPE_COLORS: Record<string, string> = {
  ORG: "#f59e0b",
  PER: "#8b5cf6",
  LOC: "#10b981",
  LAW: "#6366f1",
  MISC: "#14b8a6",
};

export function getNodeColor(label: string, type: string): string {
  if (label === "Entity") {
    return ENTITY_TYPE_COLORS[type] ?? DEFAULT_COLOR;
  }
  return LABEL_COLORS[label] ?? DEFAULT_COLOR;
}

export const LEGEND_ITEMS = [
  { label: "Document", color: LABEL_COLORS.Document },
  { label: "Chunk", color: LABEL_COLORS.Chunk },
  { label: "Organisation", color: ENTITY_TYPE_COLORS.ORG },
  { label: "Person", color: ENTITY_TYPE_COLORS.PER },
  { label: "Location", color: ENTITY_TYPE_COLORS.LOC },
  { label: "Law", color: ENTITY_TYPE_COLORS.LAW },
  { label: "Misc", color: ENTITY_TYPE_COLORS.MISC },
  { label: "Selected", color: SELECTED_COLOR },
];
