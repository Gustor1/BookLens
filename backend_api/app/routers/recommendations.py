import os
import sys
import pandas as pd
from fastapi import APIRouter, Depends
from typing import Dict, List
from app.schemas.media import MediaItem
from app.dependencies import get_db, get_recommender
from app.routers.media import format_book

# Add app_build to path if not present
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_BUILD_DIR = os.path.join(BASE_DIR, "app_build")
if APP_BUILD_DIR not in sys.path:
    sys.path.insert(0, APP_BUILD_DIR)

router = APIRouter(prefix="/api")

@router.get("/recommendations", response_model=Dict[str, List[MediaItem]])
def get_recommendations(
    media_type: str = "all",
    limit: int = 6,
    db_tuple: tuple = Depends(get_db)
):
    df, _ = db_tuple
    
    # 1. Load books
    books_df = df.drop_duplicates(subset=["Book-Title"])
    books = [MediaItem(**format_book(row)) for _, row in books_df.iterrows()]
    
    # 2. Load movies
    movies = []
    try:
        from src.media import get_media_manager
        movies_mgr = get_media_manager("movies")
        # Search empty query will fetch popular movies
        raw_movies = movies_mgr.search("")
        for m in raw_movies:
            movies.append(MediaItem(
                id=str(m["id"]),
                title=m["title"],
                creator=m.get("creator", "Inconnu"),
                publisher=m.get("publisher", "Inconnu"),
                year=str(m.get("year", "N/A")),
                rating=float(m.get("rating", 0.0)),
                rating_count=int(m.get("rating_count", 0)),
                rating_source=m.get("rating_source", "TMDB"),
                cover_url=m.get("cover_url", "/images/placeholder-movie.svg"),
                description=m.get("description", ""),
                genres=m.get("genres", []),
                media_type="movies"
            ))
    except Exception as e:
        print(f"Error loading movies for recs: {e}")
        
    # 3. Load games
    games = []
    try:
        games_mgr = get_media_manager("games")
        raw_games = games_mgr.search("")
        for g in raw_games:
            games.append(MediaItem(
                id=str(g["id"]),
                title=g["title"],
                creator=g.get("creator", "Inconnu"),
                publisher=g.get("publisher", "Inconnu"),
                year=str(g.get("year", "N/A")),
                rating=float(g.get("rating", 0.0)),
                rating_count=int(g.get("rating_count", 0)),
                rating_source=g.get("rating_source", "RAWG"),
                cover_url=g.get("cover_url", "/images/placeholder-game.svg"),
                description=g.get("description", ""),
                genres=g.get("genres", []),
                media_type="games"
            ))
    except Exception as e:
        print(f"Error loading games for recs: {e}")

    # Combine lists
    all_media = books + movies + games
    
    # Discover tonight: mix with high rating
    discover = [m for m in all_media if (m.rating or 0.0) >= 7.8]
    if not discover:
        discover = all_media[:limit]
    else:
        discover = discover[:limit]
        
    # Ecofictions: contain écofiction/dystopie/féminisme
    ecofiction = [m for m in all_media if any(g.lower() in ["écofiction", "ecofiction", "dystopie", "dystopia", "feminism", "féminisme"] for g in m.genres)]
    if not ecofiction:
        ecofiction = all_media[3:3+limit]
    else:
        ecofiction = ecofiction[:limit]
    
    # Cross media pairs: items containing similar words in title (e.g. Dune, Inception, Blade Runner)
    crossmedia = [m for m in all_media if any(keyword in m.title.lower() for keyword in ["dune", "avatar", "blade runner", "inception", "cyberpunk"])]
    if not crossmedia:
        crossmedia = all_media[6:6+limit]
    else:
        crossmedia = crossmedia[:limit]
    
    # Personalized: top rated or defaults
    personalized = sorted(all_media, key=lambda x: x.rating or 0.0, reverse=True)
    personalized = personalized[:limit]
    
    return {
        "discover": discover,
        "ecofiction": ecofiction,
        "crossmedia": crossmedia,
        "personalized": personalized
    }
