"""
BookLens — Module de recommandation hybride (Machine Learning)
Combine filtrage collaboratif (cosinus) et similarité de contenu (auteur, thème).

Approche :
1. Filtrage collaboratif classique (matrice User × Book + cosinus)
2. Similarité de contenu (TF-IDF sur auteur + thème + description)
3. Score hybride pondéré (alpha * collab + (1-alpha) * contenu)
4. Feedback utilisateur (like/dislike) pour ajuster les scores
5. Évaluation quantitative (couverture, précision)
"""

import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import pickle

# Répertoire des modèles
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
PRODUCTION_DIR = os.path.join(
    os.path.dirname(BASE_DIR), "production_artifacts"
)


class BookRecommender:
    """
    Système de recommandation hybride de livres.

    Combine :
    - Filtrage collaboratif (similarité cosinus sur la matrice user-item)
    - Similarité de contenu (TF-IDF sur auteur + thème)
    - Feedback utilisateur (like/dislike dynamique)
    """

    def __init__(self, min_ratings=3, alpha=0.7):
        """
        Args:
            min_ratings: Nombre minimum de ratings pour inclure un livre.
            alpha: Pondération du filtrage collaboratif vs contenu (0-1).
                   0.7 = 70% collab + 30% contenu.
        """
        self.min_ratings = min_ratings
        self.alpha = alpha
        self.matrix = None
        self.similarity_df = None
        self.content_similarity_df = None
        self.book_stats = None
        self.book_metadata = None  # DataFrame with Theme, Author, etc.
        self.is_fitted = False
        self.tfidf_vectorizer = None
        self.tfidf_valid_books = []
        self._feedback = {}  # {book_title: {"likes": set(), "dislikes": set()}}
        self._eval_metrics = {}

    def fit(self, df):
        """
        Entraîne le modèle hybride.

        1. Filtrage collaboratif (matrice user-item + cosinus)
        2. Similarité de contenu (TF-IDF)
        3. Évaluation quantitative
        """
        print("[ML] Entrainement du modele de recommandation hybride...")

        # ─── Filtrage collaboratif ──────────────────────────────
        book_counts = df.groupby("Book-Title")["Book-Rating"].count()
        popular_books = book_counts[book_counts >= self.min_ratings].index
        df_filtered = df[df["Book-Title"].isin(popular_books)]

        print(f"   -> Livres retenus (>= {self.min_ratings} ratings) : {len(popular_books)}")

        self.matrix = df_filtered.pivot_table(
            index="User-ID",
            columns="Book-Title",
            values="Book-Rating",
            aggfunc="mean"
        ).fillna(0)

        print(f"   -> Matrice : {self.matrix.shape[0]} users x {self.matrix.shape[1]} books")

        book_matrix = csr_matrix(self.matrix.T.values)
        collab_sim = cosine_similarity(book_matrix)
        self.similarity_df = pd.DataFrame(
            collab_sim,
            index=self.matrix.columns,
            columns=self.matrix.columns
        )

        # ─── Statistiques par livre ─────────────────────────────
        self.book_stats = df.groupby("Book-Title").agg(
            avg_rating=("Book-Rating", "mean"),
            num_ratings=("Book-Rating", "count"),
            authors=("Book-Author", "first")
        ).round(2)

        # ─── Métadonnées pour le contenu ────────────────────────
        meta_cols = ["Book-Title", "Book-Author"]
        if "Theme" in df.columns:
            meta_cols.append("Theme")
        if "Description" in df.columns:
            meta_cols.append("Description")
        if "Type" in df.columns:
            meta_cols.append("Type")
        if "Real-Rating" in df.columns:
            meta_cols.extend(["Real-Rating", "Real-Rating-Count", "Rating-Source"])

        self.book_metadata = df[meta_cols].drop_duplicates(subset=["Book-Title"]).set_index("Book-Title")

        # ─── Similarité de contenu (TF-IDF) ────────────────────
        self._build_content_similarity()

        # ─── Évaluation ────────────────────────────────────────
        self._evaluate(df_filtered)

        self.is_fitted = True
        print("   OK - Modele hybride entraine avec succes !")

    def _build_content_similarity(self):
        """Construit la matrice de similarité basée sur le contenu textuel."""
        books_in_model = list(self.similarity_df.columns)
        
        # Créer un "document" textuel pour chaque livre
        docs = []
        valid_books = []
        for title in books_in_model:
            parts = []
            if title in self.book_stats.index:
                author = str(self.book_stats.loc[title, "authors"])
                parts.append(author)
                parts.append(author)  # Double poids pour l'auteur
            if title in self.book_metadata.index:
                row = self.book_metadata.loc[title]
                if "Theme" in row.index and pd.notna(row.get("Theme")):
                    parts.append(str(row["Theme"]))
                    parts.append(str(row["Theme"]))  # Double poids
                if "Description" in row.index and pd.notna(row.get("Description")):
                    parts.append(str(row["Description"]))
                if "Type" in row.index and pd.notna(row.get("Type")):
                    parts.append(str(row["Type"]))
            
            if not parts:
                parts.append(title)  # Fallback: le titre lui-même
            
            docs.append(" ".join(parts))
            valid_books.append(title)

        if not docs:
            self.content_similarity_df = pd.DataFrame()
            return

        self.tfidf_vectorizer = TfidfVectorizer(max_features=500, stop_words=None)
        self.tfidf_valid_books = valid_books
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(docs)
        content_sim = cosine_similarity(tfidf_matrix)

        self.content_similarity_df = pd.DataFrame(
            content_sim,
            index=valid_books,
            columns=valid_books
        )
        print(f"   -> Similarité contenu TF-IDF construite ({len(valid_books)} livres)")

    def _evaluate(self, df_filtered):
        """Calcule des métriques d'évaluation quantitatives."""
        n_books = len(self.similarity_df.columns)
        n_users = self.matrix.shape[0]
        
        # Couverture : proportion de livres couverts par le modèle vs total unique
        total_unique = df_filtered["Book-Title"].nunique()
        coverage = n_books / total_unique if total_unique > 0 else 0

        # Densité de la matrice
        non_zero = (self.matrix != 0).sum().sum()
        total_cells = self.matrix.shape[0] * self.matrix.shape[1]
        density = non_zero / total_cells if total_cells > 0 else 0

        # Diversité moyenne des recommandations (échantillon)
        sample_books = list(self.similarity_df.columns[:min(20, n_books)])
        diversities = []
        for book in sample_books:
            recs = self.get_recommendations(book, n=5)
            if recs is not None and not recs.empty:
                authors = recs["Author"].dropna().unique()
                diversities.append(len(authors) / len(recs))
        
        avg_diversity = np.mean(diversities) if diversities else 0

        self._eval_metrics = {
            "n_books_in_model": n_books,
            "n_users_in_model": n_users,
            "coverage": round(coverage, 4),
            "matrix_density": round(density, 4),
            "avg_recommendation_diversity": round(avg_diversity, 4),
            "alpha_collab": self.alpha,
            "alpha_content": round(1 - self.alpha, 2),
        }
        print(f"   -> Évaluation : couverture={coverage:.1%}, densité={density:.1%}, diversité={avg_diversity:.1%}")

    def get_recommendations(self, book_title, n=5, theme_filter=None):
        """
        Obtient les N livres les plus similaires (score hybride).

        Args:
            book_title: Titre du livre de référence.
            n: Nombre de recommandations.
            theme_filter: Filtrer par thème (optionnel).

        Returns:
            pd.DataFrame ou None.
        """
        if not self.is_fitted:
            return None
        if book_title not in self.similarity_df.columns:
            return None

        # Score collaboratif
        collab_scores = self.similarity_df[book_title].drop(book_title)

        # Score contenu
        if (self.content_similarity_df is not None 
            and not self.content_similarity_df.empty 
            and book_title in self.content_similarity_df.columns):
            content_scores = self.content_similarity_df[book_title].drop(book_title)
            # Aligner les index
            common = collab_scores.index.intersection(content_scores.index)
            hybrid_scores = (
                self.alpha * collab_scores[common] +
                (1 - self.alpha) * content_scores[common]
            )
        else:
            hybrid_scores = collab_scores

        # Appliquer le feedback utilisateur
        hybrid_scores = self._apply_feedback(hybrid_scores, book_title)

        # Filtre par thème
        if theme_filter and self.book_metadata is not None and "Theme" in self.book_metadata.columns:
            themed_books = self.book_metadata[
                self.book_metadata["Theme"].astype(str).str.contains(theme_filter, case=False, na=False)
            ].index
            themed_in_model = hybrid_scores.index.intersection(themed_books)
            if len(themed_in_model) > 0:
                hybrid_scores = hybrid_scores[themed_in_model]

        top_similar = hybrid_scores.nlargest(n)

        results = pd.DataFrame({
            "Book-Title": top_similar.index,
            "Similarity-Score": top_similar.values.round(4)
        })

        for idx, row in results.iterrows():
            title = row["Book-Title"]
            info = self.get_book_info(title)
            if info:
                results.loc[idx, "Avg-Rating"] = info.get("real_rating", info.get("avg_rating"))
                results.loc[idx, "Num-Ratings"] = info.get("real_rating_count", info.get("num_ratings"))
                results.loc[idx, "Author"] = info.get("author", "Inconnu")
                results.loc[idx, "Rating-Source"] = info.get("rating_source", "Estimée")
                if "theme" in info:
                    results.loc[idx, "Theme"] = info["theme"]
                else:
                    results.loc[idx, "Theme"] = ""

        return results.reset_index(drop=True)

    def add_feedback(self, book_title, feedback_type="like"):
        """
        Ajoute un feedback utilisateur sur un livre.
        
        Args:
            book_title: Titre du livre.
            feedback_type: "like" ou "dislike".
        """
        if book_title not in self._feedback:
            self._feedback[book_title] = {"likes": 0, "dislikes": 0}
        
        if feedback_type == "like":
            self._feedback[book_title]["likes"] += 1
        elif feedback_type == "dislike":
            self._feedback[book_title]["dislikes"] += 1

    def _apply_feedback(self, scores, source_book):
        """Ajuste les scores en fonction du feedback accumulé."""
        adjusted = scores.copy()
        for title in adjusted.index:
            if title in self._feedback:
                fb = self._feedback[title]
                # Boost de +10% par like, -15% par dislike
                boost = fb["likes"] * 0.10 - fb["dislikes"] * 0.15
                adjusted[title] = max(0, adjusted[title] + boost)
        return adjusted

    def get_book_list(self):
        """Retourne la liste des livres disponibles dans le modèle."""
        if not self.is_fitted:
            return []
        return sorted(self.similarity_df.columns.tolist())

    def get_available_themes(self):
        """Retourne les thèmes disponibles dans le modèle."""
        if self.book_metadata is None or "Theme" not in self.book_metadata.columns:
            return []
        themes = self.book_metadata["Theme"].dropna().unique().tolist()
        return sorted(set(themes))

    def get_book_info(self, book_title):
        """Retourne les informations d'un livre."""
        if self.book_stats is None or book_title not in self.book_stats.index:
            return None

        stats = self.book_stats.loc[book_title]
        info = {
            "title": book_title,
            "author": stats["authors"],
            "avg_rating": stats["avg_rating"],
            "num_ratings": int(stats["num_ratings"])
        }
        
        # Ajouter les métadonnées de contenu
        if self.book_metadata is not None and book_title in self.book_metadata.index:
            meta = self.book_metadata.loc[book_title]
            if "Theme" in meta.index and pd.notna(meta.get("Theme")):
                info["theme"] = meta["Theme"]
            if "Description" in meta.index and pd.notna(meta.get("Description")):
                info["description"] = meta["Description"]
            if "Type" in meta.index and pd.notna(meta.get("Type")):
                info["type"] = meta["Type"]
            if "Real-Rating" in meta.index and pd.notna(meta.get("Real-Rating")):
                info["real_rating"] = float(meta["Real-Rating"])
                info["real_rating_count"] = float(meta.get("Real-Rating-Count", info["num_ratings"]))
                info["rating_source"] = str(meta.get("Rating-Source", "Google Books"))
        
        return info

    def explain_recommendation(self, source_book, recommended_book):
        """
        Explique pourquoi un livre est recommandé en détaillant chaque signal.
        """
        if not self.is_fitted:
            return "Le modèle n'est pas encore entraîné."
        if source_book not in self.similarity_df.columns:
            return f"Le livre '{source_book}' n'est pas dans le modèle."
        if recommended_book not in self.similarity_df.columns:
            return f"Le livre '{recommended_book}' n'est pas dans le modèle."

        collab_score = self.similarity_df.loc[source_book, recommended_book]
        
        content_score = 0
        if (self.content_similarity_df is not None 
            and not self.content_similarity_df.empty
            and source_book in self.content_similarity_df.columns
            and recommended_book in self.content_similarity_df.index):
            content_score = self.content_similarity_df.loc[source_book, recommended_book]

        hybrid_score = self.alpha * collab_score + (1 - self.alpha) * content_score
        
        source_info = self.get_book_info(source_book)
        rec_info = self.get_book_info(recommended_book)

        explanation = f"## 📚 Pourquoi '{recommended_book}' ?\n\n"
        explanation += f"**Score hybride final : {hybrid_score:.4f}**\n\n"
        explanation += f"| Signal | Score | Poids |\n|---|---|---|\n"
        explanation += f"| Filtrage Collaboratif | {collab_score:.4f} | {self.alpha:.0%} |\n"
        explanation += f"| Similarité de Contenu | {content_score:.4f} | {1-self.alpha:.0%} |\n\n"

        # Détails qualitatifs
        reasons = []
        if rec_info:
            if source_info and source_info.get("author") == rec_info.get("author"):
                reasons.append(f"📝 Même auteur : **{rec_info['author']}**")
            if source_info and rec_info:
                src_theme = source_info.get("theme", "")
                rec_theme = rec_info.get("theme", "")
                if src_theme and rec_theme and src_theme == rec_theme:
                    reasons.append(f"🏷️ Même thème : **{rec_theme}**")
            if collab_score > 0.5:
                reasons.append("👥 Les lecteurs qui ont aimé le livre source ont aussi beaucoup aimé celui-ci")
            elif collab_score > 0.2:
                reasons.append("👥 Corrélation notable dans les comportements de lecture")
            
            explanation += "### Facteurs détectés\n"
            for r in reasons:
                explanation += f"- {r}\n"

            explanation += f"\n### Statistiques\n"
            explanation += f"- Note moyenne : **{rec_info['avg_rating']}/10**\n"
            explanation += f"- Nombre de notes : **{rec_info['num_ratings']}**\n"

        return explanation

    def semantic_search(self, query, n=5):
        """
        Recherche sémantique basée sur les embeddings TF-IDF.
        Trouve les livres dont le contenu (thème, auteur, description) est sémantiquement proche de la requête.
        """
        if not self.is_fitted or self.tfidf_vectorizer is None or not self.tfidf_valid_books:
            return None
        
        # Transformer la requête en vecteur TF-IDF
        query_vec = self.tfidf_vectorizer.transform([query])
        
        # Calculer la similarité cosinus avec tous les livres existants
        # On recrée la matrice TF-IDF à partir du modèle pour calculer la similarité
        docs = []
        for title in self.tfidf_valid_books:
            parts = []
            if title in self.book_stats.index:
                author = str(self.book_stats.loc[title, "authors"])
                parts.append(author)
                parts.append(author)
            if self.book_metadata is not None and title in self.book_metadata.index:
                row = self.book_metadata.loc[title]
                if "Theme" in row.index and pd.notna(row.get("Theme")):
                    parts.append(str(row["Theme"]))
                    parts.append(str(row["Theme"]))
                if "Description" in row.index and pd.notna(row.get("Description")):
                    parts.append(str(row["Description"]))
                if "Type" in row.index and pd.notna(row.get("Type")):
                    parts.append(str(row["Type"]))
            if not parts:
                parts.append(title)
            docs.append(" ".join(parts))
            
        tfidf_matrix = self.tfidf_vectorizer.transform(docs)
        sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
        
        # Trier et obtenir le top n
        top_indices = sim_scores.argsort()[::-1][:n]
        
        results = []
        for idx in top_indices:
            score = sim_scores[idx]
            if score > 0:  # Seulement si on a un minimum de similarité
                title = self.tfidf_valid_books[idx]
                info = self.get_book_info(title)
                if info:
                    info["similarity_score"] = score
                    results.append(info)
                    
        return pd.DataFrame(results)

    def get_eval_metrics(self):
        """Retourne les métriques d'évaluation du modèle."""
        return self._eval_metrics

    def save(self, path=None):
        """Sauvegarde le modèle entraîné."""
        if path is None:
            os.makedirs(MODELS_DIR, exist_ok=True)
            path = os.path.join(MODELS_DIR, "recommender_model.pkl")

        with open(path, "wb") as f:
            pickle.dump({
                "matrix": self.matrix,
                "similarity_df": self.similarity_df,
                "content_similarity_df": self.content_similarity_df,
                "tfidf_vectorizer": self.tfidf_vectorizer,
                "tfidf_valid_books": self.tfidf_valid_books,
                "book_stats": self.book_stats,
                "book_metadata": self.book_metadata,
                "min_ratings": self.min_ratings,
                "alpha": self.alpha,
                "is_fitted": self.is_fitted,
                "_eval_metrics": self._eval_metrics,
                "_feedback": self._feedback,
            }, f)
        print(f"[SAVE] Modele sauvegarde : {path}")

    def load(self, path=None):
        """Charge un modèle sauvegardé."""
        if path is None:
            path = os.path.join(MODELS_DIR, "recommender_model.pkl")

        if not os.path.exists(path):
            return False

        with open(path, "rb") as f:
            data = pickle.load(f)

        self.matrix = data["matrix"]
        self.similarity_df = data["similarity_df"]
        self.content_similarity_df = data.get("content_similarity_df")
        self.tfidf_vectorizer = data.get("tfidf_vectorizer")
        self.tfidf_valid_books = data.get("tfidf_valid_books", [])
        self.book_stats = data["book_stats"]
        self.book_metadata = data.get("book_metadata")
        self.min_ratings = data["min_ratings"]
        self.alpha = data.get("alpha", 0.7)
        self.is_fitted = data["is_fitted"]
        self._eval_metrics = data.get("_eval_metrics", {})
        self._feedback = data.get("_feedback", {})
        print(f"[LOAD] Modele charge : {path}")
        return True


