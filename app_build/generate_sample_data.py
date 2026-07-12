import pandas as pd
import numpy as np
import os
import sys
import io
import subprocess

# Fix Windows console encoding for emoji/unicode
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

# ─── Configuration ───────────────────────────────────────────────
NUM_BOOKS = 500
NUM_USERS = 200
NUM_RATINGS = 5000
SEED = 42

# Répertoire de sortie
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")


def generate_books(n=NUM_BOOKS):
    """Génère un DataFrame de livres fictifs réalistes."""
    np.random.seed(SEED)

    adjectives = [
        "The Great", "Lost", "Dark", "Silent", "Hidden", "Last", "First",
        "Brave", "Wild", "Forgotten", "Sacred", "Broken", "Golden", "Silver",
        "Endless", "Eternal", "Ancient", "Modern", "Digital", "Secret"
    ]
    nouns = [
        "Garden", "River", "Mountain", "Ocean", "Forest", "City", "Dream",
        "Journey", "Legacy", "Mystery", "Shadow", "Light", "Storm", "Fire",
        "Wind", "Star", "Moon", "Sun", "World", "Bridge", "Tower", "Kingdom",
        "Empire", "Horizon", "Dawn", "Dusk", "Chronicle", "Tale", "Song", "Path"
    ]
    authors_first = [
        "James", "Sarah", "Michael", "Emily", "David", "Anna", "Robert",
        "Maria", "John", "Laura", "William", "Sophie", "Thomas", "Claire",
        "Daniel", "Emma", "Charles", "Alice", "George", "Olivia"
    ]
    authors_last = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor", "Thomas",
        "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris"
    ]
    publishers = [
        "Penguin Books", "HarperCollins", "Random House", "Simon & Schuster",
        "Hachette", "Macmillan", "Oxford Press", "Cambridge Press",
        "Vintage Books", "Bloomsbury", "Scholastic", "Crown Publishing"
    ]

    books = []
    used_isbns = set()
    
    # Injection de vrais ISBNs pour l'API Open Library
    real_isbns = [
        "0441172717", "0553293354", "0451524934", "0061120081", "0345339703",
        "0439064872", "0142437204", "0141439513", "0743273565", "0618260307",
        "0345339711", "0345339738", "0307593671", "0385504209", "125031318X",
        "1501110365", "0385514239", "1594130019", "0439139597", "0439136350"
    ]
    
    for isbn in real_isbns:
        used_isbns.add(isbn)
        title = f"{np.random.choice(adjectives)} {np.random.choice(nouns)} (Real ISBN)"
        author = f"{np.random.choice(authors_first)} {np.random.choice(authors_last)}"
        books.append({
            "ISBN": isbn,
            "Book-Title": title,  # Sera écrasé par Open Library
            "Book-Author": author, # Sera écrasé
            "Year-Of-Publication": np.random.randint(1950, 2024),
            "Publisher": np.random.choice(publishers),
            "Image-URL-S": f"http://images.example.com/books/{isbn}.jpg",
            "Image-URL-M": f"http://images.example.com/books/{isbn}_m.jpg",
            "Image-URL-L": f"http://images.example.com/books/{isbn}_l.jpg",
        })

    # Compléter avec des faux livres pour atteindre NUM_BOOKS
    for i in range(n - len(real_isbns)):
        while True:
            isbn = f"{np.random.randint(100000000, 999999999)}{np.random.randint(0, 10)}"
            if isbn not in used_isbns:
                used_isbns.add(isbn)
                break

        title = f"{np.random.choice(adjectives)} {np.random.choice(nouns)}"
        if np.random.random() > 0.6:
            title += f": {np.random.choice(nouns)} of {np.random.choice(nouns)}"

        author = f"{np.random.choice(authors_first)} {np.random.choice(authors_last)}"
        year = np.random.randint(1950, 2024)
        publisher = np.random.choice(publishers)
        img_url = f"http://images.example.com/books/{isbn}.jpg"

        books.append({
            "ISBN": isbn,
            "Book-Title": title,
            "Book-Author": author,
            "Year-Of-Publication": year,
            "Publisher": publisher,
            "Image-URL-S": img_url,
            "Image-URL-M": img_url.replace(".jpg", "_m.jpg"),
            "Image-URL-L": img_url.replace(".jpg", "_l.jpg"),
        })

    df = pd.DataFrame(books)

    # Doublons et anomalies
    duplicates = df.sample(5, random_state=SEED)
    df = pd.concat([df, duplicates], ignore_index=True)

    nan_indices = np.random.choice(df.index, size=10, replace=False)
    df.loc[nan_indices[:5], "Book-Author"] = np.nan
    df.loc[nan_indices[5:], "Year-Of-Publication"] = 0

    return df


