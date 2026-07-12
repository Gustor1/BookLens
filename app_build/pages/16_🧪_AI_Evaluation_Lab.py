import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.ui import inject_custom_css
from src.i18n import t, language_selector
from src.evaluation.eval_dataset import load_eval_cases, get_filtered_cases
from src.evaluation.eval_runner import EvalRunner
from src.evaluation.eval_report import generate_report_stats, save_evaluation_run

# Configurer la page
st.set_page_config(page_title=t("eval.page_title", "AI Evaluation Lab — BookLens"), page_icon="🧪", layout="wide")
inject_custom_css()

# Ajouter le sélecteur de langue dans la sidebar
language_selector()

# Initialiser l'agent et le RAG si disponible
if "recommender" not in st.session_state or "merged_df" not in st.session_state:
    st.warning(t("agent.warning_load", "⚠️ Veuillez d'abord visiter la page d'accueil pour charger les données."))
    st.stop()

if "agent" not in st.session_state:
    from src.agent import BookLensAgent
    st.session_state["agent"] = BookLensAgent(
        recommender=st.session_state["recommender"],
        metrics=st.session_state.get("metrics", {}),
        merged_df=st.session_state["merged_df"],
    )
agent = st.session_state["agent"]

if "rag_service" not in st.session_state:
    from src.rag.rag_service import RAGService
    st.session_state["rag_service"] = RAGService()
rag_service = st.session_state["rag_service"]

# En-tête de la page
st.markdown(f"# {t('eval.hero_title', '🧪 AI Evaluation Lab')}")
st.markdown(f"<p style='color: #94A3B8; margin-bottom: 1.5rem;'>{t('eval.hero_subtitle', 'Mesurez objectivement la qualité des agents, des modèles et du RAG.')}</p>", unsafe_allow_html=True)

# Boîte d'information explicative
st.info(t("eval.info_text", "Le Laboratoire d'évaluation IA permet de lancer des tests d'évaluation déterministes sur les réponses de l'agent. Les scores mesurent la fidélité de routage, la qualité du RAG (citations valides) et la sécurité logicielle."))

# ─── SECTION 1 : CONFIGURATION ET FILTRES ──────────────────────
st.markdown("---")
col_cfg1, col_cfg2 = st.columns([1, 1])

# Charger les cas d'évaluation
try:
    all_cases = load_eval_cases()
except Exception as e:
    st.error(f"Erreur de chargement du dataset d'évaluation : {e}")
    st.stop()

with col_cfg1:
    exec_mode = st.radio(
        t("eval.mode_label", "Mode d'Exécution"),
        options=["mock", "single", "comparison"],
        format_func=lambda x: t(f"eval.mode_{x}"),
        horizontal=False
    )
    
    target_provider = st.selectbox(
        t("eval.provider_label", "Modèle / Provider cible"),
        options=["nvidia", "huggingface"],
        format_func=lambda x: "NVIDIA (Llama Nemotron)" if x == "nvidia" else "Hugging Face (Llama 3.2)",
        disabled=(exec_mode == "comparison")
    )

with col_cfg2:
    categories = ["All"] + sorted(list(set(c.category for c in all_cases)))
    selected_cat = st.selectbox(t("eval.category_label", "Filtrer par catégorie"), options=categories)
    
    languages = ["All"] + sorted(list(set(c.language for c in all_cases)))
    selected_lang = st.selectbox(t("eval.lang_label", "Filtrer par langue"), options=languages)
    
    # Limite maximale d'exécution API par défaut
    limit_count = st.slider(
        t("eval.limit_label", "Nombre maximal de cas de test (Sécurité)"),
        min_value=1,
        max_value=15 if exec_mode != "mock" else 36,
        value=5 if exec_mode != "mock" else 36
    )

# Filtrer les cas
filtered_cases = get_filtered_cases(all_cases, category=selected_cat, language=selected_lang)
count_to_run = min(len(filtered_cases), limit_count)

# Déterminer si exécution autorisée
run_allowed = count_to_run > 0

