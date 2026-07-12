"""
BookLens — Agent IA conversationnel
Intègre le SDK OpenAI configuré pour NVIDIA Build (Llama 3.3).
Implémente un fallback dégradé avec détection d'intention et mémoire de conversation.
"""

import os
import re
from dotenv import load_dotenv
from src.llm_provider import is_provider_active, generate_response
from src.i18n import t

# ─── Détection d'intention ──────────────────────────────────────

INTENT_PATTERNS = {
    "stats": [r"combien", r"nombre", r"stat", r"métrique", r"donn[ée]e", r"chiffr",
              r"how many", r"statistic", r"number",
              r"多少", r"数据", r"统计"],
    "top": [r"meilleur", r"top", r"populaire", r"plus not[ée]", r"classement",
            r"best", r"popular", r"highest rated",
            r"最好", r"最高", r"热门", r"排名"],
    "recommend": [r"recommand", r"similaire", r"suggest", r"propos", r"conseil",
                  r"recommend", r"similar", r"suggest",
                  r"推荐", r"建议", r"类似"],
    "explain": [r"expliqu", r"comment", r"pourquoi", r"fonctionne", r"algorithme", r"modèle",
                r"explain", r"how", r"why", r"algorithm", r"model",
                r"解释", r"如何", r"为什么", r"算法", r"模型"],
    "academic": [r"écofémin", r"feminis", r"postcolon", r"recherche", r"guin", r"butler",
                 r"atwood", r"haraway", r"académi", r"essai", r"dystop", r"utopi",
                 r"ecofemin", r"feminist", r"academic",
                 r"生态女性", r"女性主义", r"后殖民", r"学术"],
    "compare": [r"compar", r"différen", r"commun", r"versus", r" vs ",
                r"compare", r"differenc", r"common",
                r"比较", r"区别", r"共同"],
    "summary": [r"résum", r"synthè", r"point commun", r"en commun",
                r"summar", r"synopsis",
                r"总结", r"摘要", r"大意"],
    "image": [r"génère", r"dessin", r"image", r"couverture", r"generate", r"picture", r"draw", r"生成", r"画", r"图像", r"图片"],
    "cross_media": [r"film", r"jeu", r"movie", r"game", r"console", r"crois", r"cross-media", r"cin[ée]ma", r"adaptation",
                    r"电影", r"游戏", r"改编"]
}

def detect_intent(question: str) -> str:
    """
    Détecte l'intention de l'utilisateur.
    Returns: un des labels ('stats', 'top', 'recommend', 'explain', 'academic', 'compare', 'summary', 'general')
    """
    q = question.lower()
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, q))
        if score > 0:
            scores[intent] = score
    
    if not scores:
        return "general"
    return max(scores, key=scores.get)

