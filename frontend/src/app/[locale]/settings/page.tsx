"use client";

import React from "react";
import { useI18n } from "@/components/layout/I18nProvider";
import { useSettings } from "@/components/layout/SettingsProvider";
import { Locale } from "@/lib/i18n/config";
import { Button } from "@/components/ui";
import { Settings, Globe, Eye, Shield, RotateCcw } from "lucide-react";
import PageTransition from "@/components/ui/PageTransition";

export default function SettingsPage() {
  const { locale, setLocale, t } = useI18n();
  const { theme, setTheme, reducedMotion, setReducedMotion, resetAll } = useSettings();

  return (
    <PageTransition>
      <div className="flex flex-col gap-6 md:gap-8 max-w-2xl mx-auto">
        
        {/* Title */}
        <div className="border-b border-slate-900 pb-4">
          <h1 className="text-2xl md:text-3xl font-bold font-serif text-slate-100 flex items-center gap-2.5">
            <Settings className="w-6 h-6 text-teal-400" />
            <span>{t("settings.title")}</span>
          </h1>
          <p className="text-xs md:text-sm text-slate-500 mt-1">
            Gérez vos préférences locales et paramètres d&apos;accessibilité.
          </p>
        </div>

        {/* Form Groups */}
        <div className="flex flex-col gap-5">
          
          {/* Language selection */}
          <div className="bg-card border border-border-custom rounded-xl p-5 flex items-center justify-between gap-4 font-sans">
            <div className="flex items-center gap-3">
              <Globe className="w-5 h-5 text-teal-400 shrink-0" />
              <div>
                <h4 className="text-sm font-semibold text-slate-200">
                  {t("settings.lang_label")}
                </h4>
                <p className="text-xs text-slate-500">
                  Modifier la langue d&apos;affichage de l&apos;interface.
                </p>
              </div>
            </div>
            
            <select
              value={locale}
              onChange={(e) => setLocale(e.target.value as Locale)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none cursor-pointer hover:border-slate-700 transition-all font-semibold font-sans"
            >
              <option value="fr" className="bg-[#0b0f19]">Français (FR)</option>
              <option value="en" className="bg-[#0b0f19]">English (EN)</option>
              <option value="zh" className="bg-[#0b0f19]">简体中文 (ZH)</option>
            </select>
          </div>

          {/* Theme selection */}
          <div className="bg-card border border-border-custom rounded-xl p-5 flex items-center justify-between gap-4 font-sans">
            <div className="flex items-center gap-3">
              <Eye className="w-5 h-5 text-teal-400 shrink-0" />
              <div>
                <h4 className="text-sm font-semibold text-slate-200">
                  {t("settings.theme_label")}
                </h4>
                <p className="text-xs text-slate-500">
                  Changer le style de couleurs de la plateforme.
                </p>
              </div>
            </div>

            <select
              value={theme}
              onChange={(e) => setTheme(e.target.value as "dark" | "light")}
              className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none cursor-pointer hover:border-slate-700 transition-all font-semibold font-sans"
            >
              <option value="dark" className="bg-[#0b0f19]">{t("settings.theme_dark")}</option>
              <option value="light" className="bg-[#0b0f19]">Clair (Light)</option>
            </select>
          </div>

          {/* Reduced Motion Toggle */}
          <div className="bg-card border border-border-custom rounded-xl p-5 flex items-center justify-between gap-4 font-sans">
            <div className="flex items-center gap-3">
              <RotateCcw className="w-5 h-5 text-teal-400 shrink-0" />
              <div>
                <h4 className="text-sm font-semibold text-slate-200">
                  {t("settings.reduced_motion")}
                </h4>
                <p className="text-xs text-slate-500">
                  {t("settings.reduced_motion_desc")}
                </p>
              </div>
            </div>

            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={reducedMotion}
                onChange={(e) => setReducedMotion(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-900 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-500 after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-teal-600 peer-checked:after:bg-white"></div>
            </label>
          </div>

          {/* Security details info */}
          <div className="bg-slate-950/20 border border-slate-900 rounded-xl p-5 flex items-start gap-3.5 font-sans">
            <Shield className="w-5 h-5 text-slate-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-1">
                {t("settings.privacy")}
              </h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                {t("settings.privacy_desc")}
              </p>
            </div>
          </div>

          {/* Preferences Purge */}
          <div className="mt-4 flex justify-end font-sans">
            <Button
              variant="secondary"
              onClick={resetAll}
              className="gap-2 border-red-500/10 hover:border-red-500/20 text-red-400 hover:text-red-300 bg-red-950/5 hover:bg-red-950/10 cursor-pointer"
            >
              <RotateCcw className="w-4 h-4" />
              <span>{t("settings.reset_prefs")}</span>
            </Button>
          </div>

        </div>

      </div>
    </PageTransition>
  );
}
