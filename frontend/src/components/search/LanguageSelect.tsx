import type { LanguageOption } from "../../config/languages";
import { LANGUAGE_OPTIONS } from "../../config/languages";

interface LanguageSelectProps {
  value: LanguageOption;
  onChange: (value: LanguageOption) => void;
  disabled?: boolean;
}

export function LanguageSelect({ value, onChange, disabled }: LanguageSelectProps) {
  return (
    <label className="flex flex-col gap-1 text-sm text-slate-600">
      <span className="font-medium">Language</span>
      <select
        className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value as LanguageOption)}
      >
        {LANGUAGE_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
