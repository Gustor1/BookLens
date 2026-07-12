import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.ui import inject_custom_css, render_hero, render_metric, render_media_card, TOKENS
from src.i18n import t, language_selector

# Configurer la page
st.set_page_config(page_title="Design System — MediaLens", page_icon="🎨", layout="wide")
inject_custom_css()

# Langue dans la sidebar
language_selector()

st.title("🎨 Design System — MediaLens")
st.markdown("<p style='color: #94A3B8;'>Cette page d'administration permet de visualiser et tester l'ensemble des composants graphiques, couleurs et styles de la plateforme.</p>", unsafe_allow_html=True)
st.markdown("---")

# Section 1 : Palette de couleurs
st.header("1. Palette de Couleurs & Tokens")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div style='background: {TOKENS["colors"]["bg_primary"]}; height: 80px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 0.5rem;'></div>
    <strong>Background</strong><br><small>{TOKENS["colors"]["bg_primary"]}</small>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background: {TOKENS["colors"]["surface_basic"]}; height: 80px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 0.5rem;'></div>
    <strong>Surface Card</strong><br><small>{TOKENS["colors"]["surface_basic"]}</small>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background: {TOKENS["colors"]["surface_elevated"]}; height: 80px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 0.5rem;'></div>
    <strong>Surface Elevated</strong><br><small>{TOKENS["colors"]["surface_elevated"]}</small>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style='background: {TOKENS["colors"]["accent_primary"]}; height: 80px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 0.5rem;'></div>
    <strong>Accent Teal</strong><br><small>{TOKENS["colors"]["accent_primary"]}</small>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style='background: {TOKENS["colors"]["accent_secondary"]}; height: 80px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 0.5rem;'></div>
    <strong>Accent Amber</strong><br><small>{TOKENS["colors"]["accent_secondary"]}</small>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Section 2 : Typographie et Textes
st.header("2. Typographie & Textes")
st.markdown("<h1>Titre Principal (H1) - 2.75rem</h1>", unsafe_allow_html=True)
st.markdown("<h2>Titre de Section (H2) - 1.8rem</h2>", unsafe_allow_html=True)
st.markdown("<h3>Titre de Carte (H3) - 1.3rem</h3>", unsafe_allow_html=True)
st.markdown("<p style='color: #F8FAFC;'>Texte principal (Body) - 1rem. Conçu pour une lisibilité optimale sur fond sombre.</p>", unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8;'>Texte secondaire (Muted) - 0.95rem. Utilisé pour les métadonnées et descriptions.</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Section 3 : Boutons & Saisie
st.header("3. Boutons & Contrôles")
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    st.button("Bouton Primaire", type="primary")
with col_b2:
    st.button("Bouton Secondaire", type="secondary")
with col_b3:
    st.text_input("Champ de Saisie", placeholder="Rechercher...")

st.markdown("<br>", unsafe_allow_html=True)

# Section 4 : Badges et KPI Cards
st.header("4. Badges & Métriques (KPI)")
col_k1, col_k2, col_k3, col_k4 = st.columns(4)
with col_k1:
    render_metric("Total Médias", "1 520")
with col_k2:
    render_metric("Utilisateurs Actifs", "843")
with col_k3:
    render_metric("Avis Validés", "4 107")
with col_k4:
    render_metric("Note Moyenne", "7.6/10")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("##### Badges Sémantiques :")
st.markdown("""
<span class="badge">Badge Simple</span>
<span class="badge badge-success">✅ Succès</span>
<span class="badge badge-warning">⚠️ Avertissement</span>
<span class="badge badge-danger">❌ Erreur</span>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Section 5 : Cartes Médias
st.header("5. Cartes Médias Unifiées")
col_m1, col_m2 = st.columns(2)
with col_m1:
    render_media_card(
        title="Dune",
        creator="Frank Herbert",
        publisher="Chilton Books",
        year="1965",
        rating=9.2,
        n_ratings=150,
        similarity=0.95,
        rating_source="Open Library",
        media_type="books"
    )
with col_m2:
    render_media_card(
        title="Blade Runner 2049",
        creator="Denis Villeneuve",
        publisher="Warner Bros.",
        year="2017",
        rating=8.8,
        n_ratings=320,
        similarity=0.88,
        rating_source="TMDB",
        media_type="movies"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Section 6 : Skeletons & États de Chargement
st.header("6. Skeletons (Chargement)")
st.markdown("""
<div class="generic-card">
    <div class="skeleton" style="width: 40%; height: 20px; margin-bottom: 10px;"></div>
    <div class="skeleton" style="width: 80%; height: 14px; margin-bottom: 6px;"></div>
    <div class="skeleton" style="width: 60%; height: 14px;"></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Section 7 : Accessibilité & Réduction des mouvements
st.header("7. Accessibilité & Animations")
reduce_motion = st.toggle("Réduire les animations", value=st.session_state.get("reduce_motion", False))
if reduce_motion != st.session_state.get("reduce_motion", False):
    st.session_state["reduce_motion"] = reduce_motion
    st.rerun()

st.write("État de la réduction des mouvements :", "**Activé**" if reduce_motion else "**Désactivé**")
