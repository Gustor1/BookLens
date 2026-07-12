import os
import json
import time
import requests
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
from ..base import BaseMediaManager

# Configuration du cache
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_FILE = os.path.join(BASE_DIR, "data", "cache", "games_cache.json")

# Fallback en cas d'absence de clé API
FALLBACK_GAMES = [
    {
        "id": "3328",
        "title": "The Witcher 3: Wild Hunt",
        "creator": "CD PROJEKT RED",
        "publisher": "CD PROJEKT",
        "year": "2015",
        "rating": 9.3,
        "rating_count": 6000,
        "rating_source": "RAWG (Fallback)",
        "cover_url": "https://media.rawg.io/media/games/618/618c2031a07bbff6b4e611f10db53982.jpg",
        "description": "Un jeu de rôle de fantasy en monde ouvert centré sur une histoire forte, qui se déroule dans un univers graphique époustouflant.",
        "genres": ["Action", "Jeu de rôle"],
        "platforms": ["PC", "PlayStation 4", "Xbox One"]
    },
    {
        "id": "3498",
        "title": "Grand Theft Auto V",
        "creator": "Rockstar North",
        "publisher": "Rockstar Games",
        "year": "2013",
        "rating": 9.0,
        "rating_count": 8000,
        "rating_source": "RAWG (Fallback)",
        "cover_url": "https://media.rawg.io/media/games/20a/20a5741b2c6e3d0300624098b836097e.jpg",
        "description": "Trois criminels très différents associent leurs efforts pour réaliser une série de braquages audacieux.",
        "genres": ["Action", "Aventure"],
        "platforms": ["PC", "PlayStation 4", "Xbox One", "PlayStation 5", "Xbox Series X/S"]
    },
    {
        "id": "4200",
        "title": "Portal 2",
        "creator": "Valve Software",
        "publisher": "Valve",
        "year": "2011",
        "rating": 9.6,
        "rating_count": 5500,
        "rating_source": "RAWG (Fallback)",
        "cover_url": "https://media.rawg.io/media/games/328/328361590d5405db3177cd02d18937a1.jpg",
        "description": "Portal 2 s'appuie sur la formule primée d'un gameplay, d'une histoire et d'une musique innovants.",
        "genres": ["Réflexion", "Action"],
        "platforms": ["PC", "PlayStation 3", "Xbox 360"]
    },
    {
        "id": "22511",
        "title": "The Legend of Zelda: Breath of the Wild",
        "creator": "Nintendo",
        "publisher": "Nintendo",
        "year": "2017",
        "rating": 9.4,
        "rating_count": 4000,
        "rating_source": "RAWG (Fallback)",
        "cover_url": "https://media.rawg.io/media/games/cc4/cc41902f2c3775908aaee37afaf920a2.jpg",
        "description": "Oubliez tout ce que vous savez sur les jeux The Legend of Zelda et plongez dans un monde d'exploration.",
        "genres": ["Action", "Aventure"],
        "platforms": ["Nintendo Switch", "Wii U"]
    },
    {
        "id": "643443",
        "title": "Elden Ring",
        "creator": "FromSoftware",
        "publisher": "Bandai Namco Entertainment",
        "year": "2022",
        "rating": 9.3,
        "rating_count": 3000,
        "rating_source": "RAWG (Fallback)",
        "cover_url": "https://media.rawg.io/media/games/5ec/5ec183d772d5d9757659ac457e7bb22e.jpg",
        "description": "Levez-vous, Sans-éclat, et laissez la grâce guider vos pas pour brandir la puissance du Cercle d'Elden.",
        "genres": ["Action", "Jeu de rôle"],
        "platforms": ["PC", "PlayStation 5", "Xbox Series X/S", "PlayStation 4", "Xbox One"]
    }
]

