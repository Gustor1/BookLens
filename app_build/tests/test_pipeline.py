import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# Ajuster le path pour importer src
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_cleaner import run_pipeline
from src.recommender import BookRecommender
from src.agent import BookLensAgent

def test_data_pipeline_execution():
    """
    Test basique pour s'assurer que le pipeline ETL génère bien
    un dataset final fusionné (merged_dataset.csv) non vide.
    """
    # Exécuter le pipeline complet (nettoyage + fusion)
    # Note: Cela nécessite que les fichiers raw soient présents, ce qui est le cas de notre environnement.
    run_pipeline()
    
    merged_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "merged_dataset.csv")
    assert os.path.exists(merged_path), "Le fichier fusionné doit être créé."
    
    df = pd.read_csv(merged_path)
    assert not df.empty, "Le dataset final ne doit pas être vide."
    assert "Book-Title" in df.columns, "Le dataset doit contenir des métadonnées de livres."
    assert "Book-Rating" in df.columns, "Le dataset doit contenir les notes."

def test_recommender_basic():
    """
    Test que le système de recommandation peut s'entraîner et retourner des suggestions.
    """
    merged_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "merged_dataset.csv")
    df = pd.read_csv(merged_path)
    
    rec = BookRecommender()
    rec.fit(df)
    
    # Prendre le premier livre de la liste pour demander une recommandation
    book_list = rec.get_book_list()
    assert len(book_list) > 0, "La liste des livres éligibles ne doit pas être vide."
    
    target_book = book_list[0]
    recs = rec.get_recommendations(target_book, n=3)
    
    assert recs is not None, "Les recommandations ne doivent pas être None."
    assert len(recs) > 0, "Doit retourner au moins une recommandation."
    assert "Book-Title" in recs.columns, "Doit contenir le titre."
    assert "Similarity-Score" in recs.columns, "Doit contenir le score."

@patch('src.agent.generate_response')
def test_agent_mocked_success(mock_gen_response):
    """
    Test que l'agent retourne bien le contenu de l'API lorsqu'il réussit.
    """
    mock_gen_response.return_value = "Mocked LLM Response"
    
    # Forcer l'activation LLM
    with patch.dict(os.environ, {"NVIDIA_API_KEY": "test_key"}):
        agent = BookLensAgent()
        
        response = agent.answer("Une question de test")
        assert "Mocked LLM Response" in response

@patch('src.agent.generate_response')
def test_agent_mocked_failure(mock_gen_response):
    """
    Test que l'agent gère proprement une exception API.
    """
    mock_gen_response.side_effect = Exception("API Timeout")
    
    with patch.dict(os.environ, {"NVIDIA_API_KEY": "test_key"}):
        agent = BookLensAgent()
        
        response = agent.answer("Une question de test")
        assert "API Timeout" in response
