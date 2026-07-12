import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from src.ui import inject_custom_css, render_media_card, render_source_media
from src.media import get_media_manager
from src.i18n import t

st.set_page_config(page_title=t("movies.page_title", "Films — BookLens"), page_icon="🎬", layout="wide")
inject_custom_css()

# Initialiser le manager
manager = get_media_manager("movies")

# En-tête
st.markdown(f"# {t('movies.hero_title', '🎬 Exploration de Films')}")
st.markdown(f"<p style='color: #94A3B8; margin-bottom: 2rem;'>{t('movies.hero_subtitle', 'Découvrez, recherchez et obtenez des recommandations de films.')}</p>", unsafe_allow_html=True)

# Vérification Clé API
if not manager.api_key:
    st.info("ℹ️ **Mode Démonstration** : Aucune clé API TMDB configurée. Affichage d'un catalogue de démonstration restreint. Ajoutez TMDB_API_KEY dans votre fichier .env pour activer la recherche en temps réel.")

# Recherche & Filtres
col_search, col_filter = st.columns([3, 1])

with col_search:
    search_query = st.text_input(
        "🔎 Rechercher un film",
        placeholder="Entrez un titre de film...",
        key="movie_search_input"
    )

with col_filter:
    genres = manager.get_available_genres()
    selected_genre = st.selectbox(
        "🏷️ Filtrer par genre",
        options=["Tous"] + genres,
        key="movie_genre_filter"
    )

st.markdown("---")

# Récupérer les résultats de recherche
filters = {}
if selected_genre != "Tous":
    filters["genre"] = selected_genre

results = manager.search(search_query, filters=filters)

if not results:
    st.info("Aucun film trouvé. Essayez une autre recherche.")
else:
    # Diviser en onglets: Recherche et Recommandations
    tab1, tab2 = st.tabs(["🗂️ Vue Résultats", "🎯 Obtenir des Recommandations"])
    
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        # Afficher les 10 premiers résultats
        for movie in results[:10]:
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
                st.markdown(f'<p style="color:#94A3B8; font-style:italic; font-size:0.85rem; margin-top:-0.5rem; margin-bottom:1.5rem; padding-left:95px;">"{movie["description"][:200]}..."</p>', unsafe_allow_html=True)

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        movie_options = {m["title"]: m["id"] for m in results}
        
        selected_movie_title = st.selectbox(
            "🎥 Sélectionnez un film de référence pour trouver des films similaires",
            options=list(movie_options.keys()),
            key="selected_movie_rec"
        )
        
        n_recs = st.slider("Nombre de recommandations", 1, 10, 5, key="movie_n_recs")
        
        if selected_movie_title:
            movie_id = movie_options[selected_movie_title]
            source_movie = manager.get_details(movie_id)
            
            if source_movie:
                render_source_media(
                    title=source_movie["title"],
                    creator=source_movie["creator"],
                    rating=source_movie["rating"],
                    n_ratings=source_movie["rating_count"],
                    rating_source=source_movie["rating_source"],
                    media_type="movies"
                )
                
                # Récupérer les recommandations
                recs = manager.get_recommendations(movie_id, n=n_recs)
                
                if recs:
                    st.markdown("#### 🎯 Films recommandés :")
                    for i, movie in enumerate(recs):
                        render_media_card(
                            title=f"#{i+1} — {movie['title']}",
                            creator=movie["creator"],
                            publisher=movie["publisher"],
                            year=movie["year"],
                            rating=movie["rating"],
                            n_ratings=movie["rating_count"],
                            rating_source=movie["rating_source"],
                            cover_url=movie["cover_url"],
                            similarity=movie.get("similarity"),
                            media_type="movies"
                        )
                        if movie.get("description"):
                            st.markdown(f'<p style="color:#94A3B8; font-style:italic; font-size:0.85rem; margin-top:-0.5rem; margin-bottom:1.5rem; padding-left:95px;">"{movie["description"][:200]}..."</p>', unsafe_allow_html=True)
                else:
                    st.warning("Aucune recommandation disponible pour ce film.")
