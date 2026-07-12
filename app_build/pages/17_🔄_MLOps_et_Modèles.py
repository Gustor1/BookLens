import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.ui import inject_custom_css
from src.i18n import t, language_selector
from src.mlops.experiment_tracker import ExperimentTracker
from src.mlops.model_registry import ModelRegistry
from src.mlops.drift_monitor import DriftMonitor
from src.mlops.training_service import TrainingService

# Configurer la page
st.set_page_config(page_title=t("mlops.page_title", "MLOps & Modèles — BookLens"), page_icon="📊", layout="wide")
inject_custom_css()

# Sélecteur de langue dans la sidebar
language_selector()

# Récupérer les données globales
if "merged_df" not in st.session_state or "recommender" not in st.session_state:
    st.warning(t("agent.warning_load", "⚠️ Veuillez d'abord visiter la page d'accueil pour charger les données."))
    st.stop()

df = st.session_state["merged_df"]
recommender = st.session_state["recommender"]

st.markdown(f"# {t('mlops.hero_title', '📊 MLOps & Gestion des Modèles')}")
st.markdown(f"<p style='color: #94A3B8; margin-bottom: 1.5rem;'>{t('mlops.hero_subtitle', 'Suivez le cycle de vie, la dérive de données et réentraînez le moteur de recommandation.')}</p>", unsafe_allow_html=True)

# Créer les onglets
tab1, tab2, tab3 = st.tabs([
    t("mlops.tab_production", "🚀 Production & Réentraînement"),
    t("mlops.tab_registry", "📋 Registre des Expériences"),
    t("mlops.tab_drift", "🔍 Analyse de Dérive (Drift)")
])

# ─── ONGLET 1 : PRODUCTION & RÉENTRAÎNEMENT ──────────────────
with tab1:
    st.markdown(f"### {t('mlops.prod_title', 'Modèle de Production Actif')}")
    
    # Récupérer les infos du modèle actif
    active_hybrid = ModelRegistry.get_active_model("hybrid_model")
    
    if active_hybrid:
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(t("mlops.active_name", "Nom du Modèle"), "Hybrid Recommender")
        with col_m2:
            st.metric(t("mlops.active_version", "Version Active"), f"v{active_hybrid['version']}")
        with col_m3:
            st.metric(t("mlops.active_run", "ID du Run associé"), active_hybrid["run_id"])
            
        # Métriques de ce modèle actif
        st.markdown(f"#### {t('mlops.metrics_title', 'Métriques d\'Évaluation Actuelles')}")
        metrics = active_hybrid.get("metrics", {})
        col_met1, col_met2, col_met3 = st.columns(3)
        with col_met1:
            st.metric(t("mlops.metric_coverage", "Couverture (Coverage)"), f"{metrics.get('coverage', 0.0) * 100:.1f}%")
        with col_met2:
            st.metric(t("mlops.metric_density", "Densité Matricielle"), f"{metrics.get('matrix_density', 0.0) * 100:.2f}%")
        with col_met3:
            st.metric(t("mlops.metric_diversity", "Diversité de recommandation"), f"{metrics.get('avg_recommendation_diversity', 0.0) * 100:.1f}%")
    else:
        st.info(t("mlops.no_active_model", "Aucun modèle n'est actuellement marqué comme actif dans le registre. Le système utilise le fichier par défaut de la session."))
        if st.button(t("mlops.init_registry", "Initialiser le registre avec le modèle courant")):
            # Enregistrer le modèle courant de la session
            current_metrics = recommender.get_eval_metrics() if recommender.is_fitted else {"coverage": 1.0, "matrix_density": 0.04, "avg_recommendation_diversity": 0.25}
            run_info = ExperimentTracker.log_run("hybrid_model", {"min_ratings": 3, "alpha": 0.7}, current_metrics, len(df), "initial_hash")
            ModelRegistry.register_model("", "hybrid_model", 1, current_metrics, run_info["run_id"])
            ModelRegistry.promote_to_active("hybrid_model", 1)
            st.success("Registre initialisé avec succès !")
            st.rerun()

    # Formulaire de réentraînement
    st.markdown("---")
    st.markdown(f"### {t('mlops.retrain_title', '🔄 Action : Réentraîner le modèle')}")
    st.write(t("mlops.retrain_desc", "Le réentraînement analyse le dataset chargé en mémoire et génère un nouveau modèle candidat dans le registre."))
    
    selected_strategy = st.selectbox(
        t("mlops.strategy_label", "Choisir la stratégie de modèle"),
        options=["hybrid", "content_based", "popularity"]
    )
    
    confirm_retrain = st.checkbox(t("mlops.confirm_checkbox", "Je confirme vouloir lancer le réentraînement du modèle localement."))
    
    if st.button(t("mlops.retrain_btn", "Lancer le réentraînement"), disabled=not confirm_retrain):
        with st.spinner("Entraînement en cours (TF-IDF & Matrices de similarité)..."):
            try:
                run_info = TrainingService.train_and_register(df, strategy=selected_strategy)
                st.success(f"Entraînement terminé ! Run ID : `{run_info['run_id']}` enregistré dans le registre.")
                
                # Recharger le modèle dans la session si c'est l'hybride
                if selected_strategy == "hybrid":
                    # Charger le modèle actif pour que la session Streamlit soit immédiatement à jour
                    active_model = ModelRegistry.get_active_model("hybrid_model")
                    if active_model:
                        recommender.load()
                        
                st.rerun()
            except Exception as e:
                st.error(f"Erreur d'entraînement : {e}")

