import os
import json
from typing import Dict, Any, List, Set

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_DIR = os.path.join(BASE_DIR, "data", "user_profile")
FEEDBACKS_FILE = os.path.join(PROFILE_DIR, "feedbacks.json")

os.makedirs(PROFILE_DIR, exist_ok=True)

class UserProfileManager:
    @staticmethod
    def load_feedbacks() -> Dict[str, Dict[str, str]]:
        """
        Charge les feedbacks utilisateur.
        Structure: { "media_type_title": "like" | "dislike" | "favorite" | "read" }
        """
        if not os.path.exists(FEEDBACKS_FILE):
            return {}
        try:
            with open(FEEDBACKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def save_feedback(media_type: str, title: str, feedback_type: str):
        """Enregistre une interaction utilisateur (ou la met à jour)."""
        feedbacks = UserProfileManager.load_feedbacks()
        key = f"{media_type}::{title}"
        if feedback_type == "none":
            feedbacks.pop(key, None)
        else:
            feedbacks[key] = feedback_type
            
        with open(FEEDBACKS_FILE, "w", encoding="utf-8") as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)

    @staticmethod
    def reset_feedbacks():
        """Réinitialise toutes les préférences."""
        if os.path.exists(FEEDBACKS_FILE):
            try:
                os.remove(FEEDBACKS_FILE)
            except Exception:
                pass

    @staticmethod
    def build_profile(recommender: Any = None) -> Dict[str, Any]:
        """
        Construit un profil de préférences de l'utilisateur :
        - genres préférés
        - auteurs préférés
        - thèmes exclus (dislikes)
        """
        feedbacks = UserProfileManager.load_feedbacks()
        fav_genres: Dict[str, int] = {}
        fav_authors: Dict[str, int] = {}
        disliked_genres: Set[str] = set()
        disliked_authors: Set[str] = set()
        
        for key, fb_type in feedbacks.items():
            parts = key.split("::", 1)
            if len(parts) < 2:
                continue
            media_type, title = parts
            
            # Si on a accès au modèle et aux métadonnées
            info = None
            if recommender and hasattr(recommender, "get_book_info") and media_type == "book":
                info = recommender.get_book_info(title)
                
            if info:
                genre = info.get("theme", "")
                author = info.get("author", "")
                
                if fb_type in ["like", "favorite"]:
                    if genre:
                        fav_genres[genre] = fav_genres.get(genre, 0) + 1
                    if author:
                        fav_authors[author] = fav_authors.get(author, 0) + 1
                elif fb_type == "dislike":
                    if genre:
                        disliked_genres.add(genre)
                    if author:
                        disliked_authors.add(author)
                        
        return {
            "favorite_genres": [k for k, v in sorted(fav_genres.items(), key=lambda x: x[1], reverse=True)],
            "favorite_authors": [k for k, v in sorted(fav_authors.items(), key=lambda x: x[1], reverse=True)],
            "disliked_genres": list(disliked_genres),
            "disliked_authors": list(disliked_authors)
        }

    @staticmethod
    def rerank_recommendations(recs_df: Any, media_type: str, recommender: Any = None) -> Any:
        """
        Ajuste les scores et ajoute une explication de personnalisation pour chaque recommandation.
        """
        if recs_df is None or (hasattr(recs_df, "empty") and recs_df.empty):
            return recs_df
            
        profile = UserProfileManager.build_profile(recommender)
        feedbacks = UserProfileManager.load_feedbacks()
        
        fav_genres = profile["favorite_genres"]
        fav_authors = profile["favorite_authors"]
        disliked_genres = profile["disliked_genres"]
        
        # S'assurer d'avoir la colonne de score existante
        score_col = "Similarity-Score" if "Similarity-Score" in recs_df.columns else "score"
        if score_col not in recs_df.columns:
            return recs_df
            
        # Créer les colonnes explicatives et personnalisées
        recs_df = recs_df.copy()
        recs_df["Personalized-Score"] = recs_df[score_col].astype(float)
        recs_df["Personalization-Reason"] = ""
        
        for idx, row in recs_df.iterrows():
            title = row.get("Book-Title", row.get("title", ""))
            author = row.get("Author", row.get("author", ""))
            theme = row.get("Theme", row.get("theme", ""))
            
            # Vérifier si cet élément est déjà consommé ou dislike par l'utilisateur
            fb_key = f"{media_type}::{title}"
            user_fb = feedbacks.get(fb_key)
            
            boost = 1.0
            reasons = []
            
            # Filtre des exclus
            if user_fb == "dislike":
                boost *= 0.1 # Grosse pénalité
                reasons.append("⚠️ Masqué car vous l'avez marqué 'Je n'aime pas'")
            elif user_fb == "read" or user_fb == "watched" or user_fb == "played":
                boost *= 0.8 # Légère baisse pour laisser la place aux nouveautés
                reasons.append("✓ Déjà consommé")
                
            # Boost genre favori
            if theme and theme in fav_genres:
                boost *= 1.2
                reasons.append(f"❤️ Thème préféré : {theme}")
                
            # Boost auteur favori
            if author and author in fav_authors:
                boost *= 1.2
                reasons.append(f"📝 Auteur préféré : {author}")
                
            # Pénalité genre dislike
            if theme and theme in disliked_genres:
                boost *= 0.5
                reasons.append(f"🚫 Thème écarté : {theme}")
                
            new_score = row[score_col] * boost
            recs_df.loc[idx, "Personalized-Score"] = round(new_score, 4)
            recs_df.loc[idx, "Personalization-Reason"] = " | ".join(reasons) if reasons else "Recommandé par similarité standard"
            
        # Trier par Personalized-Score décroissant
        return recs_df.sort_values(by="Personalized-Score", ascending=False).reset_index(drop=True)
