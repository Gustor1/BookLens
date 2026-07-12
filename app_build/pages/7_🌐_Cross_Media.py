import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from src.ui import inject_custom_css, render_media_card, render_source_media
from src.media import get_media_manager
from src.i18n import t

st.set_page_config(page_title=t("cross_media.page_title", "Cross-Media — BookLens"), page_icon="🌐", layout="wide")
inject_custom_css()

st.markdown(f"# {t('cross_media.hero_title', '🌐 Recommandations Croisées')}")
st.markdown(f"<p style='color: #94A3B8; margin-bottom: 2rem;'>{t('cross_media.hero_subtitle', 'À partir d\'un livre de votre choix, BookLens vous suggère des films et jeux vidéo.')}</p>", unsafe_allow_html=True)

# Initialiser les managers
books_mgr = get_media_manager("books")
movies_mgr = get_media_manager("movies")
games_mgr = get_media_manager("games")

# Liste de livres
book_list = books_mgr.get_book_list()

if not book_list:
    st.warning("⚠️ Veuillez d'abord charger les données sur la page d'accueil.")
    st.stop()

selected_book_title = st.selectbox(
    t("cross_media.select_book", "📖 Sélectionnez un livre source"),
    options=book_list,
    key="cross_book_select"
)

st.markdown("---")

if selected_book_title:
    df = st.session_state["merged_df"]
    book_row = df[df["Book-Title"] == selected_book_title]
    if not book_row.empty:
        row = book_row.iloc[0]
        isbn = row["ISBN"]
        book_details = books_mgr.get_details(isbn)
        
        render_source_media(
            title=book_details["title"],
            creator=book_details["creator"],
            rating=book_details["rating"],
            n_ratings=book_details["rating_count"],
            rating_source=book_details["rating_source"],
            media_type="books"
        )
        
        theme = book_details["genres"][0] if book_details["genres"] else "Science-Fiction"
        st.markdown(f"#### {t('cross_media.searching_match', '🔍 Recherche de correspondances pour le thème :')} **{theme}**")
        
        THEME_MAPPING = {
            "science-fiction": {"movies": "Science-Fiction", "games": "Action"},
            "fantasy": {"movies": "Fantastique", "games": "Jeu de rôle"},
            "aventure": {"movies": "Aventure", "games": "Aventure"},
            "adventure": {"movies": "Aventure", "games": "Aventure"},
            "drame": {"movies": "Drame", "games": "Jeu de rôle"},
            "drama": {"movies": "Drame", "games": "Jeu de rôle"},
            "thriller": {"movies": "Thriller", "games": "Tir"},
            "dystopie": {"movies": "Science-Fiction", "games": "Action"},
            "survival": {"movies": "Science-Fiction", "games": "Action"},
        }
        
        theme_lower = theme.lower()
        movie_genre = THEME_MAPPING.get(theme_lower, {}).get("movies", "Science-Fiction")
        game_genre = THEME_MAPPING.get(theme_lower, {}).get("games", "Action")
        
        col_movie, col_game = st.columns(2)
        
        with col_movie:
            st.markdown(f"### {t('cross_media.suggested_movie', '🎬 Film Suggéré')}")
            movies = movies_mgr.search("", filters={"genre": movie_genre})
            if not movies and movies_mgr.api_key:
                movies = movies_mgr.search(theme)
            if not movies:
                movies = movies_mgr.search("")
                
            if movies:
                movie = movies[0]
                render_media_card(
                    title=movie["title"],
                    creator=movie["creator"],
                    publisher=movie["publisher"],
                    year=movie["year"],
                    rating=movie["rating"],
                    n_ratings=movie["rating_count"],
                    rating_source=movie["rating_source"],
                    cover_url=movie["cover_url"],
                    media_type="movies"
                )
                if movie.get("description"):
                    st.markdown(f'<p style="color:#94A3B8; font-style:italic; font-size:0.85rem;">"{movie["description"][:200]}..."</p>', unsafe_allow_html=True)
            else:
                st.info("Aucun film suggéré disponible.")
                
        with col_game:
            st.markdown(f"### {t('cross_media.suggested_game', '🎮 Jeu Vidéo Suggéré')}")
            games = games_mgr.search("", filters={"genre": game_genre})
            if not games and games_mgr.api_key:
                games = games_mgr.search(theme)
            if not games:
                games = games_mgr.search("")
                
            if games:
                game = games[0]
                render_media_card(
                    title=game["title"],
                    creator=game["creator"],
                    publisher=game["publisher"],
                    year=game["year"],
                    rating=game["rating"],
                    n_ratings=game["rating_count"],
                    rating_source=game["rating_source"],
                    cover_url=game["cover_url"],
                    media_type="games"
                )
                if game.get("platforms"):
                    st.markdown(f'<p style="color:#60A5FA; font-size:0.85rem; margin-top:-0.5rem;">🎮 Plateformes: {", ".join(game["platforms"][:4])}</p>', unsafe_allow_html=True)
                if game.get("description"):
                    st.markdown(f'<p style="color:#94A3B8; font-style:italic; font-size:0.85rem;">"{game["description"][:200]}..."</p>', unsafe_allow_html=True)
            else:
                st.info("Aucun jeu vidéo suggéré disponible.")
