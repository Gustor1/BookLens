import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.ui import inject_custom_css
from src.i18n import t, language_selector
from src.llm_provider import is_provider_active
from src.media import get_media_manager
from src.data_quality import DataQualityEngine

st.set_page_config(page_title=t("arch.page_title", "Architecture — BookLens"), page_icon="🧱", layout="wide")
inject_custom_css()

# Ajouter le sélecteur de langue
language_selector()

# En-tête
st.markdown(f"# {t('arch.hero_title', '🧱 Architecture & Technologies')}")
st.markdown(f"<p style='color: #94A3B8; margin-bottom: 2rem;'>{t('arch.hero_subtitle', 'Découvrez toutes les briques et APIs qui font fonctionner le projet BookLens.')}</p>", unsafe_allow_html=True)

# Créer les onglets
tab_tech, tab_gov = st.tabs([
    t("arch.tab_briques", "🔌 Briques & APIs Connectées"),
    t("arch.tab_gov", "🏛️ Catalogue & Gouvernance de Données")
])

# ─── ONGLET 1 : BRIQUES & APIS ────────────────────────────────
with tab_tech:
    # Déterminer les statuts
    nvidia_active = is_provider_active("nvidia")
    hf_active = is_provider_active("huggingface")

    # Pour les médias
    movies_mgr = get_media_manager("movies")
    games_mgr = get_media_manager("games")
    tmdb_active = bool(movies_mgr.api_key)
    rawg_active = bool(games_mgr.api_key)

    briques = [
        {
            "name": t("arch.nvidia_name", "NVIDIA Build"),
            "icon": "🤖",
            "usage": t("arch.nvidia_usage", "Assistant conversationnel principal (Llama 3.3 Nemotron 70B)."),
            "status": t("arch.connected", "Connecté") if nvidia_active else t("arch.fallback", "Fallback local (Règles statiques)"),
            "status_class": "badge-real" if nvidia_active else "badge-estimated",
            "capabilities": t("arch.nvidia_caps", "Texte, Raisonnement, Mémoire de contexte"),
            "url": "https://build.nvidia.com"
        },
        {
            "name": t("arch.hf_name", "Hugging Face Inference"),
            "icon": "🤗",
            "usage": t("arch.hf_usage", "Génération de couvertures d'images (FLUX.1-dev) et synthèse vocale (MMS-TTS)."),
            "status": t("arch.connected", "Connecté") if hf_active else t("arch.fallback_disabled", "Non configuré (Image/Voix désactivées)"),
            "status_class": "badge-real" if hf_active else "badge-estimated",
            "capabilities": t("arch.hf_caps", "Texte, Génération d'image, Synthèse Vocale"),
            "url": "https://huggingface.co"
        },
        {
            "name": t("arch.tmdb_name", "TMDB API"),
            "icon": "🎬",
            "usage": t("arch.tmdb_usage", "Recherche en temps réel, métadonnées de films, affiches originales, notes et recommandations."),
            "status": t("arch.connected", "Connecté") if tmdb_active else t("arch.fallback", "Mode Démo (Catalogue local statique)"),
            "status_class": "badge-real" if tmdb_active else "badge-estimated",
            "capabilities": t("arch.tmdb_caps", "Métadonnées films, Posters, Recommandations"),
            "url": "https://themoviedb.org"
        },
        {
            "name": t("arch.rawg_name", "RAWG API"),
            "icon": "🎮",
            "usage": t("arch.rawg_usage", "Recherche de jeux vidéo, screenshots, studios de dével., éditeurs, plateformes et suggestions."),
            "status": t("arch.connected", "Connecté") if rawg_active else t("arch.fallback", "Mode Démo (Catalogue local statique)"),
            "status_class": "badge-real" if rawg_active else "badge-estimated",
            "capabilities": t("arch.rawg_caps", "Métadonnées jeux, Captures, Plateformes"),
            "url": "https://rawg.io"
        },
        {
            "name": t("arch.ol_name", "Open Library API"),
            "icon": "📖",
            "usage": t("arch.ol_usage", "Enrichissement des livres par des données réelles (ISBNs, couvertures, résumés, sujets)."),
            "status": t("arch.connected", "Connecté"),
            "status_class": "badge-real",
            "capabilities": t("arch.ol_caps", "Métadonnées livres, Couvertures"),
            "url": "https://openlibrary.org"
        },
        {
            "name": t("arch.ss_name", "Semantic Scholar API"),
            "icon": "🎓",
            "usage": t("arch.ss_usage", "Recherche d'articles scientifiques et synthèses critiques sur l'écoféminisme et la SF."),
            "status": t("arch.connected", "Connecté"),
            "status_class": "badge-real",
            "capabilities": t("arch.ss_caps", "Articles scientifiques, Citations, Résumés"),
            "url": "https://semanticscholar.org"
        }
    ]

    # Grille de cartes
    cols = st.columns(2)
    for idx, brique in enumerate(briques):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="generic-card" style="margin-bottom: 1.5rem; min-height: 230px; display: flex; flex-direction: column;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem;">
                    <h3 style="margin: 0; color: #60A5FA; font-size: 1.3rem;">{brique['icon']} {brique['name']}</h3>
                    <span class="badge {brique['status_class']}">{brique['status']}</span>
                </div>
                <p style="font-size: 0.9rem; color: #E2E8F0; margin-bottom: 1rem; flex-grow: 1;">{brique['usage']}</p>
                <div style="margin-top: auto; font-size: 0.85rem; color: #94A3B8; border-top: 1px solid #1E293B; padding-top: 0.8rem;">
                    <strong>{t('arch.caps_label', 'Capacités')}</strong> : {brique['capabilities']}<br>
                    <a href="{brique['url']}" target="_blank" style="color: #60A5FA; text-decoration: none; display: inline-block; margin-top: 0.5rem;">{t('arch.link_label', 'En savoir plus')} →</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─── ONGLET 2 : DATA GOVERNANCE ───────────────────────────────
