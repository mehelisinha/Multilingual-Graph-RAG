import type { ChunkResult } from "../../types/query.types";
import { LanguageBadge } from "./LanguageBadge";
import { ScoreBadge } from "./ScoreBadge";

interface ChunkCardProps {
  chunk: ChunkResult;
  citationIndex: number;
}

export function ChunkCard({ chunk, citationIndex }: ChunkCardProps) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500">[{citationIndex}]</span>
          <h3 className="text-sm font-semibold text-slate-900">{chunk.title}</h3>
        </div>
        <div className="flex items-center gap-2">
          <LanguageBadge language={chunk.language} />
          <ScoreBadge score={chunk.score} />
        </div>
      </div>
      <p className="text-sm leading-relaxed text-slate-700">{chunk.text}</p>
      <p className="mt-2 text-xs text-slate-400">
        Document {chunk.document_id} · chunk {chunk.chunk_index}
      </p>
    </article>
  );
}