# Bouton de lancement avec pop-up de confirmation pour l'API réelle
if run_allowed:
    if exec_mode != "mock":
        st.warning(f"⚠️ **{t('eval.confirm_title', 'Avertissement d\'exécution API')}** : " + 
                   t("eval.confirm_body", "Vous vous apprêtez à lancer {count} requêtes LLM réelles.").format(count=count_to_run * (2 if exec_mode == "comparison" else 1)))
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            confirm_run = st.checkbox(t("eval.confirm_yes", "Oui, lancer"), value=False)
        with col_btn2:
            st.markdown(f"<p style='color: #64748B; margin-top: 5px;'>{t('eval.confirm_no', 'Cochez la case pour déverrouiller le bouton.')}</p>", unsafe_allow_html=True)
            
        launch_clicked = st.button(t("eval.launch_btn", "🚀 Lancer l'évaluation"), disabled=not confirm_run, type="primary")
    else:
        launch_clicked = st.button(t("eval.launch_btn", "🚀 Lancer l'évaluation"), type="primary")
        confirm_run = True
else:
    launch_clicked = False
    st.info("Aucun cas de test ne correspond aux filtres sélectionnés.")

# ─── SECTION 2 : EXÉCUTION DE L'ÉVALUATION ────────────────────
if launch_clicked and confirm_run:
    runner = EvalRunner(agent)
    
    with st.spinner("Exécution de la suite d'évaluation en cours..."):
        results_run = []
        
        # Mode Comparaison
        if exec_mode == "comparison":
            st.info("Lancement comparatif sur NVIDIA et Hugging Face...")
            res_nvidia = runner.run_suite(filtered_cases, "nvidia", "single", limit=limit_count, rag_service=rag_service)
            res_hf = runner.run_suite(filtered_cases, "huggingface", "single", limit=limit_count, rag_service=rag_service)
            results_run = res_nvidia + res_hf
        # Mode Provider Unique ou Mock
        else:
            results_run = runner.run_suite(filtered_cases, target_provider, exec_mode, limit=limit_count, rag_service=rag_service)
            
        # Sauvegarder localement
        if results_run:
            json_path, csv_path, md_path = save_evaluation_run(results_run)
            st.session_state["last_eval_results"] = results_run
            st.success(f"Évaluation terminée. Rapports exportés dans `data/evaluation/results/` !")

