import { Button } from "../ui/Button";
import { LanguageSelect } from "./LanguageSelect";
import type { LanguageOption } from "../../config/languages";

interface SearchBarProps {
  query: string;
  language: LanguageOption;
  topK: number;
  isSearching: boolean;
  onQueryChange: (value: string) => void;
  onLanguageChange: (value: LanguageOption) => void;
  onTopKChange: (value: number) => void;
  onSubmit: () => void;
  onCancel: () => void;
}

const TOP_K_OPTIONS = [5, 10, 20];

export function SearchBar({
  query,
  language,
  topK,
  isSearching,
  onQueryChange,
  onLanguageChange,
  onTopKChange,
  onSubmit,
  onCancel,
}: SearchBarProps) {
  return (
    <form
      className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
      onSubmit={(event) => {
        event.preventDefault();
        void onSubmit();
      }}
    >
      <label className="flex flex-col gap-2">
        <span className="text-sm font-medium text-slate-700">Ask across DE / EN / FR / PL</span>
        <textarea
          className="min-h-[120px] w-full resize-y rounded-lg border border-slate-300 px-4 py-3 text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
          placeholder="e.g. What does GDPR Article 17 require for erasure?"
          value={query}
          disabled={isSearching}
          onChange={(event) => onQueryChange(event.target.value)}
        />
      </label>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <LanguageSelect
          value={language}
          onChange={onLanguageChange}
          disabled={isSearching}
        />
        <label className="flex flex-col gap-1 text-sm text-slate-600">
          <span className="font-medium">Results (top-k)</span>
          <select
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
            value={topK}
            disabled={isSearching}
            onChange={(event) => onTopKChange(Number(event.target.value))}
          >
            {TOP_K_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        <Button type="submit" isLoading={isSearching}>
          Search
        </Button>
        {isSearching ? (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        ) : null}
      </div>
    </form>
  );
}
