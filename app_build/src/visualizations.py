"""
BookLens — Module de visualisations
Fonctions de création de graphiques avec Plotly pour l'application Streamlit.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# ─── Palette de couleurs BookLens ────────────────────────────────
COLORS = {
    "primary": "#6366F1",      # Indigo
    "secondary": "#8B5CF6",    # Violet
    "accent": "#EC4899",       # Rose
    "success": "#10B981",      # Émeraude
    "warning": "#F59E0B",      # Ambre
    "info": "#3B82F6",         # Bleu
    "bg_dark": "#1E1B4B",      # Fond sombre
}

PALETTE = [
    "#6366F1", "#8B5CF6", "#EC4899", "#F59E0B",
    "#10B981", "#3B82F6", "#EF4444", "#14B8A6"
]

LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=13),
    margin=dict(l=40, r=40, t=50, b=40),
)


def plot_rating_distribution(df):
    """
    Graphique de la distribution des ratings.

    Args:
        df: DataFrame avec colonne 'Book-Rating'.

    Returns:
        plotly.graph_objects.Figure
    """
    df_unique = df.drop_duplicates(subset=["ISBN"]).copy()
    
    # Préférer Real-Rating si disponible
    rating_col = "Book-Rating"
    if "Real-Rating" in df_unique.columns and df_unique["Real-Rating"].notna().any():
        # Utiliser Real-Rating pour les livres qui en ont, sinon fallback
        df_unique["Display-Rating"] = df_unique["Real-Rating"].fillna(df_unique["Book-Rating"])
        rating_col = "Display-Rating"
        
    fig = px.histogram(
        df_unique,
        x=rating_col,
        nbins=10,
        title="📊 Distribution des Notes (par livre)",
        labels={rating_col: "Note", "count": "Nombre"},
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig.update_layout(**LAYOUT_DEFAULTS)
    fig.update_traces(
        marker_line_color=COLORS["secondary"],
        marker_line_width=1.5,
    )
    return fig


def plot_top_books(df, n=10):
    """
    Graphique des N livres les mieux notés.

    Args:
        df: DataFrame avec colonnes 'Book-Title' et 'Book-Rating'.
        n: Nombre de livres à afficher.

    Returns:
        plotly.graph_objects.Figure
    """
    df_unique = df.drop_duplicates(subset=["ISBN"]).copy()
    
    if "Real-Rating" in df_unique.columns and df_unique["Real-Rating"].notna().any():
        df_unique["Display-Rating"] = df_unique["Real-Rating"].fillna(df_unique["Book-Rating"])
        df_unique["Display-Count"] = df_unique["Real-Rating-Count"].fillna(1)
        
        top = (
            df_unique.query("`Display-Count` >= 2")
            .groupby("Book-Title")["Display-Rating"]
            .mean()
            .sort_values(ascending=True)
            .dropna()
            .tail(n)
        )
    else:
        top = (
            df.groupby("Book-Title")["Book-Rating"]
            .agg(["mean", "count"])
            .query("count >= 2")
            .sort_values("mean", ascending=True)
            .tail(n)["mean"]
        )

    fig = go.Figure(go.Bar(
        x=top.values,
        y=top.index,
        orientation="h",
        marker=dict(
            color=top.values,
            colorscale=[[0, COLORS["info"]], [1, COLORS["accent"]]],
        ),
        text=[f"{v:.1f}" for v in top.values],
        textposition="auto",
    ))

    fig.update_layout(
        title=f"🏆 Top {n} des Livres les Mieux Notés",
        xaxis_title="Note Moyenne",
        yaxis_title="",
        **LAYOUT_DEFAULTS,
    )
    return fig


def plot_top_authors(df, n=10):
    """
    Graphique des N auteurs les plus populaires (par nombre de ratings).

    Args:
        df: DataFrame avec colonnes 'Book-Author' et 'Book-Rating'.
        n: Nombre d'auteurs à afficher.

    Returns:
        plotly.graph_objects.Figure
    """
    top = (
        df.groupby("Book-Author")["Book-Rating"]
        .count()
        .sort_values(ascending=True)
        .tail(n)
    )

    fig = go.Figure(go.Bar(
        x=top.values,
        y=top.index,
        orientation="h",
        marker=dict(
            color=top.values,
            colorscale=[[0, COLORS["secondary"]], [1, COLORS["success"]]],
        ),
        text=top.values,
        textposition="auto",
    ))

    fig.update_layout(
        title=f"✍️ Top {n} Auteurs les Plus Populaires",
        xaxis_title="Nombre de Notes",
        yaxis_title="",
        **LAYOUT_DEFAULTS,
    )
    return fig


def plot_ratings_per_year(df):
    """
    Graphique du nombre de ratings par année de publication.

    Args:
        df: DataFrame avec colonnes 'Year-Of-Publication' et 'Book-Rating'.

    Returns:
        plotly.graph_objects.Figure
    """
    df_valid = df.dropna(subset=["Year-Of-Publication"])
    df_valid = df_valid[
        (df_valid["Year-Of-Publication"] >= 1950) &
        (df_valid["Year-Of-Publication"] <= 2024)
    ].copy()

    per_year = (
        df_valid.groupby("Year-Of-Publication")["Book-Rating"]
        .count()
        .reset_index()
    )
    per_year.columns = ["Année", "Nombre de ratings"]

    fig = px.area(
        per_year,
        x="Année",
        y="Nombre de ratings",
        title="📅 Ratings par Année de Publication",
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig.update_layout(**LAYOUT_DEFAULTS)
    fig.update_traces(
        fillcolor="rgba(99, 102, 241, 0.3)",
        line=dict(color=COLORS["primary"], width=2),
    )
    return fig


def plot_age_distribution(df):
    """
    Graphique de la distribution des âges des utilisateurs.

    Args:
        df: DataFrame avec colonne 'Age'.

    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.histogram(
        df,
        x="Age",
        nbins=20,
        title="👤 Distribution des Âges des Utilisateurs",
        labels={"Age": "Âge", "count": "Nombre"},
        color_discrete_sequence=[COLORS["secondary"]],
    )
    fig.update_layout(**LAYOUT_DEFAULTS)
    fig.update_traces(
        marker_line_color=COLORS["primary"],
        marker_line_width=1,
    )
    return fig


