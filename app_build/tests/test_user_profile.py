import pytest
import os
import json
import shutil
import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock
from src.user_profile import UserProfileManager

TEST_DIR = tempfile.mkdtemp()
TEST_FEEDBACKS_FILE = os.path.join(TEST_DIR, "feedbacks.json")

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown_dirs():
    os.makedirs(TEST_DIR, exist_ok=True)
    yield
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)


def test_save_and_load_feedback():
    with patch("src.user_profile.FEEDBACKS_FILE", TEST_FEEDBACKS_FILE):
        UserProfileManager.save_feedback("book", "Book X", "like")
        UserProfileManager.save_feedback("movie", "Movie Y", "favorite")
        UserProfileManager.save_feedback("book", "Book Z", "dislike")
        
        feedbacks = UserProfileManager.load_feedbacks()
        assert feedbacks["book::Book X"] == "like"
        assert feedbacks["movie::Movie Y"] == "favorite"
        assert feedbacks["book::Book Z"] == "dislike"
        
        # Test Reset
        UserProfileManager.reset_feedbacks()
        assert not os.path.exists(TEST_FEEDBACKS_FILE)
        assert UserProfileManager.load_feedbacks() == {}


def test_build_profile():
    with patch("src.user_profile.FEEDBACKS_FILE", TEST_FEEDBACKS_FILE):
        UserProfileManager.save_feedback("book", "Book A", "like")
        UserProfileManager.save_feedback("book", "Book B", "favorite")
        UserProfileManager.save_feedback("book", "Book C", "dislike")
        
        # Mock Recommender to supply metadata for Book A, B, C
        mock_recommender = MagicMock()
        mock_recommender.get_book_info.side_effect = lambda title: {
            "Book A": {"theme": "Sci-Fi", "author": "Author X"},
            "Book B": {"theme": "Sci-Fi", "author": "Author Y"},
            "Book C": {"theme": "Fantasy", "author": "Author Z"}
        }.get(title)
        
        profile = UserProfileManager.build_profile(mock_recommender)
        
        assert "Sci-Fi" in profile["favorite_genres"]
        assert "Author X" in profile["favorite_authors"]
        assert "Fantasy" in profile["disliked_genres"]


def test_rerank_recommendations():
    with patch("src.user_profile.FEEDBACKS_FILE", TEST_FEEDBACKS_FILE):
        UserProfileManager.reset_feedbacks()
        UserProfileManager.save_feedback("book", "Book Love", "like")
        UserProfileManager.save_feedback("book", "Book Hate", "dislike")
        
        mock_recommender = MagicMock()
        mock_recommender.get_book_info.side_effect = lambda title: {
            "Book Love": {"theme": "Sci-Fi", "author": "Author Good"},
            "Book Hate": {"theme": "Horror", "author": "Author Bad"},
            "Book Neutral": {"theme": "Romance", "author": "Author Neutral"}
        }.get(title)
        
        # DataFrame de recommendations d'entrée
        recs_df = pd.DataFrame({
            "Book-Title": ["Book Love", "Book Neutral", "Book Hate"],
            "Similarity-Score": [0.6, 0.7, 0.8], # Book Hate a le plus gros score de similarité de base
            "Author": ["Author Good", "Author Neutral", "Author Bad"],
            "Theme": ["Sci-Fi", "Romance", "Horror"]
        })
        
        reranked = UserProfileManager.rerank_recommendations(recs_df, "book", mock_recommender)
        
        # Book Hate doit se retrouver à la fin à cause de la pénalité de dislike (boost = 0.1)
        assert reranked.iloc[-1]["Book-Title"] == "Book Hate"
        assert reranked.iloc[-1]["Personalized-Score"] < 0.1
        
        # Book Love a un boost de like (1.2) + boost de son theme préféré Sci-Fi (1.2) + boost de son auteur préféré (1.2)
        # Donc son Personalized-Score doit être supérieur à son score initial de 0.6
        love_row = reranked[reranked["Book-Title"] == "Book Love"].iloc[0]
        assert love_row["Personalized-Score"] > 0.6
        assert "Thème préféré" in love_row["Personalization-Reason"]
