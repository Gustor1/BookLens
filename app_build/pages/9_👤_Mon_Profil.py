"""
📘 BookLens — Page Mon Profil de Lecture
L'utilisateur choisit ses goûts et voit des recommandations personnalisées.
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from src.ui import inject_custom_css, render_book_card

st.set_page_config(page_title="Mon Profil — BookLens", page_icon="👤", layout="wide")
inject_custom_css()

if "recommender" not in st.session_state or "merged_df" not in st.session_state:
    st.warning("⚠️ Veuillez d'abord visiter la page d'accueil pour charger les données.")
    st.stop()

recommender = st.session_state["recommender"]
df = st.session_state["merged_df"]

# ─── En-tête ────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container" style="padding: 2rem;">
    <h2 class="hero-title" style="font-size: 2.2rem;">👤 Mon Profil de Lecture</h2>
    <p class="hero-subtitle">Sélectionnez vos livres préférés et découvrez des recommandations personnalisées en temps réel.</p>
</div>
""", unsafe_allow_html=True)

# ─── Sélection des goûts ────────────────────────────────────────
st.markdown("### 📚 Vos Livres Préférés")
st.markdown("<p style='color: #94A3B8;'>Choisissez entre 1 et 5 livres que vous avez appréciés.</p>", unsafe_allow_html=True)

book_list = recommender.get_book_list()

if "profile_books" not in st.session_state:
    st.session_state["profile_books"] = []

selected_books = st.multiselect(
    "Sélectionnez vos livres favoris",
    options=book_list,
    default=st.session_state["profile_books"],
    max_selections=5,
    key="profile_multiselect",
    placeholder="Tapez pour rechercher un livre..."
)

st.session_state["profile_books"] = selected_books

# ─── Thèmes préférés ────────────────────────────────────────────
st.markdown("### 🏷️ Vos Thèmes Préférés (optionnel)")
available_themes = recommender.get_available_themes()
if available_themes:
    selected_themes = st.multiselect(
        "Filtrer par thèmes",
        options=available_themes,
        key="profile_themes",
        placeholder="Écoféminisme, Dystopie..."
    )
else:
    selected_themes = []

st.markdown("---")

# ─── Recommandations personnalisées ─────────────────────────────
if selected_books:
    st.markdown("### 🎯 Recommandations Personnalisées")
    st.markdown(f"<p style='color: #94A3B8;'>Basées sur vos {len(selected_books)} livre(s) sélectionné(s).</p>", unsafe_allow_html=True)

    # Agréger les recommandations de chaque livre sélectionné
    all_recs = {}
    for book in selected_books:
        theme_filter = selected_themes[0] if len(selected_themes) == 1 else None
        recs = recommender.get_recommendations(book, n=10, theme_filter=theme_filter)
        if recs is not None:
            for _, row in recs.iterrows():
                title = row["Book-Title"]
                if title not in selected_books:  # Ne pas recommander les livres déjà choisis
                    if title not in all_recs:
                        all_recs[title] = {
                            "score": 0,
                            "count": 0,
                            "author": row.get("Author", "Inconnu"),
                            "avg_rating": row.get("Avg-Rating"),
                            "num_ratings": row.get("Num-Ratings"),
                            "theme": row.get("Theme", ""),
                            "sources": []
                        }
                    all_recs[title]["score"] += row["Similarity-Score"]
                    all_recs[title]["count"] += 1
                    all_recs[title]["sources"].append(book)

    if all_recs:
        # Trier par score agrégé
        sorted_recs = sorted(
            all_recs.items(),
            key=lambda x: x[1]["score"] / x[1]["count"],
            reverse=True
        )[:10]

        for i, (title, data) in enumerate(sorted_recs):
            avg_score = data["score"] / data["count"]
            
            render_book_card(
                title=f"#{i+1} — {title}",
                author=data["author"],
                rating=data["avg_rating"] if isinstance(data["avg_rating"], (int, float)) else None,
                n_ratings=data["num_ratings"] if isinstance(data["num_ratings"], (int, float)) else None,
                similarity=avg_score
            )
            
            # Sources
            sources_str = ", ".join(f"*{s}*" for s in data["sources"][:3])
            st.markdown(f"<p style='color:#64748B; font-size:0.85rem;'>🔗 Recommandé car similaire à : {sources_str}</p>", unsafe_allow_html=True)
            
            if data["theme"] and pd.notna(data["theme"]):
                st.markdown(f'<span style="color:#10B981; font-size:0.85rem;">🏷️ {data["theme"]}</span>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Pas assez de données pour générer des recommandations personnalisées avec cette sélection.")
else:
    st.markdown("""
    <div style="text-align: center; padding: 4rem 0; color: #64748B;">
        <h1 style="font-size: 4rem; margin-bottom: 1rem;">📚</h1>
        <h3>Sélectionnez des livres pour commencer</h3>
        <p>Choisissez vos livres préférés ci-dessus pour obtenir des recommandations personnalisées.</p>
    </div>
    """, unsafe_allow_html=True)