def run_data_designer(config_file, num_records, dataset_name):
    """Run data-designer CLI to generate a dataset."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Clear existing folder to prevent timestamped folder creation by Data Designer
    dataset_dir = os.path.join(OUTPUT_DIR, dataset_name)
    if os.path.exists(dataset_dir):
        import shutil
        shutil.rmtree(dataset_dir)
        
    cmd = [
        "data-designer", "create", 
        config_file, 
        "--num-records", str(num_records), 
        "--dataset-name", dataset_name,
        "--output-format", "csv",
        "--artifact-path", OUTPUT_DIR
    ]
    print(f"    Running: {' '.join(cmd)}")
    subprocess.run(cmd, env=env, check=True)
    
    # data-designer creates it as {OUTPUT_DIR}/{dataset_name}/{dataset_name}.csv
    # We move it to the root of {OUTPUT_DIR}
    src_csv = os.path.join(OUTPUT_DIR, dataset_name, f"{dataset_name}.csv")
    dst_csv = os.path.join(OUTPUT_DIR, f"{dataset_name}.csv")
    
    if os.path.exists(src_csv):
        # Move and rename
        if os.path.exists(dst_csv):
            os.remove(dst_csv)
        os.rename(src_csv, dst_csv)
        # Read the resulting dataframe
        return pd.read_csv(dst_csv)
    else:
        raise FileNotFoundError(f"Data Designer did not produce the expected CSV at {src_csv}")

def main():
    """Point d'entrée : génère et sauvegarde les 3 CSV."""
    print("📚 BookLens — Génération des données d'exemple...")

    # Créer le répertoire de sortie
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Générer les données (Livres en Python natif)
    print("  → Génération des livres...")
    books = generate_books()
    books.to_csv(os.path.join(OUTPUT_DIR, "Books.csv"), index=False, sep=";")
    print(f"    ✓ {len(books)} entrées sauvegardées")

    # Générer les utilisateurs via NVIDIA Data Designer
    print("  → Génération des utilisateurs (via NVIDIA Data Designer)...")
    try:
        users = run_data_designer("data_designer_users.py", NUM_USERS, "Users")
        # Format the dataframe to match the expected format (semicolon separated)
        users = users[["User-ID", "Location", "Age"]]
        users.to_csv(os.path.join(OUTPUT_DIR, "Users.csv"), index=False, sep=";")
        print(f"    ✓ {len(users)} entrées générées par l'IA")
    except Exception as e:
        print(f"    ❌ Échec de la génération Data Designer : {e}")
        print("    Veuillez vérifier l'installation de data-designer.")
        return

    # Générer les ratings via NVIDIA Data Designer
    print("  → Génération des ratings (via NVIDIA Data Designer)...")
    try:
        ratings = run_data_designer("data_designer_ratings.py", NUM_RATINGS, "Ratings")
        ratings = ratings[["User-ID", "ISBN", "Book-Rating"]]
        ratings.to_csv(os.path.join(OUTPUT_DIR, "Ratings.csv"), index=False, sep=";")
        print(f"    ✓ {len(ratings)} entrées générées par l'IA")
    except Exception as e:
        print(f"    ❌ Échec de la génération Data Designer : {e}")
        return

    print(f"\n✅ Fichiers sauvegardés dans : {OUTPUT_DIR}")
    print("   - Books.csv")
    print("   - Users.csv")
    print("   - Ratings.csv")

if __name__ == "__main__":
    main()
