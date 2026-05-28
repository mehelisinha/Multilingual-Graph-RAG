export type LanguageCode = "de" | "en" | "fr" | "pl";
export type LanguageOption = LanguageCode | "auto";

export const LANGUAGE_OPTIONS: { value: LanguageOption; label: string }[] = [
  { value: "auto", label: "Auto-detect" },
  { value: "de", label: "Deutsch" },
  { value: "en", label: "English" },
  { value: "fr", label: "Français" },
  { value: "pl", label: "Polski" },
];

export const LANGUAGE_LABELS: Record<LanguageCode, string> = {
  de: "Deutsch",
  en: "English",
  fr: "Français",
  pl: "Polski",
};

export const LANGUAGE_FLAGS: Record<LanguageCode, string> = {
  de: "🇩🇪",
  en: "🇬🇧",
  fr: "🇫🇷",
  pl: "🇵🇱",
};
