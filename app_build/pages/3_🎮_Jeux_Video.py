import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from src.ui import inject_custom_css, render_media_card, render_source_media
from src.media import get_media_manager
from src.i18n import t

st.set_page_config(page_title=t("games.page_title", "Jeux Vidéo — BookLens"), page_icon="🎮", layout="wide")
inject_custom_css()

# Initialiser le manager
manager = get_media_manager("games")

# En-tête
st.markdown(f"# {t('games.hero_title', '🎮 Exploration de Jeux Vidéo')}")
st.markdown(f"<p style='color: #94A3B8; margin-bottom: 2rem;'>{t('games.hero_subtitle', 'Découvrez, recherchez et obtenez des recommandations de jeux vidéo.')}</p>", unsafe_allow_html=True)

# Vérification Clé API
if not manager.api_key:
    st.info("ℹ️ **Mode Démonstration** : Aucune clé API RAWG configurée. Affichage d'un catalogue de démonstration restreint. Ajoutez RAWG_API_KEY dans votre fichier .env pour activer la recherche en temps réel.")

# Recherche & Filtres
col_search, col_filter = st.columns([3, 1])

with col_search:
    search_query = st.text_input(
        "🔎 Rechercher un jeu",
        placeholder="Entrez un titre de jeu...",
        key="game_search_input"
    )

with col_filter:
    genres = manager.get_available_genres()
    selected_genre = st.selectbox(
        "🏷️ Filtrer par genre",
        options=["Tous"] + genres,
        key="game_genre_filter"
    )

st.markdown("---")

# Récupérer les résultats de recherche
filters = {}
if selected_genre != "Tous":
    filters["genre"] = selected_genre

results = manager.search(search_query, filters=filters)

if not results:
    st.info("Aucun jeu trouvé. Essayez une autre recherche.")
else:
    tab1, tab2 = st.tabs(["🗂️ Vue Résultats", "🎯 Obtenir des Recommandations"])
    
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        for game in results[:10]:
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
                st.markdown(f'<p style="color:#60A5FA; font-size:0.8rem; margin-top:-0.5rem; margin-bottom:0.5rem;">🎮 Plateformes: {", ".join(game["platforms"][:5])}</p>', unsafe_allow_html=True)
            if game.get("description"):
                desc = game["description"][:250] + "..."
                st.markdown(f'<p style="color:#94A3B8; font-style:italic; font-size:0.85rem; margin-bottom:1.5rem;">"{desc}"</p>', unsafe_allow_html=True)

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        game_options = {g["title"]: g["id"] for g in results}
        
        selected_game_title = st.selectbox(
            "🎮 Sélectionnez un jeu de référence pour trouver des jeux similaires",
            options=list(game_options.keys()),
            key="selected_game_rec"
        )
        
        n_recs = st.slider("Nombre de recommandations", 1, 10, 5, key="game_n_recs")
        
        if selected_game_title:
            game_id = game_options[selected_game_title]
            source_game = manager.get_details(game_id)
            
            if source_game:
                render_source_media(
                    title=source_game["title"],
                    creator=source_game["creator"],
                    rating=source_game["rating"],
                    n_ratings=source_game["rating_count"],
                    rating_source=source_game["rating_source"],
                    media_type="games"
                )
                
                recs = manager.get_recommendations(game_id, n=n_recs)
                
                if recs:
                    st.markdown("#### 🎯 Jeux recommandés :")
                    for i, game in enumerate(recs):
                        render_media_card(
                            title=f"#{i+1} — {game['title']}",
                            creator=game["creator"],
                            publisher=game["publisher"],
                            year=game["year"],
                            rating=game["rating"],
                            n_ratings=game["rating_count"],
                            rating_source=game["rating_source"],
                            cover_url=game["cover_url"],
                            similarity=game.get("similarity"),
                            media_type="games"
                        )
                        if game.get("platforms"):
                            st.markdown(f'<p style="color:#60A5FA; font-size:0.8rem; margin-top:-0.5rem; margin-bottom:0.5rem;">🎮 Plateformes: {", ".join(game["platforms"][:5])}</p>', unsafe_allow_html=True)
                        if game.get("description"):
                            desc = game["description"][:250] + "..."
                            st.markdown(f'<p style="color:#94A3B8; font-style:italic; font-size:0.85rem; margin-bottom:1.5rem;">"{desc}"</p>', unsafe_allow_html=True)
                else:
                    st.warning("Aucune recommandation disponible pour ce jeu.")
