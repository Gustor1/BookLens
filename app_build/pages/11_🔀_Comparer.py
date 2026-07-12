"""
📘 BookLens — Page Comparer Deux Livres
Affichage côte à côte des thèmes communs et différences entre deux livres.
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from src.ui import inject_custom_css

st.set_page_config(page_title="Comparer — BookLens", page_icon="🔀", layout="wide")
inject_custom_css()

if "recommender" not in st.session_state:
    st.warning("⚠️ Veuillez d'abord visiter la page d'accueil pour charger les données.")
    st.stop()

recommender = st.session_state["recommender"]

# ─── En-tête ────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container" style="padding: 2rem;">
    <h2 class="hero-title" style="font-size: 2.2rem;">🔀 Comparer Deux Livres</h2>
    <p class="hero-subtitle">Sélectionnez deux livres pour comparer leurs métadonnées, scores et similarité.</p>
</div>
""", unsafe_allow_html=True)

# ─── Sélection ──────────────────────────────────────────────────
book_list = recommender.get_book_list()

col1, col2 = st.columns(2)

with col1:
    book_a = st.selectbox("📖 Livre A", options=book_list, key="compare_a")
with col2:
    # Essayer de pré-sélectionner un livre différent
    default_idx = min(1, len(book_list) - 1)
    book_b = st.selectbox("📖 Livre B", options=book_list, index=default_idx, key="compare_b")

st.markdown("---")

if book_a and book_b:
    info_a = recommender.get_book_info(book_a)
    info_b = recommender.get_book_info(book_b)

    if not info_a or not info_b:
        st.error("Impossible de charger les informations d'un des livres.")
        st.stop()

    # ─── Affichage côte à côte ──────────────────────────────────
    col1, col_mid, col2 = st.columns([5, 1, 5])

    with col1:
        st.markdown(f"""
        <div class="generic-card" style="border-left: 4px solid #6366F1;">
            <h3 style="color:#F8FAFC;">📖 {info_a['title']}</h3>
            <p><span class="badge">✍️ {info_a['author']}</span></p>
            <p><span class="badge badge-warning">⭐ {info_a['avg_rating']}/10</span>
               <span class="badge">📊 {info_a['num_ratings']} avis</span></p>
        """, unsafe_allow_html=True)
        if info_a.get("theme"):
            st.markdown(f'<p><span class="badge" style="color:#10B981; background:rgba(16,185,129,0.15); border-color:rgba(16,185,129,0.3)">🏷️ {info_a["theme"]}</span></p>', unsafe_allow_html=True)
        if info_a.get("type"):
            st.markdown(f'<p><span class="badge">📑 {info_a["type"]}</span></p>', unsafe_allow_html=True)
        if info_a.get("description"):
            st.markdown(f'<p style="color:#94A3B8; font-style:italic; font-size:0.9rem;">"{info_a["description"]}"</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_mid:
        st.markdown("""
        <div style="display:flex; align-items:center; justify-content:center; height:200px;">
            <span style="font-size:2rem; color:#64748B;">⚔️</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="generic-card" style="border-left: 4px solid #EC4899;">
            <h3 style="color:#F8FAFC;">📖 {info_b['title']}</h3>
            <p><span class="badge">✍️ {info_b['author']}</span></p>
            <p><span class="badge badge-warning">⭐ {info_b['avg_rating']}/10</span>
               <span class="badge">📊 {info_b['num_ratings']} avis</span></p>
        """, unsafe_allow_html=True)
        if info_b.get("theme"):
            st.markdown(f'<p><span class="badge" style="color:#10B981; background:rgba(16,185,129,0.15); border-color:rgba(16,185,129,0.3)">🏷️ {info_b["theme"]}</span></p>', unsafe_allow_html=True)
        if info_b.get("type"):
            st.markdown(f'<p><span class="badge">📑 {info_b["type"]}</span></p>', unsafe_allow_html=True)
        if info_b.get("description"):
            st.markdown(f'<p style="color:#94A3B8; font-style:italic; font-size:0.9rem;">"{info_b["description"]}"</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── Analyse de similarité ──────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Analyse Comparative")

    if book_a == book_b:
        st.info("🔄 Vous avez sélectionné le même livre ! Choisissez deux livres différents pour une comparaison.")
    else:
        # Score de similarité
        sim_score = 0
        if (recommender.similarity_df is not None 
            and book_a in recommender.similarity_df.columns 
            and book_b in recommender.similarity_df.columns):
            sim_score = recommender.similarity_df.loc[book_a, book_b]

        content_score = 0
        if (recommender.content_similarity_df is not None
            and not recommender.content_similarity_df.empty
            and book_a in recommender.content_similarity_df.columns 
            and book_b in recommender.content_similarity_df.columns):
            content_score = recommender.content_similarity_df.loc[book_a, book_b]

        hybrid = recommender.alpha * sim_score + (1 - recommender.alpha) * content_score

        # Afficher les scores
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Score Collaboratif</div>
                <div class="metric-value">{sim_score:.4f}</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Score Contenu</div>
                <div class="metric-value">{content_score:.4f}</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Score Hybride</div>
                <div class="metric-value">{hybrid:.4f}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Points communs et différences
        st.markdown("### 🔍 Points Communs et Différences")
        
        commons = []
        differences = []

        # Même auteur ?
        if info_a["author"] == info_b["author"]:
            commons.append(f"📝 **Même auteur** : {info_a['author']}")
        else:
            differences.append(f"📝 Auteurs différents : *{info_a['author']}* vs *{info_b['author']}*")

        # Même thème ?
        theme_a = info_a.get("theme", "")
        theme_b = info_b.get("theme", "")
        if theme_a and theme_b:
            if theme_a == theme_b:
                commons.append(f"🏷️ **Même thème** : {theme_a}")
            else:
                differences.append(f"🏷️ Thèmes différents : *{theme_a}* vs *{theme_b}*")

        # Même type ?
        type_a = info_a.get("type", "")
        type_b = info_b.get("type", "")
        if type_a and type_b:
            if type_a == type_b:
                commons.append(f"📑 **Même type** : {type_a}")
            else:
                differences.append(f"📑 Types différents : *{type_a}* vs *{type_b}*")

        # Écart de note
        rating_diff = abs(info_a["avg_rating"] - info_b["avg_rating"])
        if rating_diff < 0.5:
            commons.append(f"⭐ Notes très proches ({info_a['avg_rating']} vs {info_b['avg_rating']})")
        else:
            differences.append(f"⭐ Écart de note : {rating_diff:.1f} points")

        col_common, col_diff = st.columns(2)
        with col_common:
            st.markdown("#### ✅ Points Communs")
            if commons:
                for c in commons:
                    st.markdown(f"- {c}")
            else:
                st.markdown("*Aucun point commun détecté dans les métadonnées.*")
        
        with col_diff:
            st.markdown("#### ⚡ Différences")
            if differences:
                for d in differences:
                    st.markdown(f"- {d}")
            else:
                st.markdown("*Aucune différence majeure détectée.*")