class BookLensAgent:
    """
    Agent IA pour BookLens.
    Utilise NVIDIA ou Hugging Face via la couche llm_provider.
    Sinon, utilise un fallback hors-ligne avec détection d'intention.
    """

    def __init__(self, recommender=None, metrics=None, merged_df=None):
        self.recommender = recommender
        self.metrics = metrics or {}
        self.merged_df = merged_df
        self._mentioned_books = set()
        
        # Sous-agents spécialisés (uniquement si classe parente directe)
        if type(self) is BookLensAgent:
            self.recommendation_agent = RecommendationAgent(recommender, metrics, merged_df)
            self.academic_agent = AcademicAgent(recommender, metrics, merged_df)

    def _build_system_instruction(self, lang: str):
        """Construit le prompt système avec le contexte des données."""
        
        m = self.metrics
        stats_str = f"""
        Statistiques du dataset BookLens:
        - Livres uniques: {m.get('unique_books', 'N/A')}
        - Utilisateurs: {m.get('unique_users', 'N/A')}
        - Total ratings: {m.get('total_ratings', 'N/A')}
        - Note moyenne: {m.get('avg_rating', 'N/A')}/10
        - Livre le mieux noté: {m.get('top_book', 'N/A')}
        - Auteur le plus noté: {m.get('top_author', 'N/A')}
        """
        
        academic_str = ""
        if self.merged_df is not None and "Theme" in self.merged_df.columns:
            academic_books = self.merged_df.dropna(subset=["Theme"]).drop_duplicates(subset=["ISBN"])
            if not academic_books.empty:
                academic_str = "\n\n📚 **Corpus de Recherche Académique (Sci-Fi Écoféministe, Féministe, Postcoloniale)** :\n"
                for _, row in academic_books.iterrows():
                    academic_str += f"- **{row['Book-Title']}** par {row['Book-Author']} ({row['Year-Of-Publication']}) - Thème: {row['Theme']}. {row['Description']}\n"

        eval_str = ""
        if self.recommender and hasattr(self.recommender, 'get_eval_metrics'):
            eval_m = self.recommender.get_eval_metrics()
            if eval_m:
                eval_str = f"""
        
        Métriques du modèle hybride:
        - Couverture: {eval_m.get('coverage', 'N/A')}
        - Densité matrice: {eval_m.get('matrix_density', 'N/A')}
        - Diversité recommandations: {eval_m.get('avg_recommendation_diversity', 'N/A')}
        - Pondération: {eval_m.get('alpha_collab', 0.7):.0%} collab / {eval_m.get('alpha_content', 0.3):.0%} contenu
        """

        lang_instructions = {
            "fr": "Tu dois impérativement répondre en Français.",
            "en": "You must answer in English.",
            "zh": "你必须用简体中文回答 (You must answer in Simplified Chinese). IMPORTANT: Do not translate book titles or author names, keep them in their original language (usually English) to avoid confusion with the database."
        }
        
        lang_directive = lang_instructions.get(lang, lang_instructions["fr"])

        return f"""
Tu es l'assistant IA intégré à l'application BookLens. Ton but est d'aider les utilisateurs à découvrir des livres, comprendre les recommandations et analyser les données du projet.
Le projet BookLens utilise un modèle de recommandation **hybride** combinant filtrage collaboratif et similarité de contenu (TF-IDF).

Voici le contexte actuel des données chargées dans l'application :
{stats_str}
{eval_str}

Règles de comportement :
1. {lang_directive}
2. Formate toujours tes réponses en Markdown élégant (listes, gras).
3. Si on te demande des recommandations pour un livre précis, explique les deux composantes du score hybride (collab + contenu).
4. Si on te pose des questions sur l'écoféminisme, la science-fiction postcoloniale ou la littérature critique, base tes réponses sur le Corpus de Recherche Académique ci-dessous.
5. Si on te pose des questions sur les films ou jeux vidéo, utilise le contexte cross-media fourni ou propose des œuvres connexes.
6. Si l'utilisateur pose une question hors sujet, rappelle poliment que tu es spécialisé BookLens (livres, films, et jeux vidéo).
7. Tu as accès aux métriques ci-dessus, utilise-les pour répondre sur les statistiques.
8. Si on te demande de résumer ou comparer plusieurs médias, mentionne leurs thèmes communs et différences.
9. Souviens-toi des œuvres mentionnées précédemment dans la conversation.
{academic_str}
"""

    def answer(self, question, chat_history=None, lang="fr", provider="nvidia", rag_context=None):
        """Répond à la question de l'utilisateur (Orchestrateur)."""
        if not question or not str(question).strip():
            return "Veuillez poser une question."

        self._track_mentioned_books(question)
        intent = detect_intent(question)

        # Si nous sommes déjà dans un sous-agent, répondre directement
        if type(self) is not BookLensAgent:
            if is_provider_active(provider):
                return self._answer_with_llm(question, chat_history, lang, provider, rag_context=rag_context)
            else:
                return self._answer_fallback(question, chat_history, lang, provider, rag_context=rag_context)

        # Routage vers l'Agent Académique
        if intent == "academic":
            self.academic_agent._mentioned_books = self._mentioned_books
            response = self.academic_agent.answer(question, chat_history, lang, provider, rag_context=rag_context)
            self._mentioned_books.update(self.academic_agent._mentioned_books)
            prefix = f"🤖 **[{t('agent.role_academic', 'Agent Recherche Académique')}]**\n\n"
            return prefix + response if isinstance(response, str) else response
            
        # Routage vers l'Agent Recommandation
        elif intent in ["recommend", "top", "compare", "summary", "cross_media", "image"]:
            self.recommendation_agent._mentioned_books = self._mentioned_books
            response = self.recommendation_agent.answer(question, chat_history, lang, provider, rag_context=rag_context)
            self._mentioned_books.update(self.recommendation_agent._mentioned_books)
            prefix = f"🤖 **[{t('agent.role_recommend', 'Agent Recommandations')}]**\n\n"
            if isinstance(response, dict) and response.get("type") == "image":
                response["content"] = prefix + response["content"]
                return response
            return prefix + response if isinstance(response, str) else response
            
        # Sinon, l'Orchestrateur Principal répond
        else:
            prefix = f"🤖 **[{t('agent.role_orchestrator', 'Orchestrateur Principal')}]**\n\n"
            if is_provider_active(provider):
                response = self._answer_with_llm(question, chat_history, lang, provider, rag_context=rag_context)
            else:
                response = self._answer_fallback(question, chat_history, lang, provider, rag_context=rag_context)
            return prefix + response if isinstance(response, str) else response

    def _track_mentioned_books(self, text):
        if self.recommender:
            for book in self.recommender.get_book_list():
                if book.lower() in text.lower():
                    self._mentioned_books.add(book)

    def _answer_with_llm(self, question, chat_history, lang, provider, rag_context=None):
        try:
            intent = detect_intent(question)
            
            # INTERCEPTION : Génération d'image
            if intent == "image":
                from src.llm_provider import generate_image
                try:
                    img_bytes = generate_image(question)
                    return {
                        "type": "image",
                        "content": t("agent.image_generated", "🎨 Voici l'image générée :"),
                        "image_bytes": img_bytes
                    }
                except Exception as e:
                    return f"{t('agent.image_error', '⚠️ Erreur lors de la génération de l\'image :')} {e}"
            
            # INTERCEPTION : Recherche académique
            academic_context = ""
            q_lower = question.lower()
            if intent == "academic" and any(word in q_lower for word in ["cherche", "trouve", "article", "paper", "search", "find", "找", "论文"]):
                from src.scholar_api import search_papers
                papers = search_papers(question, limit=3)
                if papers:
                    academic_context = "\n\n[CONTEXTE SEMANTIC SCHOLAR]\nL'utilisateur cherche des articles. Voici ce que l'API Semantic Scholar a retourné. Utilise ces résumés pour répondre :\n"
                    for p in papers:
                        academic_context += f"- **{p['title']}** par {p['authors']} ({p['year']}). Résumé: {p['abstract']}\n"
                else:
                    academic_context = "\n\n[CONTEXTE SEMANTIC SCHOLAR]\nAucun article trouvé sur Semantic Scholar pour cette requête."

            # INTERCEPTION : Cross-media
            cross_media_context = ""
            if intent == "cross_media" or ("recommend" in intent and any(w in q_lower for w in ["film", "movie", "jeu", "game", "console", "电影", "游戏"])):
                mentioned = []
                if self.recommender:
                    for book in self.recommender.get_book_list():
                        if book.lower() in q_lower:
                            mentioned.append(book)
                
                if mentioned:
                    book_title = mentioned[-1]
                    df = self.merged_df
                    if df is not None:
                        book_row = df[df["Book-Title"] == book_title]
                        if not book_row.empty:
                            theme = book_row.iloc[0].get("Theme", "Science-Fiction")
                            from src.media import get_media_manager
                            movies_mgr = get_media_manager("movies")
                            games_mgr = get_media_manager("games")
                            
                            THEME_MAPPING = {
                                "science-fiction": {"movies": "Science-Fiction", "games": "Action"},
                                "fantasy": {"movies": "Fantastique", "games": "Jeu de rôle"},
                                "aventure": {"movies": "Aventure", "games": "Aventure"},
                                "adventure": {"movies": "Aventure", "games": "Aventure"},
                                "drame": {"movies": "Drame", "games": "Jeu de rôle"},
                                "drama": {"movies": "Drame", "games": "Jeu de rôle"},
                                "thriller": {"movies": "Thriller", "games": "Tir"},
                                "dystopie": {"movies": "Science-Fiction", "games": "Action"},
                                "survival": {"movies": "Science-Fiction", "games": "Action"},
                            }
                            
                            theme_lower = theme.lower() if isinstance(theme, str) else "science-fiction"
                            movie_genre = THEME_MAPPING.get(theme_lower, {}).get("movies", "Science-Fiction")
                            game_genre = THEME_MAPPING.get(theme_lower, {}).get("games", "Action")
                            
                            movies = movies_mgr.search("", filters={"genre": movie_genre})
                            games = games_mgr.search("", filters={"genre": game_genre})
                            
                            cross_media_context = f"\n\n[CONTEXTE CROSS-MEDIA]\nL'utilisateur demande des suggestions cross-media basées sur le livre '{book_title}' (Thème: {theme}).\nVoici des correspondances issues des APIs :\n"
                            if movies:
                                m = movies[0]
                                cross_media_context += f"- Film suggéré: **{m['title']}** (Réalisateur: {m['creator']}, Année: {m['year']}, Note: {m['rating']}/10, Source: {m['rating_source']}). Synopsis: {m['description']}\n"
                            if games:
                                g = games[0]
                                cross_media_context += f"- Jeu vidéo suggéré: **{g['title']}** (Développeur: {g['creator']}, Année: {g['year']}, Note: {g['rating']}/10, Source: {g['rating_source']}). Description: {g['description']}\n"

            sys_prompt = self._build_system_instruction(lang) + academic_context + cross_media_context
            if rag_context:
                rag_prompt = {
                    "fr": "\n\n=== CONTEXTE DOCUMENTAIRE RAG ===\nVoici les passages extraits de tes documents importés. Réponds UNIQUEMENT à partir de ce contexte. Si le contexte ne contient pas l'information, réponds honnêtement que tu ne sais pas et n'invente rien.\n\n" + rag_context + "\n=================================",
                    "en": "\n\n=== RAG DOCUMENT CONTEXT ===\nHere are the passages extracted from your imported documents. Answer ONLY using this context. If the context does not contain the information, state honestly that you do not know and do not invent anything.\n\n" + rag_context + "\n=================================",
                    "zh": "\n\n=== RAG 文档上下文 ===\n以下是您导入的文档中提取的段落。仅根据此上下文回答。如果上下文中不包含该信息，请诚实地回答您不知道，切勿胡编乱造。\n\n" + rag_context + "\n================================="
                }
                sys_prompt = sys_prompt + rag_prompt.get(lang, rag_prompt["fr"])
            messages = [{"role": "system", "content": sys_prompt}]
            
            if chat_history:
                recent_history = chat_history[-8:]
                for msg in recent_history:
                    if isinstance(msg, dict) and msg.get("role") in ["user", "assistant"]:
                        messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": question})

            # Appel à la couche Provider LLM
            response_text = generate_response(
                messages=messages,
                provider=provider,
                temperature=0.6,
                top_p=0.95,
                max_tokens=4096
            )
            return response_text
            
        except PermissionError as e:
            return t("agent.auth_error", "⚠️ **Erreur d'authentification** : Clé API invalide ou expirée.") + f"\n\n*Détails : {e}*"
        except ConnectionError as e:
            return t("agent.connection_error", "⚠️ **Erreur de connexion / Quota** : Impossible de joindre l'API ou limite atteinte.") + f"\n\n*Détails : {e}*"
        except Exception as e:
            return f"{t('agent.unexpected_error', '⚠️ **Erreur inattendue** :')} {e}"

    def _answer_fallback(self, question, chat_history=None, lang="fr", provider="nvidia", rag_context=None):
        if rag_context:
            return t("agent_fallback.rag_requires_llm", "Le mode RAG nécessite un modèle de langage (LLM) actif. Veuillez configurer vos clés API pour utiliser ce mode.")
        intent = detect_intent(question)
        
        provider_name = "Hugging Face" if provider == "huggingface" else "NVIDIA"
        header = t("agent_fallback.header", "⚠️ **Mode Hors-ligne**\n\n*Clé API non configurée.*\n\n---\n\n").replace("NVIDIA", provider_name)
        
        if intent == "stats":
            return header + self._fallback_stats()
        elif intent == "top":
            return header + self._fallback_top()
        elif intent == "recommend":
            return header + self._fallback_recommend(question)
        elif intent == "explain":
            return header + self._fallback_explain()
        elif intent == "academic":
            return header + self._fallback_academic(question)
        elif intent == "compare":
            return header + self._fallback_compare()
        elif intent == "summary":
            return header + self._fallback_summary()
        else:
            return header + self._fallback_general()

    def _fallback_stats(self):
        return (t("agent_fallback.stats_title", "📊 **Statistiques du dataset :**\n") +
                t("agent_fallback.stats_books", "- Livres : ") + f"**{self.metrics.get('unique_books', 'N/A')}**\n" +
                t("agent_fallback.stats_users", "- Utilisateurs : ") + f"**{self.metrics.get('unique_users', 'N/A')}**\n" +
                t("agent_fallback.stats_ratings", "- Ratings : ") + f"**{self.metrics.get('total_ratings', 'N/A')}**\n" +
                t("agent_fallback.stats_avg", "- Note moyenne : ") + f"**{self.metrics.get('avg_rating', 'N/A')}/10**\n")

    def _fallback_top(self):
        return (t("agent_fallback.top_title", "🏆 **Top des données :**\n") +
                t("agent_fallback.top_book", "- Meilleur livre : ") + f"**{self.metrics.get('top_book', 'N/A')}**\n" +
                t("agent_fallback.top_author", "- Auteur le plus noté : ") + f"**{self.metrics.get('top_author', 'N/A')}**\n")

    def _fallback_recommend(self, question):
        if self.recommender and self._mentioned_books:
            last_book = list(self._mentioned_books)[-1]
            recs = self.recommender.get_recommendations(last_book, n=3)
            if recs is not None and not recs.empty:
                response = t("agent_fallback.recommend_based", "📚 **Recommandations basées sur") + f" '{last_book}' :**\n\n"
                for _, row in recs.iterrows():
                    response += f"- **{row['Book-Title']}** (score: {row['Similarity-Score']:.2f})\n"
                return response
        
        return t("agent_fallback.recommend_default", "📚 Utilisez l'onglet **⭐ Recommandations**.")

    def _fallback_explain(self):
        return t("agent_fallback.explain", "🔬 **Le Modèle Hybride BookLens**...")

    def _fallback_academic(self, question):
        response = t("agent_fallback.academic_title", "🎓 **Corpus Académique :**\n\n")
        
        q_lower = question.lower()
        if any(word in q_lower for word in ["cherche", "trouve", "article", "paper", "search", "find", "找", "论文"]):
            from src.scholar_api import search_papers
            papers = search_papers(question, limit=3)
            if papers:
                response += "🔬 **Articles trouvés sur Semantic Scholar :**\n\n"
                for p in papers:
                    response += f"- **[{p['title']}]({p['url']})** par {p['authors']} ({p['year']})\n"
                return response + "\n" + t("agent_fallback.academic_link", "\n👉 Consultez l'onglet **🎓 Recherche Académique**.")
        
        if self.merged_df is not None and "Theme" in self.merged_df.columns:
            academic = self.merged_df.dropna(subset=["Theme"]).drop_duplicates(subset=["ISBN"])
            if not academic.empty:
                filtered = academic
                for keyword in ["guin", "butler", "atwood", "haraway", "écofémin", "dystop", "ecofemin", "feminist", "生态女性", "女性主义", "后殖民"]:
                    if keyword in q_lower:
                        mask = (
                            filtered["Book-Author"].str.lower().str.contains(keyword, na=False) |
                            filtered["Theme"].str.lower().str.contains(keyword, na=False) |
                            filtered["Book-Title"].str.lower().str.contains(keyword, na=False)
                        )
                        if mask.any():
                            filtered = filtered[mask]
                            break

                for _, row in filtered.head(5).iterrows():
                    response += f"- **{row['Book-Title']}** par {row['Book-Author']} ({row['Year-Of-Publication']}) — *{row['Theme']}*\n"
                response += t("agent_fallback.academic_link", "\n👉 Consultez l'onglet **🎓 Recherche Académique**.")
                return response
        
        return response + t("agent_fallback.academic_default", "Consultez l'onglet **🎓 Recherche Académique**.")

    def _fallback_compare(self):
        if self._mentioned_books and len(self._mentioned_books) >= 2:
            books = list(self._mentioned_books)[-2:]
            return t("agent_fallback.compare_link", "🔀 Pour comparer") + f" **{books[0]}** et **{books[1]}**, " + t("agent_fallback.compare_default", "utilisez l'onglet **🔀 Comparer**.")
        return t("agent_fallback.compare_default", "🔀 Utilisez l'onglet **🔀 Comparer** pour comparer deux livres côte à côte.")

    def _fallback_summary(self):
        if self._mentioned_books:
            books_str = ", ".join(f"*{b}*" for b in list(self._mentioned_books)[-3:])
            return t("agent_fallback.summary_title", "📝 **Livres mentionnés** : ") + f"{books_str}" + t("agent_fallback.summary_prompt", "\n\nPour un résumé, activez le LLM.")
        return t("agent_fallback.summary_default", "📝 Mentionnez des titres de livres.")

    def _fallback_general(self):
        return t("agent_fallback.general", "💡 Je peux vous aider avec :\n\n...")

