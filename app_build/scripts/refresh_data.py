"""
BookLens — Script de rafraîchissement des données
Exécutable manuellement pour re-générer les données, valider, et enrichir.

Usage:
    python scripts/refresh_data.py [--enrich] [--no-generate]
"""

import sys
import os
import io
import argparse

# Fix Windows console encoding supprimé pour éviter l'erreur I/O

# Ajouter le répertoire parent au path
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)

from src.data_loader import load_all, PROCESSED_DIR, RAW_DIR
from src.data_cleaner import (
    clean_books, clean_users, clean_ratings,
    merge_datasets, generate_metrics, save_processed_data, integrate_academic_data
)
from src.data_validator import validate_all


def main():
    parser = argparse.ArgumentParser(description="BookLens — Rafraîchissement des données")
    parser.add_argument("--enrich", action="store_true", help="Enrichir via Open Library API")
    parser.add_argument("--no-generate", action="store_true", help="Ne pas re-générer les données d'exemple")
    args = parser.parse_args()

    print("=" * 60)
    print("📚 BookLens — Rafraîchissement du Pipeline de Données")
    print("=" * 60)

    # Étape 1 : Vérifier / générer les données brutes
    if not args.no_generate:
        books_csv = os.path.join(RAW_DIR, "Books.csv")
        if not os.path.exists(books_csv):
            print("\n[STEP 1] Génération des données d'exemple...")
            sys.path.insert(0, APP_DIR)
            from generate_sample_data import main as generate_data
            generate_data()
        else:
            print("\n[STEP 1] Données brutes déjà présentes, pas de re-génération.")

    # Étape 2 : Charger les données
    print("\n[STEP 2] Chargement des données...")
    books, users, ratings, academic = load_all()

    # Étape 3 : Validation
    print("\n[STEP 3] Validation des données brutes...")
    reports = validate_all(books, users, ratings, academic)
    
    invalid = [r for r in reports if not r.is_valid]
    if invalid:
        print("\n⚠️  Certains datasets ont des problèmes critiques:")
        for r in invalid:
            print(f"   - {r.dataset_name}: {len(r.issues)} erreur(s)")
        print("   Le pipeline continue malgré les erreurs (le nettoyage les corrigera).\n")

    # Étape 4 : Nettoyage
    print("[STEP 4] Nettoyage des données...")
    books_clean = clean_books(books)
    users_clean = clean_users(users)
    ratings_clean = clean_ratings(ratings)
    books_clean, ratings_clean = integrate_academic_data(
        books_clean, users_clean, ratings_clean, academic
    )

    # Étape 5 : Enrichissement (optionnel)
    if args.enrich:
        print("\n[STEP 5] Enrichissement via Open Library API...")
        from src.data_enricher import enrich_books
        books_clean = enrich_books(books_clean, max_api_calls=20, use_api=True)
    else:
        print("\n[STEP 5] Enrichissement ignoré (utilisez --enrich pour activer)")

    # Étape 6 : Fusion et sauvegarde
    print("\n[STEP 6] Fusion et sauvegarde...")
    merged = merge_datasets(books_clean, users_clean, ratings_clean)
    metrics = generate_metrics(merged)
    save_processed_data(merged)

    # Étape 7 : Résumé
    print("\n" + "=" * 60)
    print("✅ Pipeline terminé avec succès !")
    print(f"   📊 {metrics['total_ratings']} ratings")
    print(f"   📖 {metrics['unique_books']} livres uniques")
    print(f"   👤 {metrics['unique_users']} utilisateurs")
    print(f"   ⭐ Note moyenne : {metrics['avg_rating']}/10")
    print("=" * 60)

    # Supprimer l'ancien modèle pour forcer le re-training
    model_path = os.path.join(APP_DIR, "models", "recommender_model.pkl")
    if os.path.exists(model_path):
        os.remove(model_path)
        print("   🗑️ Ancien modèle supprimé (sera re-entraîné au prochain lancement)")


if __name__ == "__main__":
    main()
