import { PageWrapper } from "../components/layout/PageWrapper";
import { ResultsPanel } from "../components/results/ResultsPanel";
import { SearchBar } from "../components/search/SearchBar";
import { useSearch } from "../hooks/useSearch";
import { useQueryStore } from "../store/queryStore";

export function SearchPage() {
  const { query, setQuery, answer, chunks, detectedLanguage } = useQueryStore();
  const {
    language,
    topK,
    isSearching,
    error,
    setLanguage,
    setTopK,
    submit,
    cancel,
  } = useSearch();

  return (
    <PageWrapper>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Multilingual Search</h1>
        <p className="mt-1 text-slate-600">
          Query EU legal corpora across German, English, French, and Polish with cross-lingual
          retrieval.
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <SearchBar
          query={query}
          language={language}
          topK={topK}
          isSearching={isSearching}
          onQueryChange={setQuery}
          onLanguageChange={setLanguage}
          onTopKChange={setTopK}
          onSubmit={() => void submit()}
          onCancel={cancel}
        />
        <ResultsPanel
          answer={answer}
          chunks={chunks}
          detectedLanguage={detectedLanguage}
          isSearching={isSearching}
          error={error}
        />
      </div>
    </PageWrapper>
  );
}
