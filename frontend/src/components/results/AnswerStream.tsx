import Spinner from "../ui/Spinner";

interface AnswerStreamProps {
  answer: string;
  isSearching: boolean;
  detectedLanguage: string | null;
}

export function AnswerStream({ answer, isSearching, detectedLanguage }: AnswerStreamProps) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Answer</h2>
        {detectedLanguage ? (
          <span className="text-xs text-slate-500">
            Response language: {detectedLanguage.toUpperCase()}
          </span>
        ) : null}
      </div>
      {isSearching && !answer ? (
        <div className="flex items-center gap-2 text-slate-500">
          <Spinner />
          <span className="text-sm">Generating answer...</span>
        </div>
      ) : (
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-800">
          {answer || "Submit a query to see the generated answer."}
        </p>
      )}
    </section>
  );
}
