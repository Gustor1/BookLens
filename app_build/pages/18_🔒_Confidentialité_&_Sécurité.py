import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.ui import inject_custom_css
from src.i18n import t, language_selector

# Configurer la page
st.set_page_config(page_title=t("security.page_title", "Sécurité & Confidentialité — BookLens"), page_icon="🔒", layout="wide")
inject_custom_css()

# Langue dans la sidebar
language_selector()

lang = st.session_state.get("lang", "fr")

if lang == "fr":
    st.markdown("# 🔒 Confidentialité & Sécurité de l'IA")
    st.markdown("<p style='color: #94A3B8;'>BookLens s'engage à être transparent sur l'usage des données, la sécurité logicielle et les garde-fous de l'agent IA.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💾 Données & Stockage Local")
        st.markdown("""
        - **Zéro Cloud Privé** : Toutes vos données d'interactions, préférences, et documents PDF ingérés restent strictement sur votre machine locale (laptop/CPU).
        - **Profil de Préférences** : Vos feedbacks (Favoris, J'aime, Déjà lu) sont enregistrés dans `data/user_profile/feedbacks.json`. Aucune donnée n'est revendue ou pistée.
        - **Base Vectorielle** : Les PDF scientifiques importés pour le RAG sont découpés en chunks de texte et stockés dans la base vectorielle locale `ChromaDB` (`data/chroma_db/`).
        """)
        
        st.markdown("### 📑 Politique de Suppression du RAG")
        st.markdown("""
        - Vous pouvez supprimer définitivement tout document importé depuis l'onglet **Bibliothèque de recherche**.
        - La suppression détruit immédiatement le fichier source, ses métadonnées dans la base SQLite locale, et l'ensemble de ses chunks vectoriels dans ChromaDB.
        """)
        
    with col2:
        st.markdown("### 🔑 Gestion des API & Clés Secrètes")
        st.markdown("""
        - Les requêtes d'évaluation et de chat utilisent les variables d'environnement locales (`.env` ou `.streamlit/secrets.toml`).
        - **Sécurité des logs** : Le système de logs de monitoring filtre et retire systématiquement toutes les clés API, jetons ou paramètres de prompts système complets.
        - Aucun export de rapport d'évaluation (JSON/CSV) ne contient de secrets ou données privées.
        """)
        
        st.markdown("### ⚠️ Limitation de Responsabilité & Hallucinations")
        st.markdown("""
        - Bien que BookLens impose des contraintes strictes à l'Agent IA pour qu'il cite ses sources (document, page), les LLMs peuvent parfois halluciner ou inventer des interprétations.
        - Veuillez toujours recouper les citations critiques directement avec le document PDF source.
        """)

elif lang == "zh":
    st.markdown("# 🔒 隐私安全与智能体合规性")
    st.markdown("<p style='color: #94A3B8;'>BookLens 致力于在数据使用、软件安全和 AI 智能体护栏方面保持透明。</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💾 本地数据存储")
        st.markdown("""
        - **零私有云端依赖**：您所有的交互数据、个性化偏好以及导入的 PDF 文档都严格保存在您的本地机器上（笔记本/CPU）。
        - **偏好配置文件**：您的反馈数据（收藏、喜欢、标记已读）记录在本地的 `data/user_profile/feedbacks.json`。我们不进行任何网络追踪或数据转售。
        - **向量数据库**：导入用于 RAG 的学术 PDF 被切分为文本块，并持久化在本地的 `ChromaDB` (`data/chroma_db/`) 中。
        """)
        
        st.markdown("### 📑 RAG 文档销毁政策")
        st.markdown("""
        - 您可以在 **文献库** 页面中永久删除任何导入的文档。
        - 触发删除操作将立即销毁源文件、SQLite 本地注册表中的元数据以及 ChromaDB 向量库中与之关联的所有切片数据。
        """)
        
    with col2:
        st.markdown("### 🔑 接口密钥安全")
        st.markdown("""
        - 评估与聊天中调用的外部 LLM 基于您的本地环境变量（`.env` 或 `.streamlit/secrets.toml`）。
        - **日志安全**：系统的监控与审计日志中已自动过滤并移除了全部敏感 API 密钥和完整系统提示词。
        - 导出的 JSON、CSV 报告不会包含任何敏感数据。
        """)
        
        st.markdown("### ⚠️ 免责声明与大模型幻觉警告")
        st.markdown("""
        - 尽管 BookLens 强制智能体对文献库中的来源进行标注引用，但 LLM 仍有概率产生文本幻觉或错误归纳。
        - 请务必根据引用标识，人工核对 PDF 文档原文。
        """)

else: # en
    st.markdown("# 🔒 Privacy & AI Security")
    st.markdown("<p style='color: #94A3B8;'>BookLens is committed to transparency regarding data usage, software security, and AI guardrails.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💾 Data & Local Storage")
        st.markdown("""
        - **Zero Cloud Leakage**: All your interaction data, preference settings, and uploaded PDF documents remain strictly local on your laptop/CPU.
        - **Preference Profiling**: Your feedback (Favorites, Likes, Read marks) is stored locally in `data/user_profile/feedbacks.json`. No tracking or data selling is performed.
        - **Vector Store**: Scientific PDFs ingested for local RAG are chunked into text snippets and indexed in the persistent local `ChromaDB` (`data/chroma_db/`).
        """)
        
        st.markdown("### 📑 RAG Deletion Policy")
        st.markdown("""
        - You can permanently delete any uploaded document in the **Research Library** page.
        - Deletion instantly wipes the source file, the local SQLite metadata record, and all associated text chunks in ChromaDB.
        """)
        
    with col2:
        st.markdown("### 🔑 API Key & Secret Safety")
        st.markdown("""
        - API calls are initiated using local environment keys (`.env` or `.streamlit/secrets.toml`).
        - **Logger safety**: The monitoring system filters out any API keys, tokens, or system prompts from all application logs.
        - JSON/CSV export files generated by the Evaluation Lab never include secrets.
        """)
        
        st.markdown("### ⚠️ Disclaimer & Hallucinations")
        st.markdown("""
        - Although BookLens sets strict guardrails forcing the Agent to cite its sources, LLMs may still exhibit hallucinations.
        - Always verify critical citations against the original PDF documents.
        """)

# ─── Status Dashboard ──────────────────────────────────────────
st.markdown("---")
st.markdown(f"### ⚙️ {t('security.status_title', 'Statut des Fournisseurs de Services & APIs')}")
st.write(t("security.status_desc", "Voici l'état d'activation des différents services connectés à l'application. Cette section indique uniquement si la clé est configurée ou non (sans jamais exposer sa valeur)."))

from src.llm_provider import is_provider_active
from src.media import get_media_manager

nvidia_status = "✅ Connecté" if is_provider_active("nvidia") else "❌ Fallback local"
hf_status = "✅ Connecté" if is_provider_active("huggingface") else "❌ Non configuré"

movies_mgr = get_media_manager("movies")
games_mgr = get_media_manager("games")
tmdb_status = "✅ Connecté" if movies_mgr.api_key else "❌ Mode Démo"
rawg_status = "✅ Connecté" if games_mgr.api_key else "❌ Mode Démo"

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown(f"**🤖 NVIDIA Build API (Nemotron)** : `{nvidia_status}`")
    st.markdown(f"**🤗 Hugging Face Inference API** : `{hf_status}`")
with col_s2:
    st.markdown(f"**🎬 TMDB API (Films)** : `{tmdb_status}`")
    st.markdown(f"**🎮 RAWG API (Jeux Vidéo)** : `{rawg_status}`")

