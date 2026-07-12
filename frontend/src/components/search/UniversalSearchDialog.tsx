"use client";

import React, { useState, useEffect, useRef } from "react";
import { Search, X, ArrowRight } from "lucide-react";
import { MediaItem } from "@/types";
import { api } from "@/lib/api/client";
import { useI18n } from "@/components/layout/I18nProvider";
import Link from "next/link";
import { SourceBadge } from "../ui";

export const UniversalSearchDialog: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
  onClose
}) => {
  const { locale, t } = useI18n();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<MediaItem[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    const delayDebounce = setTimeout(async () => {
      setLoading(true);
      try {
        const items = await api.explore("all", query, "Tous", 5);
        setResults(items);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => clearTimeout(delayDebounce);
  }, [query]);

  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      onClick={handleBackdropClick}
      className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-start justify-center p-4 md:p-10 animate-fade-in"
    >
      <div className="w-full max-w-2xl bg-card border border-slate-800 rounded-2xl shadow-2xl overflow-hidden mt-10 md:mt-20">
        
        {/* Search Input Bar */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-slate-800 bg-slate-900/30">
          <Search className="w-5 h-5 text-slate-500" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("home.search_placeholder")}
            className="flex-grow bg-transparent text-slate-100 placeholder-slate-500 text-base focus:outline-none"
          />
          <button
            onClick={onClose}
            className="p-1 rounded-full hover:bg-slate-900 text-slate-400 hover:text-slate-100 transition-colors"
            aria-label={t("common.close")}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Results Pane */}
        <div className="max-h-[350px] overflow-y-auto p-4">
          {loading && (
            <div className="flex items-center justify-center py-8">
              <span className="text-sm text-slate-500">{t("common.loading")}</span>
            </div>
          )}

          {!loading && results.length > 0 && (
            <div className="flex flex-col gap-2">
              {results.map((media) => (
                <Link
                  key={media.id}
                  href={`/${locale}/media/${media.media_type}/${media.id}`}
                  onClick={onClose}
                  className="flex items-center gap-4 p-2.5 rounded-xl hover:bg-slate-900/60 border border-transparent hover:border-slate-800 transition-all group"
                >
                  <img
                    src={media.cover_url}
                    alt={media.title}
                    className="w-10 h-14 rounded object-cover bg-slate-950"
                  />
                  <div className="flex-grow">
                    <div className="flex items-center gap-2 mb-0.5">
                      <h5 className="font-semibold text-slate-200 group-hover:text-teal-400 transition-colors text-sm line-clamp-1">
                        {media.title}
                      </h5>
                      <SourceBadge type={media.media_type} />
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-1">{media.creator}</p>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-teal-400 group-hover:translate-x-1 transition-all shrink-0" />
                </Link>
              ))}
            </div>
          )}

          {!loading && query.trim() !== "" && results.length === 0 && (
            <div className="text-center py-8 text-sm text-slate-500">
              {t("explore.empty_state")}
            </div>
          )}
          
          {query.trim() === "" && (
            <div className="text-xs text-slate-500 text-center py-4">
              Tapez le nom de l&apos;œuvre (livre, film, jeu) pour chercher...
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
export default UniversalSearchDialog;
