# UI/UX Audit — MediaLens

Ce document présente l'audit complet de l'interface actuelle de l'application MediaLens/BookLens et identifie les axes d'amélioration critiques pour transformer l'application en une plateforme culturelle IA premium ("bibliothèque de nuit + cinéma éditorial + intelligence artificielle").

---

## 1. Structure Globale & Navigation

### Navigation Actuelle
- **Type** : Sidebar native Streamlit.
- **Pages** : 18 pages listées à la suite dans le répertoire `pages/`, avec des numéros et des emojis variés comme icônes.
- **Problèmes UX identifiés** :
  - La sidebar est trop chargée et longue, créant une surcharge cognitive.
  - Absence de hiérarchie visuelle claire entre les pages grand public (Recherche, Recommandations, Profil) et les pages techniques/lab (Architecture, Dashboard Technique, MLOps, AI Evaluation Lab, Graphe).
  - Les noms et numéros des fichiers de la sidebar sont visibles tels quels.
  - La transition linguistique renomme dynamiquement certains fichiers physiques, ce qui est fragile et peut perturber l'ordre d'affichage.

### Proposition de Navigation Moderne (Phase 2)
- Regrouper les pages en sections logiques :
  - **Principal** : Accueil, Explorer, Recherche, Ma bibliothèque, Assistant IA
  - **Découvrir** : Livres, Films, Jeux, Recherche académique, Bibliothèque de recherche
  - **Lab (Technique)** : Insights, Architecture, Dashboard technique, AI Evaluation Lab, MLOps, Catalogue de données, Design System
  - **Secondaire** : Paramètres / Profil, À propos
- Limiter les emojis de navigation dans la barre de menu pour adopter une iconographie épurée et homogène.

---

## 2. Palette & Cohérence Visuelle

### Constat Actuel
- **Thème** : Sombre de base, mais avec des composants natifs Streamlit (fond gris bleuté standard, boutons rouges/blancs, contrastes moyens).
- **Incohérences** :
  - Dégradés de couleur allant du bleu au violet sans charte stricte.
  - Utilisation sporadique de couleurs vives (vert vif pour le succès, orange/jaune pour les badges de modèle estimé).
  - Le style général manque de cohérence : certaines pages ont un design "glassmorphic" prononcé tandis que d'autres utilisent le rendu standard de Streamlit.

### Direction Artistique Cible (Phase 1)
- **Palette Sombre Éditoriale** :
  - Fond : Noir chaud / Bleu nuit profond (`#0B0F19`)
  - Surfaces : Noir ardoise (`#1E293B` en opacité réduite ou `#131B2E`)
  - Accent primaire : Teal pétrole élégant (`#14B8A6` ou `#0D9488`)
  - Accent secondaire rare : Ambre chaud / Corail doux (`#F59E0B` ou `#F43F5E`)
  - Texte principal : Blanc crème (`#F8FAFC`)
  - Texte secondaire : Gris bleuté (`#94A3B8`)
- **Rayons et Angles** : Harmoniser l'ensemble avec des arrondis subtils de `12px` (cartes) et `8px` (boutons, inputs).

---

## 3. Analyse Composant par Composant

### A. Page d'Accueil (`app.py`)
- **Problèmes** :
  - Présentation trop textuelle et académique.
  - Les 4 cartes de statistiques (KPI) et les 4 cartes de fonctionnalités se ressemblent et manquent de hiérarchie éditoriale.
  - Pas d'entrée de recherche universelle ou d'exploration immersive immédiate.
- **Action (Critique)** : Refondre le Hero avec une recherche universelle centrale, et ajouter une recommandation éditoriale en vedette ("À découvrir ce soir") et des collections variées au lieu de grilles standardisées.

### B. Cartes Média (`render_media_card` dans `src/ui.py`)
- **Problèmes** :
  - Le rendu actuel prend beaucoup de place verticale et flotte les images à gauche avec des hauteurs variables.
  - Les boutons d'avis (👍, 👎) et de favoris ne sont pas unifiés visuellement.
  - Les images manquantes créent des trous vides peu esthétiques.
- **Action (Importante)** : Uniformiser les cartes sous forme de grilles responsives, avec hover lisse, badges de notation cohérents, et placeholders d'image modernes.

### C. Fiches Média (Livre / Film / Jeu)
- **Problèmes** :
  - Actuellement, chaque média a un affichage un peu différent selon la page (Livres, Films, Jeux).
  - Pas de vue d'ensemble unifiée.
- **Action (Importante)** : Créer une fiche média universelle réutilisable contenant le grand visuel, le titre, le créateur, les badges de métadonnées, le résumé, et une section "Pourquoi recommandé" si applicable.

### D. Chat de l'Agent IA (`pages/6_🤖_Agent_IA.py`)
- **Problèmes** :
  - L'affichage utilise les bulles natives Streamlit qui manquent de personnalité.
  - La zone de saisie n'est pas toujours idéalement positionnée sur mobile.
  - Pas d'exemples de questions pour guider le premier contact.
- **Action (Importante)** : Style personnalisé de chat, suggestions de questions initiales en chips, et panneau latéral rétractable pour afficher les sources RAG de façon claire et sans polluer le chat.

### E. Graphiques Plotly
- **Problèmes** :
  - Certains graphiques utilisent des couleurs par défaut ou des thèmes clairs/sombres incohérents.
- **Action (Polish)** : Créer un layout de thème sombre standardisé pour toutes les figures Plotly (fond transparent, couleurs coordonnées à la palette, grilles subtiles).

---

## 4. Tableau des Priorités de Refonte

| Priorité | Élément | Action Requise | Fichiers Affectés |
| :--- | :--- | :--- | :--- |
| **Critique** | **Design System & Tokens** | Centraliser les tokens dans `src/ui.py` et créer une page de démo du Design System. | `src/ui.py`, `pages/19_Design_System.py` |
| **Critique** | **Page d'Accueil (Hero & Vedette)** | Refondre l'accueil avec un Hero éditorial de nuit et une recommandation Vedette dynamique. | `app.py` |
| **Importante** | **Navigation & Layout Global** | Remplacer la sidebar longue par une hiérarchie épurée et injecter des styles de mise en page moderne. | `app.py`, pages/* |
| **Importante** | **Cartes Médias Responsives** | Réécrire le module de rendu de cartes dans `src/ui.py` pour unifier les Livres, Films et Jeux. | `src/ui.py` |
| **Importante** | **Assistant IA & RAG Sources** | Sublimer l'UI de chat et isoler le RAG de manière moderne avec des accordéons de sources esthétiques. | `pages/6_🤖_Agent_IA.py` |
| **Polish** | **Thème Plotly & Visualisations** | Configurer une palette de couleurs uniforme pour tous les graphiques. | `src/visualizations.py` |
| **Polish** | **Réduction des Mouvements (reduced motion)** | Ajouter une bascule d'accessibilité pour désactiver toutes les animations CSS. | `src/ui.py` |
