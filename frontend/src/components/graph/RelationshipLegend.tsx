import { LEGEND_ITEMS } from "./nodeColors";

export default function RelationshipLegend() {
  return (
    <div className="absolute top-4 left-4 bg-white/90 p-3 rounded shadow-md border border-gray-100 backdrop-blur-sm pointer-events-none">
      <h4 className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wider">
        Node Types
      </h4>
      <div className="flex flex-col gap-1.5">
        {LEGEND_ITEMS.map((item) => (
          <div key={item.label} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
            <span className="text-xs text-gray-600">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
