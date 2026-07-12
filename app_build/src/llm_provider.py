"""
BookLens — Abstraction des Fournisseurs LLM (Couche Provider)
Gère l'accès aux différentes APIs de modèles (NVIDIA, Hugging Face, etc.)
sans exposer les clés ou la logique d'authentification à l'agent.
"""

import os
import requests
from dotenv import load_dotenv

# Tenter d'importer openai
try:
    import openai
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

load_dotenv()

# Modèles par défaut
DEFAULT_MODELS = {
    "nvidia": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
    "huggingface": "meta-llama/Llama-3.2-3B-Instruct"  # Modèle gratuit et rapide sur Inference API
}

# Endpoints OpenAI-compatibles
ENDPOINTS = {
    "nvidia": "https://integrate.api.nvidia.com/v1",
    "huggingface": "https://router.huggingface.co/v1"
}

def get_api_key(provider: str) -> str:
    """Récupère la clé API de manière sécurisée (secrets Streamlit puis Env var)."""
    env_key_name = f"{provider.upper()}_API_KEY"
    try:
        import streamlit as st
        # st.secrets pète une exception si le fichier secrets.toml n'existe pas
        key = st.secrets.get(env_key_name, os.environ.get(env_key_name, ""))
    except Exception:
        key = os.environ.get(env_key_name, "")
    return key

def is_provider_active(provider: str) -> bool:
    """Vérifie si le provider est correctement configuré (SDK présent et clé valide)."""
    if not HAS_OPENAI:
        return False
    key = get_api_key(provider)
    return bool(key and key.strip())

def generate_response(messages: list, provider: str = "nvidia", model: str = None, **kwargs) -> str:
    """
    Génère une réponse textuelle en routant vers le bon fournisseur.
    
    Args:
        messages: Liste de dictionnaires au format OpenAI (role/content).
        provider: "nvidia" ou "huggingface".
        model: Identifiant du modèle (si None, utilise le modèle par défaut).
        **kwargs: Autres paramètres optionnels (temperature, max_tokens, etc).
        
    Returns:
        str: Le contenu de la réponse texte.
    """
    if not is_provider_active(provider):
        raise ValueError(f"Le fournisseur '{provider}' n'est pas configuré (Clé API manquante).")

    if provider not in ENDPOINTS:
        raise ValueError(f"Le fournisseur '{provider}' n'est pas supporté.")

    api_key = get_api_key(provider)
    base_url = ENDPOINTS[provider]
    target_model = model if model else DEFAULT_MODELS.get(provider)

    # Paramètres par défaut sécurisés
    temperature = kwargs.get("temperature", 0.6)
    top_p = kwargs.get("top_p", 0.95)
    max_tokens = kwargs.get("max_tokens", 4096)

    from src.monitoring import track_api_call

    try:
        with track_api_call(provider):
            client = OpenAI(
                base_url=base_url,
                api_key=api_key
            )

            completion = client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stream=False
            )
            return completion.choices[0].message.content

    except openai.AuthenticationError:
        raise PermissionError(f"[{provider.upper()}] Clé API invalide ou expirée.")
    except openai.RateLimitError:
        raise ConnectionError(f"[{provider.upper()}] Limite de requêtes (Quota) atteinte.")
    except openai.APIConnectionError:
        raise ConnectionError(f"[{provider.upper()}] Impossible de joindre le serveur API.")
    except Exception as e:
        raise RuntimeError(f"[{provider.upper()}] Erreur inattendue : {str(e)}")

# ─── Multimodalité (Hugging Face) ──────────────────────────────────────

def generate_image(prompt: str) -> bytes:
    """
    Génère une image via l'API Hugging Face (FLUX.1-dev).
    Retourne les bytes de l'image.
    """
    api_key = get_api_key("huggingface")
    if not api_key:
        raise PermissionError("[HUGGINGFACE] Clé API manquante pour la génération d'image.")
    
    url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": prompt}
    
    from src.monitoring import track_api_call
    with track_api_call("huggingface_image"):
        response = requests.post(url, headers=headers, json=payload, timeout=40)
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            raise ConnectionError("Le modèle d'image est en cours de chargement. Veuillez réessayer dans quelques secondes.")
        elif response.status_code == 429:
            raise ConnectionError("Quota dépassé pour la génération d'image.")
        else:
            raise RuntimeError(f"Erreur API lors de la génération d'image : {response.status_code} - {response.text}")

def generate_audio(text: str, lang: str = "fr") -> bytes:
    """
    Génère de l'audio via l'API Hugging Face (MMS-TTS).
    Retourne les bytes de l'audio.
    """
    api_key = get_api_key("huggingface")
    if not api_key:
        raise PermissionError("[HUGGINGFACE] Clé API manquante pour la synthèse vocale.")
    
    # Sélection du modèle TTS selon la langue
    tts_models = {
        "fr": "facebook/mms-tts-fra",
        "en": "facebook/mms-tts-eng",
        "zh": "facebook/mms-tts-cmn"
    }
    model_id = tts_models.get(lang, tts_models["en"])
    
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": text}
    
    from src.monitoring import track_api_call
    with track_api_call("huggingface_audio"):
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            raise ConnectionError("Le modèle vocal est en cours de chargement. Veuillez réessayer dans quelques secondes.")
        elif response.status_code == 429:
            raise ConnectionError("Quota dépassé pour la synthèse vocale.")
        else:
            raise RuntimeError(f"Erreur API lors de la synthèse vocale : {response.status_code} - {response.text}")
