import { MediaItem } from "@/types";
import { MOCK_MEDIA, MOCK_BOOKS, MOCK_MOVIES, MOCK_GAMES } from "./media";

// Get Featured media (e.g. La Main gauche de la nuit)
export const getFeaturedMedia = (): MediaItem => {
  return MOCK_BOOKS[0]; // La Main gauche de la nuit
};

// Surprise Me helper
export const getRandomMedia = (): MediaItem => {
  const index = Math.floor(Math.random() * MOCK_MEDIA.length);
  return MOCK_MEDIA[index];
};

// Curated lists for Home page
export const getDiscoverTonight = (): MediaItem[] => {
  // Let's mix books, movies, games
  return [
    MOCK_BOOKS[0], // La Main gauche de la nuit
    MOCK_MOVIES[1], // Inception
    MOCK_GAMES[3], // Outer Wilds
    MOCK_BOOKS[4], // Dune book
    MOCK_MOVIES[5], // Nausicaa
  ];
};

export const getEcofictions = (): MediaItem[] => {
  return MOCK_MEDIA.filter(m => m.genres.includes("Écofiction"));
};

export const getCrossMediaPairs = (): MediaItem[] => {
  // Items that have cross-media linkages (e.g. Dune book, Dune movie, Horizon, Avatar)
  return [
    MOCK_BOOKS[4], // Dune book
    MOCK_MOVIES[4], // Dune movie
    MOCK_BOOKS[0], // Left Hand of Darkness
    MOCK_MOVIES[0], // Avatar
    MOCK_GAMES[0], // Horizon Zero Dawn
  ];
};

export const getPersonalizedRecommendations = (): MediaItem[] => {
  return [
    MOCK_BOOKS[2], // Parable of the Sower
    MOCK_MOVIES[2], // Interstellar
    MOCK_GAMES[4], // Disco Elysium
    MOCK_BOOKS[7], // Handmaid's tale
    MOCK_GAMES[7], // Frostpunk
  ];
};

// Detailed similarity lookup (mocked explanations)
export const getMockRecommendations = (mediaId: string, limit: number = 5): MediaItem[] => {
  const source = MOCK_MEDIA.find(m => m.id === mediaId);
  if (!source) return [];

  // Filter out the source itself
  let candidates = MOCK_MEDIA.filter(m => m.id !== mediaId);
  
  // Rank candidates by number of matching genres
  return candidates
    .map(c => {
      const commonGenres = c.genres.filter(g => source.genres.includes(g));
      const score = commonGenres.length / Math.max(1, new Set([...source.genres, ...c.genres]).size);
      return { item: c, score };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(c => c.item);
};

export const getMockExplanation = (sourceId: string, targetId: string) => {
  const source = MOCK_MEDIA.find(m => m.id === sourceId);
  const target = MOCK_MEDIA.find(m => m.id === targetId);
  
  if (!source || !target) {
    return {
      score: 0.0,
      reasons: ["Média source ou cible introuvable."],
      stats: {}
    };
  }

  const common = source.genres.filter(g => target.genres.includes(g));
  const reasons = [];
  
  if (source.creator === target.creator) {
    reasons.push(`Même créateur / réalisateur : ${source.creator}`);
  }
  
  if (common.length > 0) {
    reasons.push(`Partage des thèmes et genres : ${common.join(", ")}`);
  }
  
  if (source.media_type !== target.media_type) {
    reasons.push(`Liaison trans-média : Adaptation ou thématiques complémentaires entre ${source.media_type} et ${target.media_type}`);
  } else {
    reasons.push(`Recommandation intra-médias : Même format et esthétique narrative.`);
  }

  // Calculate mock score
  const baseScore = source.creator === target.creator ? 0.4 : 0.1;
  const genreScore = common.length * 0.15;
  const score = Math.min(0.98, baseScore + genreScore + 0.2); // baseline

  return {
    score: parseFloat(score.toFixed(4)),
    reasons,
    stats: {
      "Genre Match": `${common.length} genres communs`,
      "Collab Match": "84% d'utilisateurs similaires",
      "Content Similarity": `${(score * 100).toFixed(0)}%`
    }
  };
};
