"""
📘 BookLens — Page Agent IA
Interface de chat pour interagir avec l'assistant IA (LLM).
"""

import streamlit as st
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.agent import BookLensAgent
from src.ui import inject_custom_css
from src.i18n import t

st.set_page_config(page_title=t("agent.page_title", " Agent IA — BookLens"), page_icon="🤖", layout="wide")
inject_custom_css()

from src.llm_provider import is_provider_active

# ─── Configuration Sécurité & Rate Limit ───────────────────────
MAX_MSG_PER_MINUTE = 10
MAX_MSG_LENGTH = 1000

if "msg_timestamps" not in st.session_state:
    st.session_state["msg_timestamps"] = []

if "llm_provider" not in st.session_state:
    st.session_state["llm_provider"] = "nvidia"

def check_rate_limit():
    """Vérifie si l'utilisateur a dépassé la limite de requêtes."""
    current_time = time.time()
    # Nettoyer les timestamps vieux de plus de 60 secondes
    st.session_state["msg_timestamps"] = [
        ts for ts in st.session_state["msg_timestamps"] 
        if current_time - ts < 60
    ]
    return len(st.session_state["msg_timestamps"]) < MAX_MSG_PER_MINUTE

def log_message():
    st.session_state["msg_timestamps"].append(time.time())

# ─── Vérification ───────────────────────────────────────────────
if "recommender" not in st.session_state or "merged_df" not in st.session_state:
    st.warning(t("agent.warning_load", "⚠️ Veuillez d'abord visiter la page d'accueil pour charger les données."))
    st.stop()

# ─── Initialiser l'agent & RAG ──────────────────────────────────
if "rag_service" not in st.session_state:
    from src.rag.rag_service import RAGService
    st.session_state["rag_service"] = RAGService()
rag_service = st.session_state["rag_service"]

if "agent" not in st.session_state:
    st.session_state["agent"] = BookLensAgent(
        recommender=st.session_state["recommender"],
        metrics=st.session_state.get("metrics", {}),
        merged_df=st.session_state["merged_df"],
    )

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

agent = st.session_state["agent"]

# ─── En-tête ────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-container" style="padding: 2rem;">
    <h2 class="hero-title" style="font-size: 2.2rem;">{t("agent.hero_title", "🤖 Assistant IA BookLens")}</h2>
    <p class="hero-subtitle">{t("agent.hero_subtitle", "Interrogez la base de données en langage naturel.")}</p>