# ─── Sous-Agents Spécialisés ──────────────────────────────────

class RecommendationAgent(BookLensAgent):
    def __init__(self, recommender, metrics, merged_df):
        self.recommender = recommender
        self.metrics = metrics or {}
        self.merged_df = merged_df
        self._mentioned_books = set()

    def _build_system_instruction(self, lang: str) -> str:
        base_prompt = super()._build_system_instruction(lang)
        addon = {
            "fr": "\nTu es l'Agent Recommandation spécialisé. Ton but est de suggérer des livres, films et jeux vidéo de manière enthousiaste et conviviale, en expliquant les composantes du score hybride (collab/contenu) et les liens thématiques.",
            "en": "\nYou are the specialized Recommendation Agent. Your goal is to suggest books, movies, and video games in an enthusiastic and friendly manner, explaining the components of the hybrid score (collab/content) and thematic links.",
            "zh": "\n你是专职推荐代理。你的目标是以热情友好的方式推荐图书、电影和视频游戏，解释混合评分（协同/内容）的组成部分和主题关联。"
        }
        return base_prompt + addon.get(lang, addon["fr"])


class AcademicAgent(BookLensAgent):
    def __init__(self, recommender, metrics, merged_df):
        self.recommender = recommender
        self.metrics = metrics or {}
        self.merged_df = merged_df
        self._mentioned_books = set()

    def _build_system_instruction(self, lang: str) -> str:
        base_prompt = super()._build_system_instruction(lang)
        addon = {
            "fr": "\nTu es l'Agent Recherche Académique spécialisé. Ton but est de répondre de manière rigoureuse, scientifique et analytique, en te basant sur le corpus académique de science-fiction critique et les articles issus de Semantic Scholar.",
            "en": "\nYou are the specialized Academic Research Agent. Your goal is to answer in a rigorous, scientific, and analytical manner, relying on the critical science-fiction academic corpus and papers from Semantic Scholar.",
            "zh": "\n你是专职学术研究代理。你的目标是基于批判性科幻学术语料库和来自 Semantic Scholar 的论文，以严谨、科学和分析的方式进行回答。"
        }
        return base_prompt + addon.get(lang, addon["fr"])
