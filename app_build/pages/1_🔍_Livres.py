"""
📘 BookLens — Page Recherche de Livres
Permet de rechercher, filtrer et explorer la base de données de livres.
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from src.ui import inject_custom_css, render_book_card

st.set_page_config(page_title="Recherche — BookLens", page_icon="🔍", layout="wide")
inject_custom_css()

# ─── Vérification des données ───────────────────────────────────
if "merged_df" not in st.session_state:
    st.warning("⚠️ Veuillez d'abord visiter la page d'accueil pour charger les données.")
    st.stop()

df = st.session_state["merged_df"]

# ─── En-tête ────────────────────────────────────────────────────
st.markdown("# 🔍 Recherche de Livres")
st.markdown("<p style='color: #94A3B8; margin-bottom: 2rem;'>Explorez la base de données et trouvez votre prochain livre préféré.</p>", unsafe_allow_html=True)

# ─── Filtres ────────────────────────────────────────────────────
st.markdown("### 🎛️ Filtres & Recherche Sémantique")
search_mode = st.radio("Mode de recherche", ["Classique (Mots-clés purs)", "Sémantique (IA textuelle)"], horizontal=True)

col_search, col_filter1, col_filter2 = st.columns([3, 2, 2])

with col_search:
    if search_mode == "Classique (Mots-clés purs)":
        search_query = st.text_input(
            "🔎 Rechercher un livre",
            placeholder="Tapez un titre, auteur ou éditeur...",
            key="search_input"
        )
    else:
        search_query = st.text_input(
            "🧠 Recherche Sémantique",
            placeholder="Ex: 'Une histoire de survie dans un monde post-apocalyptique', 'Lutte des classes'...",
            key="semantic_input"
        )

with col_filter1:
    authors = sorted(df["Book-Author"].dropna().unique().tolist())
    selected_author = st.selectbox(
        "✍️ Filtrer par auteur",
        options=["Tous"] + authors,
        key="author_filter",
        disabled=(search_mode != "Classique (Mots-clés purs)")
    )

with col_filter2:
    if "Publisher" in df.columns:
        publishers = sorted(df["Publisher"].dropna().unique().tolist())
        selected_publisher = st.selectbox(
            "🏢 Filtrer par éditeur",
            options=["Tous"] + publishers,
            key="publisher_filter",
            disabled=(search_mode != "Classique (Mots-clés purs)")
        )
    else:
        selected_publisher = "Tous"

if search_mode == "Classique (Mots-clés purs)":
    min_rating = st.slider("⭐ Note minimale", 1, 10, 1, key="rating_slider")
st.markdown("---")

# ─── Application de la recherche ────────────────────────────────
filtered = df.copy()
is_semantic_mode = search_mode != "Classique (Mots-clés purs)"

if is_semantic_mode and search_query:
    # ─── RECHERCHE SÉMANTIQUE ───
    st.markdown(f"### 🧠 Résultats sémantiques pour : *{search_query}*")
    
    if "recommender" in st.session_state and st.session_state["recommender"].is_fitted:
        semantic_results = st.session_state["recommender"].semantic_search(search_query, n=10)
        
        if semantic_results is not None and not semantic_results.empty:
            for _, row in semantic_results.iterrows():
                title = row["title"]
                author = row.get("author", "Inconnu")
                rating = row.get("avg_rating")
                n_ratings = row.get("num_ratings")
                sim_score = row.get("similarity_score", 0)
                rating_source = row.get("rating_source", "Estimée")
                
                # Récupérer l'année et publisher depuis df global
                book_data = df[df["Book-Title"] == title].iloc[0] if title in df["Book-Title"].values else None
                year = book_data["Year-Of-Publication"] if book_data is not None else "N/A"
                publisher = book_data["Publisher"] if book_data is not None and "Publisher" in book_data else "N/A"
                
                render_book_card(
                    title=title,
                    author=author,
                    publisher=publisher,
                    year=year,
                    rating=rating if isinstance(rating, (int, float)) else None,
                    n_ratings=n_ratings if isinstance(n_ratings, (int, float)) else None,
                    similarity=sim_score,
                    rating_source=rating_source
                )
                
                theme = row.get("theme", "")
                desc = row.get("description", "")
                
                if theme and pd.notna(theme):
                    st.markdown(f'<span style="color:#10B981; font-size:0.85rem;">🏷️ {theme}</span>', unsafe_allow_html=True)
                if desc and pd.notna(desc):
                    st.markdown(f'<p style="color:#94A3B8; font-style:italic; font-size:0.85rem; margin-top:0.5rem;">"{desc}"</p>', unsafe_allow_html=True)
                    
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("Aucun résultat assez proche sémantiquement n'a été trouvé.")
    else:
        st.warning("Le modèle de recommandation n'est pas chargé. La recherche sémantique est indisponible.")

elif not is_semantic_mode:
    # ─── RECHERCHE CLASSIQUE ───
    if search_query:
        query_lower = search_query.lower()
        mask = (
            filtered["Book-Title"].str.lower().str.contains(query_lower, na=False) |
            filtered["Book-Author"].str.lower().str.contains(query_lower, na=False)
        )
        if "Publisher" in filtered.columns:
            mask = mask | filtered["Publisher"].str.lower().str.contains(query_lower, na=False)
        filtered = filtered[mask]

    if selected_author != "Tous":
        filtered = filtered[filtered["Book-Author"] == selected_author]

    if selected_publisher != "Tous" and "Publisher" in filtered.columns:
        filtered = filtered[filtered["Publisher"] == selected_publisher]

    filtered = filtered[filtered["Book-Rating"] >= min_rating]

    # ─── Résultats classiques ───
    if filtered.empty:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; background: rgba(30, 41, 59, 0.3); border-radius: 16px; border: 1px dashed rgba(255,255,255,0.1);">
            <h2 style="font-size: 3rem; margin-bottom: 1rem;">📭</h2>
            <h3 style="color: #E2E8F0;">Aucun résultat trouvé</h3>
            <p style="color: #94A3B8;">Essayez de modifier vos filtres ou d'élargir votre recherche.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Agréger par livre pour éviter les doublons d'affichage
        agg_dict = {
            "Book-Author": "first",
            "Book-Rating": "mean",
            "Year-Of-Publication": "first",
        }
        if "Publisher" in filtered.columns:
            agg_dict["Publisher"] = "first"
        if "Real-Rating" in filtered.columns:
            agg_dict["Real-Rating"] = "first"
            agg_dict["Real-Rating-Count"] = "first"
            agg_dict["Rating-Source"] = "first"

        books_agg = filtered.groupby("Book-Title").agg(agg_dict)
        rating_counts = filtered.groupby("Book-Title")["Book-Rating"].count()
        books_agg["Nb Notes"] = rating_counts
        books_agg["Book-Rating"] = books_agg["Book-Rating"].round(1)
        books_agg = books_agg.sort_values("Book-Rating", ascending=False).head(50)

        st.markdown(f"### 📚 Résultats ({len(filtered)} ratings / {len(books_agg)} livres uniques affichés)")
        
        tab1, tab2 = st.tabs(["🗂️ Vue Cartes (Top 5)", "📋 Vue Tableau"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            top5 = books_agg.head(5)
            for title, row in top5.iterrows():
                if "Real-Rating" in row and pd.notna(row["Real-Rating"]):
                    rating_to_show = row["Real-Rating"]
                    count_to_show = row["Real-Rating-Count"]
                    source_to_show = row.get("Rating-Source", "Google Books")
                else:
                    rating_to_show = row['Book-Rating']
                    count_to_show = row['Nb Notes']
                    source_to_show = "Estimée"
                    
                render_book_card(
                    title=title,
                    author=row['Book-Author'],
                    publisher=row.get('Publisher', 'N/A'),
                    year=row['Year-Of-Publication'],
                    rating=rating_to_show,
                    n_ratings=count_to_show,
                    rating_source=source_to_show
                )

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            rename_map = {
                "Book-Author": "Auteur",
                "Book-Rating": "Note Moy.",
                "Year-Of-Publication": "Année",
            }
            if "Publisher" in books_agg.columns:
                rename_map["Publisher"] = "Éditeur"
            
            display_df = books_agg.rename(columns=rename_map).reset_index().rename(columns={"Book-Title": "Titre"})
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=500,
                column_config={
                    "Note Moy.": st.column_config.NumberColumn(format="%.1f ⭐"),
                    "Nb Notes": st.column_config.NumberColumn(format="%d 📊"),
                }
            )
else:
    if is_semantic_mode:
        st.info("Veuillez entrer une requête sémantique (ex: 'un livre sur la révolte écologique').")
