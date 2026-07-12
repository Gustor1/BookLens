# Rapport de compilation et design - MediaLens V2

Ce rapport présente les composants créés, l'architecture d'API, les décisions de conception visuelle, et les résultats de validation pour le lancement de la V2.

---

## 1. Liste des fichiers créés

### Frontend Next.js V2
- `frontend/package.json` : Dépendances compilées (Next.js 16, React 19, Tailwind v4, Lucide React, Framer Motion).
- `frontend/src/app/globals.css` : Design system CSS, variables sémantiques, prefers-reduced-motion.
- `frontend/src/app/layout.tsx` : Layout racine chargeant Outfit et Playfair Display de Google Fonts.
- `frontend/src/app/page.tsx` : Redirection automatique vers `/fr`.
- `frontend/src/app/[locale]/layout.tsx` : Layout locale injectant I18nProvider, SettingsProvider, Header, BottomNavigation et Footer.
- `frontend/src/components/layout/` :
  - `I18nProvider.tsx` : Contexte client de traduction et routage d'URL locale.
  - `SettingsProvider.tsx` : Contexte d'accessibilité (thèmes, reduced motion, reset).
  - `LanguageSelector.tsx` : Dropdown de changement de langue.
  - `Header.tsx` : Navigation bureau avec recherche intégrée et cog de réglages.
  - `BottomNavigation.tsx` : Barre d'action mobile à 5 boutons.
- `frontend/src/components/ui/` :
  - `index.tsx` : Bibliothèque de boutons, badges de notation/source, tag chips, skeletons, toasts et empty states.
  - `PageTransition.tsx` : Animations fluides de page avec Framer Motion.
- `frontend/src/components/media/` :
  - `MediaCard.tsx` : Carte média avec badges de type/note et zoom progressif au hover.
  - `FeaturedMediaCard.tsx` : Carte grand format avec synopsis et "Pourquoi ce choix ?".
  - `MediaRail.tsx` : Ligne horizontale défilante avec flèches de contrôle.
- `frontend/src/components/search/` :
  - `UniversalSearchDialog.tsx` : Modal de recherche globale en surbrillance avec saisie debouncée.
- `frontend/src/lib/i18n/` :
  - `config.ts` : Dictionnaires et utilitaires légers de traduction.
  - `fr.json`, `en.json`, `zh.json` : Clés de traduction.
- `frontend/src/lib/mock/` :
  - `media.ts` : Base locale mockée (12 livres, 8 films, 8 jeux).
  - `recommendations.ts` : Moteur d'affinité et générateurs de rails locaux.
  - `profile.ts` : Système de favoris persistant dans le localStorage.
- `frontend/src/lib/api/client.ts` : Client réseau basculant en Mode Démo si FastAPI est éteint.
- `frontend/public/images/` :
  - `placeholder-book.svg`, `placeholder-movie.svg`, `placeholder-game.svg` : SVGs locaux vectoriels légers.

### Backend FastAPI Wrapper
- `backend_api/requirements.txt` : fastapi, uvicorn, pydantic, pydantic-settings, pytest, httpx.
- `backend_api/.env.example` : Configuration hôte, CORS et API keys.
- `backend_api/app/config.py` : Chargeur de configuration (priorité aux envs locales puis fallback Streamlit `.env`).
- `backend_api/app/dependencies.py` : Container d'instances globales (ChromaDB `RAGService`, `BookRecommender` pkl, agent).
- `backend_api/app/schemas/media.py` : Types Pydantic stricts.
- `backend_api/app/routers/` :
  - `health.py` : Diagnostic des services et providers.
  - `media.py` : Recherche d'exploration, fiches détaillées, soumission de likes/dislikes.
  - `recommendations.py` : Les quatre rails de recommandations.
  - `assistant.py` : Pipeline d'interaction avec `BookLensAgent` (support d'images base64).
- `backend_api/app/main.py` : Application FastAPI principale avec CORS configuré.
- `backend_api/tests/test_api.py` : Tests unitaires pytest.

---

## 2. Décisions artistiques et design system

- **Direction éditoriale** : Utilisation d'une police Serif élégante (`Playfair Display`) uniquement pour les grands titres, contrastant avec une police Sans-Serif épurée (`Outfit`) pour le corps du texte (taille confortable à partir de 16px).
- **Nuances de couleurs** : Fond noir bleuté profond (`#050811`), surfaces ardoise sombre (`#0b0f19` et `#131a26`) avec bordures très fines (`rgba(148, 163, 184, 0.08)`).
- **Accents limités** : Accent principal pétrole/teal (`#14b8a6`) pour attirer l'œil sur les actions clés. Accent ambre (`#f59e0b`) réservé aux badges de notation.
- **Accessibilité** : Contrôle du focus visible, zones cliquables minimales de 44px, attributs ARIA pour les icônes. Désactivation totale des animations au niveau racine si `prefers-reduced-motion` est détecté (ou activé dans les réglages).
