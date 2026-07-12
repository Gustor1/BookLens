"""
📘 BookLens — Page Dashboard
Graphiques interactifs pour explorer les données.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.ui import inject_custom_css
from src.visualizations import (
    plot_rating_distribution,
    plot_top_books,
    plot_top_authors,
    plot_ratings_per_year,
    plot_age_distribution,
    plot_rating_by_age_group,
    plot_publisher_distribution,
)

st.set_page_config(page_title="Dashboard — BookLens", page_icon="📊", layout="wide")
inject_custom_css()

# ─── Vérification ───────────────────────────────────────────────
if "merged_df" not in st.session_state:
    st.warning("⚠️ Veuillez d'abord visiter la page d'accueil pour charger les données.")
    st.stop()

df = st.session_state["merged_df"]
metrics = st.session_state.get("metrics", {})

# ─── En-tête ────────────────────────────────────────────────────
st.markdown("# 📊 Dashboard Analytique")
st.markdown("<p style='color: #94A3B8; margin-bottom: 2rem;'>Explorez visuellement la distribution, les tendances et les statistiques globales du dataset.</p>", unsafe_allow_html=True)

# ─── Graphiques ─────────────────────────────────────────────────

# Conteneur global pour donner un padding
st.markdown("<div style='background: rgba(30, 41, 59, 0.3); border-radius: 16px; padding: 2rem; border: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

# Ligne 1 : Distribution + Top livres
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        plot_rating_distribution(df),
        use_container_width=True,
        key="chart_rating_dist"
    )

with col2:
    st.plotly_chart(
        plot_top_books(df, n=10),
        use_container_width=True,
        key="chart_top_books"
    )

st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 2rem 0;'>", unsafe_allow_html=True)

# Ligne 2 : Top auteurs + Ratings par année
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        plot_top_authors(df, n=10),
        use_container_width=True,
        key="chart_top_authors"
    )

with col2:
    st.plotly_chart(
        plot_ratings_per_year(df),
        use_container_width=True,
        key="chart_ratings_year"
    )

st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 2rem 0;'>", unsafe_allow_html=True)

# Ligne 3 : Âge + Notes par âge
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        plot_age_distribution(df),
        use_container_width=True,
        key="chart_age_dist"
    )

with col2:
    st.plotly_chart(
        plot_rating_by_age_group(df),
        use_container_width=True,
        key="chart_rating_age"
    )

st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 2rem 0;'>", unsafe_allow_html=True)

# Ligne 4 : Éditeurs
st.plotly_chart(
    plot_publisher_distribution(df, n=10),
    use_container_width=True,
    key="chart_publishers"
)

st.markdown("</div>", unsafe_allow_html=True)

# ─── Données brutes ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📋 Voir les données brutes"):
    st.dataframe(df.head(100), use_container_width=True)
    st.markdown(f"*Affichage des 100 premières lignes sur {len(df)} total.*")
