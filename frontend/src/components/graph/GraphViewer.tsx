import { useRef, useEffect, useState, useCallback } from "react";
import ForceGraph2D, { ForceGraphMethods } from "react-force-graph-2d";
import { useGraph } from "../../hooks/useGraph";
import { GraphNode } from "../../types/graph.types";
import EntityTooltip from "./EntityTooltip";
import GraphControls from "./GraphControls";
import RelationshipLegend from "./RelationshipLegend";

export default function GraphViewer() {
  const { data, selectedEntity, setSelectedEntity, fetchSubgraph } = useGraph();
  const fgRef = useRef<ForceGraphMethods>();
  const [hoverNode, setHoverNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    // Re-center graph when data changes
    if (fgRef.current && data?.nodes.length) {
      setTimeout(() => fgRef.current?.zoomToFit(400, 50), 100);
    }
  }, [data]);

  const handleNodeClick = useCallback(
    (node: object) => {
      const n = node as GraphNode;
      setSelectedEntity(n);
      fetchSubgraph(n.id);
    },
    [fetchSubgraph, setSelectedEntity],
  );

  if (!data || data.nodes.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-gray-500 bg-gray-50 border-gray-200 border rounded-lg">
        No graph data available. Search or select an entity.
      </div>
    );
  }

  const getNodeColor = (node: object) => {
    const n = node as GraphNode;
    if (selectedEntity?.id === n.id) return "#ef4444"; // Red for selected
    switch (n.label) {
      case "Document":
        return "#3b82f6";
      case "Chunk":
        return "#9ca3af";
      case "LegalArticle":
        return "#10b981";
      case "Organisation":
        return "#f59e0b";
      case "Person":
        return "#8b5cf6";
      case "Concept":
        return "#6366f1";
      default:
        return "#6b7280";
    }
  };

  return (
    <div className="relative w-full h-full border border-gray-200 rounded-lg overflow-hidden bg-white">
      <ForceGraph2D
        ref={fgRef}
        graphData={data}
        nodeLabel="name"
        nodeColor={getNodeColor}
        nodeRelSize={6}
        linkColor={() => "#d1d5db"}
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        onNodeClick={handleNodeClick}
        onNodeHover={(node) => setHoverNode(node as GraphNode | null)}
        backgroundColor="#f9fafb"
      />
      {hoverNode && <EntityTooltip node={hoverNode} />}
      <GraphControls fgRef={fgRef} />
      <RelationshipLegend />
    </div>
  );
}
