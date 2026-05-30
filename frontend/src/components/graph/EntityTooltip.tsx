// Hover tooltip for graph nodes.

import { GraphNode } from "../../types/graph.types";

export default function EntityTooltip({ node }: { node: GraphNode }) {
  return (
    <div className="absolute bottom-4 left-4 bg-white p-3 rounded shadow-lg border border-gray-200 max-w-xs z-10 pointer-events-none">
      <h4 className="font-semibold text-gray-800 truncate">{node.name}</h4>
      <p className="text-xs text-gray-500 mt-1">
        <span className="font-medium">Type:</span> {node.type || node.label}
      </p>
      <p className="text-xs text-gray-500 truncate">
        <span className="font-medium">ID:</span> {node.id}
      </p>
    </div>
  );
}
