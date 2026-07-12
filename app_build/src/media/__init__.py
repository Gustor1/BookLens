from .books.books_manager import BooksManager
from .movies.movies_manager import MoviesManager
from .games.games_manager import GamesManager

def get_media_manager(media_type: str):
    """
    Récupère le gestionnaire correspondant au type de média.
    """
    if media_type == "books":
        return BooksManager()
    elif media_type == "movies":
        return MoviesManager()
    elif media_type == "games":
        return GamesManager()
    else:
        raise ValueError(f"Type de média inconnu: {media_type}")
