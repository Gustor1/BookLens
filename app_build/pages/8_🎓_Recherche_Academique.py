"""
📘 BookLens — Page Recherche Académique
Explore le corpus spécialisé en science-fiction écoféministe et postcoloniale,
et intègre la recherche globale Semantic Scholar.
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from src.ui import inject_custom_css
from src.i18n import t, language_selector
from src.scholar_api import search_papers

st.set_page_config(page_title=t("academic.page_title", " Recherche Académique — BookLens"), page_icon="🎓", layout="wide")
inject_custom_css()

with st.sidebar:
    language_selector()

# ─── Vérification ───────────────────────────────────────────────
if "merged_df" not in st.session_state:
    st.warning(t("home.warning_data", "⚠️ Veuillez d'abord visiter la page d'accueil pour charger les données."))
    st.stop()

df = st.session_state["merged_df"]
academic_df = df.dropna(subset=["Theme"]).drop_duplicates(subset=["ISBN"]) if "Theme" in df.columns else pd.DataFrame()

# ─── En-tête ────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-container" style="padding: 2rem;">
    <h2 class="hero-title" style="font-size: 2.2rem; background: linear-gradient(to right, #10B981, #3B82F6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        {t("academic.hero_title", "🎓 Corpus de Recherche")}
    </h2>
    <p class="hero-subtitle">
        {t("academic.hero_subtitle", "Explorez notre sélection d'œuvres locales et parcourez la base Semantic Scholar.")}
    </p>
</div>
""", unsafe_allow_html=True)

# ─── Onglets ────────────────────────────────────────────────────
tab1, tab2 = st.tabs([
    t("academic.tab_local", "📚 Base de données Locale (Livres)"),
    t("academic.tab_scholar", "🔬 Semantic Scholar (Articles)")
])

