import streamlit as st
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.ui import inject_custom_css, render_hero, render_media_card, render_metric
from src.i18n import t

# Assurer l'injection CSS
inject_custom_css()

# Vérification du chargement des données
if "merged_df" not in st.session_state or "metrics" not in st.session_state:
    st.warning("⚠️ Données non initialisées. Veuillez recharger la page d'accueil.")
    st.stop()

df = st.session_state["merged_df"]
metrics = st.session_state["metrics"]
recommender = st.session_state.get("recommender")

# ─── En-tête / Hero Premium ─────────────────────────────────────
render_hero(
    title=t("home.hero_title", "MediaLens"),
    subtitle=t("home.hero_subtitle", "Découvrez votre prochaine histoire à travers le meilleur des livres, films et jeux vidéo.")
)

# ─── Recherche Universelle Dominante ───────────────────────────
st.markdown("<div style='max-width: 600px; margin: -1.5rem auto 2.5rem auto;'>", unsafe_allow_html=True)
search_query = st.text_input(
    label="Recherche universelle",
    placeholder=t("home.search_placeholder", "Rechercher un titre, un auteur, un réalisateur..."),
    label_visibility="collapsed",
    key="universal_search_input"
)
st.markdown("</div>", unsafe_allow_html=True)

if search_query:
    # Rerouter vers la page Explorer en stockant la recherche
    st.session_state["search_query_redirect"] = search_query
    st.info(f"🔍 Redirection vers l'exploration de '{search_query}'...")
    st.markdown("""
        <script>
            window.location.hash = '#explorer';
        </script>
    """, unsafe_allow_html=True)
    # Dans Streamlit, on peut aussi simplement dire à l'utilisateur de cliquer sur Explorer dans la barre de gauche
    st.session_state["active_tab_explorer"] = True

# ─── Boutons CTA Centraux ──────────────────────────────────────
col_c1, col_c2 = st.columns([1, 1])
with col_c1:
    st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
    if st.button("🧭 " + t("home.cta_explore", "Explorer le catalogue"), type="primary", use_container_width=True):
        st.session_state["search_query_redirect"] = ""
        # Reroute
    st.markdown("</div>", unsafe_allow_html=True)
