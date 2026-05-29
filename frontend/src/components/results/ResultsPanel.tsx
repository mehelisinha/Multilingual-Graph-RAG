import type { ChunkResult } from "../../types/query.types";
import { AnswerStream } from "./AnswerStream";
import { ChunkCard } from "./ChunkCard";

interface ResultsPanelProps {
  answer: string;
  chunks: ChunkResult[];
  detectedLanguage: string | null;
  isSearching: boolean;
  error: string | null;
}

export function ResultsPanel({
  answer,
  chunks,
  detectedLanguage,
  isSearching,
  error,
}: ResultsPanelProps) {
  return (
    <div className="space-y-6">
      {error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <AnswerStream answer={answer} isSearching={isSearching} detectedLanguage={detectedLanguage} />

      {chunks.length > 0 ? (
        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-slate-900">Sources</h2>
          {chunks.map((chunk, index) => (
            <ChunkCard key={chunk.id} chunk={chunk} citationIndex={index + 1} />
          ))}
        </section>
      ) : null}
    </div>
  );
}
