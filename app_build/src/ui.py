"""
BookLens / MediaLens — Design System & UI Components
Ce module centralise la configuration visuelle, les composants réutilisables
et les tokens graphiques pour une expérience premium "bibliothèque de nuit".
"""

import streamlit as st

# Design Tokens (pour référence ou réutilisation dynamique)
TOKENS = {
    "colors": {
        "bg_primary": "#070A13",
        "bg_sidebar": "#0C101A",
        "surface_basic": "#121826",
        "surface_elevated": "#1B2336",
        "accent_primary": "#0D9488",  # Teal
        "accent_secondary": "#F59E0B",  # Ambre
        "accent_danger": "#EF4444",    # Rouge
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8"
    },
    "radius": {
        "card": "12px",
        "button": "8px",
        "badge": "99px"
    },
    "transition": {
        "fast": "120ms ease",
        "medium": "220ms ease",
        "slow": "350ms ease"
    }
}

def inject_custom_css():
    """Injecte le CSS global propre, moderne et épuré (Style Cinéma Éditorial)."""
    reduce_motion = st.session_state.get("reduce_motion", False)
    
    motion_rules = ""
    if reduce_motion:
        motion_rules = """
        * {
            animation: none !important;
            transition: none !important;
        }
        """
    else:
        motion_rules = """
        @media (prefers-reduced-motion: reduce) {
            * {
                animation: none !important;
                transition: none !important;
            }
        }
        """

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        {motion_rules}
        
        /* Reset et base */
        .stApp {{
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: {TOKENS['colors']['bg_primary']} !important;
            color: {TOKENS['colors']['text_primary']} !important;
        }}
        
        /* Masquer la bannière supérieure et le menu Streamlit natif pour une sensation produit */
        header {{
            background-color: transparent !important;
        }}
        [data-testid="stHeader"] {{
            background-color: rgba(7, 10, 19, 0.7) !important;
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}
        
        /* Styles de la Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {TOKENS['colors']['bg_sidebar']} !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }}
        [data-testid="stSidebar"] .stMarkdown {{
            padding: 0.5rem 1rem;
        }}
        
        /* Hero Section */
        .hero-container {{
            background: linear-gradient(135deg, rgba(18, 24, 38, 0.8) 0%, rgba(7, 10, 19, 0.9) 100%);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: {TOKENS['radius']['card']};
            padding: 3rem 2rem;
            text-align: center;
            margin-bottom: 2.5rem;
            animation: fadeInUp 0.4s ease-out;
        }}
        .hero-title {{
            color: {TOKENS['colors']['text_primary']};
            font-size: 2.75rem;
            font-weight: 800;
            margin-bottom: 0.75rem;
            letter-spacing: -0.025em;
            background: linear-gradient(to right, #0D9488, #38BDF8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .hero-subtitle {{
            color: {TOKENS['colors']['text_secondary']};
            font-size: 1.1rem;
            max-width: 650px;
            margin: 0 auto;
            line-height: 1.5;
        }}
        
        /* Cartes KPI et Média */
        .kpi-card {{
            background-color: {TOKENS['colors']['surface_basic']};
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: {TOKENS['radius']['card']};
            padding: 1.25rem;
            text-align: center;
            transition: border-color {TOKENS['transition']['fast']}, transform {TOKENS['transition']['fast']};
            animation: fadeInUp 0.35s ease-out both;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(13, 148, 136, 0.4);
            background-color: {TOKENS['colors']['surface_elevated']};
        }}
        .kpi-label {{
            color: {TOKENS['colors']['text_secondary']};
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.25rem;
        }}
        .kpi-value {{
            color: {TOKENS['colors']['text_primary']};
            font-size: 1.75rem;
            font-weight: 700;
        }}
        
        /* Cartes Médias / Génériques */
        .generic-card {{
            background-color: {TOKENS['colors']['surface_basic']};
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: {TOKENS['radius']['card']};
            padding: 1.25rem;
            margin-bottom: 1.25rem;
            transition: all {TOKENS['transition']['medium']};
            animation: fadeInUp 0.35s ease-out both;
        }}
        .generic-card:hover {{
            border-color: rgba(13, 148, 136, 0.3);
            background-color: {TOKENS['colors']['surface_elevated']};
            transform: scale(1.01);
        }}
        .generic-card h4 {{
            color: {TOKENS['colors']['text_primary']};
            margin-top: 0;
            margin-bottom: 0.5rem;
            font-size: 1.15rem;
            font-weight: 600;
        }}
        .generic-card p {{
            color: {TOKENS['colors']['text_secondary']};
            font-size: 0.95rem;
            line-height: 1.5;
            margin: 0;
        }}
        
        /* Badges */
        .badge {{
            background: rgba(13, 148, 136, 0.1);
            color: #0D9488;
            padding: 0.25rem 0.6rem;
            border-radius: {TOKENS['radius']['badge']};
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid rgba(13, 148, 136, 0.2);
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }}
        .badge-warning {{
            background: rgba(245, 158, 11, 0.1);
            color: #F59E0B;
            border-color: rgba(245, 158, 11, 0.2);
        }}
        .badge-danger {{
            background: rgba(239, 68, 68, 0.1);
            color: #EF4444;
            border-color: rgba(239, 68, 68, 0.2);
        }}
        .badge-success {{
            background: rgba(16, 185, 129, 0.1);
            color: #10B981;
            border-color: rgba(16, 185, 129, 0.2);
        }}
        
        /* Source Block */
        .source-book-block {{
            background: linear-gradient(135deg, rgba(13, 148, 136, 0.1) 0%, rgba(56, 189, 248, 0.05) 100%);
            border: 1px solid rgba(13, 148, 136, 0.2);
            border-left: 4px solid #0D9488;
            padding: 1.25rem;
            border-radius: {TOKENS['radius']['card']};
            margin-bottom: 1.5rem;
        }}
        .source-book-block h3 {{
            color: {TOKENS['colors']['text_primary']};
            margin: 0 0 0.5rem 0;
            font-size: 1.25rem;
        }}
        
        /* Skeletons */
        .skeleton {{
            background: linear-gradient(90deg, #121826 25%, #1B2336 50%, #121826 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
            border-radius: 6px;
        }}
        
        /* Animations CSS */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(8px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        @keyframes loading {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
    </style>
    """, unsafe_allow_html=True)


def render_hero(title, subtitle):
    """Affiche la section Hero de la page d'accueil avec style."""
    st.markdown(f"""
    <div class="hero-container">
        <h1 class="hero-title">{title}</h1>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_metric(label, value):
    """Affiche une carte de métrique/KPI."""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_feature_card(title, description, icon=""):
    """Affiche une carte de fonctionnalité."""
    st.markdown(f"""
    <div class="generic-card">
        <h4>{icon} {title}</h4>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)


def render_media_card(title, creator, publisher="N/A", year="N/A", rating=None, n_ratings=None, similarity=None, rating_source=None, cover_url=None, media_type="books"):
    """
    Affiche une carte de média unifiée pour Livres, Films et Jeux Vidéo.
    """
    creator_emoji = "✍️" if media_type == "books" else "🎬" if media_type == "movies" else "🎮"
    publisher_emoji = "🏢" if media_type == "books" else "🎥" if media_type == "movies" else "💻"
    media_icon = "📖" if media_type == "books" else "🎬" if media_type == "movies" else "🎮"
    
    # Construction des badges
    badges_html = f'<span class="badge">{creator_emoji} {creator}</span>'
    if year and year != "N/A":
        badges_html += f'<span class="badge">📅 {year}</span>'
    if publisher and publisher != "N/A":
        badges_html += f'<span class="badge">{publisher_emoji} {publisher}</span>'
        
    stats_html = ""
    if rating is not None:
        if rating_source in ["Google Books", "Open Library", "TMDB", "RAWG", "Semantic Scholar"]:
            stats_html += f'<span class="badge badge-success">✅ {rating:.1f}/10 ({rating_source})</span> '
        else:
            stats_html += f'<span class="badge badge-warning">🤖 {rating:.1f}/10 (Estimée)</span> '
            
    if n_ratings is not None:
        stats_html += f'<span class="badge">📊 {int(n_ratings)} avis</span> '
        
    if similarity is not None:
        stats_html += f'<span class="badge badge-success">🎯 Similaire à {similarity:.1%}</span>'

    # Choix de la mise en page de la couverture
    image_style = ""
    if media_type == "games":
        image_style = "width: 100%; max-height: 180px; object-fit: cover; border-radius: 8px; margin-bottom: 0.8rem;"
        float_clear = ""
    else:
        image_style = "width: 80px; height: 120px; object-fit: cover; border-radius: 6px; float: left; margin-right: 1.25rem;"
        float_clear = '<div style="clear: both;"></div>'

    cover_html = ""
    if cover_url:
        cover_html = f'<img src="{cover_url}" style="{image_style}" alt="Cover of {title}" />'
    else:
        # Placeholder visuel moderne (gris/sombre)
        cover_html = f'<div style="{image_style} background: #1B2336; display: flex; align-items: center; justify-content: center; color: #94A3B8; font-size: 1.5rem;">{media_icon}</div>'

    st.markdown(f"""
    <div class="generic-card">
        {cover_html}
        <div>
            <h4 style="margin-top: 0; font-size: 1.2rem; color: #F8FAFC;">{media_icon} {title}</h4>
            <div style="margin-bottom: 0.8rem; display: flex; flex-wrap: wrap; gap: 0.4rem;">
                {badges_html}
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
                {stats_html}
            </div>
        </div>
        {float_clear}
    </div>
    """, unsafe_allow_html=True)


def render_source_media(title, creator, rating, n_ratings, rating_source=None, media_type="books"):
    """Affiche le média de référence sélectionné pour les recommandations."""
    if rating_source in ["Google Books", "Open Library", "TMDB", "RAWG", "Semantic Scholar"]:
        rating_html = f'<span class="badge badge-success">✅ {rating:.1f}/10 ({rating_source})</span>'
    else:
        rating_html = f'<span class="badge badge-warning">🤖 {rating:.1f}/10 (Estimée)</span>'

    creator_emoji = "✍️" if media_type == "books" else "🎬" if media_type == "movies" else "🎮"
    media_icon = "📖" if media_type == "books" else "🎬" if media_type == "movies" else "🎮"

    st.markdown(f"""
    <div class="source-book-block">
        <h3>{media_icon} {title}</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
            <span class="badge">{creator_emoji} {creator}</span>
            {rating_html}
            <span class="badge">📊 {int(n_ratings)} avis</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_book_card(title, author, publisher="N/A", year="N/A", rating=None, n_ratings=None, similarity=None, rating_source=None):
    """Méthode de compatibilité pour render_media_card."""
    render_media_card(title, author, publisher, year, rating, n_ratings, similarity, rating_source, media_type="books")


def render_source_book(title, author, rating, n_ratings, rating_source=None):
    """Méthode de compatibilité pour render_source_media."""
    render_source_media(title, author, rating, n_ratings, rating_source, media_type="books")
