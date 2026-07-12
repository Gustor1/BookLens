"use client";

import React from "react";
import { useI18n } from "./I18nProvider";
import { Locale } from "@/lib/i18n/config";
import { Globe } from "lucide-react";

export const LanguageSelector: React.FC = () => {
  const { locale, setLocale } = useI18n();

  return (
    <div className="relative inline-flex items-center gap-1.5 bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-lg px-2.5 py-1.5 transition-all text-xs font-semibold text-slate-300">
      <Globe className="w-3.5 h-3.5 text-slate-400" />
      <select
        value={locale}
        onChange={(e) => setLocale(e.target.value as Locale)}
        className="bg-transparent text-slate-300 focus:outline-none cursor-pointer pr-1"
      >
        <option value="fr" className="bg-[#0b0f19] text-slate-300">FR</option>
        <option value="en" className="bg-[#0b0f19] text-slate-300">EN</option>
        <option value="zh" className="bg-[#0b0f19] text-slate-300">ZH</option>
      </select>
    </div>
  );
};
export default LanguageSelector;
