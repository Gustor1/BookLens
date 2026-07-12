"use client";

import React from "react";
import { SettingsProvider } from "@/components/layout/SettingsProvider";
import { I18nProvider } from "@/components/layout/I18nProvider";
import Header from "@/components/layout/Header";
import BottomNavigation from "@/components/layout/BottomNavigation";

export default function LocaleLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SettingsProvider>
      <I18nProvider>
        <div className="flex flex-col min-h-screen">
          {/* Header Desktop Sticky Navigation */}
          <Header />

          {/* Main content grid */}
          <main className="flex-grow max-w-7xl w-full mx-auto px-4 md:px-8 py-6 md:py-8 pb-24 md:pb-16">
            {children}
          </main>

          {/* Mobile bottom nav */}
          <BottomNavigation />

          {/* Desktop editorial footer */}
          <footer className="hidden md:block py-8 border-t border-slate-900 bg-[#050811] text-center text-xs text-slate-600">
            <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4">
              <span>&copy; {new Date().getFullYear()} MediaLens. Conçu pour l&apos;exploration culturelle.</span>
              <div className="flex gap-4">
                <span className="hover:text-slate-400 transition-colors">V2 App Shell</span>
                <span>&bull;</span>
                <span className="hover:text-slate-400 transition-colors">Python API Backend Connected</span>
              </div>
            </div>
          </footer>
        </div>
      </I18nProvider>
    </SettingsProvider>
  );
}