# ─── ONGLET 1 : BASE LOCALE ─────────────────────────────────────
with tab1:
    if academic_df.empty:
        st.info(t("academic.empty_local", "Aucun livre académique n'est actuellement disponible."))
    else:
        st.markdown(f"### 🎛️ {t('academic.filters_title', 'Filtres d exploration')}")
        col_theme, col_type, col_search = st.columns([2, 2, 3])
        
        with col_theme:
            themes = sorted(academic_df["Theme"].unique().tolist())
            selected_theme = st.selectbox(f"🌱 {t('academic.filter_theme', 'Thème principal')}", options=["Tous les thèmes"] + themes)
            
        with col_type:
            types = sorted(academic_df["Type"].unique().tolist())
            selected_type = st.selectbox(f"📚 {t('academic.filter_type', 'Type d oeuvre')}", options=["Tous les types"] + types)
            
        with col_search:
            search_query = st.text_input(f"🔎 {t('academic.search_placeholder', 'Recherche (Auteur, Titre)')}", placeholder="Ex: Ursula, Atwood...")
            
        st.markdown("---")
        filtered = academic_df.copy()
        
        if selected_theme != "Tous les thèmes":
            filtered = filtered[filtered["Theme"] == selected_theme]
        if selected_type != "Tous les types":
            filtered = filtered[filtered["Type"] == selected_type]
        if search_query:
            query_lower = search_query.lower()
            mask = (
                filtered["Book-Title"].str.lower().str.contains(query_lower, na=False) |
                filtered["Book-Author"].str.lower().str.contains(query_lower, na=False) |
                filtered["Description"].str.lower().str.contains(query_lower, na=False)
            )
            filtered = filtered[mask]
            
        st.markdown(f"### 📑 {t('academic.results_local', 'Œuvres correspondantes')} ({len(filtered)})")
        
        if filtered.empty:
            st.markdown(f"""
            <div style="text-align: center; padding: 3rem; background: rgba(30, 41, 59, 0.3); border-radius: 12px; border: 1px dashed rgba(255,255,255,0.1);">
                <h3 style="color: #94A3B8;">{t("academic.no_results", "Aucune œuvre ne correspond à vos critères.")}</h3>
            </div>
            """, unsafe_allow_html=True)
        else:
            for idx, row in filtered.iterrows():
                badges_html = f'<span class="badge" style="color:#10B981; background:rgba(16,185,129,0.15); border-color:rgba(16,185,129,0.3)">{row["Theme"]}</span>'
                badges_html += f'<span class="badge" style="color:#8B5CF6; background:rgba(139,92,246,0.15); border-color:rgba(139,92,246,0.3)">{row["Type"]}</span>'
                if row["Relevance"] == "Haute":
                    badges_html += f'<span class="badge" style="color:#F59E0B; background:rgba(245,158,11,0.15); border-color:rgba(245,158,11,0.3)">🔥 {t("academic.relevance_high", "Pertinence Majeure")}</span>'
                
                # Stats
                book_ratings = df[df["ISBN"] == row["ISBN"]]
                avg_rating = book_ratings["Book-Rating"].mean()
                num_ratings = len(book_ratings)
                
                stats_html = ""
                if pd.notna(avg_rating) and num_ratings > 0:
                    stats_html = f'<br><span class="badge badge-warning">⭐ {t("home.stat_avg", "Note moyenne")}: {avg_rating:.1f}/10 ({num_ratings})</span>'

                st.markdown(f"""
                <div class="generic-card" style="margin-bottom: 1.5rem; border-left: 4px solid #10B981;">
                    <h4>📖 {row['Book-Title']} <span style="font-weight:400; font-size:1.1rem; color:#94A3B8">par {row['Book-Author']} ({row['Year-Of-Publication']})</span></h4>
                    <div style="margin-bottom: 1rem;">
                        {badges_html}
                        {stats_html}
                    </div>
                    <p style="color: #CBD5E1; font-style: italic; border-left: 2px solid rgba(255,255,255,0.1); padding-left: 1rem; margin-bottom: 1rem;">
                        "{row['Description']}"
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"🔗 {t('academic.similar_books', 'Voir les œuvres thématiquement proches')}"):
                    similar = academic_df[
                        (academic_df["Theme"] == row["Theme"]) & 
                        (academic_df["ISBN"] != row["ISBN"])
                    ]
                    if similar.empty:
                        st.write("*Aucun autre résultat.*")
                    else:
                        for _, sim_row in similar.iterrows():
                            st.write(f"- **{sim_row['Book-Title']}** ({sim_row['Type']})")

# ─── ONGLET 2 : SEMANTIC SCHOLAR ────────────────────────────────
with tab2:
    st.markdown(f"### 🔬 {t('academic.scholar_title', 'Recherche d articles (Semantic Scholar)')}")
    st.markdown(f"*{t('academic.scholar_desc', 'Explorez plus de 200 millions d articles scientifiques en temps réel.')}*")
    
    col_schol_search, col_schol_btn = st.columns([8, 2])
    with col_schol_search:
        scholar_query = st.text_input(t("academic.scholar_placeholder", "Mots-clés (ex: ecofeminism science fiction)"), key="scholar_input")
    with col_schol_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        search_clicked = st.button(t("academic.scholar_btn", "Rechercher"), use_container_width=True)
        
    if search_clicked and scholar_query:
        with st.spinner(t("academic.scholar_loading", "Recherche en cours sur Semantic Scholar...")):
            papers = search_papers(scholar_query, limit=5)
            
            if not papers:
                st.warning(t("academic.scholar_no_result", "Aucun article trouvé ou limite de requêtes atteinte."))
            else:
                st.success(f"{len(papers)} {t('academic.scholar_success', 'articles trouvés.')}")
                
                for p in papers:
                    st.markdown(f"""
                    <div class="generic-card" style="margin-bottom: 1rem; border-left: 4px solid #3B82F6;">
                        <h4 style="margin-bottom: 0.2rem;"><a href="{p['url']}" target="_blank" style="color: #60A5FA; text-decoration: none;">📄 {p['title']}</a></h4>
                        <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 0.8rem;">
                            <strong>Auteurs:</strong> {p['authors']} | <strong>Année:</strong> {p['year']} | <strong>Citations:</strong> {p['citationCount']}
                        </p>
                        <p style="color: #CBD5E1; font-size: 0.95rem;">
                            {p['abstract']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
