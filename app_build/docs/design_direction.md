# Design Direction — MediaLens

Ce document définit les directives artistiques, la charte graphique et les composants standards du nouveau design system de MediaLens.

---

## 1. Vision & Identité Visuelle

**Concept** : *Bibliothèque cinématographique futuriste*.
Un équilibre parfait entre l'atmosphère feutrée d'une bibliothèque nocturne et la précision d'une interface de streaming premium (Netflix/Canal+). L'IA est présentée de façon sobre, précise et intégrée, et non comme un gadget "SaaS AI" futuriste kitsch.

---

## 2. Palette Sombre de Référence

Toutes les surfaces et textes de l'application s'appuient sur cette palette de couleurs :

| Rôle Visuel | Code Couleur HEX | Description |
| :--- | :--- | :--- |
| **Fond principal (Background)** | `#070A13` | Noir chaud légèrement bleuté, très reposant pour les yeux. |
| **Surface basique (Card background)** | `#121826` | Bleu ardoise très sombre, utilisé pour les cartes et blocs de base. |
| **Surface surélevée (Elevated card)** | `#1B2336` | Version légèrement plus claire pour les états de focus ou survols. |
| **Accent principal (Primary Accent)** | `#0D9488` | Teal / Bleu pétrole élégant, utilisé pour les actions principales. |
| **Accent secondaire (Secondary Accent)** | `#F59E0B` | Ambre chaud pour les états spéciaux ou notations estimées. |
| **Texte principal (Text primary)** | `#F8FAFC` | Blanc crème très doux, excellent contraste. |
| **Texte secondaire (Text secondary)** | `#94A3B8` | Gris bleuté lisible pour les descriptions et légendes. |

---

## 3. Typographie

- **Font principale (UI & Texte)** : `'Inter', sans-serif` (chargée depuis Google Fonts).
- **Titres éditoriaux** : `'Inter', sans-serif` (avec un poids `700` ou `800` et une taille fluide).
- **Hiérarchie standard** :
  - `h1` : `2.5rem` à `3rem` (Hero principal)
  - `h2` : `1.8rem` (Titres de section)
  - `h3` : `1.3rem` (Titres de cartes moyennes)
  - `body` : `1rem` / `16px` (Texte courant, garantissant une bonne accessibilité)

---

## 4. Grille & Espacements

- **Unité de base** : Grille de `4px` (tous les paddings et marges doivent être des multiples de 4 : `4px`, `8px`, `12px`, `16px`, `24px`, `32px`, `48px`).
- **Bordures** : Subtils contours semi-transparents de `1px solid rgba(255, 255, 255, 0.05)`.
- **Arrondis (Border Radius)** :
  - Cartes et blocs conteneurs : `12px`
  - Boutons, inputs et badges : `8px`

---

## 5. Règles d'Animation (Motion Guidelines)

Les animations doivent être discrètes, fluides et ne jamais fatiguer l'utilisateur.

- **Durée rapide** : `120ms` (survols simples, clics, petits changements d'état).
- **Durée moyenne** : `220ms` (apparitions simples de blocs, ouverture d'accordéon).
- **Durée lente** : `350ms` (transition de page, chargement progressif).
- **Réduction des mouvements** : Toutes les animations doivent respecter le choix système `@media (prefers-reduced-motion: reduce)` ou la bascule utilisateur.
