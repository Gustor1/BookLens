import pytest
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.i18n import load_translations, t, init_i18n

def test_translations_load():
    """Vérifie que les 3 langues chargent un dict non vide."""
    fr = load_translations("fr")
    en = load_translations("en")
    zh = load_translations("zh")
    
    assert fr and isinstance(fr, dict), "Le français doit se charger."
    assert en and isinstance(en, dict), "L'anglais doit se charger."
    assert zh and isinstance(zh, dict), "Le chinois doit se charger."
    
    assert "home" in fr
    assert "home" in en
    assert "home" in zh

def test_t_function():
    """Test la fonction t() de récupération de clé avec fallback."""
    # Setup state
    if "lang" not in st.session_state:
        st.session_state["lang"] = "fr"
    init_i18n()
    
    # Test valid key
    assert t("home.feat_search", "Fallback") != "Fallback"
    
    # Test invalid key returns default
    assert t("invalid.key.path", "Fallback Default") == "Fallback Default"
    
    # Test missing key without default returns the key string
    assert t("missing.key") == "missing.key"
