import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.ui import inject_custom_css
from src.i18n import t, language_selector
from src.rag.rag_service import RAGService

# Configurer la page
st.set_page_config(page_title=t("library.page_title", "Bibliothèque de recherche — BookLens"), page_icon="📚", layout="wide")
inject_custom_css()

# Ajouter le sélecteur de langue dans la sidebar
language_selector()

# Initialiser le service RAG
if "rag_service" not in st.session_state:
    st.session_state["rag_service"] = RAGService()
rag_service = st.session_state["rag_service"]

# En-tête de la page
st.markdown(f"# {t('library.hero_title', '📚 Bibliothèque de recherche')}")
st.markdown(f"<p style='color: #94A3B8; margin-bottom: 2rem;'>{t('library.hero_subtitle', 'Gérez vos documents scientifiques PDF et explorez-les sémantiquement.')}</p>", unsafe_allow_html=True)

st.info(t("library.cloud_storage_warning", "💡 En mode cloud (Streamlit Community Cloud), les documents importés sont stockés de façon temporaire. Ils seront effacés lors du prochain redémarrage de l'application. Pour indexer de gros volumes de documents de façon persistante, exécutez le projet en local."))

# ─── SECTION 1 : IMPORTATION ──────────────────────────────────
st.markdown(f"### {t('library.upload_section', '📤 Importer des documents PDF')}")
uploaded_files = st.file_uploader(
    t("library.upload_help", "Glissez-déposez des fichiers PDF ici (max 20 Mo par fichier)"),
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Éviter de réimporter le même fichier s'il est déjà enregistré
        existing_docs = rag_service.list_documents()
        if any(d["filename"] == uploaded_file.name for d in existing_docs):
            continue
            
        with st.spinner(f"Indexation de {uploaded_file.name}..."):
            try:
                pdf_bytes = uploaded_file.read()
                doc_info = rag_service.import_document(pdf_bytes, uploaded_file.name)
                msg_success = t("library.import_success", "Document {name} indexé avec succès ({chunks} chunks).")
                st.success(msg_success.format(name=uploaded_file.name, chunks=doc_info["chunk_count"]))
            except Exception as e:
                msg_error = t("library.import_error", "⚠️ Impossible d'indexer {name} : {error}")
                st.error(msg_error.format(name=uploaded_file.name, error=str(e)))
                
    # Recharger les données pour mettre à jour la liste
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── SECTION 2 : REGISTER & LISTE ─────────────────────────────
st.markdown(f"### {t('library.doc_list', '📋 Documents indexés')}")
docs = rag_service.list_documents()

if not docs:
    st.info(t("library.no_docs", "Aucun document indexé pour le moment. Veuillez importer des PDF ci-dessus."))
else:
    # Créer un tableau dynamique
    cols = st.columns([4, 3, 1, 1, 2])
    
    # En-têtes du tableau
    with cols[0]: st.markdown(f"**{t('library.col_name', 'Nom du document')}**")
    with cols[1]: st.markdown(f"**{t('library.col_date', 'Date d\'import')}**")
    with cols[2]: st.markdown(f"**{t('library.col_pages', 'Pages')}**")
    with cols[3]: st.markdown(f"**{t('library.col_chunks', 'Chunks')}**")
    with cols[4]: st.markdown(f"**{t('library.col_actions', 'Action')}**")
    
    st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
    
    # Lignes du tableau
    for doc in docs:
        c1, c2, c3, c4, c5 = st.columns([4, 3, 1, 1, 2])
        with c1: st.write(doc["filename"])
        with c2: st.write(doc["import_date"])
        with c3: st.write(doc["page_count"])
        with c4: st.write(doc["chunk_count"])
        with c5:
            # Bouton de suppression unique
            if st.button(t("library.delete_btn", "🗑️ Supprimer"), key=f"del_{doc['document_id']}", use_container_width=True):
                with st.spinner("Suppression..."):
                    rag_service.delete_document(doc["document_id"])
                st.success(t("library.deleted", "Document supprimé."))
                st.rerun()
        st.markdown("<hr style='margin: 0.3rem 0; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── SECTION 3 : RECHERCHE SÉMANTIQUE DE PREVIEW ───────────────
st.markdown(f"### {t('library.search_section', '🔍 Recherche Sémantique dans la Bibliothèque')}")

if not docs:
    st.warning(t("library.no_docs_search", "Veuillez d'abord ajouter des documents pour effectuer une recherche."))
else:
    col_input, col_doc, col_limit = st.columns([5, 3, 2])
    
    with col_input:
        query_text = st.text_input(
            t("library.query_label", "Votre recherche"),
            placeholder=t("library.query_placeholder", "Posez une question sur vos documents..."),
            key="library_query_input"
        )
        
    with col_doc:
        doc_options = [t("library.filter_all", "Tous les documents")] + [d["filename"] for d in docs]
        selected_doc = st.selectbox(
            t("library.filter_label", "Filtrer par document"),
            options=doc_options
        )
        
    with col_limit:
        n_results = st.slider(
            t("library.results_count", "Nombre de passages à récupérer"),
            min_value=3,
            max_value=5,
            value=4
        )
        
    if query_text.strip():
        filter_file = None if selected_doc == t("library.filter_all", "Tous les documents") else selected_doc
        
        with st.spinner("Recherche des passages sémantiques..."):
            results = rag_service.query(query_text, n_results=n_results, filter_filename=filter_file)
            
        if not results:
            st.info(t("library.no_results", "Aucun passage pertinent trouvé."))
        else:
            for idx, res in enumerate(results):
                is_suspicious = res["metadata"].get("is_suspicious", False)
                card_style = "border-color: #EF4444;" if is_suspicious else ""
                
                st.markdown(f"""
                <div class="generic-card" style="margin-bottom: 1rem; {card_style}">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="color: #60A5FA; font-weight: 600;">📄 {res['metadata']['filename']} (Page {res['metadata']['page']})</span>
                        <span class="badge {'badge-real' if not is_suspicious else 'badge-estimated'}">Similarity: {res['score']:.1%}</span>
                    </div>
                    <p style="font-style: italic; color: #E2E8F0; line-height: 1.5;">"{res['content']}"</p>
                </div>
                """, unsafe_allow_html=True)
