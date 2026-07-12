import os
import json
import time
import requests
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
from ..base import BaseMediaManager

# Configuration du cache
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_FILE = os.path.join(BASE_DIR, "data", "cache", "movies_cache.json")

# Fallback en cas d'absence de clé API
FALLBACK_MOVIES = [
    {
        "id": "19995",
        "title": "Avatar",
        "creator": "James Cameron",
        "publisher": "20th Century Fox",
        "year": "2009",
        "rating": 7.5,
        "rating_count": 28000,
        "rating_source": "TMDB (Fallback)",
        "cover_url": "https://image.tmdb.org/t/p/w500/kyeqWiccfx4ZR47eKA0n564ysHR.jpg",
        "description": "Sur la lointaine planète de Pandora, un héros malgré lui se lance dans un voyage de rédemption et de découverte.",
        "genres": ["Action", "Aventure", "Science-Fiction"]
    },
    {
        "id": "27205",
        "title": "Inception",
        "creator": "Christopher Nolan",
        "publisher": "Warner Bros. Pictures",
        "year": "2010",
        "rating": 8.4,
        "rating_count": 33000,
        "rating_source": "TMDB (Fallback)",
        "cover_url": "https://image.tmdb.org/t/p/w500/9gk7adHYeHCwb0mFy7wUgU05UeG.jpg",
        "description": "Un voleur professionnel qui s'infiltre dans le subconscient des gens pour voler des secrets industriels.",
        "genres": ["Action", "Science-Fiction", "Thriller"]
    },
    {
        "id": "157336",
        "title": "Interstellar",
        "creator": "Christopher Nolan",
        "publisher": "Paramount Pictures",
        "year": "2014",
        "rating": 8.3,
        "rating_count": 31000,
        "rating_source": "TMDB (Fallback)",
        "cover_url": "https://image.tmdb.org/t/p/w500/gEU2QUnwZ622zU2cl5v2zq41Omc.jpg",
        "description": "Un groupe d'explorateurs voyage au-delà de cette galaxie pour savoir si l'homme peut vivre dans les étoiles.",
        "genres": ["Aventure", "Drame", "Science-Fiction"]
    },
    {
        "id": "603",
        "title": "Matrix",
        "creator": "Lana Wachowski, Lilly Wachowski",
        "publisher": "Warner Bros. Pictures",
        "year": "1999",
        "rating": 8.2,
        "rating_count": 24000,
        "rating_source": "TMDB (Fallback)",
        "cover_url": "https://image.tmdb.org/t/p/w500/f89U3wLz24ybbGv2nZk69N3n6Ue.jpg",
        "description": "Un programmeur informatique découvre que sa réalité n'est qu'une simulation virtuelle.",
        "genres": ["Action", "Science-Fiction"]
    },
    {
        "id": "438631",
        "title": "Dune",
        "creator": "Denis Villeneuve",
        "publisher": "Legendary Pictures",
        "year": "2021",
        "rating": 7.9,
        "rating_count": 9000,
        "rating_source": "TMDB (Fallback)",
        "cover_url": "https://image.tmdb.org/t/p/w500/s94ikvL9rC1z29N1361qC887qQ6.jpg",
        "description": "L'histoire de Paul Atréides, jeune homme brillant voué à un destin hors du commun sur la planète la plus dangereuse de l'univers.",
        "genres": ["Science-Fiction", "Aventure"]
    }
]

