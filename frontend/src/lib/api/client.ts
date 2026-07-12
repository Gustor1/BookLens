import { MediaItem, MediaType } from "@/types";
import { MOCK_MEDIA } from "../mock/media";
import { getMockRecommendations, getMockExplanation, getDiscoverTonight, getEcofictions, getCrossMediaPairs, getPersonalizedRecommendations } from "../mock/recommendations";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export const isDemoMode = (): boolean => {
  return !API_BASE_URL;
};

// Generic fetcher helper
async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  // Ensure we remove trailing slash from base url if present and start endpoint with slash
  const base = API_BASE_URL.endsWith("/") ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
  const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${base}${path}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  getPublicConfig: async () => {
    if (isDemoMode()) {
      return {
        status: "healthy",
        version: "2.0.0-mock",
        providers: { nvidia: false, huggingface: false }
      };
    }
    try {
      return await apiFetch<{ status: string; version: string; providers: Record<string, boolean> }>("/api/config/public");
    } catch (e) {
      console.warn("Failed to contact API config, fallback to local settings.", e);
      return {
        status: "healthy",
        version: "2.0.0-fallback",
        providers: { nvidia: false, huggingface: false }
      };
    }
  },

  explore: async (
    mediaType: string = "all",
    query: string = "",
    genre: string = "Tous",
    limit: number = 20
  ): Promise<MediaItem[]> => {
    if (isDemoMode()) {
      let list = [...MOCK_MEDIA];
      if (mediaType !== "all") {
        list = list.filter(m => m.media_type === mediaType);
      }
      if (query) {
        const q = query.toLowerCase();
        list = list.filter(m => m.title.toLowerCase().includes(q) || m.creator.toLowerCase().includes(q));
      }
      if (genre && genre !== "Tous" && genre !== "All") {
        list = list.filter(m => m.genres.includes(genre));
      }
      return list.slice(0, limit);
    }
    
    try {
      const queryParams = new URLSearchParams({
        media_type: mediaType,
        query,
        genre,
        limit: String(limit)
      });
      const res = await apiFetch<{ items: MediaItem[] }>(`/api/explore?${queryParams.toString()}`);
      return res.items;
    } catch (e) {
      console.error("Explore API failed, fallback to mock.", e);
      // Fallback
      return api.explore("all", query, genre, limit);
    }
  },

  getMediaDetail: async (type: string, id: string): Promise<{
    media: MediaItem;
    why_recommended?: string;
    explanation?: any;
    similars: MediaItem[];
  }> => {
    if (isDemoMode() || id.startsWith("book-") || id.startsWith("movie-") || id.startsWith("game-")) {
      const media = MOCK_MEDIA.find(m => m.id === id);
      if (!media) throw new Error("Media not found in mock database");
      
      const similars = getMockRecommendations(id, 5);
      const explanation = similars.length > 0 ? getMockExplanation(id, similars[0].id) : undefined;
      
      return {
        media,
        why_recommended: media.id === MOCK_MEDIA[0].id ? "Chef-d'œuvre incontournable de la SF anthropologique." : "Œuvre culte et thématiques profondes.",
        explanation,
        similars
      };
    }
    
    return apiFetch(`/api/media/${type}/${id}`);
  },

  getRecommendations: async (mediaType: string = "all", limit: number = 6): Promise<Record<string, MediaItem[]>> => {
    if (isDemoMode()) {
      return {
        discover: getDiscoverTonight().slice(0, limit),
        ecofiction: getEcofictions().slice(0, limit),
        crossmedia: getCrossMediaPairs().slice(0, limit),
        personalized: getPersonalizedRecommendations().slice(0, limit)
      };
    }
    
    try {
      const queryParams = new URLSearchParams({
        media_type: mediaType,
        limit: String(limit)
      });
      return await apiFetch<Record<string, MediaItem[]>>(`/api/recommendations?${queryParams.toString()}`);
    } catch (e) {
      console.error("Recommendations API failed, fallback to mock.", e);
      const res = {
        discover: getDiscoverTonight().slice(0, limit),
        ecofiction: getEcofictions().slice(0, limit),
        crossmedia: getCrossMediaPairs().slice(0, limit),
        personalized: getPersonalizedRecommendations().slice(0, limit)
      };
      return res;
    }
  },

  submitFeedback: async (mediaId: string, mediaType: string, feedbackType: "like" | "dislike"): Promise<{ status: string }> => {
    if (isDemoMode()) {
      console.log(`Mock Feedback: ${feedbackType} on ${mediaType} ${mediaId}`);
      return { status: "success" };
    }
    try {
      return await apiFetch("/api/profile/feedback", {
        method: "POST",
        body: JSON.stringify({ media_id: mediaId, media_type: mediaType, feedback_type: feedbackType })
      });
    } catch (e) {
      console.error("Feedback submission failed.", e);
      return { status: "error" };
    }
  },

  chatWithAssistant: async (
    question: string,
    chatHistory: { role: string; content: string }[],
    lang: string = "fr",
    provider: string = "nvidia"
  ): Promise<{ response: string; type: string; image_bytes_b64?: string }> => {
    if (isDemoMode()) {
      // Simulate answer after 800ms
      await new Promise(r => setTimeout(r, 800));
      
      const q = question.toLowerCase();
      if (q.includes("dune")) {
        return {
          response: "🤖 **[Mode Démo]** *Dune* de Frank Herbert est le pivot d'une structure trans-média fascinante. Dans le roman de 1965, l'écologie aride d'Arrakis pose les bases de l'écofiction moderne. Au cinéma, Denis Villeneuve traduit visuellement cette immensité désertique en insistant sur la fragilité de l'eau. Dans l'univers vidéoludique (*Dune: Spice Wars*), l'aspect géopolitique et la lutte territoriale pour la ressource (l'Épice) forcent le joueur à gérer la survie en milieu hostile, bouclant ainsi l'exploration interactive de cet écosystème.",
          type: "text"
        };
      } else if (q.includes("le guin") || q.includes("écofémin") || q.includes("butler")) {
        return {
          response: "🤖 **[Mode Démo]** L'écoféminisme en science-fiction déconstruit la dualité traditionnelle homme/nature et technologie/corps. Dans *La Main gauche de la nuit*, Ursula K. Le Guin explore une humanité androgyne qui élimine le genre comme vecteur de pouvoir. Son essai critique *Le Récit-Panier* propose d'aborder l'histoire non pas par la violence héroïque (la lance) mais par le soin et l'inclusivité (le panier réceptacle). Octavia Butler, dans *La Parabole du semeur*, montre comment l'hyperempathie et la création de communautés d'entraide deviennent des outils de survie face à l'effondrement climatique.",
          type: "text"
        };
      } else if (q.includes("inception") || q.includes("nolan")) {
        return {
          response: "🤖 **[Mode Démo]** *Inception* de Christopher Nolan se caractérise par une narration asymétrique et une architecture onirique imbriquée. Si vous cherchez des thèmes similaires :\n- En Littérature : *La Cité des permutants* de Greg Egan explore la conscience simulée et les réalités subjectives démultipliées.\n- En Jeu Vidéo : *Detroit: Become Human* ou *Disco Elysium* questionnent la perception de soi, la psyché fragmentée et la reconstruction de la mémoire à travers des choix arborescents.",
          type: "text"
        };
      } else {
        return {
          response: "🤖 **[Mode Démo]** Bonjour ! Je suis l'assistant culturel de MediaLens, tournant actuellement sur un modèle linguistique simulé en local.\n\nN'hésitez pas à m'interroger sur :\n- Les ponts thématiques entre livres, films et jeux vidéo de notre catalogue.\n- Le corpus écoféministe et les romans d'Ursula K. Le Guin ou d'Octavia Butler.\n- Vos recommandations ou la théorie du Récit-Panier.",
          type: "text"
        };
      }
    }

    try {
      return await apiFetch<{ response: string; type: string; image_bytes_b64?: string }>("/api/assistant/chat", {
        method: "POST",
        body: JSON.stringify({ question, chat_history: chatHistory, lang, provider })
      });
    } catch (e) {
      console.error("Assistant API call failed, falling back to mock reply.", e);
      // fallback
      const API_BASE_URL_backup = process.env.NEXT_PUBLIC_API_BASE_URL;
      (process.env as any).NEXT_PUBLIC_API_BASE_URL = "";
      const reply = await api.chatWithAssistant(question, chatHistory, lang, provider);
      (process.env as any).NEXT_PUBLIC_API_BASE_URL = API_BASE_URL_backup;
      return reply;
    }
  }
};