# ─── SECTION 3 : RESSORTS ET RAPPORTS ──────────────────────────
if "last_eval_results" in st.session_state:
    results = st.session_state["last_eval_results"]
    stats = generate_report_stats(results)
    
    st.markdown("---")
    st.markdown(f"## {t('eval.results_title', '📊 Résultats de la Suite d\'Évaluation')}")
    
    # KPIs en colonnes
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric(t("eval.kpi_total", "Cas exécutés"), stats.get("total_cases", 0))
    with col_kpi2:
        st.metric(t("eval.kpi_score", "Score moyen"), f"{stats.get('avg_score', 0)}/100")
    with col_kpi3:
        st.metric(t("eval.kpi_success", "Taux de réussite"), f"{stats.get('success_rate', 0)}%")
    with col_kpi4:
        st.metric(t("eval.kpi_latency", "Latence moyenne"), f"{stats.get('avg_latency_ms', 0):.0f} ms")
        
    col_kpi5, col_kpi6, col_kpi7, col_kpi8 = st.columns(4)
    with col_kpi5:
        st.metric(t("eval.kpi_fallback", "Taux de fallback"), f"{stats.get('fallback_rate', 0)}%")
    with col_kpi6:
        st.metric(t("eval.kpi_routing", "Routage correct"), f"{stats.get('correct_routing_rate', 0)}%")
    with col_kpi7:
        st.metric(t("eval.kpi_citations", "Citations RAG valides"), f"{stats.get('valid_citations_rate', 0)}%")
    with col_kpi8:
        # Couleur rouge pour les failles critiques de sécurité
        security_fails = stats.get("security_critical_failures", 0)
        st.metric(t("eval.kpi_security", "Échecs de sécurité"), security_fails, delta=-security_fails if security_fails > 0 else 0, delta_color="inverse")

    # Graphiques d'analyse
    df_results = pd.DataFrame([r.to_dict() for r in results])
    
    # Extraire les infos des cas de test correspondants
    cases_dict = {c.id: c for c in all_cases}
    df_results["category"] = df_results["case_id"].map(lambda x: cases_dict[x].category if x in cases_dict else "Unknown")
    df_results["language"] = df_results["case_id"].map(lambda x: cases_dict[x].language if x in cases_dict else "Unknown")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_plot1, col_plot2 = st.columns([1, 1])
    
    import plotly.express as px
    
    with col_plot1:
        # Score moyen par catégorie
        df_cat = df_results.groupby(["category", "provider"])["score"].mean().reset_index()
        fig_cat = px.bar(
            df_cat, 
            x="category", 
            y="score", 
            color="provider",
            barmode="group",
            title="Score moyen par catégorie",
            color_discrete_sequence=["#6366F1", "#10B981"]
        )
        fig_cat.update_layout(font_color="#E2E8F0", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_plot2:
        # Score moyen par langue
        df_lang = df_results.groupby(["language", "provider"])["score"].mean().reset_index()
        fig_lang = px.bar(
            df_lang, 
            x="language", 
            y="score", 
            color="provider",
            barmode="group",
            title="Score moyen par langue",
            color_discrete_sequence=["#8B5CF6", "#EC4899"]
        )
        fig_lang.update_layout(font_color="#E2E8F0", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_lang, use_container_width=True)

    # Zone de téléchargement des exports
    st.markdown("### 📥 Télécharger les rapports d'évaluation")
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    # Convertir en formats lisibles pour Streamlit
    json_data = json.dumps({"stats": stats, "results": [r.to_dict() for r in results]}, ensure_ascii=False, indent=2)
    csv_data = df_results[["case_id", "provider", "routing_detected", "latency_ms", "success", "score", "reasons"]].to_csv(index=False)
    
    with col_exp1:
        st.download_button(t("eval.export_json", "📥 Exporter JSON"), data=json_data, file_name=f"report_{results[0].run_id}.json", mime="application/json", use_container_width=True)
    with col_exp2:
        st.download_button(t("eval.export_csv", "📥 Exporter CSV"), data=csv_data, file_name=f"report_{results[0].run_id}.csv", mime="text/csv", use_container_width=True)
    with col_exp3:
        # Markdown
        run_id = results[0].run_id
        md_content = f"# Eval Report {run_id}\n\nSuccess Rate: {stats['success_rate']}%\nAverage Score: {stats['avg_score']}/100"
        st.download_button(t("eval.export_md", "📥 Exporter Markdown"), data=md_content, file_name=f"report_{run_id}.md", mime="text/markdown", use_container_width=True)

    # ─── SECTION 4 : TABLEAU DÉTAILLÉ PER CAS ─────────────────────
    st.markdown("---")
    st.markdown(f"### {t('eval.details_title', '📋 Détails de l\'Exécution par Cas')}")
    
    for idx, row in df_results.iterrows():
        status_color = "#10B981" if row["success"] else "#EF4444"
        badge_text = "PASSED" if row["success"] else "FAILED"
        
        # Récupérer l'entrée attendue
        case_item = cases_dict.get(row["case_id"])
        case_input = case_item.input if case_item else ""
        
        with st.expander(f"Code : `{row['case_id']}` | Score : **{row['score']}/100** | Statut : :span[{badge_text}]{{{status_color}}}"):
            c_det1, c_det2 = st.columns([1, 1])
            with c_det1:
                st.markdown(f"**Question (Input)** :\n> {case_input}")
                st.markdown(f"**Routage détecté** : `{row['routing_detected']}`")
                st.markdown(f"**Latence** : `{row['latency_ms']:.1f} ms`")
            with c_det2:
                st.markdown(f"**Modèle / Provider** : `{row['provider'].upper()}`")
                st.markdown(f"**Remarques / Échecs** :")
                if row["reasons"]:
                    for reason in row["reasons"]:
                        st.markdown(f"- ❌ {reason}")
                else:
                    st.markdown("- ✅ Tout est conforme.")
                    
            st.markdown("**Réponse de l'Agent** :")
            st.code(row["response"], language="markdown")
else:
    st.info(t("eval.empty_results", "Aucune évaluation n'a encore été lancée pour cette session."))
