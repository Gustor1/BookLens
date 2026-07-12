import { MediaItem } from "@/types";
import { MOCK_MEDIA } from "./media";

const FAVORITES_KEY = "medialens_favorites";

export const getFavorites = (): MediaItem[] => {
  if (typeof window === "undefined") return [];
  const stored = localStorage.getItem(FAVORITES_KEY);
  if (!stored) {
    // Default favorites for illustration
    return [MOCK_MEDIA[0], MOCK_MEDIA[4]];
  }
  try {
    const ids: string[] = JSON.parse(stored);
    return MOCK_MEDIA.filter(m => ids.includes(m.id));
  } catch (e) {
    return [];
  }
};

export const isFavorite = (id: string): boolean => {
  if (typeof window === "undefined") return false;
  const stored = localStorage.getItem(FAVORITES_KEY);
  if (!stored) return id === MOCK_MEDIA[0].id || id === MOCK_MEDIA[4].id;
  try {
    const ids: string[] = JSON.parse(stored);
    return ids.includes(id);
  } catch (e) {
    return false;
  }
};

export const toggleFavorite = (id: string): boolean => {
  if (typeof window === "undefined") return false;
  const stored = localStorage.getItem(FAVORITES_KEY);
  let ids: string[] = [];
  if (!stored) {
    ids = [MOCK_MEDIA[0].id, MOCK_MEDIA[4].id];
  } else {
    try {
      ids = JSON.parse(stored);
    } catch (e) {
      ids = [];
    }
  }

  const idx = ids.indexOf(id);
  let added = false;
  if (idx > -1) {
    ids.splice(idx, 1);
  } else {
    ids.push(id);
    added = true;
  }
  localStorage.setItem(FAVORITES_KEY, JSON.stringify(ids));
  return added;
};
