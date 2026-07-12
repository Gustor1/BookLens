from abc import ABC, abstractmethod

class BaseMediaManager(ABC):
    """
    Interface commune pour la gestion des différents types de médias (Livres, Films, Jeux Vidéo).
    """

    @abstractmethod
    def search(self, query: str, filters: dict = None) -> list:
        """
        Recherche des médias par mot-clé et applique des filtres.
        
        Args:
            query: Terme de recherche (titre, créateur, etc.).
            filters: Dictionnaire de filtres (ex: {"genre": "Action"}).
            
        Returns:
            list: Liste de dictionnaires de médias formatés.
        """
        pass

    @abstractmethod
    def get_recommendations(self, media_id: str, n: int = 5, filters: dict = None) -> list:
        """
        Génère des recommandations hybrides ou basées sur le contenu pour un média source.
        
        Args:
            media_id: Identifiant unique du média (ISBN, TMDB ID, RAWG ID).
            n: Nombre de recommandations souhaitées.
            filters: Dictionnaire de filtres (ex: {"genre": "Action"}).
            
        Returns:
            list: Liste de dictionnaires de médias recommandés avec score de similarité.
        """
        pass

    @abstractmethod
    def get_details(self, media_id: str) -> dict:
        """
        Récupère les détails complets d'un média spécifique.
        
        Args:
            media_id: Identifiant unique du média.
            
        Returns:
            dict: Dictionnaire contenant toutes les métadonnées détaillées.
        """
        pass

    @abstractmethod
    def get_available_genres(self) -> list:
        """
        Récupère la liste des genres/thèmes disponibles pour le filtrage.
        
        Returns:
            list: Liste de chaînes de caractères.
        """
        pass
