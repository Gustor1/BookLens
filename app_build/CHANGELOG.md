# Changelog

Toutes les modifications notables du projet BookLens seront documentées dans ce fichier.

## [9.0.0] - Refonte UI/UX Complète (MediaLens)

### Ajouts
- **Audit & Orientations Artistiques** : Documentation initiale de refonte (`docs/ui_ux_audit.md` et `docs/design_direction.md`).
- **Page Design System** (`pages/19_🎨_Design_System.py`) : Playground d'administration permettant de valider les cartes, badges, et boutons sous le nouveau style.
- **Page Explorer** (`pages/20_🧭_Explorer.py`) : Recherche unifiée et filtres de catalogue croisé pour tous les médias.
- **Hub MediaLens Lab** (`pages/21_🧪_MediaLens_Lab.py`) : Centralisation technique pour tous les modules de diagnostic et d'expérimentation.
- **Bouton Surprise Me** : Choix et rendu aléatoire d'un élément culturel disponible.

### Modifications
- **Routage Centralisé (st.navigation)** : Conversion de `app.py` en routeur. Remplacement de la sidebar longue Streamlit par une structure de navigation regroupée.
- **Surcharge CSS (src/ui.py)** : Refonte des tokens, styles de cartes, transitions, et gestion d'accessibilité reduced-motion.
- **Interface de Chat (pages/6_🤖_Agent_IA.py)** : Suppression des avatars natifs, mise en page sous forme de bulles personnalisées élégantes, et masquage des sources RAG dans des accordéons rétractables sous les réponses.

## [8.1.0] - MLOps, Personnalisation & Cloud Readiness

### Ajouts
- **Dossier de tests de préparation cloud** (`tests/test_cloud_readiness.py`) : 4 tests unitaires couvrant l'absence de secrets, le mode fallback de l'agent, le fallback offline des gestionnaires de médias et la création automatique de répertoires temporaires.
- **Diagnostics de Gouvernance de Données** (`src/data_quality.py`) : Diagnostics de complétude (valeurs manquantes), conformité des plages et anomalies (doublons) pour l'ensemble des sources.
- **Reranking & Feedback** (`src/user_profile.py`) : Enregistrement local des préférences utilisateurs (favoris, likes, dislikes) et ajustement sémantique dynamique en temps réel.
- **Workflow CI/CD GitHub Actions** (`.github/workflows/tests.yml`) : Exécution de tests automatique sous Python 3.12 à chaque commit/PR.
- **Configuration de Tests pytest** (`pyproject.toml`) : Initialisation automatique des arguments de test pour la compatibilité Windows/Cloud.
- **Icônes uniques dans la sidebar** : Suppression de tous les doublons d'émojis dans les pages Streamlit.

## [8.0.0] - AI Evaluation Lab (Phase 8)

### Ajouts
- **Dataset de test versionné** (`data/evaluation/eval_cases.json`) : 36 cas de test répartis équitablement entre FR, EN et ZH (12 chacun) couvrant la recommandation, la recherche, le RAG, le routage et la robustesse logicielle.
- **Moteur d'évaluation** (`src/evaluation/eval_runner.py`) : Modes Mock, Single Provider, et Comparison (NVIDIA vs Hugging Face) avec limite de sécurité d'appels API (10 max) et génération/indexation automatique de PDF de test.
- **Métriques et scoring** (`src/evaluation/eval_metrics.py`) : Métriques déterministes de langue, routage, présence/validité des citations RAG et conformité de sécurité. Calcul d'un score de 0 à 100 avec déductions objectives.
- **Rapports et exports** (`src/evaluation/eval_report.py`) : Exportation des runs en JSON, CSV et rapports Markdown adaptés pour présentation portfolio.
- **Dashboard Lab** (`pages/16_🧪_AI_Evaluation_Lab.py`) : Interface Streamlit avec graphiques Plotly de distribution et score par catégorie/langue, et explorateur interactif.
- **Tests unitaires d'évaluation** : 7 tests unitaires pytest (`tests/test_evaluation.py`) validant le calcul des scores, le schéma JSON, la détection des fausses citations et injections.

## [7.0.0] - RAG Académique Local (Phase 7)

### Ajouts
- **Module RAG 100% Local** (`src/rag/`) : Ingestion, chunking sémantique de 800 caractères avec 150 overlap, et recherche sémantique basée sur ChromaDB et sentence-transformers multilingues CPU.
- **Bibliothèque de Recherche** (`pages/10_📚_Bibliothèque_de_recherche.py`) : Interface de dépôt PDF, de visualisation du registre et de recherche de passages.
- **Sécurité et Filtrage Actif** : Détection et neutralisation par expressions régulières des tentatives simples d'injection de prompt dans les PDF.
- **Intégration Agent IA RAG** : Mode RAG ("Recherche dans mes documents") ajoutant un prompt système contraignant et affichant les extraits de sources sous chaque réponse.
- **Renommage dynamique de page** : Le nom du fichier de la page 10 change à la volée selon la langue active (FR, EN, ZH) pour s'adapter à la sidebar Streamlit.
- **Tests unitaires RAG** : 5 nouveaux tests unitaires pytest (`tests/test_rag.py`) couvrant toutes les fonctionnalités RAG.