with col_c2:
    st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
    if st.button("🤖 " + t("home.cta_agent", "Discuter avec l'IA"), type="secondary", use_container_width=True):
        st.info("🤖 Utilisez l'onglet **Assistant IA** dans la barre latérale.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ─── Recommandation Vedette ("À découvrir ce soir") ──────────────
st.markdown(f"### 🎬 {t('home.featured_title', 'À Découvrir ce Soir (Sélection Éditoriale)')}")
col_v1, col_v2 = st.columns([2, 3])

# Choisir un élément phare de façon stable (par exemple le livre le mieux noté ou un classique)
featured_item = None
if df is not None and not df.empty:
    # Prendre un livre culte comme Dune ou similaire, ou par défaut le premier
    classic_books = df[df["Book-Title"].str.contains("Dune|1984|Neuromancer|Foundation", case=False, na=False)]
    if not classic_books.empty:
        featured_item = classic_books.iloc[0]
    else:
        featured_item = df.iloc[0]

if featured_item is not None:
    with col_v1:
        # Affiche le média vedette
        render_media_card(
            title=featured_item.get("Book-Title", "N/A"),
            creator=featured_item.get("Book-Author", "N/A"),
            publisher=featured_item.get("Publisher", "N/A"),
            year=str(featured_item.get("Year-Of-Publication", "N/A")),
            rating=featured_item.get("Book-Rating", 8.5),
            n_ratings=featured_item.get("Number-Of-Ratings", 42),
            rating_source="Open Library",
            media_type="books"
        )
    with col_v2:
        st.markdown(f"""
        <div style='background: rgba(30, 41, 59, 0.3); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.05); height: 100%;'>
            <h4 style='color: #0D9488; margin-top: 0;'>💡 {t("home.why_featured", "Pourquoi cette suggestion ?")}</h4>
            <p style='color: #E2E8F0; font-size: 1.05rem; line-height: 1.6; margin-bottom: 1rem;'>
                Ce chef-d'œuvre incontournable de la science-fiction pose des questions profondes sur l'écologie, 
                le pouvoir et l'adaptation humaine. Il constitue le point d'ancrage parfait pour explorer 
                notre catalogue de recommandations croisées (films et jeux vidéo correspondants).
            </p>
            <span class="badge">🔥 Populaire</span>
            <span class="badge badge-success">⭐ Chef-d'œuvre</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ─── Collections & Curations Thématiques ───────────────────────
st.markdown(f"### 📁 {t('home.collections_title', 'Collections Sélectionnées')}")
col_t1, col_t2, col_t3 = st.columns(3)

with col_t1:
    st.markdown(f"""
    <div class="generic-card" style="height: 100%;">
        <h4>🌾 {t("home.coll_ecofiction", "Écofictions & Utopies")}</h4>
        <p style="margin-bottom: 1rem;">Des récits explorant les relations entre l'humanité et la biosphère à travers la science-fiction écoféministe et critique.</p>
        <span class="badge">Ursula K. Le Guin</span>
        <span class="badge">Octavia Butler</span>
    </div>
    """, unsafe_allow_html=True)

with col_t2:
    st.markdown(f"""
    <div class="generic-card" style="height: 100%;">
        <h4>💻 {t("home.coll_cyberpunk", "Cyberpunk & Réalité Virtuelle")}</h4>
        <p style="margin-bottom: 1rem;">Plongez dans des mondes corporatistes futuristes mêlant intelligence artificielle, réseaux et modifications corporelles.</p>
        <span class="badge">William Gibson</span>
        <span class="badge">Blade Runner</span>
    </div>
    """, unsafe_allow_html=True)

with col_t3:
    st.markdown(f"""
    <div class="generic-card" style="height: 100%;">
        <h4>🚀 {t("home.coll_space_opera", "Space Opera Éditorial")}</h4>
        <p style="margin-bottom: 1rem;">Des voyages spatiaux épiques et des fresques de civilisations galactiques basées sur des bases scientifiques et géopolitiques solides.</p>
        <span class="badge">Isaac Asimov</span>
        <span class="badge">Arthur C. Clarke</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ─── Bouton Surprise / Surprends-moi ───────────────────────────
st.markdown(f"### 🎲 {t('home.surprise_title', 'Une hésitation ?')}")
col_s1, col_s2 = st.columns([1, 2])
with col_s1:
    st.write(t("home.surprise_desc", "Laissez le hasard décider pour vous. Cliquez sur le bouton pour obtenir une suggestion aléatoire issue de notre base culturelle."))
    surprise_btn = st.button("🎲 " + t("home.surprise_btn", "Surprends-moi !"))
with col_s2:
    if surprise_btn and df is not None and not df.empty:
        # Sélection aléatoire
        random_row = df.sample(n=1).iloc[0]
        st.markdown(f"**✨ {t('home.surprise_result', 'Votre suggestion aléatoire :')}**")
        render_media_card(
            title=random_row.get("Book-Title", "N/A"),
            creator=random_row.get("Book-Author", "N/A"),
            publisher=random_row.get("Publisher", "N/A"),
            year=str(random_row.get("Year-Of-Publication", "N/A")),
            rating=random_row.get("Book-Rating"),
            n_ratings=random_row.get("Number-Of-Ratings"),
            rating_source="Open Library",
            media_type="books"
        )

st.markdown("<br><br>", unsafe_allow_html=True)

# ─── Statistiques Clés ──────────────────────────────────────────
st.markdown(f"### 📊 {t('home.stats_title', 'Statistiques Clés de l\'App')}")
cols = st.columns(4)
with cols[0]: render_metric(f"📖 {t('home.stat_books', 'Livres')}", f"{metrics.get('unique_books', 0):,}".replace(",", " "))
with cols[1]: render_metric(f"🎬 {t('home.stat_movies', 'Films')}", "20") # Valeur cache/mock
with cols[2]: render_metric(f"🎮 {t('home.stat_games', 'Jeux Vidéo')}", "20") # Valeur cache/mock
with cols[3]: render_metric(f"⭐ {t('home.stat_ratings', 'Note Moyenne')}", f"{metrics.get('avg_rating', 0)}/10")
