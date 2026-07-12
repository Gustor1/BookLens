"use client";

import React, { useState, useEffect } from "react";
import { useI18n } from "@/components/layout/I18nProvider";
import { MediaItem } from "@/types";
import { api } from "@/lib/api/client";
import { Button, TagChip, Skeleton, EmptyState } from "@/components/ui";
import { MediaCard } from "@/components/media/MediaCard";
import { Search, SlidersHorizontal } from "lucide-react";
import PageTransition from "@/components/ui/PageTransition";

export default function ExplorePage() {
  const { t } = useI18n();
  const [activeTab, setActiveTab] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeGenre, setActiveGenre] = useState("Tous");
  const [sortBy, setSortBy] = useState<"rating" | "year">("rating");
  
  const [items, setItems] = useState<MediaItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showMobileFilters, setShowMobileFilters] = useState(false);

  const genres = [
    "Tous",
    "Science-Fiction",
    "Écofiction",
    "Féminisme",
    "Dystopie",
    "Fantasy",
    "Aventure",
    "Cyberpunk",
    "Cinéma d'auteur",
    "Exploration",
    "Jeu de rôle",
    "Essai"
  ];

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const results = await api.explore(activeTab, searchQuery, activeGenre, 40);
        
        const sorted = [...results].sort((a, b) => {
          if (sortBy === "rating") {
            return (b.rating || 0) - (a.rating || 0);
          } else {
            return parseInt(b.year || "0") - parseInt(a.year || "0");
          }
        });
        
        setItems(sorted);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [activeTab, searchQuery, activeGenre, sortBy]);

  return (
    <PageTransition>
      <div className="flex flex-col gap-6 md:gap-8">
        
        {/* Title and Sort Controls */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-900 pb-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold font-serif text-slate-100">
              {t("explore.title")}
            </h1>
            <p className="text-xs md:text-sm text-slate-500 mt-1">
              Explorez et filtrez nos collections trans-média.
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-semibold uppercase">{t("explore.sort_rating")} :</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as "rating" | "year")}
              className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none cursor-pointer hover:border-slate-700 transition-all font-semibold font-sans"
            >
              <option value="rating">Top Notes</option>
              <option value="year">Date de sortie</option>
            </select>
          </div>
        </div>

        {/* Tab Selection */}
        <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar border-b border-slate-900/60">
          {[
            { id: "all", label: t("explore.filter_all") },
            { id: "books", label: t("explore.filter_books") },
            { id: "movies", label: t("explore.filter_movies") },
            { id: "games", label: t("explore.filter_games") }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id);
                setActiveGenre("Tous");
              }}
              className={`px-4 py-2 border-b-2 font-semibold text-sm transition-all whitespace-nowrap cursor-pointer ${
                activeTab === tab.id
                  ? "border-teal-500 text-teal-400 font-bold"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Main layout grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
          
          {/* Desktop Filters Panel */}
          <div className="hidden lg:flex flex-col gap-6 bg-card/30 border border-border-custom rounded-xl p-5">
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
                Rechercher
              </h4>
              <div className="relative">
                <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t("explore.search_media_placeholder")}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500 transition-all font-sans"
                />
              </div>
            </div>

            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
                {t("explore.genre")}
              </h4>
              <div className="flex flex-wrap gap-2">
                {genres.map((genre) => (
                  <TagChip
                    key={genre}
                    label={genre}
                    active={activeGenre === genre}
                    onClick={() => setActiveGenre(genre)}
                  />
                ))}
              </div>
            </div>

            <Button
              variant="ghost"
              className="text-xs text-slate-500 hover:text-slate-300 mt-2"
              onClick={() => {
                setSearchQuery("");
                setActiveGenre("Tous");
              }}
            >
              {t("explore.clear_filters")}
            </Button>
          </div>

          {/* Mobile Filters Panel */}
          <div className="lg:hidden flex flex-col gap-3">
            <div className="flex gap-2">
              <div className="relative flex-grow">
                <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t("explore.search_media_placeholder")}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500 transition-all font-sans"
                />
              </div>
              <button
                onClick={() => setShowMobileFilters(!showMobileFilters)}
                className={`p-2 border rounded-lg flex items-center justify-center transition-all cursor-pointer ${
                  showMobileFilters
                    ? "bg-teal-500/10 border-teal-500/30 text-teal-400"
                    : "bg-slate-900 border-slate-800 text-slate-400"
                }`}
                aria-label="Filter chips drawer"
              >
                <SlidersHorizontal className="w-5 h-5" />
              </button>
            </div>

            {/* Mobile Genre list */}
            {showMobileFilters && (
              <div className="p-4 bg-card border border-border-custom rounded-xl flex flex-col gap-3 animate-fade-in">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  {t("explore.genre")}
                </h4>
                <div className="flex flex-wrap gap-2">
                  {genres.map((genre) => (
                    <TagChip
                      key={genre}
                      label={genre}
                      active={activeGenre === genre}
                      onClick={() => setActiveGenre(genre)}
                    />
                  ))}
                </div>
                <button
                  onClick={() => {
                    setSearchQuery("");
                    setActiveGenre("Tous");
                    setShowMobileFilters(false);
                  }}
                  className="text-xs text-center text-teal-400 mt-2 hover:underline cursor-pointer"
                >
                  {t("explore.clear_filters")}
                </button>
              </div>
            )}
          </div>

          {/* Grid Area */}
          <div className="lg:col-span-3">
            {loading ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-4 gap-4 md:gap-6">
                {Array.from({ length: 8 }).map((_, idx) => (
                  <div key={idx} className="flex flex-col gap-3">
                    <Skeleton className="aspect-[2/3] w-full rounded-xl" />
                    <Skeleton className="h-4 w-3/4 rounded" />
                    <Skeleton className="h-3 w-1/2 rounded" />
                  </div>
                ))}
              </div>
            ) : items.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-4 gap-4 md:gap-6">
                {items.map((media) => (
                  <div key={media.id}>
                    <MediaCard media={media} />
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-12">
                <EmptyState
                  title={t("explore.empty_state")}
                  description={t("explore.empty_desc")}
                  actionLabel={t("explore.clear_filters")}
                  onAction={() => {
                    setSearchQuery("");
                    setActiveGenre("Tous");
                  }}
                />
              </div>
            )}
          </div>

        </div>

      </div>
    </PageTransition>
  );
}
