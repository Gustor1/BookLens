"""
BookLens — Module de chargement des données
Charge les fichiers CSV bruts (Books, Users, Ratings).
"""

import pandas as pd
import os


# ─── Chemins par défaut ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def load_books(path=None):
    """
    Charge le fichier Books.csv.

    Args:
        path: Chemin vers le fichier. Si None, utilise le chemin par défaut.

    Returns:
        pd.DataFrame: DataFrame des livres bruts.
    """
    if path is None:
        path = os.path.join(RAW_DIR, "Books.csv")

    print(f"[BOOKS] Chargement des livres depuis : {path}")

    # Essayer plusieurs encodages courants
    for encoding in ["utf-8", "latin-1", "iso-8859-1"]:
        try:
            df = pd.read_csv(path, sep=";", encoding=encoding, on_bad_lines="skip")
            print(f"   OK - {len(df)} lignes chargees (encodage: {encoding})")
            return df
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Impossible de lire {path} avec les encodages disponibles.")


def load_users(path=None):
    """
    Charge le fichier Users.csv.

    Args:
        path: Chemin vers le fichier. Si None, utilise le chemin par défaut.

    Returns:
        pd.DataFrame: DataFrame des utilisateurs bruts.
    """
    if path is None:
        path = os.path.join(RAW_DIR, "Users.csv")

    print(f"[USERS] Chargement des utilisateurs depuis : {path}")

    for encoding in ["utf-8", "latin-1", "iso-8859-1"]:
        try:
            df = pd.read_csv(path, sep=";", encoding=encoding, on_bad_lines="skip")
            print(f"   OK - {len(df)} lignes chargees (encodage: {encoding})")
            return df
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Impossible de lire {path} avec les encodages disponibles.")


def load_ratings(path=None):
    """
    Charge le fichier Ratings.csv.

    Args:
        path: Chemin vers le fichier. Si None, utilise le chemin par défaut.

    Returns:
        pd.DataFrame: DataFrame des ratings bruts.
    """
    if path is None:
        path = os.path.join(RAW_DIR, "Ratings.csv")

    print(f"[RATINGS] Chargement des ratings depuis : {path}")

    for encoding in ["utf-8", "latin-1", "iso-8859-1"]:
        try:
            df = pd.read_csv(path, sep=";", encoding=encoding, on_bad_lines="skip")
            print(f"   OK - {len(df)} lignes chargees (encodage: {encoding})")
            return df
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Impossible de lire {path} avec les encodages disponibles.")

def load_academic_data(path=None):
    """
    Charge le fichier academic_scifi_books.csv.
    """
    if path is None:
        path = os.path.join(RAW_DIR, "academic_scifi_books.csv")
    
    print(f"[ACADEMIC] Chargement depuis : {path}")
    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8")
        print(f"   OK - {len(df)} livres académiques chargés")
        return df
    except Exception as e:
        print(f"   ERREUR chargement livres académiques : {e}")
        return pd.DataFrame()


def load_all():
    """
    Charge les trois datasets bruts.

    Returns:
        tuple: (books_df, users_df, ratings_df)
    """
    books = load_books()
    users = load_users()
    ratings = load_ratings()
    academic = load_academic_data()
    return books, users, ratings, academic