class GamesManager(BaseMediaManager):
    def __init__(self):
        self.api_key = self._load_api_key()
        self.cache = self._load_cache()
        
    def _load_api_key(self):
        try:
            if st.secrets and "RAWG_API_KEY" in st.secrets:
                key = st.secrets["RAWG_API_KEY"]
                if key and not key.startswith("your_"):
                    return key
        except Exception:
            pass
        # Puis variable d'environnement
        key = os.environ.get("RAWG_API_KEY")
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
        return {"games": {}, "queries": {}}

    def _save_cache(self):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving games cache: {e}")

    def _get_headers(self):
        return {"User-Agent": "BookLens/1.0"}

    def _clean_html(self, raw_html):
        cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]+|#x[0-9a-f]+);')
        return re.sub(cleanr, '', raw_html) if raw_html else ""

    def search(self, query: str, filters: dict = None) -> list:
        if not self.api_key:
            # Mode fallback
            results = FALLBACK_GAMES
            if query:
                q = query.lower()
                results = [g for g in results if q in g["title"].lower() or q in g["creator"].lower()]
            if filters and "genre" in filters and filters["genre"] != "Tous":
                results = [g for g in results if filters["genre"] in g["genres"]]
            return results

        query = query.strip() if query else ""
        cache_key = f"{query}_{json.dumps(filters, sort_keys=True)}"
        
        # Cache check
        if cache_key in self.cache["queries"]:
            cached_ids = self.cache["queries"][cache_key]
            return [self.cache["games"][gid] for gid in cached_ids if gid in self.cache["games"]]

        url = "https://api.rawg.io/api/games"
        params = {
            "key": self.api_key,
            "page_size": 20
        }
        if query:
            params["search"] = query
        else:
            # Populaire par défaut
            params["ordering"] = "-rating"

        from src.monitoring import track_api_call
        try:
            with track_api_call("rawg"):
                r = requests.get(url, params=params, headers=self._get_headers(), timeout=5)
                r.raise_for_status()
                
            data = r.json()
            results = data.get("results", [])
            
            formatted_results = []
            cached_ids = []
            for g in results:
                gid = str(g["id"])
                details = self.get_details(gid)
                if details:
                    # Filtres de genre
                    if filters and "genre" in filters and filters["genre"] != "Tous":
                        if filters["genre"] not in details["genres"]:
                            continue
                    formatted_results.append(details)
                    cached_ids.append(gid)
                    
            self.cache["queries"][cache_key] = cached_ids
            self._save_cache()
            return formatted_results
            
        except Exception as e:
            print(f"Error searching games: {e}")
            return []

    def get_details(self, media_id: str) -> dict:
        media_id = str(media_id)
        if media_id in self.cache["games"]:
            return self.cache["games"][media_id]

        if not self.api_key:
            # Fallback
            for g in FALLBACK_GAMES:
                if g["id"] == media_id:
                    return g
            return {}

        url = f"https://api.rawg.io/api/games/{media_id}"
        params = {"key": self.api_key}
        from src.monitoring import track_api_call
        try:
            with track_api_call("rawg"):
                r = requests.get(url, params=params, headers=self._get_headers(), timeout=5)
                r.raise_for_status()
                
            data = r.json()
            
            # Dev & Publisher
            dev_name = "Développeur Inconnu"
            pub_name = "Éditeur Inconnu"
            
            devs = data.get("developers", [])
            if devs:
                dev_name = devs[0]["name"]
                
            pubs = data.get("publishers", [])
            if pubs:
                pub_name = pubs[0]["name"]
                
            # Date -> Année
            year = "N/A"
            released = data.get("released", "")
            if released:
                year = released.split("-")[0]
                
            # RAWG Note est sur 5. On multiplie par 2 pour mettre sur 10.
            rating = float(data.get("rating", 0)) * 2
            
            cover_url = data.get("background_image", "")
            genres = [g["name"] for g in data.get("genres", [])]
            platforms = [p["platform"]["name"] for p in data.get("platforms", [])]
            
            desc = self._clean_html(data.get("description", ""))
            
            details = {
                "id": media_id,
                "title": data.get("name", ""),
                "creator": dev_name,
                "publisher": pub_name,
                "year": year,
                "rating": round(rating, 1),
                "rating_count": int(data.get("ratings_count", 0)),
                "rating_source": "RAWG",
                "cover_url": cover_url,
                "description": desc,
                "genres": genres,
                "platforms": platforms
            }
            
            self.cache["games"][media_id] = details
            self._save_cache()
            return details
            
        except Exception as e:
            print(f"Error getting game details: {e}")
            return {}

    def get_recommendations(self, media_id: str, n: int = 5, filters: dict = None) -> list:
        media_id = str(media_id)
        if not self.api_key:
            # Fallback local simple
            source_game = self.get_details(media_id)
            if not source_game:
                return []
            candidates = [g for g in FALLBACK_GAMES if g["id"] != media_id]
            recs = []
            for g in candidates:
                common_genres = set(source_game["genres"]).intersection(set(g["genres"]))
                score = len(common_genres) / max(1, len(set(source_game["genres"]).union(set(g["genres"]))))
                g_copy = g.copy()
                g_copy["similarity"] = score
                recs.append(g_copy)
            recs = sorted(recs, key=lambda x: x["similarity"], reverse=True)[:n]
            return recs

        # Suggestions endpoint de RAWG
        url = f"https://api.rawg.io/api/games/{media_id}/suggested"
        params = {"key": self.api_key}
        from src.monitoring import track_api_call
        try:
            try:
                with track_api_call("rawg"):
                    r = requests.get(url, params=params, headers=self._get_headers(), timeout=5)
                    r.raise_for_status()
            except Exception:
                print(f"Suggested endpoint failed for {media_id}, trying game-series")
                url_series = f"https://api.rawg.io/api/games/{media_id}/game-series"
                with track_api_call("rawg"):
                    r = requests.get(url_series, params=params, headers=self._get_headers(), timeout=5)
                    r.raise_for_status()
            
            data = r.json()
            raw_recs = data.get("results", [])[:15]
            
            source_details = self.get_details(media_id)
            if not source_details:
                return []
                
            candidates = []
            for item in raw_recs:
                details = self.get_details(str(item["id"]))
                if details:
                    if filters and "genre" in filters and filters["genre"] != "Tous":
                        if filters["genre"] not in details["genres"]:
                            continue
                    candidates.append(details)
                    
            if not candidates:
                return []
                
            # Calcul hybride : TF-IDF
            source_text = source_details["title"] + " " + " ".join(source_details["genres"]) + " " + source_details["description"]
            candidate_texts = [c["title"] + " " + " ".join(c["genres"]) + " " + c["description"] for c in candidates]
            
            vectorizer = TfidfVectorizer(stop_words=None)
            tfidf = vectorizer.fit_transform([source_text] + candidate_texts)
            similarities = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
            
            results = []
            for idx, candidate in enumerate(candidates):
                content_score = float(similarities[idx])
                collab_score = 1.0 - (idx / len(candidates))
                
                hybrid_score = 0.5 * collab_score + 0.5 * content_score
                
                c_copy = candidate.copy()
                c_copy["similarity"] = hybrid_score
                results.append(c_copy)
                
            results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:n]
            return results
            
        except Exception as e:
            print(f"Error getting game recommendations: {e}")
            return []

    def get_available_genres(self) -> list:
        # Genres principaux de jeux vidéo
        return [
            "Action", "Aventure", "Jeu de rôle", "Stratégie", "Tir",
            "Réflexion", "Simulation", "Sports", "Course", "Combat",
            "Plateforme", "Indépendant", "Famille", "Arcade", "Educatif"
        ]
