import os
import json
import datetime
import uuid
import threading
from src.rag.document_processor import process_pdf
from src.rag.vector_store import VectorStore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOADS_DIR = os.path.join(BASE_DIR, "data", "uploads")
METADATA_DIR = os.path.join(BASE_DIR, "data", "rag_metadata")
METADATA_FILE = os.path.join(METADATA_DIR, "documents.json")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

_metadata_lock = threading.Lock()

class RAGService:
    def __init__(self, persist_dir=None):
        self.vector_store = VectorStore(persist_dir)
        
    def _load_metadata(self) -> dict:
        if os.path.exists(METADATA_FILE):
            try:
                with open(METADATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"documents": []}
        
    def _save_metadata(self, data: dict):
        try:
            with open(METADATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[RAGService] Error saving metadata: {e}")
            
    def import_document(self, pdf_bytes: bytes, filename: str) -> dict:
        """
        Valide, découpe, génère les embeddings et indexe un PDF.
        Retourne le dictionnaire des métadonnées du document.
        """
        doc_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOADS_DIR, f"{doc_id}.pdf")
        
        # Enregistrer localement
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
            
        try:
            # 1. Process PDF (Extraction & Chunking)
            chunks = process_pdf(pdf_bytes, filename, len(pdf_bytes))
            
            # 2. Extraire les métadonnées de base
            pages = set(c["metadata"]["page"] for c in chunks)
            page_count = len(pages) if pages else 0
            
            # 3. Indexer dans ChromaDB
            self.vector_store.add_chunks(chunks, doc_id)
            
            # 4. Enregistrer dans le registre JSON de métadonnées
            with _metadata_lock:
                meta = self._load_metadata()
                doc_info = {
                    "document_id": doc_id,
                    "filename": filename,
                    "title": filename.replace(".pdf", ""),
                    "import_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "page_count": page_count,
                    "chunk_count": len(chunks),
                    "status": "Indexed"
                }
                meta["documents"].append(doc_info)
                self._save_metadata(meta)
                
            # Logging structuré technique
            from src.monitoring import track_call
            track_call("rag_import", 0.0, True)
            
            return doc_info
            
        except Exception as e:
            # Nettoyer en cas d'erreur
            if os.path.exists(file_path):
                os.remove(file_path)
            from src.monitoring import track_call
            track_call("rag_import", 0.0, False, str(e))
            raise e
            
    def delete_document(self, doc_id: str):
        """Supprime le document du vector store, du disque, et du registre."""
        with _metadata_lock:
            meta = self._load_metadata()
            docs = meta.get("documents", [])
            
            # Trouver le document
            doc_to_delete = None
            for d in docs:
                if d["document_id"] == doc_id:
                    doc_to_delete = d
                    break
                    
            if doc_to_delete:
                try:
                    # 1. Supprimer de ChromaDB
                    self.vector_store.delete_document(doc_id)
                except Exception as e:
                    print(f"[RAGService] Error deleting from store: {e}")
                    
                # 2. Supprimer le fichier
                file_path = os.path.join(UPLOADS_DIR, f"{doc_id}.pdf")
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"[RAGService] Error deleting file: {e}")
                        
                # 3. Mettre à jour le registre
                docs.remove(doc_to_delete)
                self._save_metadata(meta)
                
                # Logging structuré technique
                from src.monitoring import track_call
                track_call("rag_delete", 0.0, True)
                
    def list_documents(self) -> list:
        """Retourne la liste des documents indexés."""
        with _metadata_lock:
            return self._load_metadata().get("documents", [])
            
    def query(self, query_text: str, n_results: int = 4, filter_filename: str = None) -> list:
        """Exécute une recherche sémantique sémantique et logue l'événement."""
        start_time = datetime.datetime.now()
        try:
            results = self.vector_store.query(query_text, n_results, filter_filename)
            latency = (datetime.datetime.now() - start_time).total_seconds()
            
            # Logging structuré
            from src.monitoring import track_call
            track_call("rag_query", latency, True)
            
            return results
        except Exception as e:
            latency = (datetime.datetime.now() - start_time).total_seconds()
            from src.monitoring import track_call
            track_call("rag_query", latency, False, str(e))
            return []
