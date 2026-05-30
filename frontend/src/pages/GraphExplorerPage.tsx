import React, { useEffect, useState } from 'react';
import { PageWrapper } from "../components/layout/PageWrapper";
import GraphViewer from '../components/graph/GraphViewer';
import { graphApi } from '../api/graph';
import { useGraphStore } from '../store/graphStore';
import { Search, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

export function GraphExplorerPage() {
  const [entities, setEntities] = useState<{ id: string; name: string; type: string; degree: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  const { fetchSubgraph } = useGraphStore(state => ({
    fetchSubgraph: async (id: string) => {
      state.setLoading(true);
      try {
        const data = await graphApi.getSubgraph(id);
        state.setData(data);
      } catch(e: any) {
        toast.error('Failed to load subgraph');
      } finally {
        state.setLoading(false);
      }
    }
  }));

  useEffect(() => {
    async function loadEntities() {
      setLoading(true);
      try {
        const data = await graphApi.getEntities();
        setEntities(data);
      } catch (err) {
        toast.error('Failed to load entities list');
      } finally {
        setLoading(false);
      }
    }
    loadEntities();
  }, []);

  const filteredEntities = entities.filter(e => e.name.toLowerCase().includes(searchTerm.toLowerCase())).slice(0, 50);

  return (
    <PageWrapper>
      <div className="flex h-[calc(100vh-8rem)] gap-6">
        {/* Sidebar for entity selection */}
        <div className="w-80 flex flex-col bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100">
            <h2 className="font-semibold text-lg text-slate-800">Entities</h2>
            <p className="text-xs text-slate-500 mt-1">Select an entity to explore its neighborhood</p>
            <div className="mt-4 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input
                type="text"
                placeholder="Search entities..."
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {loading ? (
              <div className="flex justify-center p-4"><Loader2 className="animate-spin text-blue-500" /></div>
            ) : filteredEntities.length > 0 ? (
              <ul className="space-y-1">
                {filteredEntities.map(entity => (
                  <li key={entity.id}>
                    <button
                      onClick={() => fetchSubgraph(entity.id)}
                      className="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 transition-colors flex flex-col"
                    >
                      <span className="font-medium text-sm text-slate-800 truncate w-full">{entity.name}</span>
                      <span className="text-xs text-slate-500 flex justify-between mt-0.5">
                        <span>{entity.type}</span>
                        <span>Degree: {entity.degree}</span>
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500 text-center p-4">No entities found.</p>
            )}
          </div>
        </div>
        
        {/* Main graph viewer */}
        <div className="flex-1 bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          <GraphViewer />
        </div>
      </div>
    </PageWrapper>
  );
}
