"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useI18n } from "@/components/layout/I18nProvider";
import { MediaItem } from "@/types";
import { api } from "@/lib/api/client";
import { Button, RatingBadge, SourceBadge, TagChip, Skeleton } from "@/components/ui";
import { MediaCard } from "@/components/media/MediaCard";
import { ArrowLeft, Heart, ThumbsUp, ThumbsDown, HelpCircle, Info } from "lucide-react";
import { toggleFavorite, isFavorite } from "@/lib/mock/profile";
import PageTransition from "@/components/ui/PageTransition";

export default function MediaDetailPage() {
  const { type, id } = useParams() as { type: string; id: string };
  const { locale, t } = useI18n();
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<{
    media: MediaItem;
    why_recommended?: string;
    explanation?: any;
    similars: MediaItem[];
  } | null>(null);

  const [favorited, setFavorited] = useState(false);
  const [liked, setLiked] = useState<boolean | null>(null);
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);

  useEffect(() => {
    async function loadDetails() {
      if (!id) return;
      setLoading(true);
      try {
        const details = await api.getMediaDetail(type, id);
        setData(details);
        setFavorited(isFavorite(id));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadDetails();
  }, [type, id]);

  const handleFavoriteToggle = () => {
    const status = toggleFavorite(id);
    setFavorited(status);
  };

  const handleFeedback = async (val: "like" | "dislike") => {
    try {
      await api.submitFeedback(id, type, val);
      setLiked(val === "like");
      setFeedbackSuccess(val === "like" ? "Merci pour votre évaluation positive !" : "Feedback enregistré.");
      setTimeout(() => setFeedbackSuccess(null), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col gap-8 max-w-4xl mx-auto py-8">
        <Skeleton className="h-10 w-24 rounded" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Skeleton className="aspect-[2/3] w-full rounded-2xl" />
          <div className="md:col-span-2 flex flex-col gap-4">
            <Skeleton className="h-10 w-3/4 rounded" />
            <Skeleton className="h-6 w-1/4 rounded" />
            <Skeleton className="h-32 w-full rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-16">
        <h2 className="text-2xl font-serif text-slate-100 mb-2">Média introuvable</h2>
        <Button onClick={() => router.back()}>Retour</Button>
      </div>
    );
  }

  const { media, why_recommended, explanation, similars } = data;

  return (
    <PageTransition>
      <div className="max-w-5xl mx-auto flex flex-col gap-8 md:gap-12 pb-10">
        
        {/* Back Navigation */}
        <div>
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-slate-400 hover:text-slate-200 transition-colors text-sm font-semibold cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Retour</span>
          </button>
        </div>

        {/* Hero Area */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8 md:gap-12">
          
          {/* Left Column (Cover art & Favorites) */}
          <div className="md:col-span-2 flex flex-col items-center">
            <div className="relative w-full aspect-[2/3] rounded-2xl border border-border-custom overflow-hidden shadow-2xl bg-slate-950 max-w-[320px] md:max-w-none">
              <img
                src={media.cover_url || "/images/placeholder-book.svg"}
                alt={media.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 left-4 flex flex-col gap-2 z-10">
                <SourceBadge type={media.media_type} />
                {media.rating && media.rating > 0 && <RatingBadge rating={media.rating} />}
              </div>
            </div>
            
            <div className="flex gap-3 w-full max-w-[320px] md:max-w-none mt-6">
              <Button
                variant={favorited ? "primary" : "secondary"}
                onClick={handleFavoriteToggle}
                className="flex-grow gap-2 py-2.5 cursor-pointer"
              >
                <Heart className={`w-4 h-4 ${favorited ? "fill-white" : ""}`} />
                <span>{favorited ? "Favori" : "Ajouter aux favoris"}</span>
              </Button>
            </div>
          </div>

          {/* Right Column (Details) */}
          <div className="md:col-span-3 flex flex-col justify-center">
            <div className="flex flex-wrap gap-2 mb-3">
              {media.genres.map(g => (
                <TagChip key={g} label={g} />
              ))}
            </div>
            
            <h1 className="text-3xl md:text-5xl font-bold font-serif text-slate-100 mb-2 leading-tight">
              {media.title}
            </h1>
            
            <p className="text-sm md:text-base text-slate-400 mb-6">
              {t("media.creator")}: <span className="text-slate-200 font-semibold">{media.creator}</span>
            </p>

            {/* Tech Specs */}
            <div className="grid grid-cols-2 gap-4 border-y border-slate-900 py-4 mb-6 text-sm text-slate-400">
              <div>
                <span className="block text-[10px] text-slate-500 uppercase tracking-widest">{t("media.publisher")}</span>
                <span className="text-slate-200 font-medium">{media.publisher || "Inconnu"}</span>
              </div>
              <div>
                <span className="block text-[10px] text-slate-500 uppercase tracking-widest">{t("media.year")}</span>
                <span className="text-slate-200 font-medium">{media.year || "N/A"}</span>
              </div>
              <div>
                <span className="block text-[10px] text-slate-500 uppercase tracking-widest">{t("media.rating_source")}</span>
                <span className="text-slate-200 font-medium">{media.rating_source || "N/A"}</span>
              </div>
              <div>
                <span className="block text-[10px] text-slate-500 uppercase tracking-widest font-sans">Évaluations</span>
                <span className="text-slate-200 font-medium">{media.rating_count ? media.rating_count.toLocaleString() : 0}</span>
              </div>
            </div>

            {/* Description */}
            <div className="mb-6">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                {t("media.synopsis")}
              </h4>
              <p className="text-sm text-slate-300 leading-relaxed font-sans">
                {media.description || "Aucun synopsis disponible."}
              </p>
            </div>

            {/* Like/Dislike trigger */}
            <div className="bg-slate-950/20 border border-border-custom rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <span className="text-xs text-slate-400 font-medium">Recommanderiez-vous cette œuvre ?</span>
              <div className="flex items-center gap-2 shrink-0">
                <Button
                  variant={liked === true ? "primary" : "secondary"}
                  onClick={() => handleFeedback("like")}
                  className="gap-1.5 px-3 py-1.5 cursor-pointer"
                >
                  <ThumbsUp className="w-3.5 h-3.5" />
                  <span className="text-xs">{t("media.feedback_like")}</span>
                </Button>
                <Button
                  variant={liked === false ? "primary" : "secondary"}
                  onClick={() => handleFeedback("dislike")}
                  className="gap-1.5 px-3 py-1.5 cursor-pointer"
                >
                  <ThumbsDown className="w-3.5 h-3.5" />
                  <span className="text-xs">{t("media.feedback_dislike")}</span>
                </Button>
              </div>
            </div>
            {feedbackSuccess && (
              <span className="text-xs text-teal-400 font-medium mt-2 block animate-fade-in font-sans">
                {feedbackSuccess}
              </span>
            )}
          </div>

        </div>

        {/* Recommendation explanation layout */}
        {explanation && (
          <section className="bg-card border border-border-custom rounded-2xl p-6 md:p-8">
            <div className="flex items-center gap-2 mb-4">
              <HelpCircle className="w-5 h-5 text-teal-400" />
              <h3 className="text-lg font-bold font-serif text-slate-100">
                {t("media.explanation_title")}
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 items-center">
              
              <div className="bg-slate-950/40 border border-slate-900 rounded-xl p-4 text-center">
                <span className="block text-[10px] text-slate-500 uppercase tracking-widest mb-1">
                  {t("media.explanation_hybrid")}
                </span>
                <span className="text-3xl font-extrabold text-teal-400 font-serif">
                  {(explanation.score * 100).toFixed(0)}%
                </span>
                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-3 max-w-[120px] mx-auto">
                  <div
                    className="bg-teal-500 h-full rounded-full"
                    style={{ width: `${explanation.score * 100}%` }}
                  />
                </div>
              </div>

              <div className="md:col-span-2 flex flex-col gap-2 font-sans">
                {explanation.reasons.map((reason: string, idx: number) => (
                  <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-300">
                    <Info className="w-4 h-4 text-teal-500 shrink-0 mt-0.5" />
                    <span>{reason}</span>
                  </div>
                ))}
              </div>

            </div>
          </section>
        )}

        {/* Similar media grid list */}
        {similars.length > 0 && (
          <section className="border-t border-slate-900 pt-8">
            <h3 className="text-xl font-bold font-serif text-slate-100 mb-6 tracking-wide">
              {t("media.recs_title")}
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 md:gap-6">
              {similars.map(sim => (
                <div key={sim.id}>
                  <MediaCard media={sim} />
                </div>
              ))}
            </div>
          </section>
        )}

      </div>
    </PageTransition>
  );
}
