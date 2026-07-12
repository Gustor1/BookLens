def get_embedding_function():
    """
    Retourne la fonction d'embeddings pour ChromaDB.
    Utilise sentence-transformers multilingue par défaut (paraphrase-multilingual-MiniLM-L12-v2),
    et bascule sur ONNXMiniLM_L6_V2 (modèle par défaut de Chroma) si indisponible ou en cas d'erreur.
    """
    try:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        return SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    except Exception as e:
        print(f"[RAG] Fallback sur le modèle d'embeddings ONNXMiniLM par défaut : {e}")
        try:
            from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
            return ONNXMiniLM_L6_V2()
        except Exception as e2:
            raise RuntimeError(f"Échec critique de l'initialisation des embeddings ChromaDB : {e2}")
