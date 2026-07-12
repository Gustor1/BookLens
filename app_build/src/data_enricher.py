"""
BookLens — Module d'enrichissement des données
Récupère des métadonnées supplémentaires depuis l'API Open Library.
Fournit un fallback local si l'API n'est pas disponible.
"""

import pandas as pd
import os
import json
import time

# Le répertoire de cache pour stocker les résultats API
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "data", "cache")


def _fetch_from_openlibrary(isbn: str) -> dict:
    """
    Récupère les métadonnées d'un livre depuis l'API Open Library.
    """
    try:
        import urllib.request
        import json as _json
        from src.monitoring import track_api_call

        # Utiliser jscmd=details pour obtenir plus d'informations (comme la description)
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=details"
        req = urllib.request.Request(url, headers={"User-Agent": "BookLens/1.0"})
        
        with track_api_call("open_library"):
            with urllib.request.urlopen(req, timeout=5) as response:
                data = _json.loads(response.read().decode())

        key = f"ISBN:{isbn}"
        if key not in data:
            return {}

        details = data[key].get("details", {})
        
        # Extraction sécurisée de la description
        desc = details.get("description", "")
        if isinstance(desc, dict):
            desc = desc.get("value", "")

        authors = details.get("authors", [])
        author_names = ", ".join(a.get("name", "") for a in authors if isinstance(a, dict))
        
        subjects = details.get("subjects", [])
        subject_names = [s for s in subjects if isinstance(s, str)][:5]

        # Utiliser l'URL thumbnail_url comme fallback ou construire la medium cover
        cover_url = data[key].get("thumbnail_url", "")
        if cover_url:
            cover_url = cover_url.replace("-S.jpg", "-M.jpg")

        result = {
            "title": details.get("title", ""),
            "authors": author_names,
            "publish_date": details.get("publish_date", ""),
            "subjects": subject_names,
            "cover_url": cover_url,
            "description": desc
        }
        return result

    except Exception as e:
        print(f"Error fetching {isbn}: {e}")
        return {}


def _fetch_from_google_books(isbn: str) -> dict:
    """
    Récupère la note moyenne et le nombre de notes depuis l'API Google Books.
    """
    try:
        import urllib.request
        import json as _json
        from src.monitoring import track_api_call

        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        req = urllib.request.Request(url, headers={"User-Agent": "BookLens/1.0"})
        
        with track_api_call("google_books"):
            with urllib.request.urlopen(req, timeout=5) as response:
                data = _json.loads(response.read().decode())
            
        if "items" not in data or len(data["items"]) == 0:
            return {}
            
        vol_info = data["items"][0].get("volumeInfo", {})
        
        # Google Books donne la note sur 5, on convertit sur 10
        avg_rating = vol_info.get("averageRating")
        if avg_rating is not None:
            avg_rating = avg_rating * 2
            
        return {
            "averageRating": avg_rating,
            "ratingsCount": vol_info.get("ratingsCount")
        }
    except Exception as e:
        print(f"Error fetching Google Books for {isbn}: {e}")
        return {}


def _load_cache() -> dict:
    """Charge le cache local des enrichissements."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, "enrichment_cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def _save_cache(cache: dict):
    """Sauvegarde le cache local."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, "enrichment_cache.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def enrich_books(df: pd.DataFrame, max_api_calls: int = 50, use_api: bool = True) -> pd.DataFrame:
    """
    Enrichit le DataFrame de livres avec des métadonnées Open Library.
    Écrase les fausses données générées si la vraie donnée est trouvée.
    """
    print("[ENRICH] Enrichissement des métadonnées des livres...")
    df = df.copy()

    cache = _load_cache()
    api_calls = 0

    if "Subjects" not in df.columns:
        df["Subjects"] = None
    if "Cover-URL" not in df.columns:
        df["Cover-URL"] = None
    if "Description" not in df.columns:
        df["Description"] = None
    if "Real-Rating" not in df.columns:
        df["Real-Rating"] = None
    if "Real-Rating-Count" not in df.columns:
        df["Real-Rating-Count"] = None
    if "Rating-Source" not in df.columns:
        df["Rating-Source"] = "Estimée"

    for idx, row in df.iterrows():
        isbn = str(row.get("ISBN", "")).strip()
        if not isbn:
            continue

        result = None
        # Vérifier le cache d'abord
        if isbn in cache:
            result = cache[isbn]
        elif use_api and api_calls < max_api_calls:
            result = _fetch_from_openlibrary(isbn)
            if result:
                # Si Open Library a marché, on essaie de choper la note Google Books
                gb_data = _fetch_from_google_books(isbn)
                if gb_data and gb_data.get("averageRating") is not None:
                    result["averageRating"] = gb_data["averageRating"]
                    result["ratingsCount"] = gb_data.get("ratingsCount")
                    result["ratingSource"] = "Google Books"
                else:
                    # Pas de note trouvée
                    pass
                cache[isbn] = result
            api_calls += 1
            time.sleep(0.3)  # Rate limiting
            
        if result:
            # Écraser les données si elles existent
            if result.get("title"):
                df.at[idx, "Book-Title"] = result["title"]
            if result.get("authors"):
                df.at[idx, "Book-Author"] = result["authors"]
            if result.get("publish_date"):
                # Extraction basique de l'année
                year = result["publish_date"][-4:]
                if year.isdigit():
                    df.at[idx, "Year-Of-Publication"] = int(year)
            if result.get("subjects"):
                df.at[idx, "Subjects"] = "; ".join(result["subjects"])
            if result.get("cover_url"):
                df.at[idx, "Cover-URL"] = result["cover_url"]
                df.at[idx, "Image-URL-M"] = result["cover_url"]
            if result.get("description"):
                df.at[idx, "Description"] = result["description"]
            
            if result.get("averageRating") is not None:
                df.at[idx, "Real-Rating"] = float(result["averageRating"])
                df.at[idx, "Real-Rating-Count"] = float(result.get("ratingsCount", 1))
                df.at[idx, "Rating-Source"] = result.get("ratingSource", "Google Books")

    _save_cache(cache)
    print(f"   -> {api_calls} appels API effectués, {len(cache)} livres en cache")
    return df
