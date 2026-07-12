"use client";

import React from "react";
import Link from "next/link";
import { MediaItem } from "@/types";
import { useI18n } from "@/components/layout/I18nProvider";
import { RatingBadge, SourceBadge } from "../ui";
import { motion } from "framer-motion";
import { useSettings } from "@/components/layout/SettingsProvider";

export const MediaCard: React.FC<{ media: MediaItem }> = ({ media }) => {
  const { locale } = useI18n();
  const { reducedMotion } = useSettings();

  const cardContent = (
    <div className="group flex flex-col h-full bg-card rounded-xl border border-border-custom overflow-hidden transition-all duration-240 hover:border-slate-700/60 hover:shadow-xl hover:shadow-teal-500/5">
      {/* Cover Image Container */}
      <div className="relative aspect-[2/3] w-full overflow-hidden bg-slate-950">
        <img
          src={media.cover_url || "/images/placeholder-book.svg"}
          alt={media.title}
          className={`w-full h-full object-cover transition-transform duration-380 ${
            reducedMotion ? "" : "group-hover:scale-105"
          }`}
          loading="lazy"
        />
        
        {/* Badges Overlay */}
        <div className="absolute top-2 left-2 flex flex-col gap-1.5 z-10">
          <SourceBadge type={media.media_type} />
          {media.rating && media.rating > 0 && <RatingBadge rating={media.rating} />}
        </div>
      </div>

      {/* Details */}
      <div className="flex flex-col flex-grow p-3 md:p-4">
        <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
          {media.genres[0] || ""}
        </span>
        <h4 className="font-semibold text-slate-200 group-hover:text-teal-400 transition-colors line-clamp-1 text-sm md:text-base mb-0.5">
          {media.title}
        </h4>
        <p className="text-xs text-slate-400 line-clamp-1">
          {media.creator}
        </p>
      </div>
    </div>
  );

  return (
    <Link href={`/${locale}/media/${media.media_type}/${media.id}`} className="block h-full">
      {reducedMotion ? (
        cardContent
      ) : (
        <motion.div
          whileHover={{ y: -4 }}
          transition={{ duration: 0.2 }}
          className="h-full"
        >
          {cardContent}
        </motion.div>
      )}
    </Link>
  );
};
export default MediaCard;
