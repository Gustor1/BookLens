"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n } from "./I18nProvider";
import { Home, Compass, Search, MessageSquare, Menu } from "lucide-react";
import { UniversalSearchDialog } from "../search/UniversalSearchDialog";

export const BottomNavigation: React.FC = () => {
  const { locale, t } = useI18n();
  const pathname = usePathname();
  const [searchOpen, setSearchOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === `/${locale}`) {
      return pathname === path;
    }
    return pathname === path || pathname.startsWith(path + "/");
  };

  const navItems = [
    { name: t("nav.home"), path: `/${locale}`, icon: Home },
    { name: t("nav.explore"), path: `/${locale}/explore`, icon: Compass },
    { name: "Rechercher", path: "search_dialog", icon: Search, isAction: true },
    { name: t("nav.assistant"), path: `/${locale}/assistant`, icon: MessageSquare },
    { name: t("nav.more"), path: `/${locale}/settings`, icon: Menu },
  ];

  return (
    <>
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-slate-950/90 backdrop-blur-md border-t border-slate-800/60 z-40 px-2 py-2 flex justify-around items-center">
        {navItems.map((item, idx) => {
          const Icon = item.icon;
          
          if (item.isAction) {
            return (
              <button
                key={idx}
                onClick={() => setSearchOpen(true)}
                className="flex flex-col items-center justify-center gap-1 p-1.5 text-slate-400 hover:text-slate-100 transition-all active:scale-90"
                aria-label="Open search dialog"
              >
                <Icon className="w-5 h-5 text-slate-400" />
                <span className="text-[10px] font-semibold text-slate-500">
                  {item.name}
                </span>
              </button>
            );
          }

          const active = isActive(item.path);

          return (
            <Link
              key={item.path}
              href={item.path}
              className={`flex flex-col items-center justify-center gap-1 p-1.5 transition-all ${
                active
                  ? "text-teal-400"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] font-semibold">
                {item.name}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Universal Search Dialog Modal Overlay */}
      <UniversalSearchDialog isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
};
export default BottomNavigation;
