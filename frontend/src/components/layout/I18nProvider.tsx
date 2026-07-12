"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { Locale, translate } from "@/lib/i18n/config";
import { useParams, useRouter, usePathname } from "next/navigation";

interface I18nContextType {
  locale: Locale;
  setLocale: (lang: Locale) => void;
  t: (key: string, fallback?: string) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();
  
  const [locale, setLocaleState] = useState<Locale>("fr");

  useEffect(() => {
    if (params?.locale) {
      const currentLocale = params.locale as string;
      if (["fr", "en", "zh"].includes(currentLocale)) {
        setLocaleState(currentLocale as Locale);
      }
    }
  }, [params?.locale]);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    // Replace the locale prefix in the URL and navigate
    const segments = pathname.split("/");
    if (segments.length > 1 && ["fr", "en", "zh"].includes(segments[1])) {
      segments[1] = newLocale;
      router.push(segments.join("/"));
    } else {
      router.push(`/${newLocale}`);
    }
  };

  const t = (key: string, fallback?: string) => {
    return translate(locale, key, fallback);
  };

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
};

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used within an I18nProvider");
  }
  return context;
};
