"""
BookLens — Graphe de Connexions Thématiques
Visualisation réseau avec NetworkX et Plotly.
"""

import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from src.ui import inject_custom_css

st.set_page_config(page_title="Graphe Thématique — BookLens", page_icon="🕸️", layout="wide")
inject_custom_css()

if "recommender" not in st.session_state or "merged_df" not in st.session_state:
    st.warning("⚠️ Veuillez d'abord visiter la page d'accueil pour charger les données.")
    st.stop()

recommender = st.session_state["recommender"]
df = st.session_state["merged_df"]

st.markdown("""
<div class="hero-container" style="padding: 2rem;">
    <h2 class="hero-title" style="font-size: 2.2rem;">🕸️ Graphe de Connexions Thématiques</h2>
    <p class="hero-subtitle">Visualisez les liens sémantiques et collaboratifs entre les œuvres.</p>
</div>
""", unsafe_allow_html=True)

# ─── Contrôles ──────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    themes = recommender.get_available_themes()
    selected_theme = st.selectbox("Thème principal à explorer", options=["Tous les thèmes"] + themes)
with col2:
    max_nodes = st.slider("Nombre max de livres (Noeuds)", 10, 150, 50)
with col3:
    sim_threshold = st.slider("Seuil de similarité (Arêtes)", 0.05, 1.0, 0.1, step=0.05)

st.markdown("---")

# ─── Génération du Graphe ───────────────────────────────────────
if not recommender.is_fitted or recommender.content_similarity_df is None or recommender.content_similarity_df.empty:
    st.info("Le modèle hybride n'a pas pu construire de matrice de similarité. Générez plus de données ou relancez le modèle.")
    st.stop()

with st.spinner("Construction du graphe interactif..."):
    # 1. Sélectionner les noeuds
    sim_df = recommender.content_similarity_df
    available_books = list(sim_df.index)
    
    # Filtrer par thème si demandé
    if selected_theme != "Tous les thèmes":
        themed_books = recommender.book_metadata[
            recommender.book_metadata["Theme"] == selected_theme
        ].index
        available_books = [b for b in available_books if b in themed_books]
    
    # Limiter le nombre
    available_books = available_books[:max_nodes]
    
    if len(available_books) < 2:
        st.warning("Pas assez de livres trouvés pour ce thème afin de dessiner un graphe.")
        st.stop()

    # 2. Construire NetworkX
    G = nx.Graph()
    for book in available_books:
        info = recommender.get_book_info(book)
        G.add_node(
            book,
            title=book,
            author=info.get("author", "Inconnu"),
            rating=info.get("avg_rating", 0),
            theme=info.get("theme", "Inconnu")
        )
        
    # Ajouter arêtes
    sub_sim = sim_df.loc[available_books, available_books]
    for i in range(len(available_books)):
        for j in range(i+1, len(available_books)):
            b1 = available_books[i]
            b2 = available_books[j]
            w = sub_sim.loc[b1, b2]
            if w >= sim_threshold:
                G.add_edge(b1, b2, weight=w)
                
    # 3. Positionnement (Spring Layout)
    pos = nx.spring_layout(G, seed=42, k=0.5)
    
    # 4. Plotly Traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#CBD5E1'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    
    theme_colors = {
        "Féminisme": "#EC4899",
        "Écoféminisme": "#10B981",
        "Science-Fiction": "#8B5CF6",
        "Dystopie": "#F59E0B",
        "Inconnu": "#64748B"
    }
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        attrs = G.nodes[node]
        node_text.append(f"<b>{attrs['title']}</b><br>Auteur: {attrs['author']}<br>Thème: {attrs['theme']}<br>Note: {attrs['rating']:.1f}/10")
        
        # Color by theme
        c = theme_colors.get(attrs['theme'], "#3B82F6")
        node_color.append(c)
        
        # Size by degree
        deg = len(list(G.neighbors(node)))
        node_size.append(10 + deg * 3)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text' if max_nodes <= 30 else 'markers',
        text=[G.nodes[n]['title'] if max_nodes <= 30 else "" for n in G.nodes()],
        textposition="top center",
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line_width=2,
            line_color='#1E293B'
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title=dict(text='', font=dict(size=16)),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
             )
             
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.markdown("""
<div class="generic-card">
    <h4>💡 Interprétation du graphe</h4>
    <ul>
        <li><strong>Noeuds</strong> : Chaque point est un livre. Plus un point est gros, plus il est sémantiquement lié à d'autres livres (hub thématique).</li>
        <li><strong>Arêtes (Lignes)</strong> : Deux livres sont reliés si leur similarité textuelle dépasse le seuil choisi.</li>
        <li><strong>Couleurs</strong> : Les couleurs représentent les différents thèmes (vert=écoféminisme, rose=féminisme, violet=SF, etc).</li>
    </ul>
</div>
""", unsafe_allow_html=True)
