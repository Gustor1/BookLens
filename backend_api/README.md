# MediaLens FastAPI Backend Wrapper

Wrapper minimal sous FastAPI pour exposer les services Data/ML/RAG et l'agent conversationnel existant de MediaLens.

## Architecture & Réutilisation

Le serveur API charge dynamiquement le dossier `app_build` dans son `sys.path` au démarrage. Il importe directement les modules existants sans dupliquer de logique de code :
- `src.media.get_media_manager` pourTMDB (films) et RAWG (jeux vidéo).
- `src.recommender.BookRecommender` chargé depuis son fichier pkl d'entraînement.
- `src.agent.BookLensAgent` pour répondre aux questions de l'assistant.
- `src.rag.rag_service.RAGService` connecté à l'instance locale persistante ChromaDB.

## Démarrage rapide

1. **Préparer l'environnement** :
   Il est recommandé d'utiliser un environnement virtuel python (venv) à la racine du projet pour installer les dépendances de `app_build/requirements.txt` et `backend_api/requirements.txt`.
   ```bash
   python -m venv .venv
   # Activer le venv (Windows) :
   .venv\Scripts\activate
   # Installer les dépendances :
   pip install -r app_build/requirements.txt
   pip install -r backend_api/requirements.txt
   ```

2. **Configurer l'environnement** :
   Créez un fichier `.env` dans `backend_api/` (ou laissez le wrapper charger automatiquement les variables depuis `app_build/.env`) :
   ```env
   PORT=8000
   ALLOWED_ORIGINS=http://localhost:3000
   ```

3. **Lancer le serveur API** :
   ```bash
   cd backend_api
   uvicorn app.main:app --reload --port 8000
   ```
   L'API sera accessible sur [http://localhost:8000](http://localhost:8000).

4. **Documentation de l'API** :
   Une documentation interactive Swagger est automatiquement disponible sur [http://localhost:8000/docs](http://localhost:8000/docs).

## Endpoints principaux

- `GET /api/health` : Statut général et santé des modèles.
- `GET /api/config/public` : Fournisseurs LLM configurés et capacités actives (sans clé API).
- `GET /api/explore?media_type=all&query=&genre=` : Recherche et filtre les livres, films et jeux.
- `GET /api/media/{media_type}/{media_id}` : Fiche détaillée d'une œuvre avec score d'affinité hybride.
- `GET /api/recommendations?media_type=all` : Les quatre rails de recommandations.
- `POST /api/profile/feedback` : Likes et dislikes utilisateur.
- `POST /api/assistant/chat` : Interface de chat connectée à l'agent IA.
