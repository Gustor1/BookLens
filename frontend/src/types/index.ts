export type MediaType = "books" | "movies" | "games";

export interface MediaItem {
  id: string;
  title: string;
  creator: string;
  publisher?: string;
  year?: string;
  rating?: number;
  rating_count?: number;
  rating_source?: string;
  cover_url?: string;
  description?: string;
  genres: string[];
  media_type: MediaType;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  type?: "text" | "image";
  image_bytes_b64?: string;
  timestamp: string;
  sources?: string[];
}
