import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.ui import inject_custom_css, render_hero
from src.i18n import t, language_selector

# Setup page
st.set_page_config(page_title="MediaLens Lab", page_icon="🧪", layout="wide")
inject_custom_css()

# Language selector in sidebar
language_selector()

# Title
st.title("🧪 MediaLens Lab")
st.markdown("<p style='color: #94A3B8; margin-bottom: 2rem;'>Bienvenue dans le laboratoire technique de MediaLens. Cet espace regroupe les outils de diagnostic, d'évaluation d'agent IA, de monitoring MLOps et d'analyse d'architecture.</p>", unsafe_allow_html=True)
st.markdown("---")

# Cards for each sub-module
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="generic-card" style="height: 100%;">
        <h4>🧱 Architecture & APIs</h4>
        <p style="margin-bottom: 1rem; color: #94A3B8;">
            Visualisez en temps réel l'état des connexions externes de la plateforme (NVIDIA Build, Hugging Face, Open Library, TMDB, RAWG) et leur mode de fallback.
        </p>
        <span class="badge">API Status</span>
        <span class="badge">APIs Grid</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="generic-card" style="height: 100%;">
        <h4>🧪 AI Evaluation Lab</h4>
        <p style="margin-bottom: 1rem; color: #94A3B8;">
            Exécutez notre suite de tests automatisée sur 36 cas d'usage multi-langues pour auditer la latence, la robustesse aux injections et la précision des citations du RAG.
        </p>
        <span class="badge">Model Quality</span>
        <span class="badge">Auto-scoring</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="generic-card" style="height: 100%;">
        <h4>🕸️ Graphe Relationnel</h4>
        <p style="margin-bottom: 1rem; color: #94A3B8;">
            Explorez les connexions thématiques et les ponts conceptuels entre les différents médias (livres, films, jeux vidéo) de notre univers.
        </p>
        <span class="badge">Network Theory</span>
        <span class="badge">Cross-media Connections</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="generic-card" style="height: 100%;">
        <h4>⚙️ Dashboard Technique</h4>
        <p style="margin-bottom: 1rem; color: #94A3B8;">
            Analysez les métriques d'exploitation : volumes d'appels aux APIs tierces, taux de réussite, latences moyennes et console de logs JSON structurés en direct.
        </p>
        <span class="badge">Telemetry</span>
        <span class="badge">Log Viewer</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="generic-card" style="height: 100%;">
        <h4>🔄 MLOps & Modèles</h4>
        <p style="margin-bottom: 1rem; color: #94A3B8;">
            Gérez le cycle de vie du modèle hybride : suivi des entraînements, détection de dérives de données (data drift) et réentraînement en un clic.
        </p>
        <span class="badge">Data Drift</span>
        <span class="badge">Training Hub</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="generic-card" style="height: 100%;">
        <h4>🎨 Design System</h4>
        <p style="margin-bottom: 1rem; color: #94A3B8;">
            Accédez à la bibliothèque de composants, palettes de couleurs, grilles et réglages d'accessibilité de notre design system unifié.
        </p>
        <span class="badge">Tokens</span>
        <span class="badge">UI Playground</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.info("💡 Utilisez la barre latérale gauche pour naviguer directement dans chacun de ces modules du laboratoire.")