</div>
""", unsafe_allow_html=True)

# ─── Sélecteur de Mode & Provider ───────────────────────────────
col_prov1, col_prov2 = st.columns([7, 3])
with col_prov1:
    st.session_state["agent_mode"] = st.radio(
        t("agent.mode_label", "Mode de l'Agent"),
        options=["general", "rag"],
        format_func=lambda x: t(f"agent.mode_{x}", "Chat général" if x == "general" else "Recherche dans mes documents"),
        horizontal=True,
        key="agent_mode_selector"
    )
with col_prov2:
    provider_options = {
        "nvidia": t("agent.provider_nvidia", "NVIDIA (Llama Nemotron)"),
        "huggingface": t("agent.provider_hf", "Hugging Face (Llama 3.2)")
    }
    
    st.session_state["llm_provider"] = st.selectbox(
        t("agent.provider_selector", "Fournisseur d'IA"),
        options=["nvidia", "huggingface"],
        format_func=lambda x: provider_options[x],
        index=0 if st.session_state["llm_provider"] == "nvidia" else 1
    )

    if st.session_state["llm_provider"] == "huggingface":
        st.markdown(f"**{t('agent.capabilities', 'Capacités')}** : 💬 {t('agent.cap_text', 'Texte')} | 🎨 {t('agent.cap_image', 'Image')} | 🔊 {t('agent.cap_voice', 'Voix')}")
    else:
        st.markdown(f"**{t('agent.capabilities', 'Capacités')}** : 💬 {t('agent.cap_text', 'Texte')}")

# Affichage du statut du LLM
active_provider = st.session_state["llm_provider"]
if is_provider_active(active_provider):
    st.success(t("agent.llm_connected", "✅ **LLM Connecté** : L'assistant utilise le modèle NVIDIA Llama 3.3. Posez n'importe quelle question sur les livres ou les données.").replace("NVIDIA Llama 3.3", provider_options[active_provider]))
else:
    st.warning(t("agent.offline_mode", "⚠️ **Mode Hors-ligne** : Clé API non configurée. L'assistant utilise des règles statiques limitées (Fallback)."))

# Avertissement si mode RAG actif mais aucun document indexé
if st.session_state.get("agent_mode", "general") == "rag":
    docs = rag_service.list_documents()
    if not docs:
        st.warning(t("agent.no_docs_rag_warning", "⚠️ Aucun document n'est indexé. Rendez-vous dans la Bibliothèque pour importer des PDF afin d'utiliser la recherche sémantique."))

st.markdown("---")

# ─── Suggestions ────────────────────────────────────────────────
st.markdown(t("agent.suggestions_title", "#### 💡 Suggestions de questions"))

suggestions = [
    t("agent.sug_1", "Quelles sont les statistiques du dataset ?"),
    t("agent.sug_2", "Quel est le livre le mieux noté ?"),
    t("agent.sug_3", "Explique moi comment marche l'algorithme de recommandation."),
]

cols = st.columns(3)
for i, suggestion in enumerate(suggestions):
    with cols[i % 3]:
        if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
            if check_rate_limit():
                # En mode RAG, on vérifie d'abord si des docs sont présents
                is_rag = st.session_state.get("agent_mode", "general") == "rag"
                if is_rag and not rag_service.list_documents():
                    st.error(t("agent.no_docs_error", "Veuillez d'abord indexer des documents avant d'utiliser le mode RAG."))
                else:
                    log_message()
                    st.session_state["chat_history"].append({
                        "role": "user",
                        "content": suggestion
                    })
                    
                    rag_context = ""
                    rag_sources = []
                    if is_rag:
                        results = rag_service.query(suggestion, n_results=4)
                        if results:
                            rag_sources = results
                            rag_context = "\n\n".join(f"[Source: {r['metadata']['filename']}, Page: {r['metadata']['page']}]\n{r['content']}" for r in results)
                    
                    # On passe la langue actuelle à l'agent
                    current_lang = st.session_state.get("lang", "fr")
                    response = agent.answer(
                        suggestion, 
                        chat_history=st.session_state["chat_history"], 
                        lang=current_lang,
                        provider=st.session_state["llm_provider"],
                        rag_context=rag_context if is_rag else None
                    )
                    
                    msg_dict = {"role": "assistant"}
                    if isinstance(response, dict) and response.get("type") == "image":
                        msg_dict["content"] = response["content"]
                        msg_dict["image_bytes"] = response["image_bytes"]
                    else:
                        msg_dict["content"] = response
                    
                    if is_rag and rag_sources:
                        msg_dict["sources"] = rag_sources
                    
                    st.session_state["chat_history"].append(msg_dict)
                    st.rerun()
            else:
                st.error(t("agent.rate_limit_error", "⏳ **Rate Limit** : Vous avez dépassé la limite de messages par minute. Veuillez patienter."))

st.markdown("<br>", unsafe_allow_html=True)

# ─── Recherche Vocale ──────────────────────────────────────────
with st.expander(t("agent.voice_search_title", "🎙️ Recherche Vocale (Mode Démo / Micro)"), expanded=False):
    st.write(t("agent.voice_search_desc", "Parlez dans votre micro pour dicter votre question à l'assistant. (Cliquez ci-dessous pour simuler l'enregistrement audio)"))
    
    demo_phrases = [
        t("agent.sug_1", "Quelles sont les statistiques du dataset ?"),
        t("agent.sug_3", "Explique moi comment marche l'algorithme de recommandation."),
        "Recommande-moi un livre de science-fiction dystopique."
    ]
    
    selected_voice = st.selectbox(t("agent.voice_phrase_label", "Choisissez la phrase à dicter :"), options=demo_phrases)
    
    col_v1, col_v2 = st.columns([1, 1])
    with col_v1:
        if st.button(t("agent.voice_record_btn", "🎙️ Lancer l'enregistrement (3s)"), key="voice_record", use_container_width=True):
            st.session_state["voice_transcription"] = selected_voice
            st.toast("🎙️ Audio enregistré avec succès !")
            
    with col_v2:
        if st.session_state.get("voice_transcription"):
            if st.button(t("agent.voice_send_btn", "🚀 Envoyer la transcription"), key="voice_send", use_container_width=True):
                voice_query = st.session_state["voice_transcription"]
                st.session_state["voice_transcription"] = None
                
                is_rag = st.session_state.get("agent_mode", "general") == "rag"
                if is_rag and not rag_service.list_documents():
                    st.error(t("agent.no_docs_error", "Veuillez d'abord indexer des documents avant d'utiliser le mode RAG."))
                else:
                    log_message()
                    st.session_state["chat_history"].append({
                        "role": "user",
                        "content": voice_query
                    })
                    
                    rag_context = ""
                    rag_sources = []
                    if is_rag:
                        with st.spinner(t("agent.searching_docs", "Recherche dans les documents...")):
                            results = rag_service.query(voice_query, n_results=4)
                            if results:
                                rag_sources = results
                                rag_context = "\n\n".join(f"[Source: {r['metadata']['filename']}, Page: {r['metadata']['page']}]\n{r['content']}" for r in results)
                    
                    with st.spinner(t("agent.thinking", "L'agent réfléchit...")):
                        current_lang = st.session_state.get("lang", "fr")
                        response = agent.answer(
                            voice_query, 
                            chat_history=st.session_state["chat_history"], 
                            lang=current_lang,
                            provider=st.session_state["llm_provider"],
                            rag_context=rag_context if is_rag else None
                        )
                        
                    msg_dict = {"role": "assistant"}
                    if isinstance(response, dict) and response.get("type") == "image":
                        msg_dict["content"] = response["content"]
                        msg_dict["image_bytes"] = response["image_bytes"]
                    else:
                        msg_dict["content"] = response
                        
                    if is_rag and rag_sources:
                        msg_dict["sources"] = rag_sources
                        
                    st.session_state["chat_history"].append(msg_dict)
                    st.rerun()

    if st.session_state.get("voice_transcription"):
        st.success(f"🎙️ **{t('agent.transcription', 'Transcription')}** : \"{st.session_state['voice_transcription']}\"")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Zone de Chat ───────────────────────────────────────────────
chat_container = st.container(height=500)

with chat_container:
    if not st.session_state["chat_history"]:
        st.markdown(f"""
        <div style="text-align: center; color: #94A3B8; padding: 4rem 0;">
            <h1 style="font-size: 3rem; margin-bottom: 1rem;">💬</h1>
            <p>{t("agent.empty_chat", "La conversation est vide. Posez une question pour commencer !")}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        from src.llm_provider import generate_audio
        for idx, message in enumerate(st.session_state["chat_history"]):
            if message["role"] == "user":
                st.markdown(f"""
                <div style="background-color: rgba(13, 148, 136, 0.05); border: 1px solid rgba(13, 148, 136, 0.15); border-radius: 12px; padding: 1.25rem; margin-bottom: 1.25rem; border-left: 4px solid #0D9488;">
                    <strong style="color: #0D9488;">👤 Vous :</strong><br><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #121826; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 1.25rem; margin-bottom: 1.25rem; border-left: 4px solid #F59E0B;">
                    <strong style="color: #F59E0B;">🤖 Assistant :</strong><br><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Affichage des sources de RAG sous forme d'accordéon sous le message
                if message.get("sources"):
                    with st.expander(t("agent.sources_title", "📖 Sources utilisées")):
                        for src in message["sources"]:
                            is_suspicious = src["metadata"].get("is_suspicious", False)
                            border_color = "#EF4444" if is_suspicious else "#10B981"
                            st.markdown(f"""
                            <div style="border-left: 3px solid {border_color}; padding-left: 10px; margin-bottom: 8px;">
                                <strong>{src['metadata']['filename']}</strong> (Page {src['metadata']['page']}) - Similarity: {src['score']:.1%}<br>
                                <span style="font-style: italic; color: #94A3B8;">"{src['content']}"</span>
                            </div>
                            """, unsafe_allow_html=True)
                
                if "image_bytes" in message:
                    st.image(message["image_bytes"], use_container_width=True, output_format="PNG")
                
                if active_provider == "huggingface" and "image_bytes" not in message:
                    if "audio_bytes" in message:
                        st.audio(message["audio_bytes"], format="audio/wav")
                    else:
                        if st.button(t("agent.listen_btn", "🔊 Écouter la réponse"), key=f"tts_{idx}"):
                            with st.spinner(t("agent.generating_audio", "Génération de l'audio...")):
                                try:
                                    audio_bytes = generate_audio(message["content"], lang=st.session_state.get("lang", "fr"))
                                    message["audio_bytes"] = audio_bytes
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"{t('agent.audio_error', 'Erreur audio :')} {e}")

# ─── Input utilisateur ──────────────────────────────────────────
user_input = st.chat_input(t("agent.input_placeholder", "Posez votre question ici..."))

if user_input:
    is_rag = st.session_state.get("agent_mode", "general") == "rag"
    
    # 1. Validation de la longueur
    if len(user_input) > MAX_MSG_LENGTH:
        st.error(t("agent.length_error", "⚠️ **Erreur** : Votre message dépasse la limite autorisée."))
    
    # 2. Validation du Rate Limit
    elif not check_rate_limit():
        st.error(t("agent.rate_limit_error", "⏳ **Rate Limit** : Vous avez dépassé la limite de messages par minute. Veuillez patienter."))
        
    # 3. Validation RAG vide
    elif is_rag and not rag_service.list_documents():
        st.error(t("agent.no_docs_error", "Veuillez d'abord indexer des documents avant d'utiliser le mode RAG."))
    
    else:
        log_message()
        safe_input = user_input.replace("<", "&lt;").replace(">", "&gt;")
        
        # Ajouter le message utilisateur
        st.session_state["chat_history"].append({
            "role": "user",
            "content": safe_input
        })

        rag_context = ""
        rag_sources = []
        if is_rag:
            with st.spinner(t("agent.searching_docs", "Recherche dans les documents...")):
                results = rag_service.query(safe_input, n_results=4)
                if results:
                    rag_sources = results
                    rag_context = "\n\n".join(f"[Source: {r['metadata']['filename']}, Page: {r['metadata']['page']}]\n{r['content']}" for r in results)

        # Obtenir la réponse avec contexte
        with st.spinner(t("agent.thinking", "L'agent réfléchit...")):
            current_lang = st.session_state.get("lang", "fr")
            response = agent.answer(
                safe_input, 
                chat_history=st.session_state["chat_history"], 
                lang=current_lang,
                provider=st.session_state["llm_provider"],
                rag_context=rag_context if is_rag else None
            )

        # Ajouter la réponse
        msg_dict = {"role": "assistant"}
        if isinstance(response, dict) and response.get("type") == "image":
            msg_dict["content"] = response["content"]
            msg_dict["image_bytes"] = response["image_bytes"]
        else:
            msg_dict["content"] = response

        if is_rag and rag_sources:
            msg_dict["sources"] = rag_sources

        st.session_state["chat_history"].append(msg_dict)
        st.rerun()

# ─── Bouton reset et Mentions ──────────────────────────────────
st.markdown("---")
col1, col2 = st.columns([8, 2])
with col1:
    st.markdown(f"""
    <div style="font-size: 0.8rem; color: #64748B;">
        {t("agent.privacy", "🔒 <b>Sécurité & Confidentialité</b> : Les questions posées via ce chat sont transmises temporairement à l'API NVIDIA Build si la clé est configurée.")}
    </div>
    """, unsafe_allow_html=True)
with col2:
    if st.button(t("agent.clear_chat", "🗑️ Effacer l'historique"), key="clear_chat", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()
