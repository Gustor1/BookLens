# 🎙️ Script de Démonstration Portfoliio — BookLens (2-3 Minutes)

Ce script de pitch et de démonstration est conçu pour présenter efficacement BookLens à un recruteur ou un jury technique.

---

## ⏱️ Structure Temporelle de la Démo

*   **0:00 - 0:30** : Introduction & Pitch Projet
*   **0:30 - 1:15** : Moteur ML Hybride & Personnalisation temps réel
*   **1:15 - 2:00** : Module RAG local & Recherche Académique
*   **2:00 - 2:30** : AI Evaluation Lab & MLOps (Vitrine Technique)

---

## 🎙️ Guide de Défilement & Narration

### 1. Introduction (Page d'accueil)
- **Ce que vous dites** : "Bonjour, je vous présente BookLens, une application web interactive conçue comme une vitrine technologique full-stack. L'objectif est de démontrer comment intégrer au sein d'un même produit du Data Engineering, un moteur de recommandation de Machine Learning hybride, et un module d'IA générative locale avec RAG scientifique."
- **Ce que vous faites** : Affichez la page d'accueil avec les statistiques globales (Livres, Utilisateurs, Notes).

### 2. Le Moteur ML & La Personnalisation (Onglets Recommandations et Films/Jeux)
- **Ce que vous dites** : "Le cœur algorithmique repose sur un modèle hybride : il combine un filtrage collaboratif basé sur la similarité cosinus des notes de lecteurs (70% du poids) et une similarité de contenu TF-IDF sur les métadonnées textuelles (30%). L'utilisateur peut interagir directement pour aimer (👍), rejeter (👎) ou ajouter en favori (❤️). L'application ajuste instantanément le score de recommandation et affiche un badge expliquant pourquoi l'œuvre a été suggérée."
- **Ce que vous faites** :
  1. Allez sur **⭐ Recommandations**.
  2. Choisissez un livre source.
  3. Cliquez sur 👍 ou ❤️ sur l'une des recommandations pour montrer le toast et le reranking immédiat avec le badge explicatif.
  4. Basculez sur **Cross-Media** pour montrer qu'à partir d'un livre, BookLens suggère des films associés (via TMDB API) et des jeux vidéo thématiquement proches (via RAWG API).

### 3. Recherche Académique & RAG Local (Onglet Bibliothèque RAG)
- **Ce que vous dites** : "Pour aller plus loin, BookLens intègre une bibliothèque de recherche scientifique avec un module RAG (Retrieval-Augmented Generation) 100% local qui tourne sur CPU. L'utilisateur dépose son PDF, le système le découpe et génère des embeddings sémantiques multilingues. L'agent IA utilise alors ce contexte pour répondre de manière vérifiable, en citant les pages et documents exacts sous forme de sources accordéons."
- **Ce que vous faites** :
  1. Allez sur **📚 Bibliothèque**.
  2. Montrez un PDF déjà indexé (ou uploadez-en un petit de test).
  3. Allez sur **🤖 Agent IA**, basculez en mode *Recherche dans mes documents*, posez une question liée au document, et ouvrez l'accordéon *Sources utilisées* sous la réponse de l'agent.

### 4. MLOps, Evaluation & Gouvernance (Onglet MLOps & Eval Lab)
- **Ce que vous dites** : "Enfin, pour assurer la fiabilité de la solution en production, j'ai implémenté un module MLOps qui suit les métriques d'entraînement, vérifie la dérive des données (drift) sur la note moyenne et les thèmes, et permet de réentraîner le modèle en un clic. Un 'AI Evaluation Lab' automatise également l'audit de 36 cas de tests (robustesse, injections de prompts, qualité RAG) et renvoie des graphiques de performance et de latence."
- **Ce que vous faites** :
  1. Allez sur **🔄 MLOps et Modèles** pour montrer les runs d'entraînement et le drift.
  2. Allez sur **🧪 AI Evaluation Lab** pour montrer le taux de succès global et la matrice de latence de l'agent IA.
- **Ce que vous dites** : "Merci pour votre écoute. BookLens démontre qu'il est possible de concevoir une application d'IA générative et de ML de niveau production, robuste, multilingue et respectueuse de la confidentialité des données."