# ─── ONGLET 2 : HISTORIQUE DES EXPÉRIENCES ────────────────────
with tab2:
    st.markdown(f"### {t('mlops.registry_title', '📋 Registre des Modèles & Historique des Runs')}")
    
    runs = ExperimentTracker.get_all_runs()
    
    if runs:
        df_runs = pd.DataFrame(runs)
        
        # Aplatir les paramètres et métriques pour l'affichage
        df_runs["strategy"] = df_runs["params"].map(lambda x: x.get("strategy", "hybrid"))
        df_runs["alpha"] = df_runs["params"].map(lambda x: x.get("alpha", 0.7))
        df_runs["coverage"] = df_runs["metrics"].map(lambda x: f"{x.get('coverage', 0.0) * 100:.1f}%")
        df_runs["density"] = df_runs["metrics"].map(lambda x: f"{x.get('matrix_density', 0.0) * 100:.2f}%")
        df_runs["diversity"] = df_runs["metrics"].map(lambda x: f"{x.get('avg_recommendation_diversity', 0.0) * 100:.1f}%")
        
        # Sélectionner les colonnes pour l'affichage
        display_cols = ["run_id", "model_name", "strategy", "timestamp", "dataset_size", "alpha", "coverage", "density", "diversity"]
        st.dataframe(df_runs[display_cols], use_container_width=True)
        
        # Promotion d'un modèle en production
        st.markdown(f"#### {t('mlops.promote_title', 'Promouvoir une version spécifique en Production')}")
        registry = ModelRegistry.get_registry()
        if registry:
            model_options = [f"{item['model_name']} (v{item['version']}) - Status: {item['status']}" for item in registry]
            selected_model_str = st.selectbox(t("mlops.promote_select", "Sélectionner le modèle à activer"), options=model_options)
            
            # Extraire le nom et la version
            selected_idx = model_options.index(selected_model_str)
            target_item = registry[selected_idx]
            
            if st.button(t("mlops.promote_btn", "Promouvoir ce modèle"), disabled=(target_item["status"] == "active")):
                success = ModelRegistry.promote_to_active(target_item["model_name"], target_item["version"])
                if success:
                    st.success(f"Le modèle `{target_item['model_name']} v{target_item['version']}` a été promu avec succès en production !")
                    st.rerun()
                else:
                    st.error("Échec de la promotion du modèle.")
    else:
        st.info(t("mlops.no_runs", "Aucune expérimentation enregistrée."))

# ─── ONGLET 3 : ANALYSE DE DÉRIVE (DRIFT) ─────────────────────
with tab3:
    st.markdown(f"### {t('mlops.drift_title', '🔍 Détection de Dérive de Données')}")
    
    # Rapport de santé des données
    health = DriftMonitor.analyze_dataset_health(df)
    
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        st.metric(t("mlops.health_status", "Statut de Santé"), health["status"].upper(), delta=None if health["status"] == "healthy" else "Warning")
    with col_h2:
        st.metric(t("mlops.health_rows", "Lignes analysées"), health["total_rows"])
    with col_h3:
        st.metric(t("mlops.health_anomalies", "Anomalies de notes"), health["invalid_ratings_count"])
        
    st.markdown("#### Taux de valeurs manquantes par colonne (%)")
    st.bar_chart(pd.Series(health["missing_rates"]))
    
    # Comparaison de drift avec un sous-ensemble historique simulé (50% de taille)
    st.markdown("#### Simulation de dérive sur les données")
    if len(df) > 50:
        # On simule un dataset historique de référence en prenant les 50% premières lignes
        ref_df = df.iloc[:len(df)//2]
        cur_df = df.iloc[len(df)//2:]
        
        drift_metrics = DriftMonitor.calculate_distribution_drift(ref_df, cur_df)
        
        col_dr1, col_dr2, col_dr3 = st.columns(3)
        with col_dr1:
            st.metric(t("mlops.drift_rating", "Dérive de la Note Moyenne"), drift_metrics["rating_mean_drift"])
        with col_dr2:
            st.metric(t("mlops.drift_theme", "Dérive de Distribution de Thème"), drift_metrics["theme_drift_magnitude"])
        with col_dr3:
            drift_status = "OUI" if drift_metrics["drift_detected"] else "NON"
            st.metric(t("mlops.drift_detected", "Dérive détectée (>0.15)"), drift_status)
    else:
        st.info("Pas assez de données pour simuler le calcul de dérive.")
