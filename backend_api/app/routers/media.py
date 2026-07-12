import os
import sys
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.schemas.media import ExploreResponse, MediaItem, MediaDetailResponse, FeedbackRequest, FeedbackResponse
from app.dependencies import get_db, get_recommender

# Add app_build to path if not present
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_BUILD_DIR = os.path.join(BASE_DIR, "app_build")
if APP_BUILD_DIR not in sys.path:
    sys.path.insert(0, APP_BUILD_DIR)

from src.media import get_media_manager

router = APIRouter(prefix="/api")

def format_book(row) -> dict:
    rc = 0
    if "Real-Rating-Count" in row and pd.notna(row["Real-Rating-Count"]):
        rc = int(row["Real-Rating-Count"])
    elif "Rating-Count" in row and pd.notna(row["Rating-Count"]):
        rc = int(row["Rating-Count"])
        
    r_val = 0.0
    if "Real-Rating" in row and pd.notna(row["Real-Rating"]):
        r_val = float(row["Real-Rating"])
    elif "Book-Rating" in row and pd.notna(row["Book-Rating"]):
        r_val = float(row["Book-Rating"])
        
    genres = []
    if "Theme" in row and pd.notna(row["Theme"]):
        genres = [str(row["Theme"])]
    else:
        genres = ["Science-Fiction"]

    return {
        "id": str(row.get("ISBN", row["Book-Title"])),
        "title": str(row["Book-Title"]),
        "creator": str(row["Book-Author"]),
        "publisher": str(row.get("Publisher", "Inconnu")),
        "year": str(row.get("Year-Of-Publication", "N/A")),
        "rating": r_val,
        "rating_count": rc,
        "rating_source": str(row.get("Rating-Source", "Google Books")),
        "cover_url": str(row.get("Image-URL-L", "/images/placeholder-book.svg")),
        "description": str(row.get("Description", "Aucune description disponible.")),
        "genres": genres,
        "media_type": "books"
    }

