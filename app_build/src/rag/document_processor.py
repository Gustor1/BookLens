import io
import re

def clean_and_check_injection(text: str) -> tuple[bool, str]:
    """
    Détecte et neutralise les tentatives simples d'injection de prompt.
    Retourne (est_suspect, texte_nettoyé).
    """
    suspicious_patterns = [
        r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions",
        r"ignore\s+les\s+instructions",
        r"ignorer\s+les\s+consignes",
        r"reveal\s+(?:your\s+)?system\s+prompt",
        r"révéler\s+la\s+clé",
        r"api\s+key",
        r"system\s+prompt",
        r"you\s+must\s+now\s+act\s+as",
        r"tu\s+dois\s+maintenant\s+agir\s+en\s+tant\s+que",
        r"override\s+instructions",
        r"consigne\s+système"
    ]
    
    is_suspicious = False
    text_lower = text.lower()
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text_lower):
            is_suspicious = True
            break
            
    if is_suspicious:
        # Neutralisation par préfixe d'avertissement et échappement
        cleaned = f"[CONTENU SUSPECT SIGNALÉ PAR LE FILTRE DE SÉCURITÉ : INJECTION LOGIQUE POTENTIELLE]\n{text}"
        return True, cleaned
        
    return False, text


def process_pdf(pdf_bytes: bytes, filename: str, file_size: int) -> list:
    """
    Valide le document, extrait le texte par page et le découpe en chunks.
    Retourne une liste de dictionnaires contenant content, metadata.
    """
    # 1. Validation de la taille et de l'extension
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Le fichier doit être au format PDF.")
        
    if file_size > 20 * 1024 * 1024:
        raise ValueError("La taille du fichier ne doit pas dépasser 20 Mo.")
        
    if len(pdf_bytes) == 0:
        raise ValueError("Le fichier PDF est vide.")

    # 2. Extraction du texte page par page
    pages = []
    
    # Tentative avec PyMuPDF
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for i, page in enumerate(doc):
            text = page.get_text() or ""
            pages.append((i + 1, text))
    except (ImportError, Exception):
        # Fallback sur pypdf
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append((i + 1, text))
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la lecture du PDF : {str(e)}")

    # 3. Vérification de la présence de texte
    total_len = sum(len(text.strip()) for _, text in pages)
    if total_len == 0:
        raise ValueError("Le document PDF ne contient aucun texte extractible (numérisé sans OCR).")

    # 4. Chunking par page
    chunks = []
    chunk_size = 800
    overlap = 150
    
    for page_num, text in pages:
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        if not cleaned_text:
            continue
            
        start = 0
        chunk_idx = 0
        while start < len(cleaned_text):
            end = start + chunk_size
            chunk_content = cleaned_text[start:end]
            
            # Vérification de sécurité (injection de prompt)
            is_suspicious, final_content = clean_and_check_injection(chunk_content)
            
            chunks.append({
                "content": final_content,
                "metadata": {
                    "page": page_num,
                    "chunk_index": chunk_idx,
                    "filename": filename,
                    "is_suspicious": is_suspicious
                }
            })
            
            start += chunk_size - overlap
            chunk_idx += 1
            
    return chunks
