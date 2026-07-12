"""
📘 BookLens — Page À Propos
Architecture technique, stack et choix de conception pour le portfolio.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from src.ui import inject_custom_css

st.set_page_config(page_title="À Propos — BookLens", page_icon="ℹ️", layout="wide")
inject_custom_css()

# ─── En-tête ────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container" style="padding: 2rem;">
    <h2 class="hero-title" style="font-size: 2.2rem;">ℹ️ À Propos de BookLens</h2>
    <p class="hero-subtitle">Architecture technique, stack technologique et choix de conception.</p>
</div>
""", unsafe_allow_html=True)

# ─── Architecture ───────────────────────────────────────────────
st.markdown("### 🏗️ Architecture du Projet")

st.markdown("""
```
📘 BookLens
│
├── 🔧 Data Engineering          ─── Chargement, Validation, Nettoyage, Enrichissement API
│   ├── data_loader.py           → Charge les CSV bruts (Books, Users, Ratings, Academic)
│   ├── data_validator.py        → Validation de schéma, types, détection d'anomalies
│   ├── data_cleaner.py          → Nettoyage (doublons, valeurs manquantes, âges aberrants)
│   ├── data_enricher.py         → Enrichissement via Open Library API (avec cache local)
│   └── scripts/refresh_data.py  → Script de rafraîchissement manuel du pipeline
│
├── 🤖 Machine Learning          ─── Recommandation Hybride
│   └── recommender.py           → Filtrage Collaboratif + Similarité Contenu (TF-IDF)
│                                  + Feedback utilisateur + Évaluation quantitative
│
├── 💬 Agent IA                   ─── LLM + Fallback intelligent
│   └── agent.py                 → Gemini SDK + Détection d'intention + Mémoire de conversation
│
├── 🎨 Frontend                   ─── Streamlit + Design System
│   ├── ui.py                    → CSS centralisé (Dark Mode, Glassmorphism, Animations)
│   └── visualizations.py        → Graphiques Plotly (thème sombre natif)
│
└── 📄 Pages
    ├── 🔍 Recherche             → Exploration libre de la base de données
    ├── ⭐ Recommandations       → Recommandations hybrides + Feedback + Filtrage thème
    ├── 📊 Dashboard             → Graphiques analytiques interactifs
    ├── 🤖 Agent IA              → Chat avec assistant (LLM ou Fallback)
    ├── 🎓 Recherche Académique  → Corpus SF écoféministe/postcoloniale
    ├── 👤 Mon Profil            → Profil de lecture simulé (multi-livres)
    ├── 🔀 Comparer              → Comparaison côte à côte de 2 livres
    └── ℹ️ À Propos              → Cette page
```
""")

# ─── Stack ──────────────────────────────────────────────────────
st.markdown("### 🔧 Stack Technologique")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="generic-card">
        <h4>🐍 Backend & Data</h4>
        <p>
            <span class="badge">Python 3.9+</span>
            <span class="badge">pandas</span>
            <span class="badge">NumPy</span>
            <span class="badge">scikit-learn</span>
            <span class="badge">SciPy</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="generic-card">
        <h4>🤖 Intelligence Artificielle</h4>
        <p>
            <span class="badge">Google Gemini SDK</span>
            <span class="badge">TF-IDF Vectorizer</span>
            <span class="badge">Cosinus Similarity</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="generic-card">
        <h4>🎨 Frontend</h4>
        <p>
            <span class="badge">Streamlit</span>
            <span class="badge">Plotly</span>
            <span class="badge">CSS Custom (Glassmorphism)</span>
            <span class="badge">Inter Font</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="generic-card">
        <h4>📦 APIs & Enrichissement</h4>
        <p>
            <span class="badge">Open Library API</span>
            <span class="badge">Cache JSON local</span>
            <span class="badge">python-dotenv</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─── Choix de conception ────────────────────────────────────────
st.markdown("### 💡 Choix de Conception")

st.markdown("""
<div class="generic-card" style="border-left: 4px solid #6366F1;">
    <h4>Pourquoi un modèle Hybride ?</h4>
    <p>Le filtrage collaboratif seul souffre du problème du <strong>Cold Start</strong> : un nouveau livre sans notes ne peut pas être recommandé.
    En ajoutant une composante de contenu (TF-IDF sur auteur, thème, description), nous compensons partiellement ce problème.
    Le score final est une combinaison pondérée : <strong>70% collab + 30% contenu</strong>.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="generic-card" style="border-left: 4px solid #10B981;">
    <h4>Pourquoi un Fallback IA honnête ?</h4>
    <p>Plutôt que de simuler un LLM avec des règles statiques, nous affichons <strong>transparentement</strong> le mode utilisé.
    Si la clé Gemini est absente, l'utilisateur voit un bandeau "Mode Hors-ligne" et des réponses structurées par détection d'intention,
    ce qui montre une maîtrise de la gestion des états dégradés — compétence clé en production.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="generic-card" style="border-left: 4px solid #EC4899;">
    <h4>Pourquoi le Dark Mode et le Glassmorphism ?</h4>
    <p>Le choix visuel reflète les standards actuels des dashboards analytiques modernes (comme Vercel, Linear, ou Stripe).
    Le CSS est centralisé dans un seul module (<code>ui.py</code>) plutôt que dispersé dans chaque page,
    garantissant cohérence et maintenabilité.</p>
</div>
""", unsafe_allow_html=True)

# ─── Déploiement ────────────────────────────────────────────────
st.markdown("### 🚀 Déploiement")

st.markdown("""
**Streamlit Community Cloud** est la cible de déploiement recommandée :

1. Poussez le code sur un repo GitHub
2. Connectez-vous à [share.streamlit.io](https://share.streamlit.io)
3. Sélectionnez votre repo et pointez vers `app_build/app.py`
4. Ajoutez vos secrets (ex: `GEMINI_API_KEY`) dans les paramètres de l'app

> 💡 L'application fonctionne parfaitement **sans clé API** grâce au système de fallback.
""")

# ─── Métriques modèle ──────────────────────────────────────────
if "recommender" in st.session_state:
    recommender = st.session_state["recommender"]
    eval_m = recommender.get_eval_metrics()
    if eval_m:
        st.markdown("### 📊 Métriques du Modèle (Session Actuelle)")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Livres dans le modèle</div>
                <div class="metric-value">{eval_m.get('n_books_in_model', 0)}</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Couverture</div>
                <div class="metric-value">{eval_m.get('coverage', 0):.1%}</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Densité Matrice</div>
                <div class="metric-value">{eval_m.get('matrix_density', 0):.2%}</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Diversité</div>
                <div class="metric-value">{eval_m.get('avg_recommendation_diversity', 0):.1%}</div>
            </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748B;'><em>BookLens v3.0 — Projet Portfolio Data Engineering, ML & IA</em></p>", unsafe_allow_html=True)