## [6.0.0] - Vitrine Technique et Monitoring (Phase 6)

### Ajouts
- **Module de Monitoring** (`src/monitoring.py`) : Enregistrement de la latence, du taux de réussite et du nombre d'appels à toutes les APIs (NVIDIA, Hugging Face, Open Library, Google Books, Semantic Scholar, TMDB, RAWG).
- **Dashboard Technique & Admin** (`pages/12_📊_Dashboard_Technique.py`) : Tableaux de bord Plotly affichant les statistiques de performance des APIs et console de visualisation des logs JSON structurés en temps réel.
- **Visualisation d'Architecture** (`pages/11_🧱_Architecture.py`) : Grille interactive documentant le rôle, le statut (Connecté / Fallback) et les capacités de chaque brique technologique.
- **Routage Multi-Agents** : Subdivision de l'agent en `RecommendationAgent` et `AcademicAgent` héritant d'un orchestrateur transparent (`BookLensAgent`) pour séparer les contextes système et spécialités.
- **Logs structurés JSON** : Fichier local `logs/app.log` géré par un `RotatingFileHandler`.

## [5.0.0] - Extension Multimédia (Phase 5)

### Ajouts
- **Architecture Modulaire Multimédia** (`src/media/`) : Découpage unifié (Livres, Films, Jeux Vidéo) héritant d'une classe abstraite `BaseMediaManager`.
- **Intégration de l'API TMDB** : Section Films connectée aux données TMDB en temps réel avec cache local et système de recommandation hybride.
- **Intégration de l'API RAWG** : Section Jeux Vidéo connectée aux données RAWG en temps réel avec cache local et système de recommandation hybride.
- **Recommandations Croisées (Cross-Media)** : Page dédiée reliant les livres, les films et les jeux vidéo par thématiques communes.
- **Support des API dans l'Agent IA** : L'agent intercepte les requêtes cross-media et enrichit son contexte via les managers multimédia.
- **Internationalisation (i18n)** : Traduction complète des nouvelles interfaces en français, anglais et chinois.

## [4.0.0] - Multimodalité et Capacités Étendues (Phase 4)

### Ajouts
- **Génération d'images (FLUX.1-dev)** : Intégration de l'API Hugging Face Inference pour générer des images directement depuis le chat (via l'intention `image`).
- **Synthèse Vocale (MMS-TTS)** : Ajout d'un bouton "🔊 Écouter" sous les réponses texte de l'agent. Utilise des modèles spécifiques à la langue (fr/en/zh).
- **Indicateurs de capacités** : L'interface du chat affiche désormais dynamiquement quelles fonctionnalités sont supportées par le fournisseur actif (Texte, Image, Voix).

## [3.1.0] - Architecture Multi-Fournisseurs (Phase 3)

### Ajouts
- **Couche Provider LLM** : Abstraction de la logique de génération IA (`src/llm_provider.py`) pour prendre en charge plusieurs fournisseurs.
- **Support Hugging Face** : Intégration de l'Inference API de Hugging Face via l'endpoint compatible OpenAI.
- **Sélecteur de Modèles** : Ajout d'une interface graphique dans l'Agent IA pour basculer facilement entre NVIDIA (Llama 3.3 Nemotron) et Hugging Face (Llama 3.2 3B).

## [3.0.0] - État Stable (Phase 0)

### Ajouts (Fonctionnalités actuelles)
- **Data Engineering** : Pipeline complet d'extraction, nettoyage (gestion doublons/valeurs manquantes) et intégration de données (Books, Users, Ratings).
- **Génération Synthétique** : Intégration du skill NVIDIA Data Designer pour générer des profils utilisateurs et ratings cohérents via IA.
- **Machine Learning** : Système de recommandation hybride (Filtrage Collaboratif Cosinus + Filtrage par Contenu TF-IDF) pondéré dynamiquement avec système de feedback (Thumbs up/down).
- **Agent IA Conversationnel** : Assistant natif connecté au LLM NVIDIA Llama 3.3 (Nemotron 49B) avec contexte de la base de données.
- **Système de Fallback IA** : Mode dégradé hors-ligne avec détection d'intention (expressions régulières) si l'API IA est indisponible.
- **Recherche Académique** : Section dédiée à un corpus ciblé (SF Écoféministe, Postcoloniale, etc.) intégré nativement aux recommandations.
- **Dashboard Analytique** : Graphiques Plotly pour la distribution des notes et statistiques des données.
- **Comparateur** : Outil d'analyse côte à côte de deux livres (métadonnées, scores).

### Modifications
- Remplacement du SDK Google GenAI (Gemini) par OpenAI (NVIDIA Build) pour l'Agent IA.
- Migration vers une exécution 100% CPU (retrait du support expérimental NVIDIA cuDF pour assurer la compatibilité matérielle large).
