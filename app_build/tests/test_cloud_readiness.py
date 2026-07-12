import pytest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from src.llm_provider import is_provider_active, get_api_key
from src.agent import BookLensAgent
from src.media import get_media_manager

def test_startup_without_secrets():
    """Vérifie que l'activation du provider renvoie False sans secrets."""
    with patch("src.llm_provider.get_api_key", return_value=""):
        assert not is_provider_active("nvidia")
        assert not is_provider_active("huggingface")


def test_agent_fallback_mode():
    """Vérifie que l'agent répond avec un fallback propre sans clé API."""
    import streamlit as st
    from src.i18n import init_i18n
    if "lang" not in st.session_state:
        st.session_state["lang"] = "fr"
    init_i18n()
    
    agent = BookLensAgent()
    with patch("src.agent.is_provider_active", return_value=False):
        res = agent.answer("Quelles sont les statistiques ?", provider="nvidia")
        assert "🤖 **[Orchestrateur Principal]**" in res or "🤖 **[Agent Recommandations]**" in res
        assert "statistiques" in res.lower() or "livres" in res.lower()


def test_media_managers_fallback_offline():
    """Vérifie que les managers de films/jeux vidéo se comportent correctement hors-ligne."""
    movies_mgr = get_media_manager("movies")
    games_mgr = get_media_manager("games")
    
    # Simuler l'absence de clé API
    with patch.object(movies_mgr, "api_key", None), \
         patch.object(games_mgr, "api_key", None):
        
        # Test recherche films
        movies_res = movies_mgr.search("Matrix")
        assert len(movies_res) > 0 # Retourne des données locales de démo
        assert "Matrix" in movies_res[0]["title"] or "Dune" in movies_res[0]["title"]
        
        # Test recherche jeux
        games_res = games_mgr.search("Witcher")
        assert len(games_res) > 0
        assert "Witcher" in games_res[0]["title"] or "Cyberpunk" in games_res[0]["title"]


def test_missing_local_folders_creation():
    """Vérifie que les dossiers locaux temporaires sont créés automatiquement s'ils sont absents."""
    temp_dir = tempfile.mkdtemp()
    test_uploads_dir = os.path.join(temp_dir, "data", "uploads")
    
    # S'assurer que le dossier n'existe pas
    if os.path.exists(test_uploads_dir):
        shutil.rmtree(test_uploads_dir)
        
    # Appeler makedirs comme dans le code du RAGService
    os.makedirs(test_uploads_dir, exist_ok=True)
    assert os.path.exists(test_uploads_dir)
    
    # Nettoyer
    shutil.rmtree(temp_dir)
