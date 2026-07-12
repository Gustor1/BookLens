import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.ui import inject_custom_css
from src.i18n import t
from src.monitoring import get_metrics, get_recent_logs, clear_metrics

st.set_page_config(page_title=t("dash_tech.page_title", "Dashboard Technique — BookLens"), page_icon="📊", layout="wide")
inject_custom_css()

# En-tête
st.markdown(f"# {t('dash_tech.hero_title', '📊 Dashboard Technique & Admin')}")
st.markdown(f"<p style='color: #94A3B8; margin-bottom: 2rem;'>{t('dash_tech.hero_subtitle', 'Suivez les performances des APIs, les temps de réponse et les logs structurés en direct.')}</p>", unsafe_allow_html=True)

# Charger les données de télémétrie
metrics = get_metrics()
apis_data = metrics.get("apis", {})

# Calculs globaux
total_calls = sum(api.get("calls", 0) for api in apis_data.values())
total_errors = sum(api.get("errors", 0) for api in apis_data.values())
error_rate = (total_errors / total_calls) if total_calls > 0 else 0.0

active_provider = st.session_state.get("llm_provider", "nvidia").upper()

# ─── MÉTRO-CARDS ───────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{t('dash_tech.total_calls', 'Total Appels API')}</div>
        <div class="metric-value">{total_calls}</div>
    </div>""", unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{t('dash_tech.error_rate', 'Taux d\'erreur')}</div>
        <div class="metric-value" style="color: {'#EF4444' if error_rate > 0.1 else '#10B981'};">{error_rate:.1%}</div>
    </div>""", unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{t('dash_tech.active_provider', 'Provider Chat Actif')}</div>
        <div class="metric-value" style="color: #60A5FA; font-size: 1.8rem;">{active_provider}</div>
    </div>""", unsafe_allow_html=True)

with m4:
    # Calculer le temps de réponse moyen global
    total_lat = sum(api.get("total_latency", 0.0) for api in apis_data.values())
    avg_lat = (total_lat / total_calls) if total_calls > 0 else 0.0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{t('dash_tech.avg_latency', 'Latence Globale')}</div>
        <div class="metric-value">{avg_lat:.3f} s</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── GRAPHIQUES & TABLEAU DE DÉTAIL ───────────────────────────
if total_calls == 0:
    st.info(t("dash_tech.no_data", "Aucune donnée de télémétrie disponible pour le moment. Interrogez l'Agent IA ou parcourez l'application pour générer des appels API."))
else:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown(f"#### 📈 {t('dash_tech.calls_dist', 'Distribution des Appels')}")
        labels = list(apis_data.keys())
        values = [api.get("calls", 0) for api in apis_data.values()]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=.4,
            textinfo='percent+label',
            marker=dict(colors=['#6366F1', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#3B82F6', '#06B6D4'])
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E2E8F0'),
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        st.markdown(f"#### ⏱️ {t('dash_tech.latencies_comp', 'Latence Moyenne par API (secondes)')}")
        apis = list(apis_data.keys())
        latencies = [api.get("avg_latency", 0.0) for api in apis_data.values()]
        
        fig = go.Figure(data=[go.Bar(
            x=apis,
            y=latencies,
            marker_color='#60A5FA',
            text=[f"{l:.3f}s" for l in latencies],
            textposition='auto'
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E2E8F0'),
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis=dict(gridcolor='#1E293B'),
            yaxis=dict(gridcolor='#1E293B'),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    # Tableau de détail
    st.markdown(f"#### 📋 {t('dash_tech.detail_table', 'Détails des performances par API')}")
    
    # Créer un DataFrame pour affichage propre
    table_rows = []
    for api_name, api in apis_data.items():
        table_rows.append({
            "API/Provider": api_name,
            t("dash_tech.col_calls", "Appels"): api.get("calls", 0),
            t("dash_tech.col_success", "Succès"): api.get("success", 0),
            t("dash_tech.col_errors", "Erreurs"): api.get("errors", 0),
            t("dash_tech.col_latency", "Latence Moyenne"): f"{api.get('avg_latency', 0.0):.3f} s"
        })
    st.dataframe(table_rows, use_container_width=True, hide_index=True)

# ─── CONSOLE DE LOGS EN DIRECT ─────────────────────────────────
st.markdown("---")
st.markdown(f"#### 🪵 {t('dash_tech.live_logs', 'Live Logs - logs/app.log (15 dernières entrées JSON)')}")

logs = get_recent_logs(15)
if logs:
    log_text = "\n".join(logs)
    st.code(log_text, language="json")
else:
    st.code("{}", language="json")

# Bouton de reset
col_actions1, col_actions2 = st.columns([8, 2])
with col_actions2:
    if st.button(t("dash_tech.reset_btn", "🗑️ Réinitialiser les Métriques"), use_container_width=True):
        clear_metrics()
        st.rerun()
