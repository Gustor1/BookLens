import json
import os
import streamlit as st

# Langues supportées
SUPPORTED_LANGUAGES = {
    "fr": "Français",
    "en": "English",
    "zh": "中文 (Simplifié)"
}
DEFAULT_LANGUAGE = "fr"

def load_translations(lang: str) -> dict:
    """Charge le fichier JSON de traduction pour la langue donnée."""
    locale_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "locales")
    file_path = os.path.join(locale_dir, f"{lang}.json")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to default language if file not found
        if lang != DEFAULT_LANGUAGE:
            return load_translations(DEFAULT_LANGUAGE)
        return {}
    except json.JSONDecodeError:
        return {}

def init_i18n():
    """Initialise la langue dans st.session_state si elle n'existe pas."""
    if "lang" not in st.session_state:
        st.session_state["lang"] = DEFAULT_LANGUAGE
        try:
            update_library_page_filename(DEFAULT_LANGUAGE)
        except Exception:
            pass
    
    # Charger les traductions pour la langue actuelle
    if "translations" not in st.session_state or st.session_state.get("_last_lang") != st.session_state["lang"]:
        st.session_state["translations"] = load_translations(st.session_state["lang"])
        st.session_state["_last_lang"] = st.session_state["lang"]

def t(key: str, default: str = None) -> str:
    """
    Récupère la traduction pour une clé donnée.
    Supporte la notation pointée (ex: "home.title").
    """
    if "translations" not in st.session_state:
        init_i18n()
        
    keys = key.split('.')
    val = st.session_state["translations"]
    
    for k in keys:
        if isinstance(val, dict) and k in val:
            val = val[k]
        else:
            return default if default is not None else key
            
    return val if isinstance(val, str) else (default if default is not None else key)

def language_selector():
    """Affiche le sélecteur de langue dans la sidebar."""
    init_i18n()
    
    # Inverser le dictionnaire pour obtenir le code à partir du nom
    lang_names = list(SUPPORTED_LANGUAGES.values())
    current_lang_name = SUPPORTED_LANGUAGES.get(st.session_state["lang"], SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE])
    
    # Trouver l'index de la langue actuelle
    index = lang_names.index(current_lang_name) if current_lang_name in lang_names else 0
    
    selected_name = st.sidebar.selectbox(
        "🌐 Language / Langue",
        options=lang_names,
        index=index,
        key="lang_selector_ui"
    )
    
    # Retrouver le code langue
    selected_code = next(code for code, name in SUPPORTED_LANGUAGES.items() if name == selected_name)
    
    if selected_code != st.session_state["lang"]:
        st.session_state["lang"] = selected_code
        st.session_state["translations"] = load_translations(selected_code)
        st.session_state["_last_lang"] = selected_code
        
        # Renommer la page bibliothèque selon la langue active
        try:
            update_library_page_filename(selected_code)
        except Exception:
            pass
            
        st.rerun()

def update_library_page_filename(lang: str):
    """Renomme la page de bibliothèque de recherche selon la langue active."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pages_dir = os.path.join(base_dir, "pages")
    if not os.path.exists(pages_dir):
        return

    # Nom cible selon la langue
    target_names = {
        "fr": "10_📚_Bibliothèque_de_recherche.py",
        "en": "10_📚_Research_Library.py",
        "zh": "10_📚_研究文献库.py"
    }
    target_name = target_names.get(lang, target_names["fr"])
    
    # Trouver le fichier actuel commençant par 10_📚_
    current_name = None
    try:
        for f in os.listdir(pages_dir):
            if f.startswith("10_📚_") and f.endswith(".py"):
                current_name = f
                break
    except Exception:
        return
            
    if current_name and current_name != target_name:
        src_path = os.path.join(pages_dir, current_name)
        dst_path = os.path.join(pages_dir, target_name)
        try:
            if os.path.exists(dst_path):
                os.remove(dst_path)
            os.rename(src_path, dst_path)
        except Exception:
            pass
