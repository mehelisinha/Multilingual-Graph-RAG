import type { LanguageCode } from "../../config/languages";
import { LANGUAGE_FLAGS, LANGUAGE_LABELS } from "../../config/languages";

interface LanguageBadgeProps {
  language: string;
}

function normalizeLanguage(language: string): LanguageCode | null {
  const code = language.toLowerCase().slice(0, 2);
  if (code in LANGUAGE_LABELS) {
    return code as LanguageCode;
  }
  return null;
}

export function LanguageBadge({ language }: LanguageBadgeProps) {
  const code = normalizeLanguage(language);
  const label = code ? LANGUAGE_LABELS[code] : language.toUpperCase();
  const flag = code ? LANGUAGE_FLAGS[code] : "🌐";

  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
      <span aria-hidden>{flag}</span>
      <span>{code?.toUpperCase() ?? label}</span>
    </span>
  );
}
