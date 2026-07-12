"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n } from "./I18nProvider";
import { Search, Compass, MessageSquare, Library, Settings } from "lucide-react";
import { LanguageSelector } from "./LanguageSelector";
import { UniversalSearchDialog } from "../search/UniversalSearchDialog";

export const Header: React.FC = () => {
  const { locale, t } = useI18n();
  const pathname = usePathname();
  const [searchOpen, setSearchOpen] = useState(false);

  const navItems = [
    { name: t("nav.explore"), path: `/${locale}/explore`, icon: Compass },
    { name: t("nav.assistant"), path: `/${locale}/assistant`, icon: MessageSquare },
    { name: t("nav.library"), path: `/${locale}/library`, icon: Library },
  ];

  const isActive = (path: string) => {
    return pathname === path || pathname.startsWith(path + "/");
  };

  return (
    <>
      <header className="sticky top-0 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/40 z-40 px-4 md:px-8 py-3.5 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          
          {/* Logo / Wordmark */}
          <Link href={`/${locale}`} className="flex items-center gap-2">
            <span className="font-serif text-xl md:text-2xl font-bold text-slate-100 tracking-wider hover:text-teal-400 transition-colors">
              MediaLens
            </span>
            <span className="hidden md:inline-block px-1.5 py-0.5 rounded text-[9px] font-bold bg-teal-500/10 border border-teal-500/20 text-teal-400">
              V2
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`flex items-center gap-2 text-sm font-semibold transition-all ${
                    active
                      ? "text-teal-400"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Action Tools */}
          <div className="flex items-center gap-3">
            {/* Universal Search Button */}
            <button
              onClick={() => setSearchOpen(true)}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-100 transition-all active:scale-95 flex items-center gap-2"
              aria-label={t("nav.search_placeholder")}
            >
              <Search className="w-4 h-4" />
              <span className="hidden lg:inline text-xs text-slate-500 font-semibold pr-2">Rechercher...</span>
            </button>

            {/* Language Selection */}
            <LanguageSelector />

            {/* Settings Trigger */}
            <Link
              href={`/${locale}/settings`}
              className={`p-2 rounded-lg bg-slate-900 border border-slate-800 transition-all active:scale-95 ${
                isActive(`/${locale}/settings`)
                  ? "text-teal-400 border-teal-500/20 bg-teal-500/5"
                  : "text-slate-400 hover:text-slate-100"
              }`}
              aria-label={t("nav.settings")}
            >
              <Settings className="w-4 h-4" />
            </Link>
          </div>

        </div>
      </header>

      {/* Universal Search Modal Overlay */}
      <UniversalSearchDialog isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
};
export default Header;
