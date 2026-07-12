import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.ui import inject_custom_css, render_media_card
from src.media import get_media_manager
from src.i18n import t

# Page setup
st.set_page_config(page_title="Explorer — MediaLens", page_icon="🧭", layout="wide")
inject_custom_css()

# Vérification du chargement des données
if "merged_df" not in st.session_state:
    st.warning("⚠️ Veuillez d'abord visiter la page d'accueil pour charger les données.")
    st.stop()

df = st.session_state["merged_df"]

# Récupérer la redirection de recherche universelle depuis la Home
default_search = ""
if "search_query_redirect" in st.session_state and st.session_state["search_query_redirect"]:
    default_search = st.session_state["search_query_redirect"]
    # Vider la redirection pour éviter les boucles
    st.session_state["search_query_redirect"] = ""

# Titre
st.title("🧭 " + t("nav.explore", "Explorer le catalogue"))
st.markdown("<p style='color: #94A3B8; margin-bottom: 2rem;'>Recherchez et filtrez l'ensemble des livres, films et jeux vidéo de notre catalogue culturel.</p>", unsafe_allow_html=True)

# ─── Filtres Principaux (Chips / Navigation) ────────────────────
media_filter = st.radio(
    label="Filtrer par type de média",
    options=["Tous", "Livres", "Films", "Jeux Vidéo"],
    index=0,
    horizontal=True,
    key="explorer_media_type_filter"
)

# ─── Barre de Recherche Universelle & Tri ─────────────────────
col_search, col_sort = st.columns([3, 1])

with col_search:
    search_query = st.text_input(
        "🔎 " + t("home.search_placeholder", "Rechercher..."),
        value=default_search,
        placeholder="Entrez un titre, un auteur, un genre...",
        key="explorer_search_query"
    )

with col_sort:
    sort_option = st.selectbox(
        "Sort by",
        options=["Tri par défaut", "Note (décroissant)", "Année (décroissant)"],
        key="explorer_sort_option"
    )

st.markdown("---")

results = []

# ─── Recherche Livres ───
if media_filter in ["Tous", "Livres"]:
    books_results = df.copy()
    if search_query:
        books_results = books_results[
            books_results["Book-Title"].str.contains(search_query, case=False, na=False) |
            books_results["Book-Author"].str.contains(search_query, case=False, na=False) |
            books_results["Publisher"].str.contains(search_query, case=False, na=False)
        ]
    
    for _, row in books_results.iterrows():
        results.append({
            "title": row.get("Book-Title"),
            "creator": row.get("Book-Author", "Inconnu"),
            "publisher": row.get("Publisher", "N/A"),
            "year": str(row.get("Year-Of-Publication", "N/A")),
            "rating": row.get("Book-Rating"),
            "rating_count": row.get("Number-Of-Ratings"),
            "rating_source": "Open Library",
            "media_type": "books",
            "cover_url": None
        })

# ─── Recherche Films ───
if media_filter in ["Tous", "Films"]:
    movies_mgr = get_media_manager("movies")
    movies_res = movies_mgr.search(search_query)
    for m in movies_res:
        results.append({
            "title": m["title"],
            "creator": m["creator"],
            "publisher": m["publisher"],
            "year": str(m["year"]),
            "rating": m["rating"],
            "rating_count": m["rating_count"],
            "rating_source": m["rating_source"],
            "media_type": "movies",
            "cover_url": m["cover_url"]
        })

# ─── Recherche Jeux Vidéo ───
if media_filter in ["Tous", "Jeux Vidéo"]:
    games_mgr = get_media_manager("games")
    games_res = games_mgr.search(search_query)
    for g in games_res:
        results.append({
            "title": g["title"],
            "creator": g["creator"],
            "publisher": g["publisher"],
            "year": str(g["year"]),
            "rating": g["rating"],
            "rating_count": g["rating_count"],
            "rating_source": g["rating_source"],
            "media_type": "games",
            "cover_url": g["cover_url"]
        })

# ─── Tri des résultats ───
if sort_option == "Note (décroissant)":
    results = sorted(results, key=lambda x: x["rating"] if x["rating"] is not None else 0, reverse=True)
elif sort_option == "Année (décroissant)":
    # Extraire l'année en nombre
    def extract_year(y):
        try:
            return int(''.join(filter(str.isdigit, y)))
        except ValueError:
            return 0
    results = sorted(results, key=lambda x: extract_year(x["year"]), reverse=True)

# ─── Rendu des Cartes ───
if not results:
    st.info("Aucun résultat trouvé pour votre recherche.")
else:
    # Pagination simple ou affichage limité à 30 pour la performance
    st.write(f"Affichage de {min(len(results), 30)} résultats sur {len(results)} trouvés :")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Créer deux colonnes pour un rendu grille élégant
    col1, col2 = st.columns(2)
    for idx, item in enumerate(results[:30]):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            render_media_card(
                title=item["title"],
                creator=item["creator"],
                publisher=item["publisher"],
                year=item["year"],
                rating=item["rating"],
                n_ratings=item["rating_count"],
                rating_source=item["rating_source"],
                cover_url=item["cover_url"],
                media_type=item["media_type"]
            )
