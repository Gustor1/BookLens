"""
BookLens — Module de validation des données
Vérifie le schéma, les types, les valeurs manquantes et détecte les anomalies.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationReport:
    """Rapport de validation pour un dataset."""
    dataset_name: str
    total_rows: int = 0
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    is_valid: bool = True

    def add_issue(self, msg: str):
        self.issues.append(msg)
        self.is_valid = False

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def summary(self) -> str:
        status = "✅ VALIDE" if self.is_valid else "❌ INVALIDE"
        lines = [f"[VALIDATION] {self.dataset_name} — {status} ({self.total_rows} lignes)"]
        for issue in self.issues:
            lines.append(f"   ❌ {issue}")
        for warning in self.warnings:
            lines.append(f"   ⚠️ {warning}")
        return "\n".join(lines)


# ─── Schémas attendus ────────────────────────────────────────────

BOOKS_SCHEMA = {
    "ISBN": "object",
    "Book-Title": "object",
    "Book-Author": "object",
    "Year-Of-Publication": "number",
    "Publisher": "object",
}

USERS_SCHEMA = {
    "User-ID": "object",
    "Location": "object",
    "Age": "number",
}

RATINGS_SCHEMA = {
    "User-ID": "object",
    "ISBN": "object",
    "Book-Rating": "number",
}

ACADEMIC_SCHEMA = {
    "ISBN": "object",
    "Book-Title": "object",
    "Book-Author": "object",
    "Year-Of-Publication": "number",
    "Theme": "object",
    "Description": "object",
    "Relevance": "object",
    "Type": "object",
}


def _check_schema(df: pd.DataFrame, schema: dict, report: ValidationReport):
    """Vérifie que les colonnes attendues sont présentes et du bon type général."""
    for col, expected_type in schema.items():
        if col not in df.columns:
            report.add_issue(f"Colonne manquante : '{col}'")
        else:
            if expected_type == "number":
                converted = pd.to_numeric(df[col], errors="coerce")
                pct_failed = converted.isna().sum() - df[col].isna().sum()
                if pct_failed > 0:
                    pct = pct_failed / len(df) * 100
                    if pct > 20:
                        report.add_issue(f"Colonne '{col}' : {pct:.1f}% de valeurs non numériques")
                    elif pct > 0:
                        report.add_warning(f"Colonne '{col}' : {pct:.1f}% de valeurs non numériques")


def _check_missing(df: pd.DataFrame, critical_cols: list, report: ValidationReport):
    """Vérifie les valeurs manquantes pour les colonnes critiques."""
    for col in critical_cols:
        if col in df.columns:
            n_missing = df[col].isna().sum()
            if n_missing > 0:
                pct = n_missing / len(df) * 100
                if pct > 50:
                    report.add_issue(f"Colonne '{col}' : {pct:.1f}% de valeurs manquantes")
                elif pct > 5:
                    report.add_warning(f"Colonne '{col}' : {pct:.1f}% de valeurs manquantes ({n_missing})")


def detect_rating_anomalies(ratings_df: pd.DataFrame) -> dict:
    """
    Détecte les anomalies dans les ratings.
    
    Returns:
        dict avec les statistiques d'anomalies détectées.
    """
    anomalies = {
        "total_ratings": len(ratings_df),
        "duplicates": 0,
        "out_of_range": 0,
        "suspicious_users": [],
        "details": []
    }

    # 1. Doublons exacts (même user, même livre)
    dupes = ratings_df.duplicated(subset=["User-ID", "ISBN"], keep=False)
    anomalies["duplicates"] = dupes.sum()
    if anomalies["duplicates"] > 0:
        anomalies["details"].append(
            f"{anomalies['duplicates']} ratings en double (même user + même livre)"
        )

    # 2. Ratings hors plage
    if "Book-Rating" in ratings_df.columns:
        oor = (ratings_df["Book-Rating"] < 0) | (ratings_df["Book-Rating"] > 10)
        anomalies["out_of_range"] = oor.sum()
        if anomalies["out_of_range"] > 0:
            anomalies["details"].append(
                f"{anomalies['out_of_range']} ratings hors de la plage [0-10]"
            )

    # 3. Utilisateurs suspects (trop de ratings — possible bot/spam)
    if "User-ID" in ratings_df.columns:
        user_counts = ratings_df["User-ID"].value_counts()
        # Un utilisateur avec plus de 3x l'écart-type est suspect
        mean_c = user_counts.mean()
        std_c = user_counts.std()
        threshold = mean_c + 3 * std_c
        suspects = user_counts[user_counts > threshold]
        if not suspects.empty:
            anomalies["suspicious_users"] = suspects.index.tolist()[:5]  # Top 5
            anomalies["details"].append(
                f"{len(suspects)} utilisateur(s) avec un nombre de ratings anormalement élevé (seuil: {threshold:.0f})"
            )

    return anomalies


def validate_books(df: pd.DataFrame) -> ValidationReport:
    """Valide le dataset Books."""
    report = ValidationReport("Books", total_rows=len(df))
    _check_schema(df, BOOKS_SCHEMA, report)
    _check_missing(df, ["ISBN", "Book-Title", "Book-Author"], report)

    # Vérifier les ISBN dupliqués
    n_dup = df.duplicated(subset=["ISBN"]).sum()
    if n_dup > 0:
        report.add_warning(f"{n_dup} ISBN dupliqués détectés")

    return report


def validate_users(df: pd.DataFrame) -> ValidationReport:
    """Valide le dataset Users."""
    report = ValidationReport("Users", total_rows=len(df))
    _check_schema(df, USERS_SCHEMA, report)
    _check_missing(df, ["User-ID"], report)

    # Vérifier les âges aberrants
    if "Age" in df.columns:
        ages = pd.to_numeric(df["Age"], errors="coerce")
        aberrant = ((ages < 5) | (ages > 120)).sum()
        if aberrant > 0:
            report.add_warning(f"{aberrant} âges aberrants (<5 ou >120)")

    return report


def validate_ratings(df: pd.DataFrame) -> ValidationReport:
    """Valide le dataset Ratings."""
    report = ValidationReport("Ratings", total_rows=len(df))
    _check_schema(df, RATINGS_SCHEMA, report)
    _check_missing(df, ["User-ID", "ISBN", "Book-Rating"], report)

    # Anomalies
    anomalies = detect_rating_anomalies(df)
    for detail in anomalies["details"]:
        report.add_warning(detail)

    return report


def validate_academic(df: pd.DataFrame) -> ValidationReport:
    """Valide le dataset Académique."""
    report = ValidationReport("Academic", total_rows=len(df))
    if df.empty:
        report.add_warning("Dataset académique vide (pas de fichier chargé)")
        return report
    _check_schema(df, ACADEMIC_SCHEMA, report)
    _check_missing(df, ["ISBN", "Book-Title", "Book-Author", "Theme"], report)
    return report


def validate_all(books_df, users_df, ratings_df, academic_df=None) -> List[ValidationReport]:
    """
    Exécute toutes les validations et affiche un résumé.
    
    Returns:
        Liste de ValidationReport.
    """
    reports = [
        validate_books(books_df),
        validate_users(users_df),
        validate_ratings(ratings_df),
    ]
    if academic_df is not None:
        reports.append(validate_academic(academic_df))

    print("\n" + "=" * 60)
    print("📋 RAPPORT DE VALIDATION DES DONNÉES")
    print("=" * 60)
    for r in reports:
        print(r.summary())
    print("=" * 60 + "\n")

    return reports
