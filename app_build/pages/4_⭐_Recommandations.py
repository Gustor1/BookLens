import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from src.ui import inject_custom_css, render_book_card, render_source_book
from src.i18n import t, language_selector
from src.user_profile import UserProfileManager

st.set_page_config(page_title=t("recs.page_title", "Recommandations — BookLens"), page_icon="⭐", layout="wide")
inject_custom_css()

# Sélecteur de langue dans la sidebar
language_selector()

# Vérification
if "recommender" not in st.session_state:
    st.warning("⚠️ Veuillez d'abord visiter la page d'accueil pour charger le modèle.")
    st.stop()

recommender = st.session_state["recommender"]

# ─── En-tête ────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-container" style="padding: 2rem;">
    <h2 class="hero-title" style="font-size: 2.2rem;">{t("recs.hero_title", "⭐ Recommandations Hybrides")}</h2>
    <p class="hero-subtitle">{t("recs.hero_subtitle", "Sélectionnez un livre et découvrez des suggestions basées sur le filtrage collaboratif et la similarité de contenu.")}</p>
</div>
""", unsafe_allow_html=True)

st.info(t("recs.cloud_storage_warning", "💡 En mode cloud (Streamlit Community Cloud), vos préférences de personnalisation sont stockées de façon temporaire dans votre session et seront réinitialisées lors du redémarrage de l'application. Pour une persistance durable, exécutez le projet localement."))

# ─── Sélection du livre ─────────────────────────────────────────
book_list = recommender.get_book_list()

if not book_list:
    st.error(t("recs.no_data", "❌ Le modèle n'a pas assez de données pour faire des recommandations."))
    st.stop()

# Reset preferences button
col_reset1, col_reset2 = st.columns([8, 2])
with col_reset2:
    if st.button(t("recs.reset_pref", "🔄 Réinitialiser les préférences"), use_container_width=True):
        UserProfileManager.reset_feedbacks()
        st.toast(t("recs.reset_toast", "Préférences réinitialisées avec succès !"))
        st.rerun()

col1, col2, col3 = st.columns([3, 1, 2])

with col1:
    selected_book = st.selectbox(
        t("recs.choose_book", "📚 Choisissez un livre source"),
        options=book_list,
        key="book_select"
    )

with col2:
    n_recs = st.number_input(
        t("recs.num_results", "Nombre de résultats"),
        min_value=1,
        max_value=20,
        value=5,
        key="n_recs"
    )

with col3:
    themes = recommender.get_available_themes()
    theme_options = [t("recs.all_themes", "Tous les thèmes")] + themes
    selected_theme = st.selectbox(
        t("recs.filter_theme", "🏷️ Filtrer par thème"),
        options=theme_options,
        key="theme_filter"
    )

st.markdown("---")

# ─── Livre sélectionné ──────────────────────────────────────────
if selected_book:
    info = recommender.get_book_info(selected_book)

    if info:
        render_source_book(
            title=info['title'],
            author=info['author'],
            rating=info.get('real_rating', info['avg_rating']),
            n_ratings=info.get('real_rating_count', info['num_ratings']),
            rating_source=info.get('rating_source', 'Estimée')
        )
        # Afficher thème et description si disponibles
        extra_info = []
        if info.get("theme"):
            extra_info.append(f"🏷️ **{t('recs.theme', 'Thème')}** : {info['theme']}")
        if info.get("type"):
            extra_info.append(f"📑 **{t('recs.type', 'Type')}** : {info['type']}")
        if extra_info:
            st.markdown(" · ".join(extra_info))

    # ─── Recommandations ────────────────────────────────────────
    st.markdown(f"### {t('recs.selections', '🎯 Sélections personnalisées pour vous')}")
    st.markdown("<br>", unsafe_allow_html=True)

    theme_filter = None if selected_theme == t("recs.all_themes", "Tous les thèmes") or selected_theme == "Tous les thèmes" else selected_theme
    recs = recommender.get_recommendations(selected_book, n=n_recs, theme_filter=theme_filter)

    # Reranking personnalisé
    recs = UserProfileManager.rerank_recommendations(recs, "book", recommender)

    if recs is not None and not recs.empty:
        for i, row in recs.iterrows():
            similarity = row.get("Personalized-Score", row.get("Similarity-Score", 0))
            avg_rating = row.get("Avg-Rating", None)
            num_ratings = row.get("Num-Ratings", None)
            author = row.get("Author", "Inconnu")
            theme = row.get("Theme", "")
            reason = row.get("Personalization-Reason", "")

            render_book_card(
                title=f"#{i+1} — {row['Book-Title']}",
                author=author,
                rating=avg_rating if isinstance(avg_rating, (int, float)) else None,
                n_ratings=num_ratings if isinstance(num_ratings, (int, float)) else None,
                similarity=similarity,
                rating_source=row.get("Rating-Source", "Estimée")
            )
            
            # Thème badge et Raison de personnalisation
            badge_cols = st.columns([1, 1])
            with badge_cols[0]:
                if theme and pd.notna(theme):
                    st.markdown(f'<span style="color:#10B981; font-size:0.85rem;">🏷️ {theme}</span>', unsafe_allow_html=True)
            with badge_cols[1]:
                if reason:
                    st.markdown(f'<span style="color:#6366F1; font-size:0.85rem; font-weight:bold;">💡 {reason}</span>', unsafe_allow_html=True)

            # Feedback buttons
            fb_col1, fb_col2, fb_col3, fb_col4, fb_col5 = st.columns([1, 1, 1, 1, 6])
            rec_title = row["Book-Title"]
            with fb_col1:
                if st.button("❤️", key=f"fav_{i}", help=t("recs.help_fav", "Ajouter aux favoris")):
                    UserProfileManager.save_feedback("book", rec_title, "favorite")
                    st.toast(f"❤️ '{rec_title}' " + t("recs.toast_fav", "ajouté aux favoris"))
                    st.rerun()
            with fb_col2:
                if st.button("👍", key=f"like_{i}", help=t("recs.help_like", "J'aime")):
                    UserProfileManager.save_feedback("book", rec_title, "like")
                    st.toast(f"👍 '{rec_title}' " + t("recs.toast_like", "aimé"))
                    st.rerun()
            with fb_col3:
                if st.button("👎", key=f"dislike_{i}", help=t("recs.help_dislike", "Je n'aime pas")):
                    UserProfileManager.save_feedback("book", rec_title, "dislike")
                    st.toast(f"❌ '{rec_title}' " + t("recs.toast_dislike", "écarté"))
                    st.rerun()
            with fb_col4:
                if st.button("📖", key=f"read_{i}", help=t("recs.help_read", "Déjà lu")):
                    UserProfileManager.save_feedback("book", rec_title, "read")
                    st.toast(f"📖 '{rec_title}' " + t("recs.toast_read", "marqué comme lu"))
                    st.rerun()

            # Barre de progression
            sim_pct = max(0.0, min(1.0, float(similarity)))
            st.progress(sim_pct)
            st.markdown("<br>", unsafe_allow_html=True)

        # ─── Export PDF ─────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            from src.export_pdf import generate_recommendations_pdf
            pdf_bytes = generate_recommendations_pdf(selected_book, recs)
            
            st.download_button(
                label=t("recs.export_pdf", "📥 Exporter la sélection en PDF"),
                data=pdf_bytes,
                file_name=f"Recommandations_BookLens_{selected_book.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"Export PDF non disponible : {e}")

        # ─── Explication détaillée ──────────────────────────────
        st.markdown("---")
        st.markdown(f"### {t('recs.understand_algo', '💡 Comprendre l\'algorithme')}")

        with st.expander(t("recs.how_it_works", "🔬 Comment fonctionne le modèle hybride ?"), expanded=False):
            eval_m = recommender.get_eval_metrics()
            st.markdown(f"""
            **{t('recs.hybrid_model', 'Le Modèle Hybride BookLens')}** {t('recs.combines_two', 'combine deux approches complémentaires :')}

            1. **{t('recs.collab_title', 'Filtrage Collaboratif')} ({eval_m.get('alpha_collab', 0.7):.0%} {t('recs.collab_score', 'du score')})** : {t('recs.collab_desc', 'Compare les livres selon les notes des lecteurs. Deux livres sont similaires si les mêmes lecteurs leur ont donné les mêmes notes.')}
            2. **{t('recs.content_title', 'Similarité de Contenu')} ({eval_m.get('alpha_content', 0.3):.0%} {t('recs.content_score', 'du score')})** : {t('recs.content_desc', 'Compare les livres selon leurs métadonnées (auteur, thème, description) via TF-IDF.')}
            3. **{t('recs.feedback_title', 'Personnalisation & Feedback')}** : {t('recs.feedback_desc', 'Vos interactions (likes, dislikes, favoris, déjà lu) ajustent en temps réel les scores de recommandation.')}
            
            | {t('recs.tbl_metric', 'Métrique')} | {t('recs.tbl_value', 'Valeur')} |
            |---|---|
            | {t('recs.tbl_coverage', 'Couverture')} | {eval_m.get('coverage', 0):.1%} |
            | {t('recs.tbl_density', 'Densité matrice')} | {eval_m.get('matrix_density', 0):.2%} |
            | {t('recs.tbl_diversity', 'Diversité')} | {eval_m.get('avg_recommendation_diversity', 0):.1%} |
            """)

        if len(recs) > 0:
            with st.expander(t("recs.tech_explanation", "📝 Explication technique du 1er résultat")):
                top_rec = recs.iloc[0]["Book-Title"]
                explanation = recommender.explain_recommendation(
                    selected_book, top_rec
                )
                st.markdown(explanation)
    else:
        st.info(t("recs.no_recs_filters", "📚 Pas assez de données pour générer des recommandations pertinentes pour ce livre avec ces filtres."))
