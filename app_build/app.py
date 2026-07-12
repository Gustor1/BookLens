"""
📘 MediaLens — Point d'entrée principal & Routage
Gère l'initialisation globale des données et définit la structure de navigation moderne.
"""

import streamlit as st
import pandas as pd
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialiser l'état Streamlit très tôt
if "lang" not in st.session_state:
    st.session_state["lang"] = "fr"

from src.data_loader import load_all, PROCESSED_DIR, RAW_DIR
from src.data_cleaner import (
    clean_books, clean_users, clean_ratings,
    merge_datasets, generate_metrics, save_processed_data, integrate_academic_data
)
from src.recommender import BookRecommender, generate_ml_report
from src.ui import inject_custom_css
from src.i18n import t

# Configurer la mise en page de base pour toute la navigation
st.set_page_config(
    page_title="MediaLens",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injecter le CSS global
inject_custom_css()

# ─── Initialisation des données (cache) ─────────────────────────
@st.cache_data(show_spinner="📚 Chargement des données...")
def init_data():
    if not os.path.exists(os.path.join(RAW_DIR, "Books.csv")):
        from generate_sample_data import main as generate_data
        generate_data()

    processed_path = os.path.join(PROCESSED_DIR, "merged_dataset.csv")
    if os.path.exists(processed_path):
        merged = pd.read_csv(processed_path)
        metrics = generate_metrics(merged)
        return merged, metrics

    books, users, ratings, academic = load_all()
    books_clean = clean_books(books)
    users_clean = clean_users(users)
    ratings_clean = clean_ratings(ratings)
    
    # Intégration des données académiques
    books_clean, ratings_clean = integrate_academic_data(books_clean, users_clean, ratings_clean, academic)
    
    merged = merge_datasets(books_clean, users_clean, ratings_clean)
    metrics = generate_metrics(merged)
    save_processed_data(merged)
    return merged, metrics

@st.cache_resource(show_spinner="🤖 Chargement du modèle ML...")
def init_recommender(_merged_df):
    recommender = BookRecommender(min_ratings=2)
    recommender.fit(_merged_df)
    recommender.save()
    return recommender

# Exécuter le chargement silencieux au démarrage
merged_df, metrics = init_data()
recommender = init_recommender(merged_df)

st.session_state["merged_df"] = merged_df
st.session_state["metrics"] = metrics
st.session_state["recommender"] = recommender

# ─── Déclaration des Pages (st.navigation) ─────────────────────
pages_config = {
    t("nav.section_main", "Principal"): [
        st.Page("pages/0_🏠_Accueil.py", title=t("nav.home", "Accueil"), icon="🏠", default=True),
        st.Page("pages/20_🧭_Explorer.py", title=t("nav.explore", "Explorer"), icon="🧭"),
        st.Page("pages/10_📚_Bibliothèque_de_recherche.py", title=t("nav.library", "Ma Bibliothèque"), icon="📚"),
        st.Page("pages/6_🤖_Agent_IA.py", title=t("nav.agent", "Assistant IA"), icon="🤖"),
    ],
    t("nav.section_discover", "Découvrir"): [
        st.Page("pages/1_🔍_Livres.py", title=t("nav.books", "Livres"), icon="📖"),
        st.Page("pages/2_🎬_Films.py", title=t("nav.movies", "Films"), icon="🎬"),
        st.Page("pages/3_🎮_Jeux_Video.py", title=t("nav.games", "Jeux Vidéo"), icon="🎮"),
        st.Page("pages/8_🎓_Recherche_Academique.py", title=t("nav.academic", "Recherche Académique"), icon="🎓"),
    ],
    t("nav.section_lab", "Lab"): [
        st.Page("pages/21_🧪_MediaLens_Lab.py", title=t("nav.lab_hub", "Lab Hub"), icon="🧪"),
        st.Page("pages/9_👤_Mon_Profil.py", title=t("nav.insights", "Insights & Profil"), icon="👤"),
        st.Page("pages/12_🧱_Architecture.py", title=t("nav.architecture", "Architecture & APIs"), icon="🧱"),
        st.Page("pages/13_⚙️_Dashboard_Technique.py", title=t("nav.tech_dashboard", "Dashboard Technique"), icon="⚙️"),
        st.Page("pages/16_🧪_AI_Evaluation_Lab.py", title=t("nav.eval_lab", "AI Evaluation Lab"), icon="🧪"),
        st.Page("pages/17_🔄_MLOps_et_Modèles.py", title=t("nav.mlops", "MLOps & Modèles"), icon="🔄"),
        st.Page("pages/15_🕸️_Graphe.py", title=t("nav.graph", "Graphe Relationnel"), icon="🕸️"),
        st.Page("pages/19_🎨_Design_System.py", title=t("nav.design_system", "Design System"), icon="🎨"),
    ],
    t("nav.section_plus", "Plus"): [
        st.Page("pages/11_🔀_Comparer.py", title=t("nav.compare", "Comparer"), icon="🔀"),
        st.Page("pages/14_ℹ️_A_Propos.py", title=t("nav.about", "À Propos"), icon="ℹ️"),
        st.Page("pages/18_🔒_Confidentialité_&_Sécurité.py", title=t("nav.security", "Confidentialité & Sécurité"), icon="🔒"),
    ]
}

# Charger la navigation
pg = st.navigation(pages_config)
pg.run()
