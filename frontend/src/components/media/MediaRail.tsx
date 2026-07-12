"use client";

import React, { useRef } from "react";
import { MediaItem } from "@/types";
import { MediaCard } from "./MediaCard";
import { ChevronLeft, ChevronRight } from "lucide-react";

export const MediaRail: React.FC<{ title: string; items: MediaItem[] }> = ({ title, items }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  const handleScroll = (direction: "left" | "right") => {
    if (scrollRef.current) {
      const { scrollLeft, clientWidth } = scrollRef.current;
      const offset = clientWidth * 0.75;
      scrollRef.current.scrollTo({
        left: direction === "left" ? scrollLeft - offset : scrollLeft + offset,
        behavior: "smooth"
      });
    }
  };

  if (!items || items.length === 0) return null;

  return (
    <div className="flex flex-col mb-8 md:mb-12">
      {/* Header with scroll buttons */}
      <div className="flex justify-between items-end mb-4 px-1">
        <h3 className="text-lg md:text-xl font-bold font-serif text-slate-100 tracking-wide">
          {title}
        </h3>
        <div className="flex gap-2">
          <button
            onClick={() => handleScroll("left")}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white active:scale-95 transition-all"
            aria-label="Scroll left"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleScroll("right")}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white active:scale-95 transition-all"
            aria-label="Scroll right"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Scrollable Container */}
      <div
        ref={scrollRef}
        className="flex gap-4 md:gap-6 overflow-x-auto pb-4 no-scrollbar scroll-smooth snap-x snap-mandatory"
      >
        {items.map(media => (
          <div key={media.id} className="w-[160px] md:w-[220px] shrink-0 snap-start">
            <MediaCard media={media} />
          </div>
        ))}
      </div>
    </div>
  );
};
export default MediaRail;
