"use client";

import React, { useState, useEffect } from "react";
import { useI18n } from "@/components/layout/I18nProvider";
import { MediaItem } from "@/types";
import { getFavorites } from "@/lib/mock/profile";
import { isDemoMode } from "@/lib/api/client";
import { Button, EmptyState, Skeleton } from "@/components/ui";
import { MediaCard } from "@/components/media/MediaCard";
import { Heart, FileText, Upload, AlertCircle } from "lucide-react";
import PageTransition from "@/components/ui/PageTransition";

export default function LibraryPage() {
  const { t } = useI18n();
  const [activeTab, setActiveTab] = useState<"favorites" | "documents">("favorites");
  const [favorites, setFavorites] = useState<MediaItem[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [demoActive, setDemoActive] = useState(false);

  useEffect(() => {
    async function loadLibraryData() {
      setLoading(true);
      try {
        setDemoActive(isDemoMode());
        
        // Load favorites
        const favs = getFavorites();
        setFavorites(favs);

        // Load documents (if API is active)
        if (!isDemoMode()) {
          setDocuments([]);
        } else {
          // Mock documents
          setDocuments([
            { id: "doc-1", title: "Le Recit-Panier - Ursula Le Guin.pdf", date: "12/07/2026", size: "1.2 MB", status: "Indexed" },
            { id: "doc-2", title: "Donna Haraway - Manifeste Cyborg.pdf", date: "10/07/2026", size: "2.4 MB", status: "Indexed" }
          ]);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadLibraryData();
  }, [activeTab]);

  return (
    <PageTransition>
      <div className="flex flex-col gap-6 md:gap-8">
        
        {/* Title */}
        <div className="border-b border-slate-900 pb-4">
          <h1 className="text-2xl md:text-3xl font-bold font-serif text-slate-100">
            {t("library.title")}
          </h1>
          <p className="text-xs md:text-sm text-slate-500 mt-1">
            Gérez vos œuvres préférées et vos documents de recherche RAG.
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 border-b border-slate-900/60 pb-1">
          <button
            onClick={() => setActiveTab("favorites")}
            className={`flex items-center gap-2 pb-2 font-semibold text-sm border-b-2 cursor-pointer transition-all ${
              activeTab === "favorites"
                ? "border-teal-500 text-teal-400 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Heart className="w-4 h-4" />
            <span>{t("library.tab_favorites")}</span>
          </button>
          <button
            onClick={() => setActiveTab("documents")}
            className={`flex items-center gap-2 pb-2 font-semibold text-sm border-b-2 cursor-pointer transition-all ${
              activeTab === "documents"
                ? "border-teal-500 text-teal-400 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>{t("library.tab_documents")}</span>
          </button>
        </div>

        {/* Tab Contents */}
        <div className="min-h-[250px]">
          {loading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {Array.from({ length: 4 }).map((_, idx) => (
                <Skeleton key={idx} className="aspect-[2/3] w-full rounded-xl" />
              ))}
            </div>
          ) : activeTab === "favorites" ? (
            favorites.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {favorites.map((media) => (
                  <div key={media.id}>
                    <MediaCard media={media} />
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                title={t("library.favorites_empty")}
                description={t("library.favorites_desc")}
              />
            )
          ) : (
            // Documents RAG
            <div className="flex flex-col gap-6">
              
              {/* Document upload box */}
              <div className="border border-dashed border-slate-800 rounded-2xl p-8 bg-slate-950/20 text-center flex flex-col items-center max-w-xl mx-auto w-full">
                <Upload className="w-10 h-10 text-slate-600 mb-3" />
                <h3 className="text-sm font-semibold text-slate-300 mb-1">
                  {t("library.upload_btn")}
                </h3>
                <p className="text-xs text-slate-500 mb-4 max-w-xs leading-relaxed font-sans">
                  Déposez un fichier PDF critique ou de recherche pour étendre les connaissances de l&apos;assistant.
                </p>
                
                {demoActive ? (
                  <div className="inline-flex items-center gap-1.5 text-[11px] text-amber-500 bg-amber-500/10 border border-amber-500/20 rounded-lg px-3 py-1.5 font-sans">
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>{t("library.backend_required")}</span>
                  </div>
                ) : (
                  <Button variant="primary" className="text-xs cursor-pointer">
                    Parcourir les fichiers
                  </Button>
                )}
              </div>

              {/* Document register list */}
              {documents.length > 0 && (
                <div className="flex flex-col gap-3 max-w-xl mx-auto w-full mt-4">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest px-1">
                    Documents indexés dans le RAG
                  </h4>
                  <div className="flex flex-col gap-2.5 font-sans">
                    {documents.map((doc) => (
                      <div
                        key={doc.id}
                        className="flex items-center justify-between p-3.5 bg-card border border-border-custom rounded-xl"
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="w-5 h-5 text-teal-400" />
                          <div>
                            <h5 className="text-sm font-semibold text-slate-200 line-clamp-1">{doc.title}</h5>
                            <span className="text-[10px] text-slate-500">{doc.date} &bull; {doc.size}</span>
                          </div>
                        </div>
                        <span className="text-[10px] bg-teal-500/10 border border-teal-500/20 text-teal-400 px-2 py-0.5 rounded font-bold">
                          {doc.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          )}
        </div>

      </div>
    </PageTransition>
  );
}