def plot_rating_by_age_group(df):
    """
    Graphique de la note moyenne par tranche d'âge.

    Args:
        df: DataFrame avec colonnes 'Age' et 'Book-Rating'.

    Returns:
        plotly.graph_objects.Figure
    """
    df_copy = df.copy()
    bins = [0, 18, 25, 35, 45, 55, 65, 100]
    labels = ["<18", "18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
    df_copy["Tranche d'âge"] = pd.cut(df_copy["Age"], bins=bins, labels=labels)

    avg_by_age = (
        df_copy.groupby("Tranche d'âge", observed=True)["Book-Rating"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        avg_by_age,
        x="Tranche d'âge",
        y="Book-Rating",
        title="📈 Note Moyenne par Tranche d'Âge",
        labels={"Book-Rating": "Note moyenne", "Tranche d'âge": "Tranche d'âge"},
        color="Book-Rating",
        color_continuous_scale=[[0, COLORS["info"]], [1, COLORS["accent"]]],
    )
    fig.update_layout(**LAYOUT_DEFAULTS)
    return fig


def plot_publisher_distribution(df, n=10):
    """
    Graphique des éditeurs les plus représentés.

    Args:
        df: DataFrame avec colonne 'Publisher'.
        n: Nombre d'éditeurs à afficher.

    Returns:
        plotly.graph_objects.Figure
    """
    if "Publisher" not in df.columns:
        return go.Figure().update_layout(title="Données éditeurs non disponibles")

    top_publishers = df["Publisher"].value_counts().head(n)

    fig = px.pie(
        values=top_publishers.values,
        names=top_publishers.index,
        title=f"📚 Top {n} Éditeurs",
        color_discrete_sequence=PALETTE,
        hole=0.4,
    )
    fig.update_layout(**LAYOUT_DEFAULTS)
    fig.update_traces(textinfo="label+percent", textposition="outside")
    return fig
