# État d'avancement - MediaLens V2

Ce document résume les étapes réalisées pour le lancement de la V2 de MediaLens.

---

## 1. Étapes terminées

### Frontend Next.js 16 (`frontend/`)
- [x] Initialisation du projet App Router TypeScript avec Tailwind CSS.
- [x] Injection du Design System dans `globals.css` (Background slate-dark, accent teal/petroleum blue, reduced motion support).
- [x] Implémentation du système i18n natif et léger pour **FR / EN / ZH** (dictionnaires complets).
- [x] Création d'une base de données locale mockée de 12 livres, 8 films et 8 jeux vidéo.
- [x] Création de l'API Client gérant de façon transparente le **Mode Démo** (localStorage pour les favoris, réponses locales de l'assistant) et la connexion réelle FastAPI.
- [x] Création des composants réutilisables : `Button`, `IconButton`, `RatingBadge`, `SourceBadge`, `TagChip`, `Skeleton`, `EmptyState`, `ErrorState`, `UniversalSearchDialog`.
- [x] Écrans terminés :
  - **Accueil** : Hero avec boutons d'actions, featured story, surprise me animée, 4 rails trans-médias.
  - **Explorer** : Recherche debouncée, filtres par genres (tiroir responsive sur mobile), tri par note/année, grille responsive avec Skeletons de chargement.
  - **Fiche média** : Hero avec cover art, tags, note et source, synopsis détaillé, like/dislike, calcul d'explication d'affinité IA, rail d'œuvres similaires.
  - **Assistant IA** : Chat premium avec bulles, indicateur de mode démo, sélecteur de mode (Découverte, Académique, Documents), suggestions de questions.
  - **Bibliothèque** : Gestionnaire de favoris, registre des documents de recherche, module d'import PDF avec message explicite.
  - **Réglages** : Modification de la langue, du thème, réduction des animations, réinitialisation complète.

### Backend FastAPI Wrapper (`backend_api/`)
- [x] Déclaration des dépendances dans `requirements.txt`.
- [x] Configuration des schémas Pydantic stricts dans `app/schemas/media.py`.
- [x] Injection de `app_build` dans le path Python pour réutiliser la logique existante.
- [x] Routeurs FastAPI :
  - `health.py` : Santé de l'API et des modèles.
  - `media.py` : Catalogue d'exploration, fiches détaillées et feedback (comme `BookRecommender.add_feedback`).
  - `recommendations.py` : Génération des 4 rails éditoriaux trans-média.
  - `assistant.py` : Intégration directe de `BookLensAgent` pour le chat (support de la génération d'images Flux en base64).

---

## 2. Éléments restants / Limitations connues

1. **RAG Uploads** : L'importation de documents RAG sur l'écran "Bibliothèque" indique une connexion requise en mode démo. Le service sous-jacent `RAGService` est prêt, l'endpoint d'upload pourra être exposé dans une étape future.
2. **CORS en production** : Configuré pour `http://localhost:3000` par défaut dans `config.py`.

---

## 3. Prochaines étapes suggérées

Pour tester l'application en local :
1. Lancez l'installation des dépendances Python du backend.
2. Lancez le serveur FastAPI (`uvicorn app.main:app`).
3. Lancez le serveur de développement Next.js (`npm run dev`).
