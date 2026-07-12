"use client";

import React from "react";
import Link from "next/link";
import { MediaItem } from "@/types";
import { useI18n } from "@/components/layout/I18nProvider";
import { RatingBadge, SourceBadge, Button } from "../ui";
import { ArrowRight } from "lucide-react";

export const FeaturedMediaCard: React.FC<{ media: MediaItem }> = ({ media }) => {
  const { locale, t } = useI18n();

  return (
    <div className="bg-card rounded-2xl border border-border-custom overflow-hidden shadow-2xl">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 md:gap-8">
        
        {/* Cover Art Container */}
        <div className="md:col-span-2 relative aspect-[4/5] md:aspect-auto md:h-full min-h-[300px] bg-slate-950">
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

        {/* Text Details */}
        <div className="md:col-span-3 flex flex-col justify-center p-6 md:p-8 md:pl-0">
          <span className="text-xs font-semibold text-teal-400 uppercase tracking-widest mb-2">
            {t("home.featured")}
          </span>
          <h3 className="text-2xl md:text-4xl font-bold font-serif text-slate-100 mb-2 leading-tight">
            {media.title}
          </h3>
          <p className="text-xs md:text-sm text-slate-400 mb-4">
            {t("media.creator")}: <span className="text-slate-200">{media.creator}</span>
          </p>
          
          <p className="text-sm text-slate-300 leading-relaxed mb-6 line-clamp-4">
            {media.description}
          </p>

          {/* "Why this choice?" Section */}
          <div className="bg-slate-950/40 border border-border-custom rounded-xl p-4 mb-6">
            <h5 className="text-xs font-semibold text-teal-400 uppercase tracking-wider mb-1.5">
              {t("home.why_recommended")}
            </h5>
            <p className="text-xs text-slate-400 leading-relaxed">
              Ce chef-d&apos;œuvre d&apos;écriture aborde de manière visionnaire les notions de genre et d&apos;écologie politique dans un système narratif complexe. C&apos;est le point d&apos;entrée idéal pour comprendre l&apos;impact sociétal de l&apos;écofiction.
            </p>
          </div>

          <Link href={`/${locale}/media/${media.media_type}/${media.id}`}>
            <Button variant="primary" className="gap-2">
              <span>{t("home.cta_explore")}</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>

      </div>
    </div>
  );
};
export default FeaturedMediaCard;