def generate_ml_report(recommender, metrics, output_path=None):
    """Génère un rapport ML complet avec les métriques d'évaluation hybride."""
    if output_path is None:
        os.makedirs(PRODUCTION_DIR, exist_ok=True)
        output_path = os.path.join(PRODUCTION_DIR, "ml_report.md")

    n_books = len(recommender.get_book_list()) if recommender.is_fitted else 0
    matrix_shape = recommender.matrix.shape if recommender.matrix is not None else (0, 0)
    eval_m = recommender.get_eval_metrics()

    example_recs = None
    example_book = None
    if recommender.is_fitted and n_books > 0:
        example_book = recommender.get_book_list()[0]
        example_recs = recommender.get_recommendations(example_book, n=3)

    report = f"""# 📊 BookLens — Rapport Machine Learning

## 1. Vue d'ensemble du modèle

| Paramètre | Valeur |
|---|---|
| Type de modèle | **Hybride** (Collaboratif + Contenu) |
| Mesure de similarité | Cosinus (collab) + TF-IDF (contenu) |
| Pondération collab / contenu | {eval_m.get('alpha_collab', 0.7):.0%} / {eval_m.get('alpha_content', 0.3):.0%} |
| Seuil min. de ratings | {recommender.min_ratings} |
| Livres dans le modèle | {n_books} |
| Taille de la matrice | {matrix_shape[0]} users × {matrix_shape[1]} books |

## 2. Données utilisées

| Métrique | Valeur |
|---|---|
| Total ratings | {metrics.get('total_ratings', 'N/A')} |
| Livres uniques | {metrics.get('unique_books', 'N/A')} |
| Utilisateurs uniques | {metrics.get('unique_users', 'N/A')} |
| Note moyenne | {metrics.get('avg_rating', 'N/A')} |
| Livre le mieux noté | {metrics.get('top_book', 'N/A')} |

## 3. Métriques d'Évaluation Quantitatives

| Métrique | Valeur | Description |
|---|---|---|
| Couverture du catalogue | {eval_m.get('coverage', 0):.1%} | Proportion de livres couverts par le modèle |
| Densité de la matrice | {eval_m.get('matrix_density', 0):.2%} | Proportion de cellules non-nulles dans la matrice user-item |
| Diversité des recommandations | {eval_m.get('avg_recommendation_diversity', 0):.1%} | Diversité des auteurs dans les recommandations |

> 💡 **Interprétation** : Une densité faible signifie que la matrice est très creuse (typique des systèmes de recommandation réels). La diversité mesure si les recommandations ne sont pas toutes du même auteur.

## 4. Approche Hybride

### Filtrage Collaboratif ({eval_m.get('alpha_collab', 0.7):.0%})
On compare les livres selon les **comportements de lecture** des utilisateurs. Deux livres sont "similaires" si les mêmes personnes les ont appréciés de la même manière.

### Similarité de Contenu ({eval_m.get('alpha_content', 0.3):.0%})
On compare les livres selon leurs **métadonnées textuelles** (auteur, thème, description). Deux livres du même auteur ou du même thème auront un score de contenu élevé, même sans ratings en commun.

### Feedback Utilisateur
Les utilisateurs peuvent "liker" ou "disliker" une recommandation. Ce feedback ajuste dynamiquement les scores futurs (+10% par like, -15% par dislike).

## 5. Limites et Améliorations

| Limite | Solution Possible |
|---|---|
| Cold start (nouveaux livres) | La similarité de contenu compense partiellement |
| Sparsité de la matrice | Matrix Factorization (SVD) |
| Pas d'embeddings sémantiques | Embeddings de phrases (Sentence-BERT) |
| Feedback non persisté | Base de données utilisateur |

"""

    if example_recs is not None and example_book:
        report += f"""## 6. Exemple de recommandation

**Livre sélectionné** : {example_book}

| Rang | Livre recommandé | Score hybride | Thème |
|---|---|---|---|
"""
        for i, row in example_recs.iterrows():
            theme = row.get("Theme", "") or ""
            report += f"| {i+1} | {row['Book-Title']} | {row['Similarity-Score']:.4f} | {theme} |\n"

    report += "\n---\n*Rapport généré automatiquement par BookLens v3.0*\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[SAVE] Rapport ML sauvegarde : {output_path}")
