import time
import uuid
import datetime
import os
from typing import List, Dict, Any, Tuple
from src.evaluation.eval_models import EvalCase, EvalResult
from src.evaluation.eval_metrics import compute_case_metrics
from src.agent import BookLensAgent
from src.llm_provider import is_provider_active

# Générateur de PDF minimal de test
def create_test_pdf_bytes(text: str = "This is a RAG test document about ecofeminism, Donna Haraway, and the Cyborg Manifesto.") -> bytes:
    """Génère les octets d'un fichier PDF minimal valide contenant du texte."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type/Catalog/Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type/Pages/Kids[3 0 R]/Count 1>> endobj\n"
        b"3 0 obj <</Type/Page/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/MediaBox[0 0 595 842]/Contents 5 0 R>> endobj\n"
        b"4 0 obj <</Type/Font/Subtype/Type1/BaseFont/Helvetica>> endobj\n"
        b"5 0 obj <</Length 120>> stream\n"
        b"BT\n/F1 12 Tf\n72 712 Td\n(" + text.encode('latin1', 'ignore') + b") Tj\nET\n"
        b"endstream\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f\n"
        b"0000000009 00000 n\n"
        b"0000000056 00000 n\n"
        b"0000000111 00000 n\n"
        b"0000000212 00000 n\n"
        b"0000000282 00000 n\n"
        b"trailer <</Size 6/Root 1 0 R>>\n"
        b"startxref\n433\n"
        b"%%EOF\n"
    )

def get_mock_response(case: EvalCase) -> str:
    """Retourne une réponse fictive réaliste pour le mode Mock."""
    lang = case.expected_language
    
    if case.category == "Robustesse":
        if "clé" in case.input.lower() or "secret" in case.input.lower() or "ignore" in case.input.lower():
            if lang == "fr":
                return "Désolé, je ne peux pas révéler de clés secrètes ni ignorer les consignes système."
            elif lang == "zh":
                return "抱歉，我无法提供安全密钥或忽略系统指令。"
            else:
                return "Sorry, I cannot reveal secret keys or override system instructions."
        if not case.input.strip():
            if lang == "fr":
                return "Veuillez poser une question."
            elif lang == "zh":
                return "请输入您的问题。"
            else:
                return "Please enter a question."
        if lang == "fr":
            return "C'est hors sujet pour ce chat littéraire."
        elif lang == "zh":
            return "这超出了本助手的范围。"
        else:
            return "This is out of scope for this assistant."

    if case.category == "RAG PDF":
        if "manifeste" in case.input.lower() or "definition" in case.input.lower() or "赛博格" in case.input:
            if lang == "fr":
                return "D'après le document de ma bibliothèque (test_academic.pdf, page 1), le Manifeste Cyborg est une théorie féministe de Donna Haraway."
            elif lang == "zh":
                return "根据我文献库中的PDF (test_academic.pdf, 第 1 页)，赛博格宣言是唐娜·哈拉维的一项女权主义理论。"
            else:
                return "According to the library document (test_academic.pdf, page 1), the Cyborg Manifesto is a feminist theory by Donna Haraway."
        else:
            if lang == "fr":
                return "D'après les documents consultés (test_academic.pdf), je ne trouve aucune information sur ce sujet."
            elif lang == "zh":
                return "根据所查询的文献 (test_academic.pdf)，我无法找到关于此主题的信息。"
            else:
                return "Based on the documents searched (test_academic.pdf), I cannot find any information on this topic."

    if case.category == "Recherche académique":
        if lang == "fr":
            return "Voici des articles de Semantic Scholar : Haraway, D. (1985) 'Cyborg Manifesto' étudiant l'écoféminisme et la SF."
        elif lang == "zh":
            return "以下是来自 Semantic Scholar 的学术文献：哈拉维（1985）的《赛博格宣言》，探讨了生态女性主义和科幻文学。"
        else:
            return "Here are research papers from Semantic Scholar: Haraway, D. (1985) 'Cyborg Manifesto' on ecofeminism."

    if case.category == "Recommandations cross-media":
        if lang == "fr":
            return "Pour Dune (livre), je te conseille le film Dune (Denis Villeneuve) et le jeu Dune: Spice Wars. Thèmes communs : écologie et politique."
        elif lang == "zh":
            return "对于《沙丘》，我向您推荐同名电影以及游戏《沙丘：香料战争》。共同主题：生态与政治。"
        else:
            return "For Dune, I suggest Dune (movie) and Dune: Spice Wars (game). Common themes: ecology and politics."

    # Par défaut (Recommandations livres, etc.)
    if lang == "fr":
        return "Je vous recommande vivement d'explorer le roman de science-fiction dystopique 1984 de George Orwell."
    elif lang == "zh":
        return "我向您推荐乔治·奥威尔的经典反乌托邦科幻小说《1984》。"
    else:
        return "I highly recommend reading 1984 by George Orwell, a classic dystopian sci-fi novel."


class EvalRunner:
    def __init__(self, agent: BookLensAgent = None):
        self.agent = agent
        
    def run_case(self, case: EvalCase, provider: str, mode: str, rag_service: Any = None) -> EvalResult:
        """Exécute un cas de test unique."""
        run_id = str(uuid.uuid4())[:8]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        start_time = time.time()
        
        # 1. Mode Mock (Simulé)
        if mode == "mock":
            time.sleep(0.05)  # Légère attente pour simuler la latence
            response_text = get_mock_response(case)
            latency_ms = (time.time() - start_time) * 1000
            
            # Évaluer
            expected_agent = case.expected_agent or "BookLensAgent"
            score, metrics, reasons = compute_case_metrics(
                case=case,
                response=response_text,
                routing_detected=expected_agent,
                provider_success=True,
                is_fallback=False
            )
            
            return EvalResult(
                case_id=case.id,
                provider=provider,
                response=response_text,
                routing_detected=expected_agent,
                latency_ms=latency_ms,
                success=score >= 70,
                score=score,
                metrics=metrics,
                reasons=reasons,
                run_id=run_id,
                timestamp=timestamp
            )
            
        # 2. Exécution réelle
        if not self.agent:
            raise ValueError("L'agent principal doit être fourni pour l'exécution réelle.")
            
        # Gérer le RAG temporaire si nécessaire
        rag_context = None
        temp_doc_id = None
        
        if case.requires_rag and rag_service:
            try:
                # Créer et indexer un PDF de test
                pdf_bytes = create_test_pdf_bytes()
                doc_info = rag_service.import_document(pdf_bytes, "test_academic.pdf")
                temp_doc_id = doc_info["document_id"]
                
                # Récupérer les chunks
                results = rag_service.query(case.input, n_results=4)
                if results:
                    rag_context = "\n\n".join(f"[Source: {r['metadata']['filename']}, Page: {r['metadata']['page']}]\n{r['content']}" for r in results)
            except Exception as e:
                print(f"[EvalRunner] Erreur d'initialisation du RAG de test : {e}")
                
        # Interroger l'agent
        is_active = is_provider_active(provider)
        try:
            # Capturer le routage d'agent en cours d'exécution
            # Comme BookLensAgent préfixe la réponse, on pourra l'extraire
            response = self.agent.answer(
                question=case.input,
                chat_history=[],
                lang=case.language,
                provider=provider,
                rag_context=rag_context
            )
            
            # Extraire l'agent sélectionné du préfixe
            # Format: "🤖 **[Agent Recommandations]**\n\n..."
            routing_detected = "BookLensAgent"
            if "Agent Recherche Académique" in response:
                routing_detected = "AcademicAgent"
            elif "Agent Recommandations" in response:
                routing_detected = "RecommendationAgent"
                
            response_clean = response
            # Retirer le préfixe pour le score
            if response.startswith("🤖 **["):
                parts = response.split("]**\n\n", 1)
                if len(parts) > 1:
                    response_clean = parts[1]
                    
        except Exception as e:
            response_clean = f"Erreur critique lors de l'exécution de l'agent : {str(e)}"
            routing_detected = "BookLensAgent"
            
        latency_ms = (time.time() - start_time) * 1000
        
        # Nettoyer le document de test
        if temp_doc_id and rag_service:
            try:
                rag_service.delete_document(temp_doc_id)
            except Exception as e:
                print(f"[EvalRunner] Impossible de supprimer le document temporaire de RAG : {e}")
                
        # Calcul des scores
        score, metrics, reasons = compute_case_metrics(
            case=case,
            response=response_clean,
            routing_detected=routing_detected,
            provider_success=is_active and not response_clean.startswith("Erreur critique"),
            is_fallback=not is_active
        )
        
        return EvalResult(
            case_id=case.id,
            provider=provider,
            response=response_clean,
            routing_detected=routing_detected,
            latency_ms=latency_ms,
            success=score >= 70,
            score=score,
            metrics=metrics,
            reasons=reasons,
            run_id=run_id,
            timestamp=timestamp
        )

    def run_suite(self, cases: List[EvalCase], provider: str, mode: str, limit: int = 10, rag_service: Any = None) -> List[EvalResult]:
        """Exécute une suite de cas de test avec limite de sécurité."""
        results = []
        execution_cases = cases[:limit]
        
        # Enregistrer dans le log central de monitoring
        from src.monitoring import track_call
        track_call(f"eval_run_start_{provider}_{mode}", 0.0, True)
        
        for case in execution_cases:
            res = self.run_case(case, provider, mode, rag_service)
            results.append(res)
            
        track_call(f"eval_run_end_{provider}_{mode}", 0.0, True)
        return results
