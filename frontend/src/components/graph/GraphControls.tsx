import React from "react";
import { ZoomIn, ZoomOut, Maximize } from "lucide-react";

import { ForceGraphMethods } from "react-force-graph-2d";

export default function GraphControls({
  fgRef,
}: {
  fgRef: React.MutableRefObject<ForceGraphMethods | undefined>;
}) {
  return (
    <div className="absolute top-4 right-4 flex flex-col gap-2 bg-white p-2 rounded shadow-md border border-gray-100">
      <button
        onClick={() => fgRef.current?.zoom(fgRef.current.zoom() * 1.2, 400)}
        className="p-1 hover:bg-gray-100 rounded"
        title="Zoom In"
      >
        <ZoomIn size={18} />
      </button>
      <button
        onClick={() => fgRef.current?.zoom(fgRef.current.zoom() / 1.2, 400)}
        className="p-1 hover:bg-gray-100 rounded"
        title="Zoom Out"
      >
        <ZoomOut size={18} />
      </button>
      <button
        onClick={() => fgRef.current?.zoomToFit(400, 50)}
        className="p-1 hover:bg-gray-100 rounded"
        title="Fit to Screen"
      >
        <Maximize size={18} />
      </button>
    </div>
  );
}