with tab_gov:
    st.markdown(f"### {t('arch.gov_title', '🏛️ Gouvernance de Données & Diagnostics de Qualité')}")
    st.write(t("arch.gov_desc", "BookLens applique des règles d'audit strictes pour nettoyer, dédoublonner et valider l'intégrité de ses sources locales et distantes."))
    
    # Bouton de rafraîchissement
    if st.button(t("arch.refresh_diag", "🔄 Lancer les diagnostics de qualité")):
        st.session_state["last_quality_report"] = DataQualityEngine.run_diagnostics()
        st.success(t("arch.diag_success", "Diagnostics terminés avec succès !"))
        
    report = st.session_state.get("last_quality_report")
    if not report:
        report = DataQualityEngine.run_diagnostics()
        st.session_state["last_quality_report"] = report
        
    # Affichage des cartes de santé par dataset
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    datasets_info = report.get("datasets", {})
    
    with col_d1:
        books_stat = datasets_info.get("books", {})
        st.metric("Books.csv", f"{books_stat.get('total_rows', 0)} lignes", delta=f"{books_stat.get('duplicates', 0)} doublons", delta_color="inverse")
    with col_d2:
        users_stat = datasets_info.get("users", {})
        st.metric("Users.csv", f"{users_stat.get('total_rows', 0)} users", delta=f"{users_stat.get('duplicates', 0)} doublons", delta_color="inverse")
    with col_d3:
        ratings_stat = datasets_info.get("ratings", {})
        st.metric("Ratings.csv", f"{ratings_stat.get('total_rows', 0)} notes", delta=f"{ratings_stat.get('duplicates', 0)} doublons", delta_color="inverse")
    with col_d4:
        acad_stat = datasets_info.get("academic", {})
        st.metric("Academic Corpus", f"{acad_stat.get('total_rows', 0)} lignes", delta=None)

    st.markdown("---")
    st.markdown(f"### 📋 Rapport Qualité Complet")
    
    md_content = DataQualityEngine.generate_markdown_report()
    st.markdown(md_content)
    
    # Télécharger le rapport
    st.download_button(
        t("arch.download_report", "📥 Télécharger le rapport de gouvernance (.json)"),
        data=json.dumps(report, ensure_ascii=False, indent=2),
        file_name="data_quality_report.json",
        mime="application/json",
        use_container_width=True
    )
