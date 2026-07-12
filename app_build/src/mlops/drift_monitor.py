import pandas as pd
import numpy as np
from typing import Dict, Any

class DriftMonitor:
    @staticmethod
    def analyze_dataset_health(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse l'intégrité et la santé globale d'un dataset pour détecter les anomalies."""
        total_rows = len(df)
        if total_rows == 0:
            return {"status": "empty", "missing_rates": {}, "invalid_ratings": 0}
            
        # 1. Taux de valeurs manquantes par colonne clé
        missing_rates = {}
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_rates[col] = round((missing_count / total_rows) * 100, 2)
            
        # 2. Vérification des notes invalides
        invalid_ratings = 0
        if "Book-Rating" in df.columns:
            # Les ratings doivent être entre 1 et 10 (les 0 sont exclus lors du nettoyage des ratings implicites)
            invalid_ratings = int(((df["Book-Rating"] < 0) | (df["Book-Rating"] > 10)).sum())
            
        # 3. Vérification des âges aberrants si colonne présente
        invalid_ages = 0
        if "User-Age" in df.columns or "Age" in df.columns:
            age_col = "User-Age" if "User-Age" in df.columns else "Age"
            invalid_ages = int(((df[age_col] < 5) | (df[age_col] > 110)).sum())
            
        # Déterminer le statut de santé
        status = "healthy"
        critical_issues = []
        
        if missing_rates.get("Book-Title", 0) > 5.0 or missing_rates.get("Book-Rating", 0) > 5.0:
            status = "warning"
            critical_issues.append("Taux élevé de valeurs manquantes sur les colonnes clés.")
        if invalid_ratings > 0 or invalid_ages > 0:
            status = "warning"
            critical_issues.append(f"Données invalides détectées : {invalid_ratings} notes / {invalid_ages} âges.")
            
        return {
            "status": status,
            "total_rows": total_rows,
            "missing_rates": missing_rates,
            "invalid_ratings_count": invalid_ratings,
            "invalid_ages_count": invalid_ages,
            "critical_issues": critical_issues
        }

    @staticmethod
    def calculate_distribution_drift(reference_df: pd.DataFrame, current_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule la dérive de distribution (drift) entre un dataset de référence 
        et un nouveau dataset pour la note moyenne et la répartition des thèmes.
        """
        metrics = {}
        
        # 1. Drift de la note moyenne
        ref_rating_mean = 0.0
        cur_rating_mean = 0.0
        rating_drift = 0.0
        
        if "Book-Rating" in reference_df.columns and "Book-Rating" in current_df.columns:
            ref_rating_mean = float(reference_df["Book-Rating"].mean())
            cur_rating_mean = float(current_df["Book-Rating"].mean())
            rating_drift = abs(cur_rating_mean - ref_rating_mean)
            
        metrics["rating_mean_reference"] = round(ref_rating_mean, 2)
        metrics["rating_mean_current"] = round(cur_rating_mean, 2)
        metrics["rating_mean_drift"] = round(rating_drift, 3)
        
        # 2. Dérive sur les thèmes/genres
        theme_drift_detected = False
        drift_magnitude = 0.0
        
        if "Theme" in reference_df.columns and "Theme" in current_df.columns:
            ref_themes = reference_df["Theme"].value_counts(normalize=True).to_dict()
            cur_themes = current_df["Theme"].value_counts(normalize=True).to_dict()
            
            # Calculer la dérive cumulée (somme des différences absolues)
            all_keys = set(ref_themes.keys()) | set(cur_themes.keys())
            total_diff = 0.0
            for key in all_keys:
                diff = abs(ref_themes.get(key, 0.0) - cur_themes.get(key, 0.0))
                total_diff += diff
            drift_magnitude = total_diff / 2.0  # Normalisé entre 0 et 1
            theme_drift_detected = drift_magnitude > 0.15
            
        metrics["theme_drift_magnitude"] = round(drift_magnitude, 3)
        metrics["drift_detected"] = theme_drift_detected or (rating_drift > 0.5)
        
        return metrics
