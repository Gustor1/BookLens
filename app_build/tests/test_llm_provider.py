"""
Tests unitaires pour la couche llm_provider.
Vérifie le bon routage vers les APIs de NVIDIA et Hugging Face.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.llm_provider import generate_response, is_provider_active, ENDPOINTS, DEFAULT_MODELS

@pytest.fixture
def mock_openai():
    with patch("src.llm_provider.OpenAI") as mock:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_message = MagicMock()
        mock_message.message.content = "Mocked Response"
        mock_completion.choices = [mock_message]
        mock_client.chat.completions.create.return_value = mock_completion
        mock.return_value = mock_client
        yield mock

@patch("src.llm_provider.get_api_key", return_value="fake_key")
def test_generate_response_nvidia(mock_get_api_key, mock_openai):
    """Teste que le provider NVIDIA route vers la bonne URL et utilise le bon modèle."""
    messages = [{"role": "user", "content": "Hello"}]
    response = generate_response(messages, provider="nvidia")
    
    assert response == "Mocked Response"
    mock_openai.assert_called_once_with(
        base_url=ENDPOINTS["nvidia"],
        api_key="fake_key"
    )
    mock_openai.return_value.chat.completions.create.assert_called_once_with(
        model=DEFAULT_MODELS["nvidia"],
        messages=messages,
        temperature=0.6,
        top_p=0.95,
        max_tokens=4096,
        stream=False
    )

@patch("src.llm_provider.get_api_key", return_value="fake_key")
def test_generate_response_huggingface(mock_get_api_key, mock_openai):
    """Teste que le provider Hugging Face route vers la bonne URL et utilise le bon modèle."""
    messages = [{"role": "user", "content": "Hello HF"}]
    response = generate_response(messages, provider="huggingface")
    
    assert response == "Mocked Response"
    mock_openai.assert_called_once_with(
        base_url=ENDPOINTS["huggingface"],
        api_key="fake_key"
    )
    mock_openai.return_value.chat.completions.create.assert_called_once_with(
        model=DEFAULT_MODELS["huggingface"],
        messages=messages,
        temperature=0.6,
        top_p=0.95,
        max_tokens=4096,
        stream=False
    )

@patch("src.llm_provider.get_api_key", return_value="")
def test_generate_response_missing_key(mock_get_api_key):
    """Vérifie qu'une erreur est levée si la clé est manquante."""
    with pytest.raises(ValueError, match="n'est pas configuré"):
        generate_response([{"role": "user", "content": "test"}], provider="nvidia")

def test_generate_response_invalid_provider():
    """Vérifie qu'une erreur est levée pour un fournisseur inconnu."""
    with patch("src.llm_provider.is_provider_active", return_value=True):
        with pytest.raises(ValueError, match="n'est pas supporté"):
            generate_response([{"role": "user", "content": "test"}], provider="inconnu")

@patch("src.llm_provider.requests.post")
@patch("src.llm_provider.get_api_key", return_value="fake_hf_key")
def test_generate_image(mock_get_api_key, mock_post):
    """Teste la génération d'image via l'API Hugging Face."""
    from src.llm_provider import generate_image
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_image_bytes"
    mock_post.return_value = mock_response
    
    result = generate_image("Un chat cyberpunk")
    
    assert result == b"fake_image_bytes"
    mock_post.assert_called_once()
    assert "FLUX.1-dev" in mock_post.call_args[0][0]
    
@patch("src.llm_provider.requests.post")
@patch("src.llm_provider.get_api_key", return_value="fake_hf_key")
def test_generate_audio(mock_get_api_key, mock_post):
    """Teste la génération d'audio via l'API Hugging Face."""
    from src.llm_provider import generate_audio
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_audio_bytes"
    mock_post.return_value = mock_response
    
    result = generate_audio("Bonjour", lang="fr")
    
    assert result == b"fake_audio_bytes"
    mock_post.assert_called_once()
    assert "mms-tts-fra" in mock_post.call_args[0][0]

@patch("src.llm_provider.requests.post")
@patch("src.llm_provider.get_api_key", return_value="fake_hf_key")
def test_generate_image_error(mock_get_api_key, mock_post):
    """Teste la gestion des erreurs API pour la génération d'image (ex: 503 loading)."""
    from src.llm_provider import generate_image
    
    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_post.return_value = mock_response
    
    with pytest.raises(ConnectionError, match="en cours de chargement"):
        generate_image("test")