class MoviesManager(BaseMediaManager):
    def __init__(self):
        self.api_key = self._load_api_key()
        self.cache = self._load_cache()
        
    def _load_api_key(self):
        try:
            if st.secrets and "TMDB_API_KEY" in st.secrets:
                key = st.secrets["TMDB_API_KEY"]
                if key and not key.startswith("your_"):
                    return key
        except Exception:
            pass
        # Puis variable d'environnement
        key = os.environ.get("TMDB_API_KEY")
        if key and not key.startswith("your_"):
            return key
        return None

    def _load_cache(self):
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"movies": {}, "queries": {}}

    def _save_cache(self):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving movies cache: {e}")

    def _get_headers(self):
        headers = {"User-Agent": "BookLens/1.0"}
        if self.api_key and (self.api_key.startswith("ey") or len(self.api_key) > 50):
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def search(self, query: str, filters: dict = None) -> list:
        if not self.api_key:
            # Mode fallback
            results = FALLBACK_MOVIES
            if query:
                q = query.lower()
                results = [m for m in results if q in m["title"].lower() or q in m["creator"].lower()]
            if filters and "genre" in filters and filters["genre"] != "Tous":
                results = [m for m in results if filters["genre"] in m["genres"]]
            return results

        # Nettoyer la requête
        query = query.strip() if query else ""
        cache_key = f"{query}_{json.dumps(filters, sort_keys=True)}"
        
        # Vérifier le cache des requêtes
        if cache_key in self.cache["queries"]:
            cached_ids = self.cache["queries"][cache_key]
            return [self.cache["movies"][mid] for mid in cached_ids if mid in self.cache["movies"]]

        # Si pas de requête, ramener des films populaires
        url = "https://api.themoviedb.org/3/search/movie" if query else "https://api.themoviedb.org/3/movie/popular"
        params = {
            "language": "fr-FR",
            "page": 1
        }
        if self.api_key and not (self.api_key.startswith("ey") or len(self.api_key) > 50):
            params["api_key"] = self.api_key
        if query:
            params["query"] = query

        from src.monitoring import track_api_call
        try:
            with track_api_call("tmdb"):
                r = requests.get(url, params=params, headers=self._get_headers(), timeout=5)
                r.raise_for_status()
            
            data = r.json()
            results = data.get("results", [])[:20]
            
            formatted_results = []
            cached_ids = []
            for m in results:
                mid = str(m["id"])
                # Récupérer les détails complets (avec les crédits pour le réalisateur)
                details = self.get_details(mid)
                if details:
                    # Appliquer les filtres de genre
                    if filters and "genre" in filters and filters["genre"] != "Tous":
                        if filters["genre"] not in details["genres"]:
                            continue
                    formatted_results.append(details)
                    cached_ids.append(mid)
                    
            # Enregistrer la requête dans le cache
            self.cache["queries"][cache_key] = cached_ids
            self._save_cache()
            return formatted_results
            
        except Exception as e:
            print(f"Error searching movies: {e}")
            return []

    def get_details(self, media_id: str) -> dict:
        media_id = str(media_id)
        if media_id in self.cache["movies"]:
            return self.cache["movies"][media_id]

        if not self.api_key:
            # Fallback
            for m in FALLBACK_MOVIES:
                if m["id"] == media_id:
                    return m
            return {}

        url = f"https://api.themoviedb.org/3/movie/{media_id}"
        params = {
            "language": "fr-FR",
            "append_to_response": "credits"
        }
        if self.api_key and not (self.api_key.startswith("ey") or len(self.api_key) > 50):
            params["api_key"] = self.api_key
        from src.monitoring import track_api_call
        try:
            with track_api_call("tmdb"):
                r = requests.get(url, params=params, headers=self._get_headers(), timeout=5)
                r.raise_for_status()
                
            data = r.json()
            
            # Extraction du réalisateur
            director = "Réalisateur Inconnu"
            credits = data.get("credits", {})
            crew = credits.get("crew", [])
            directors = [member["name"] for member in crew if member.get("job") == "Director"]
            if directors:
                director = ", ".join(directors)
                
            # Studio
            publisher = "Studio Inconnu"
            companies = data.get("production_companies", [])
            if companies:
                publisher = companies[0]["name"]
                
            # Date de sortie -> Année
            year = "N/A"
            release_date = data.get("release_date", "")
            if release_date:
                year = release_date.split("-")[0]
                
            cover_path = data.get("poster_path")
            cover_url = f"https://image.tmdb.org/t/p/w500{cover_path}" if cover_path else ""
            
            genres = [g["name"] for g in data.get("genres", [])]
            
            details = {
                "id": media_id,
                "title": data.get("title", ""),
                "creator": director,
                "publisher": publisher,
                "year": year,
                "rating": float(data.get("vote_average", 0)),
                "rating_count": int(data.get("vote_count", 0)),
                "rating_source": "TMDB",
                "cover_url": cover_url,
                "description": data.get("overview", ""),
                "genres": genres
            }
            
            self.cache["movies"][media_id] = details
            self._save_cache()
            return details
            
        except Exception as e:
            print(f"Error getting movie details for {media_id}: {e}")
            return {}

    def get_recommendations(self, media_id: str, n: int = 5, filters: dict = None) -> list:
        media_id = str(media_id)
        if not self.api_key:
            # Fallback local simple
            source_movie = self.get_details(media_id)
            if not source_movie:
                return []
            candidates = [m for m in FALLBACK_MOVIES if m["id"] != media_id]
            # Calcul de similarité local sur les genres
            recs = []
            for m in candidates:
                common_genres = set(source_movie["genres"]).intersection(set(m["genres"]))
                score = len(common_genres) / max(1, len(set(source_movie["genres"]).union(set(m["genres"]))))
                m_copy = m.copy()
                m_copy["similarity"] = score
                recs.append(m_copy)
            recs = sorted(recs, key=lambda x: x["similarity"], reverse=True)[:n]
            return recs

        # Récupération TMDB
        url = f"https://api.themoviedb.org/3/movie/{media_id}/recommendations"
        params = {
            "language": "fr-FR",
            "page": 1
        }
        if self.api_key and not (self.api_key.startswith("ey") or len(self.api_key) > 50):
            params["api_key"] = self.api_key
        from src.monitoring import track_api_call
        try:
            with track_api_call("tmdb"):
                r = requests.get(url, params=params, headers=self._get_headers(), timeout=5)
                r.raise_for_status()
            
            data = r.json()
            raw_recs = data.get("results", [])[:15]
            
            # Fetch details for the source movie
            source_details = self.get_details(media_id)
            if not source_details:
                return []
                
            candidates = []
            for item in raw_recs:
                details = self.get_details(str(item["id"]))
                if details:
                    # Filtres optionnels
                    if filters and "genre" in filters and filters["genre"] != "Tous":
                        if filters["genre"] not in details["genres"]:
                            continue
                    candidates.append(details)
                    
            if not candidates:
                return []
                
            # Calcul hybride : TF-IDF de contenu
            source_text = source_details["title"] + " " + " ".join(source_details["genres"]) + " " + source_details["description"]
            candidate_texts = [c["title"] + " " + " ".join(c["genres"]) + " " + c["description"] for c in candidates]
            
            vectorizer = TfidfVectorizer(stop_words=None)
            tfidf = vectorizer.fit_transform([source_text] + candidate_texts)
            similarities = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
            
            # Combiner similarité de contenu et popularité/ordre API
            results = []
            for idx, candidate in enumerate(candidates):
                content_score = float(similarities[idx])
                # TMDB API donne déjà des résultats ordonnés par pertinence collaborative
                # Donc on donne un poids à l'ordre d'apparition
                collab_score = 1.0 - (idx / len(candidates))
                
                # Formule Hybride : 50% collab + 50% contenu
                hybrid_score = 0.5 * collab_score + 0.5 * content_score
                
                c_copy = candidate.copy()
                c_copy["similarity"] = hybrid_score
                results.append(c_copy)
                
            # Trier et couper à N
            results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:n]
            return results
            
        except Exception as e:
            print(f"Error getting movie recommendations: {e}")
            return []

    def get_available_genres(self) -> list:
        # Liste standard des genres cinématographiques
        return [
            "Action", "Aventure", "Animation", "Comédie", "Crime", 
            "Documentaire", "Drame", "Familial", "Fantastique", "Histoire", 
            "Horreur", "Musique", "Mystère", "Romance", "Science-Fiction", 
            "Téléfilm", "Thriller", "Guerre", "Western"
        ]
