"use client";

import React, { useState, useEffect } from "react";
import { useI18n } from "@/components/layout/I18nProvider";
import { FeaturedMediaCard } from "@/components/media/FeaturedMediaCard";
import { MediaRail } from "@/components/media/MediaRail";
import { Button } from "@/components/ui";
import { api, isDemoMode } from "@/lib/api/client";
import { MediaItem } from "@/types";
import { Compass, Sparkles, MessageSquare } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import PageTransition from "@/components/ui/PageTransition";

export default function HomePage() {
  const { locale, t } = useI18n();
  const router = useRouter();
  const [featured, setFeatured] = useState<MediaItem | null>(null);
  const [rails, setRails] = useState<Record<string, MediaItem[]>>({});
  const [surpriseLoading, setSurpriseLoading] = useState(false);
  const [demoActive, setDemoActive] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        setDemoActive(isDemoMode());
        
        // Load featured
        const items = await api.explore("all", "", "Tous", 1);
        if (items.length > 0) {
          setFeatured(items[0]);
        }
        
        // Load rails
        const recs = await api.getRecommendations("all", 8);
        setRails(recs);
      } catch (err) {
        console.error("Error loading home page data", err);
      }
    }
    loadData();
  }, []);

  const handleSurprise = async () => {
    setSurpriseLoading(true);
    // Short non-intrusive animation delay
    await new Promise(r => setTimeout(r, 600));
    try {
      const items = await api.explore("all", "", "Tous", 30);
      if (items.length > 0) {
        const randomItem = items[Math.floor(Math.random() * items.length)];
        router.push(`/${locale}/media/${randomItem.media_type}/${randomItem.id}`);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSurpriseLoading(false);
    }
  };

  return (
    <PageTransition>
      <div className="flex flex-col gap-10 md:gap-14">
        
        {/* Demo Mode Banner */}
        {demoActive && (
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between bg-teal-500/10 border border-teal-500/20 rounded-xl px-4 py-3 text-xs text-teal-400 gap-2">
            <span className="font-semibold">🧭 {t("common.demo_mode")} : Les données et réponses de l&apos;assistant sont simulées localement en mode démo.</span>
            <span className="opacity-75 text-[10px] uppercase font-bold tracking-wider">Mocks Actifs</span>
          </div>
        )}

        {/* Hero Section */}
        <section className="text-center py-8 md:py-16 max-w-3xl mx-auto flex flex-col items-center">
          <h1 className="text-3xl md:text-6xl font-bold font-serif text-slate-100 mb-4 md:mb-6 leading-tight tracking-tight">
            {t("home.hero_title")}
          </h1>
          <p className="text-sm md:text-lg text-slate-400 mb-8 max-w-xl leading-relaxed">
            {t("home.hero_subtitle")}
          </p>

          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto justify-center">
            <Link href={`/${locale}/explore`} className="w-full sm:w-auto">
              <Button variant="primary" className="gap-2 text-sm md:text-base px-6 py-3 w-full">
                <Compass className="w-4 h-4 md:w-5 h-5" />
                <span>{t("home.cta_explore")}</span>
              </Button>
            </Link>
            
            <Link href={`/${locale}/assistant`} className="w-full sm:w-auto">
              <Button variant="secondary" className="gap-2 text-sm md:text-base px-6 py-3 w-full">
                <MessageSquare className="w-4 h-4 md:w-5 h-5 text-teal-400" />
                <span>{t("home.cta_assistant")}</span>
              </Button>
            </Link>

            <Button
              variant="secondary"
              onClick={handleSurprise}
              isLoading={surpriseLoading}
              className="gap-2 text-sm md:text-base px-6 py-3 border-amber-500/20 hover:border-amber-500/40 text-amber-500 w-full"
            >
              <Sparkles className="w-4 h-4 md:w-5 h-5 fill-amber-500/10" />
              <span>{t("home.random_surprise")}</span>
            </Button>
          </div>
        </section>

        {/* Featured Story */}
        {featured && (
          <section className="flex flex-col">
            <FeaturedMediaCard media={featured} />
          </section>
        )}

        {/* Media Rails */}
        <section className="flex flex-col gap-2">
          <MediaRail
            title={t("home.rails.discover")}
            items={rails.discover || []}
          />
          <MediaRail
            title={t("home.rails.ecofiction")}
            items={rails.ecofiction || []}
          />
          <MediaRail
            title={t("home.rails.crossmedia")}
            items={rails.crossmedia || []}
          />
          <MediaRail
            title={t("home.rails.recommendations")}
            items={rails.personalized || []}
          />
        </section>

      </div>
    </PageTransition>
  );
}
