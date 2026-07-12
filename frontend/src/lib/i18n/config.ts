import fr from "./fr.json";
import en from "./en.json";
import zh from "./zh.json";

export type Locale = "fr" | "en" | "zh";

export const translations = {
  fr,
  en,
  zh
};

export function getTranslation(locale: Locale) {
  return translations[locale] || translations.fr;
}

export function translate(locale: Locale, key: string, fallback: string = ""): string {
  const trans = getTranslation(locale);
  const parts = key.split(".");
  let current: any = trans;
  for (const part of parts) {
    if (current && typeof current === "object" && part in current) {
      current = current[part];
    } else {
      return fallback || key;
    }
  }
  return typeof current === "string" ? current : fallback || key;
}
