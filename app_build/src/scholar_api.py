"""
BookLens — Semantic Scholar API
Module pour interagir avec l'API Semantic Scholar.
Implémente un système de cache local pour contourner les limites de requêtes (100 req / 5 min).
"""

import os
import json
import urllib.request
import urllib.parse
from urllib.error import HTTPError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "data", "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "scholar_cache.json")

def _load_cache() -> dict:
    os.makedirs(CACHE_DIR, exist_ok=True)
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}

def _save_cache(cache: dict):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def search_papers(query: str, limit: int = 5) -> list:
    """
    Recherche des articles scientifiques sur Semantic Scholar.
    Retourne une liste de dictionnaires contenant les métadonnées.
    """
    query = query.strip()
    if not query:
        return []

    cache = _load_cache()
    cache_key = f"{query.lower()}_{limit}"

    if cache_key in cache:
        return cache[cache_key]

    # Préparer la requête API
    encoded_query = urllib.parse.quote(query)
    fields = "title,authors,year,abstract,citationCount,url"
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded_query}&limit={limit}&fields={fields}"
    
    req = urllib.request.Request(url, headers={"User-Agent": "BookLens/1.0 (academic research)"})
    
    from src.monitoring import track_api_call
    try:
        with track_api_call("semantic_scholar"):
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                papers = data.get("data", [])
            
            # Formater les résultats
            results = []
            for p in papers:
                authors = ", ".join(a.get("name", "") for a in p.get("authors", []))
                results.append({
                    "title": p.get("title", "Titre inconnu"),
                    "authors": authors if authors else "Auteurs inconnus",
                    "year": p.get("year", "N/A"),
                    "abstract": p.get("abstract") or "Aucun résumé disponible.",
                    "citationCount": p.get("citationCount", 0),
                    "url": p.get("url", "#")
                })
            
            # Sauvegarder dans le cache
            cache[cache_key] = results
            _save_cache(cache)
            return results

    except HTTPError as e:
        if e.code == 429:
            print("[ScholarAPI] Rate limit dépassé (HTTP 429).")
        else:
            print(f"[ScholarAPI] Erreur HTTP: {e.code}")
        return []
    except Exception as e:
        print(f"[ScholarAPI] Erreur inattendue: {e}")
        return []