@router.get("/explore", response_model=ExploreResponse)
def explore_media(
    media_type: str = "all",
    query: str = "",
    genre: str = "Tous",
    limit: int = 20,
    db_tuple: tuple = Depends(get_db)
):
    df, _ = db_tuple
    results = []

    # 1. BOOKS EXPLORATION
    if media_type in ["all", "books"]:
        books_df = df.drop_duplicates(subset=["Book-Title"])
        if query:
            q = query.lower()
            books_df = books_df[
                books_df["Book-Title"].astype(str).str.lower().str.contains(q) |
                books_df["Book-Author"].astype(str).str.lower().str.contains(q)
            ]
        if genre and genre != "Tous":
            if "Theme" in books_df.columns:
                books_df = books_df[books_df["Theme"].astype(str).str.lower().str.contains(genre.lower())]
        
        for _, row in books_df.head(limit).iterrows():
            results.append(MediaItem(**format_book(row)))

    # 2. MOVIES EXPLORATION
    if media_type in ["all", "movies"]:
        try:
            movies_mgr = get_media_manager("movies")
            # Convert filter options
            filters = {"genre": genre} if genre != "Tous" else None
            movies_list = movies_mgr.search(query, filters)
            for m in movies_list[:limit]:
                # Ensure all required schemas are present
                results.append(MediaItem(
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
            print(f"Error querying movies: {e}")

    # 3. GAMES EXPLORATION
    if media_type in ["all", "games"]:
        try:
            games_mgr = get_media_manager("games")
            filters = {"genre": genre} if genre != "Tous" else None
            games_list = games_mgr.search(query, filters)
            for g in games_list[:limit]:
                results.append(MediaItem(
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
            print(f"Error querying games: {e}")

    return ExploreResponse(
        items=results[:limit],
        total=len(results),
        media_type=media_type,
        query=query,
        genre=genre
    )

@router.get("/media/{media_type}/{media_id}", response_model=MediaDetailResponse)
def get_media_detail(
    media_type: str,
    media_id: str,
    db_tuple: tuple = Depends(get_db),
    recommender=Depends(get_recommender)
):
    df, _ = db_tuple
    
    if media_type == "books":
        # Search by ISBN or Title
        books_df = df[df["ISBN"] == media_id]
        if books_df.empty:
            books_df = df[df["Book-Title"] == media_id]
        
        if books_df.empty:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book_info = format_book(books_df.iloc[0])
        media_obj = MediaItem(**book_info)
        
        # Get recommendations using BookRecommender
        similars = []
        explanation = None
        try:
            recs_df = recommender.get_recommendations(media_obj.title, n=5)
            if recs_df is not None and not recs_df.empty:
                for _, row in recs_df.iterrows():
                    # Look up in df
                    rec_rows = df[df["Book-Title"] == row["Book-Title"]]
                    if not rec_rows.empty:
                        similars.append(MediaItem(**format_book(rec_rows.iloc[0])))
                
                # Fetch first explanation
                if len(similars) > 0:
                    exp_text = recommender.explain_recommendation(media_obj.title, similars[0].title)
                    # Parse reasons from explanation markdown
                    reasons = [r.replace("-", "").strip() for r in exp_text.split("\n") if r.strip().startswith("-")]
                    explanation = {
                        "score": float(row.get("Similarity-Score", 0.7)),
                        "reasons": reasons if reasons else ["Forte similarité collaborative."],
                        "stats": {
                            "avg_rating": str(row.get("Avg-Rating", "7.0")),
                            "source": str(row.get("Rating-Source", "BookLens"))
                        }
                    }
        except Exception as e:
            print(f"Error generating recommendations: {e}")

        return MediaDetailResponse(
            media=media_obj,
            why_recommended="Recommandation de contenu IA.",
            explanation=explanation,
            similars=similars
        )

    elif media_type in ["movies", "games"]:
        try:
            mgr = get_media_manager(media_type)
            m = mgr.get_details(media_id)
            if not m:
                raise HTTPException(status_code=404, detail=f"{media_type} not found")
                
            media_obj = MediaItem(
                id=str(m["id"]),
                title=m["title"],
                creator=m.get("creator", "Inconnu"),
                publisher=m.get("publisher", "Inconnu"),
                year=str(m.get("year", "N/A")),
                rating=float(m.get("rating", 0.0)),
                rating_count=int(m.get("rating_count", 0)),
                rating_source=m.get("rating_source", media_type.upper()),
                cover_url=m.get("cover_url", f"/images/placeholder-{media_type[:-1]}.svg"),
                description=m.get("description", ""),
                genres=m.get("genres", []),
                media_type=media_type
            )
            
            # Fetch recommendations from manager
            similars = []
            try:
                recs = mgr.get_recommendations(media_id, n=5)
                for r in recs:
                    similars.append(MediaItem(
                        id=str(r["id"]),
                        title=r["title"],
                        creator=r.get("creator", "Inconnu"),
                        publisher=r.get("publisher", "Inconnu"),
                        year=str(r.get("year", "N/A")),
                        rating=float(r.get("rating", 0.0)),
                        rating_count=int(r.get("rating_count", 0)),
                        rating_source=r.get("rating_source", media_type.upper()),
                        cover_url=r.get("cover_url", f"/images/placeholder-{media_type[:-1]}.svg"),
                        description=r.get("description", ""),
                        genres=r.get("genres", []),
                        media_type=media_type
                    ))
            except Exception as ex:
                print(f"Error fetching recommendations: {ex}")
                
            return MediaDetailResponse(
                media=media_obj,
                why_recommended="Choix populaire dans la catégorie.",
                similars=similars
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    else:
        raise HTTPException(status_code=400, detail="Invalid media type")

@router.post("/profile/feedback", response_model=FeedbackResponse)
def submit_feedback(
    req: FeedbackRequest,
    recommender=Depends(get_recommender)
):
    if req.media_type == "books":
        try:
            recommender.add_feedback(req.media_id, req.feedback_type)
            recommender.save()
            return FeedbackResponse(status="success", message="Feedback appliqué au modèle hybride.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Non-critical log for movies/games
        print(f"[API Feedback] Received {req.feedback_type} for {req.media_type} {req.media_id}")
        return FeedbackResponse(status="success", message="Feedback enregistré localement (mode démo).")
