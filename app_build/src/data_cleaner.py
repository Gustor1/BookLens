"""
BookLens — Module de nettoyage et fusion des données
Nettoie chaque dataset puis les fusionne en un dataset exploitable.
"""

import pandas as pd
import numpy as np
import os
from .data_loader import PROCESSED_DIR


def clean_books(df):
    """
    Nettoie le DataFrame des livres.

    Opérations :
    - Suppression des doublons (basé sur ISBN)
    - Correction du type Year-Of-Publication
    - Remplacement des années invalides (0, >2025, <1000) par NaN
    - Remplissage des auteurs manquants par "Auteur Inconnu"

    Args:
        df: DataFrame brut des livres.

    Returns:
        pd.DataFrame: DataFrame nettoyé.
    """
    print("[CLEAN] Nettoyage des livres...")
    df = df.copy()

    # 1. Supprimer les doublons
    n_before = len(df)
    df = df.drop_duplicates(subset=["ISBN"], keep="first")
    n_after = len(df)
    print(f"   -> Doublons supprimes : {n_before - n_after}")

    # 2. Corriger Year-Of-Publication
    df["Year-Of-Publication"] = pd.to_numeric(
        df["Year-Of-Publication"], errors="coerce"
    )
    # Remplacer les années invalides
    invalid_years = (df["Year-Of-Publication"] < 1000) | (
        df["Year-Of-Publication"] > 2025
    )
    df.loc[invalid_years, "Year-Of-Publication"] = np.nan
    print(f"   -> Annees invalides corrigees : {invalid_years.sum()}")

    # 3. Remplir les auteurs manquants
    n_missing_authors = df["Book-Author"].isna().sum()
    df["Book-Author"] = df["Book-Author"].fillna("Auteur Inconnu")
    print(f"   -> Auteurs manquants remplis : {n_missing_authors}")

    # 4. Nettoyer les espaces
    for col in ["Book-Title", "Book-Author", "Publisher"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    print(f"   OK - {len(df)} livres apres nettoyage")
    return df


def clean_users(df):
    """
    Nettoie le DataFrame des utilisateurs.

    Opérations :
    - Suppression des doublons (basé sur User-ID)
    - Filtrage des âges aberrants (<5 ou >100)
    - Remplacement des âges manquants par la médiane

    Args:
        df: DataFrame brut des utilisateurs.

    Returns:
        pd.DataFrame: DataFrame nettoyé.
    """
    print("[CLEAN] Nettoyage des utilisateurs...")
    df = df.copy()

    # 1. Supprimer les doublons
    n_before = len(df)
    df = df.drop_duplicates(subset=["User-ID"], keep="first")
    print(f"   -> Doublons supprimes : {n_before - len(df)}")

    # 2. Corriger les âges
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

    # Marquer les âges aberrants comme NaN
    aberrant = (df["Age"] < 5) | (df["Age"] > 100)
    n_aberrant = aberrant.sum()
    df.loc[aberrant, "Age"] = np.nan
    print(f"   -> Ages aberrants supprimes : {n_aberrant}")

    # Remplir par la médiane
    median_age = df["Age"].median()
    n_missing = df["Age"].isna().sum()
    df["Age"] = df["Age"].fillna(median_age)
    df["Age"] = df["Age"].astype(int)
    print(f"   -> Ages manquants remplis par mediane ({median_age:.0f}) : {n_missing}")

    print(f"   OK - {len(df)} utilisateurs apres nettoyage")
    return df


def clean_ratings(df):
    """
    Nettoie le DataFrame des ratings.

    Opérations :
    - Suppression des doublons (même User-ID + ISBN)
    - Vérification que les ratings sont entre 0 et 10
    - Suppression des ratings implicites (0) pour le ML

    Args:
        df: DataFrame brut des ratings.

    Returns:
        pd.DataFrame: DataFrame nettoyé (ratings explicites uniquement, 1-10).
    """
    print("[CLEAN] Nettoyage des ratings...")
    df = df.copy()

    # 1. Supprimer les doublons
    n_before = len(df)
    df = df.drop_duplicates(subset=["User-ID", "ISBN"], keep="first")
    print(f"   -> Doublons supprimes : {n_before - len(df)}")

    # 2. Vérifier la plage des ratings
    df["Book-Rating"] = pd.to_numeric(df["Book-Rating"], errors="coerce")
    invalid = (df["Book-Rating"] < 0) | (df["Book-Rating"] > 10)
    df = df[~invalid]
    print(f"   -> Ratings hors plage supprimes : {invalid.sum()}")

    # 3. Séparer ratings explicites (1-10) des implicites (0)
    n_implicit = (df["Book-Rating"] == 0).sum()
    df_explicit = df[df["Book-Rating"] > 0].copy()
    print(f"   -> Ratings implicites (=0) retires : {n_implicit}")

    print(f"   OK - {len(df_explicit)} ratings explicites apres nettoyage")
    return df_explicit


def integrate_academic_data(books_df, users_df, ratings_df, academic_df):
    """
    Intègre les livres académiques dans le dataset principal et génère des ratings synthétiques.
    """
    if academic_df.empty:
        return books_df, ratings_df
        
    print("[INTEGRATION] Ajout du corpus académique...")
    
    # S'assurer que le format correspond
    academic_books = academic_df.copy()
    
    # 1. Ajouter les livres
    new_books = pd.concat([books_df, academic_books], ignore_index=True)
    
    # 2. Générer des fausses notes pour le filtrage collaboratif
    np.random.seed(42)
    user_ids = users_df["User-ID"].unique()
    new_ratings = []
    
    for isbn in academic_books["ISBN"]:
        # Générer 5 à 15 notes (entre 7 et 10 car ce sont des classiques)
        n_ratings = np.random.randint(5, 16)
        chosen_users = np.random.choice(user_ids, size=n_ratings, replace=False)
        for uid in chosen_users:
            new_ratings.append({
                "User-ID": uid,
                "ISBN": isbn,
                "Book-Rating": np.random.randint(7, 11)
            })
            
    synthetic_ratings_df = pd.DataFrame(new_ratings)
    final_ratings = pd.concat([ratings_df, synthetic_ratings_df], ignore_index=True)
    
    print(f"   -> {len(academic_books)} livres académiques ajoutés")
    print(f"   -> {len(synthetic_ratings_df)} notes synthétiques injectées")
    
    return new_books, final_ratings


def merge_datasets(books_df, users_df, ratings_df):
    """
    Fusionne les trois datasets nettoyés.

    Jointure : Ratings -> Books (sur ISBN) -> Users (sur User-ID)

    Args:
        books_df: DataFrame des livres nettoyés.
        users_df: DataFrame des utilisateurs nettoyés.
        ratings_df: DataFrame des ratings nettoyés.

    Returns:
        pd.DataFrame: Dataset fusionné complet.
    """
    print("[MERGE] Fusion des datasets...")

    # Ratings + Books
    merged = ratings_df.merge(books_df, on="ISBN", how="inner")
    print(f"   -> Apres fusion Ratings x Books : {len(merged)} lignes")

    # + Users
    merged = merged.merge(users_df, on="User-ID", how="inner")
    print(f"   -> Apres fusion avec Users : {len(merged)} lignes")

    # Colonnes finales utiles (incluant les nouvelles colonnes académiques)
    columns_to_keep = [
        "User-ID", "ISBN", "Book-Rating", "Book-Title", "Book-Author",
        "Year-Of-Publication", "Publisher", "Age", "Location",
        "Theme", "Description", "Relevance", "Type",
        "Real-Rating", "Real-Rating-Count", "Rating-Source"
    ]
    available_columns = [c for c in columns_to_keep if c in merged.columns]
    merged = merged[available_columns]

    print(f"   OK - Dataset final : {len(merged)} lignes x {len(merged.columns)} colonnes")
    return merged


def generate_metrics(merged_df):
    """
    Génère des métriques descriptives sur le dataset fusionné.

    Args:
        merged_df: DataFrame fusionné.

    Returns:
        dict: Dictionnaire de métriques clés.
    """
    unique_books_df = merged_df.drop_duplicates(subset=["ISBN"])
    has_real_ratings = "Real-Rating" in unique_books_df.columns and unique_books_df["Real-Rating"].notna().any()
    
    if has_real_ratings:
        real_books = unique_books_df[unique_books_df["Real-Rating"].notna()]
        avg_rating = round(real_books["Real-Rating"].mean(), 2)
        total_ratings = int(real_books["Real-Rating-Count"].sum())
        median_rating = real_books["Real-Rating"].median()
        is_mixed = len(real_books) < len(unique_books_df)
    else:
        avg_rating = round(merged_df["Book-Rating"].mean(), 2)
        total_ratings = len(merged_df)
        median_rating = merged_df["Book-Rating"].median()
        is_mixed = True
        
    metrics = {
        "total_ratings": total_ratings,
        "is_mixed_ratings": is_mixed,
        "unique_books": merged_df["ISBN"].nunique(),
        "unique_users": merged_df["User-ID"].nunique(),
        "unique_authors": merged_df["Book-Author"].nunique(),
        "avg_rating": avg_rating,
        "median_rating": median_rating,
        "min_year": int(merged_df["Year-Of-Publication"].min())
        if merged_df["Year-Of-Publication"].notna().any()
        else None,
        "max_year": int(merged_df["Year-Of-Publication"].max())
        if merged_df["Year-Of-Publication"].notna().any()
        else None,
        "avg_age": round(merged_df["Age"].mean(), 1),
        "top_book": merged_df.groupby("Book-Title")["Book-Rating"]
        .mean()
        .idxmax(),
        "top_author": merged_df.groupby("Book-Author")["Book-Rating"]
        .count()
        .idxmax(),
    }
    return metrics


def save_processed_data(merged_df):
    """
    Sauvegarde le dataset fusionné dans data/processed/.

    Args:
        merged_df: DataFrame fusionné à sauvegarder.
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    output_path = os.path.join(PROCESSED_DIR, "merged_dataset.csv")
    merged_df.to_csv(output_path, index=False)
    print(f"[SAVE] Dataset sauvegarde : {output_path}")


def run_pipeline():
    """
    Exécute le pipeline complet de nettoyage.

    Returns:
        tuple: (merged_df, metrics)
    """
    from .data_loader import load_all
    from .data_validator import validate_all

    # Charger
    books, users, ratings, academic = load_all()

    # Valider
    validate_all(books, users, ratings, academic)

    # Nettoyer
    books_clean = clean_books(books)
    users_clean = clean_users(users)
    ratings_clean = clean_ratings(ratings)
    
    # Intégrer les données académiques
    books_clean, ratings_clean = integrate_academic_data(books_clean, users_clean, ratings_clean, academic)

    # Fusionner
    merged = merge_datasets(books_clean, users_clean, ratings_clean)

    # Métriques
    metrics = generate_metrics(merged)

    # Sauvegarder
    save_processed_data(merged)

    return merged, metrics

