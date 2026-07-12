import os
import pandas as pd
from typing import Dict, Any, Tuple
from src.recommender import BookRecommender
from src.mlops.experiment_tracker import ExperimentTracker
from src.mlops.model_registry import ModelRegistry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMP_MODEL_FILE = os.path.join(BASE_DIR, "models", "temp_training_model.pkl")

class TrainingService:
    @staticmethod
    def train_popularity_model(df: pd.DataFrame) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Simule l'entraînement d'un modèle basé uniquement sur la popularité (baseline).
        Calcule les métriques correspondantes.
        """
        params = {"min_ratings": 3, "strategy": "popularity", "alpha": 1.0}
        
        # Livres populaires
        book_counts = df.groupby("Book-Title")["Book-Rating"].count()
        popular_books = book_counts[book_counts >= 3].index.tolist()
        
        coverage = len(popular_books) / df["Book-Title"].nunique() if df["Book-Title"].nunique() > 0 else 0.0
        
        # Densité (n'a pas de sens pour la popularité pure, on met 0.0)
        density = 0.0
        
        # Diversité des recommandations (auteurs différents dans les plus populaires)
        top_books = df.groupby("Book-Title").agg(
            rating_count=("Book-Rating", "count"),
            author=("Book-Author", "first")
        ).nlargest(10, "rating_count")
        
        authors = top_books["author"].dropna().unique()
        diversity = len(authors) / len(top_books) if len(top_books) > 0 else 0.0
        
        metrics = {
            "n_books_in_model": len(popular_books),
            "n_users_in_model": df["User-ID"].nunique(),
            "coverage": round(coverage, 4),
            "matrix_density": round(density, 4),
            "avg_recommendation_diversity": round(diversity, 4),
            "alpha_collab": 1.0,
            "alpha_content": 0.0
        }
        
        return params, metrics

    @staticmethod
    def train_and_register(df: pd.DataFrame, strategy: str = "hybrid") -> Dict[str, Any]:
        """
        Entraîne un modèle selon la stratégie sélectionnée ('popularity', 'content_based', 'hybrid')
        et l'enregistre dans le tracker d'expérimentations et le registre des modèles.
        """
        dataset_hash = ExperimentTracker.compute_dataset_hash(df)
        dataset_size = len(df)
        
        if strategy == "popularity":
            params, metrics = TrainingService.train_popularity_model(df)
            
            # Enregistrer le run d'expérimentation
            run_info = ExperimentTracker.log_run("popularity_baseline", params, metrics, dataset_size, dataset_hash)
            
            # Récupérer la dernière version ou incrémenter
            registry = ModelRegistry.get_registry()
            version = sum(1 for item in registry if item["model_name"] == "popularity_baseline") + 1
            
            # Enregistrer dans le registre
            ModelRegistry.register_model("", "popularity_baseline", version, metrics, run_info["run_id"])
            return run_info
            
        elif strategy == "content_based":
            # Créer un BookRecommender avec alpha=0.0 (100% contenu)
            recommender = BookRecommender(min_ratings=3, alpha=0.0)
            recommender.fit(df)
            metrics = recommender.get_eval_metrics()
            params = {"min_ratings": 3, "strategy": "content_based", "alpha": 0.0}
            
            # Sauvegarder dans un fichier temporaire
            recommender.save(TEMP_MODEL_FILE)
            
            run_info = ExperimentTracker.log_run("content_based_model", params, metrics, dataset_size, dataset_hash)
            
            registry = ModelRegistry.get_registry()
            version = sum(1 for item in registry if item["model_name"] == "content_based_model") + 1
            
            ModelRegistry.register_model(TEMP_MODEL_FILE, "content_based_model", version, metrics, run_info["run_id"])
            
            if os.path.exists(TEMP_MODEL_FILE):
                os.remove(TEMP_MODEL_FILE)
            return run_info
            
        elif strategy == "hybrid":
            # Modèle hybride par défaut (alpha=0.7)
            recommender = BookRecommender(min_ratings=3, alpha=0.7)
            recommender.fit(df)
            metrics = recommender.get_eval_metrics()
            params = {"min_ratings": 3, "strategy": "hybrid", "alpha": 0.7}
            
            recommender.save(TEMP_MODEL_FILE)
            
            run_info = ExperimentTracker.log_run("hybrid_model", params, metrics, dataset_size, dataset_hash)
            
            registry = ModelRegistry.get_registry()
            version = sum(1 for item in registry if item["model_name"] == "hybrid_model") + 1
            
            ModelRegistry.register_model(TEMP_MODEL_FILE, "hybrid_model", version, metrics, run_info["run_id"])
            
            # Si aucune version n'est active actuellement, promouvoir cette version par défaut
            active_model = ModelRegistry.get_active_model("hybrid_model")
            if not active_model:
                ModelRegistry.promote_to_active("hybrid_model", version)
                
            if os.path.exists(TEMP_MODEL_FILE):
                os.remove(TEMP_MODEL_FILE)
            return run_info
        else:
            raise ValueError(f"Stratégie d'entraînement inconnue : {strategy}")
