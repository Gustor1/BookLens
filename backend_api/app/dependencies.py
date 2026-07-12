import os
import sys
import pandas as pd

# Add app_build to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_BUILD_DIR = os.path.join(BASE_DIR, "app_build")
if APP_BUILD_DIR not in sys.path:
    sys.path.insert(0, APP_BUILD_DIR)

# Set environment variables so the code uses the correct API key configurations
from app.config import settings
if settings.NVIDIA_API_KEY:
    os.environ["NVIDIA_API_KEY"] = settings.NVIDIA_API_KEY
if settings.HF_API_KEY:
    os.environ["HF_API_KEY"] = settings.HF_API_KEY
if settings.TMDB_API_KEY:
    os.environ["TMDB_API_KEY"] = settings.TMDB_API_KEY
if settings.RAWG_API_KEY:
    os.environ["RAWG_API_KEY"] = settings.RAWG_API_KEY

from src.data_cleaner import (
    clean_books, clean_users, clean_ratings,
    merge_datasets, generate_metrics, save_processed_data, integrate_academic_data
)
from src.recommender import BookRecommender
from src.rag.rag_service import RAGService
from src.agent import BookLensAgent

# Global singletons
_merged_df = None
_metrics = None
_recommender = None
_rag_service = None

def get_db():
    global _merged_df, _metrics
    if _merged_df is None:
        processed_path = os.path.join(APP_BUILD_DIR, "data", "processed", "merged_dataset.csv")
        if os.path.exists(processed_path):
            print(f"[API] Loading processed data from {processed_path}")
            _merged_df = pd.read_csv(processed_path)
            _metrics = generate_metrics(_merged_df)
        else:
            print("[API] Processed data not found. Loading and cleaning raw data...")
            # We change Cwd temporarily to APP_BUILD_DIR to load files correctly
            old_cwd = os.getcwd()
            try:
                os.chdir(APP_BUILD_DIR)
                from src.data_loader import load_all
                books, users, ratings, academic = load_all()
                books_clean = clean_books(books)
                users_clean = clean_users(users)
                ratings_clean = clean_ratings(ratings)
                books_clean, ratings_clean = integrate_academic_data(books_clean, users_clean, ratings_clean, academic)
                _merged_df = merge_datasets(books_clean, users_clean, ratings_clean)
                _metrics = generate_metrics(_merged_df)
                save_processed_data(_merged_df)
            finally:
                os.chdir(old_cwd)
    return _merged_df, _metrics

def get_recommender():
    global _recommender
    if _recommender is None:
        df, _ = get_db()
        _recommender = BookRecommender(min_ratings=2)
        model_path = os.path.join(APP_BUILD_DIR, "models", "recommender_model.pkl")
        if os.path.exists(model_path):
            print(f"[API] Loading recommender model from {model_path}")
            _recommender.load(model_path)
        else:
            print("[API] Recommender model not found. Fitting...")
            _recommender.fit(df)
            _recommender.save(model_path)
    return _recommender

def get_rag_service():
    global _rag_service
    if _rag_service is None:
        persist_dir = os.path.join(APP_BUILD_DIR, "data", "chroma_db")
        _rag_service = RAGService(persist_dir=persist_dir)
    return _rag_service

def get_agent():
    df, metrics = get_db()
    rec = get_recommender()
    return BookLensAgent(recommender=rec, metrics=metrics, merged_df=df)
