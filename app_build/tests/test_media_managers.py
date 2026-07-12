import pytest
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.media import get_media_manager
from src.media.books.books_manager import BooksManager
from src.media.movies.movies_manager import MoviesManager
from src.media.games.games_manager import GamesManager

def test_get_media_manager():
    """Vérifie que l'initialisation des managers retourne le bon type."""
    assert isinstance(get_media_manager("books"), BooksManager)
    assert isinstance(get_media_manager("movies"), MoviesManager)
    assert isinstance(get_media_manager("games"), GamesManager)
    
    with pytest.raises(ValueError):
        get_media_manager("invalid")

def test_movies_manager_fallback():
    """Vérifie le fonctionnement du MoviesManager en mode fallback sans clé API."""
    mgr = MoviesManager()
    mgr.api_key = None  # Force le mode fallback
    
    results = mgr.search("Avatar")
    assert len(results) > 0
    assert results[0]["title"] == "Avatar"
    assert results[0]["rating_source"] == "TMDB (Fallback)"
    
    details = mgr.get_details("27205")
    assert details["title"] == "Inception"
    
    recs = mgr.get_recommendations("19995", n=2)
    assert len(recs) == 2
    assert "similarity" in recs[0]

def test_games_manager_fallback():
    """Vérifie le fonctionnement du GamesManager en mode fallback sans clé API."""
    mgr = GamesManager()
    mgr.api_key = None  # Force le mode fallback
    
    results = mgr.search("Witcher")
    assert len(results) > 0
    assert "The Witcher" in results[0]["title"]
    assert results[0]["rating_source"] == "RAWG (Fallback)"
    
    details = mgr.get_details("4200")
    assert details["title"] == "Portal 2"
    
    recs = mgr.get_recommendations("3328", n=2)
    assert len(recs) == 2
    assert "similarity" in recs[0]

def test_books_manager():
    """Vérifie le fonctionnement du BooksManager."""
    df = pd.DataFrame({
        "Book-Title": ["Dune", "1984"],
        "Book-Author": ["Frank Herbert", "George Orwell"],
        "ISBN": ["1", "2"],
        "Year-Of-Publication": [1965, 1949],
        "Theme": ["Science-Fiction", "Science-Fiction"],
        "Book-Rating": [9.0, 8.5],
        "Real-Rating": [9.2, 8.7],
        "Real-Rating-Count": [100, 200],
        "Rating-Source": ["Google Books", "Google Books"]
    })
    mgr = BooksManager(df=df)
    
    results = mgr.search("Dune")
    assert len(results) == 1
    assert results[0]["title"] == "Dune"
    assert results[0]["rating_source"] == "Google Books"
    
    book_list = mgr.get_book_list()
    assert len(book_list) == 2
    assert "1984" in book_list
