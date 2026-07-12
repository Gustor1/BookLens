import os
import chromadb
from src.rag.embeddings import get_embedding_function

class VectorStore:
    def __init__(self, persist_dir=None):
        if persist_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            persist_dir = os.path.join(base_dir, "data", "chroma_db")
            
        os.makedirs(persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_fn = get_embedding_function()
        self.collection = self.client.get_or_create_collection(
            name="academic_rag",
            embedding_function=self.embedding_fn
        )
        
    def add_chunks(self, chunks: list, document_id: str):
        if not chunks:
            return
            
        ids = []
        documents = []
        metadatas = []
        
        for c in chunks:
            meta = c["metadata"].copy()
            meta["document_id"] = document_id
            
            chunk_id = f"{document_id}_{meta['page']}_{meta['chunk_index']}"
            
            ids.append(chunk_id)
            documents.append(c["content"])
            metadatas.append(meta)
            
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
    def delete_document(self, document_id: str):
        self.collection.delete(
            where={"document_id": document_id}
        )
        
    def query(self, query_text: str, n_results: int = 4, filter_filename: str = None) -> list:
        total_items = self.collection.count()
        if total_items == 0:
            return []
            
        where_filter = {}
        if filter_filename:
            where_filter = {"filename": filter_filename}
            
        results = self.collection.query(
            query_texts=[query_text],
            n_results=min(n_results, total_items),
            where=where_filter if where_filter else None
        )
        
        formatted = []
        if not results or not results["documents"] or len(results["documents"][0]) == 0:
            return []
            
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
        
        for i in range(len(docs)):
            score = round(1.0 - distances[i], 3)
            formatted.append({
                "content": docs[i],
                "metadata": metas[i],
                "score": score
            })
            
        return sorted(formatted, key=lambda x: x["score"], reverse=True)
