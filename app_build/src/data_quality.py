import os
import json
import pandas as pd
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
REPORT_FILE = os.path.join(REPORTS_DIR, "data_quality_report.json")

os.makedirs(REPORTS_DIR, exist_ok=True)

class DataQualityEngine:
    @staticmethod
    def run_diagnostics() -> Dict[str, Any]:
        """
        Exécute des diagnostics de qualité sur l'ensemble des sources du projet
        et génère un rapport JSON consolidé.
        """
        report = {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "datasets": {}
        }
        
        # 1. Diagnostic Livres
        books_path = os.path.join(DATA_DIR, "raw", "Books.csv")
        if os.path.exists(books_path):
            try:
                df_books = pd.read_csv(books_path)
                report["datasets"]["books"] = DataQualityEngine._analyze_df(
                    df_books, 
                    required_cols=["Book-Title", "Book-Author", "ISBN"],
                    name="Books.csv"
                )
            except Exception as e:
                report["datasets"]["books"] = {"error": str(e)}
                
        # 2. Diagnostic Users
        users_path = os.path.join(DATA_DIR, "raw", "Users.csv")
        if os.path.exists(users_path):
            try:
                df_users = pd.read_csv(users_path)
                report["datasets"]["users"] = DataQualityEngine._analyze_df(
                    df_users, 
                    required_cols=["User-ID"],
                    name="Users.csv"
                )
                # Spécifique Users: âges hors limites
                if "Age" in df_users.columns:
                    bad_ages = ((df_users["Age"] < 0) | (df_users["Age"] > 110)).sum()
                    report["datasets"]["users"]["anomalies"] = {
                        "invalid_ages": int(bad_ages)
                    }
            except Exception as e:
                report["datasets"]["users"] = {"error": str(e)}
                
        # 3. Diagnostic Ratings
        ratings_path = os.path.join(DATA_DIR, "raw", "Ratings.csv")
        if os.path.exists(ratings_path):
            try:
                df_ratings = pd.read_csv(ratings_path)
                report["datasets"]["ratings"] = DataQualityEngine._analyze_df(
                    df_ratings, 
                    required_cols=["User-ID", "ISBN", "Book-Rating"],
                    name="Ratings.csv"
                )
                # Spécifique Ratings: notes hors plage 0-10
                if "Book-Rating" in df_ratings.columns:
                    bad_ratings = ((df_ratings["Book-Rating"] < 0) | (df_ratings["Book-Rating"] > 10)).sum()
                    report["datasets"]["ratings"]["anomalies"] = {
                        "invalid_ratings_bounds": int(bad_ratings)
                    }
            except Exception as e:
                report["datasets"]["ratings"] = {"error": str(e)}
                
        # 4. Diagnostic Academic Corpus
        academic_path = os.path.join(DATA_DIR, "raw", "academic_scifi_books.csv")
        if os.path.exists(academic_path):
            try:
                df_acad = pd.read_csv(academic_path)
                report["datasets"]["academic"] = DataQualityEngine._analyze_df(
                    df_acad, 
                    required_cols=["Book-Title", "Book-Author"],
                    name="academic_scifi_books.csv"
                )
            except Exception as e:
                report["datasets"]["academic"] = {"error": str(e)}
                
        # Sauvegarder le rapport localement
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        return report

    @staticmethod
    def _analyze_df(df: pd.DataFrame, required_cols: List[str], name: str) -> Dict[str, Any]:
        """Analyse interne d'un DataFrame."""
        total_rows = len(df)
        missing = {}
        for col in df.columns:
            missing[col] = int(df[col].isna().sum())
            
        # Doublons (lignes entières)
        duplicates = int(df.duplicated().sum())
        
        # Vérifier si des colonnes essentielles manquent complètement
        missing_required = [c for c in required_cols if c not in df.columns]
        
        # Statut de qualité
        status = "healthy"
        reasons = []
        if duplicates > 0:
            status = "warning"
            reasons.append(f"{duplicates} doublons détectés.")
        if missing_required:
            status = "critical"
            reasons.append(f"Colonnes clés absentes : {missing_required}.")
            
        # Vérifier si des valeurs clés sont manquantes
        for r_col in required_cols:
            if r_col in df.columns and missing[r_col] > 0:
                status = "warning"
                reasons.append(f"{missing[r_col]} valeurs manquantes dans la colonne clé '{r_col}'.")
                
        return {
            "name": name,
            "status": status,
            "total_rows": total_rows,
            "duplicates": duplicates,
            "missing_values": missing,
            "reasons": reasons
        }

    @staticmethod
    def generate_markdown_report() -> str:
        """Génère un résumé lisible du rapport de qualité de données."""
        report = DataQualityEngine.run_diagnostics()
        
        md = f"# 🏛️ Rapport de Gouvernance & Qualité des Données\n\n"
        md += f"**Généré le** : `{report['timestamp']}`\n\n"
        
        for name, details in report["datasets"].items():
            if "error" in details:
                md += f"### ❌ {name.upper()} : Erreur de lecture\n- {details['error']}\n\n"
                continue
                
            status_emoji = "✅" if details["status"] == "healthy" else "⚠️" if details["status"] == "warning" else "🚨"
            md += f"### {status_emoji} Dataset : `{details['name']}` ({details['status'].upper()})\n"
            md += f"- **Lignes totales** : {details['total_rows']}\n"
            md += f"- **Doublons** : {details['duplicates']}\n"
            
            if details["reasons"]:
                md += "- **Remarques** :\n"
                for r in details["reasons"]:
                    md += f"  - {r}\n"
            else:
                md += "- **Remarques** : Aucune anomalie détectée.\n"
                
            md += "\n"
            
        return md
