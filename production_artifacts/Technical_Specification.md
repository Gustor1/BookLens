# 📘 BookLens — Spécification Technique

## 1. Résumé du Projet

**BookLens** est une application pédagogique de recommandation de livres. Elle sert d'introduction pratique à trois domaines :
- **Data Engineering** : chargement, nettoyage et fusion de données CSV
- **Machine Learning** : système de recommandation simple (filtrage collaboratif)
- **Agent IA** : module conversationnel qui explique les recommandations et les métriques

L'application est construite avec **Streamlit** et utilise le dataset **Book-Crossing** (livres, utilisateurs, ratings).

---

## 2. Objectifs Fonctionnels

### 2.1 Data Engineering
- Charger 3 fichiers CSV : `Books.csv`, `Users.csv`, `Ratings.csv`
- Nettoyer les données : doublons, valeurs manquantes, types incorrects
- Fusionner les datasets en un dataset final exploitable
- Sauvegarder le dataset nettoyé dans `data/processed/`
- Générer des métriques (nombre de livres, utilisateurs, ratings, distributions)

### 2.2 Machine Learning
- Implémenter un système de recommandation par **filtrage collaboratif basé sur les items** (corrélation entre livres)
- Approche pédagogique : matrice user-item → corrélation → recommandations
- Sauvegarder la matrice de corrélation et les résultats
- Générer un rapport ML clair dans `production_artifacts/ml_report.md`

### 2.3 Application Streamlit
- **Page d'accueil** : présentation du projet, statistiques clés
- **Recherche de livre** : barre de recherche avec filtres
- **Recommandations** : sélectionner un livre et obtenir des recommandations similaires
- **Dashboard** : graphiques simples (top livres, distribution des ratings, etc.)

### 2.4 Agent IA
- Module intégré dans Streamlit (onglet dédié)
- Répond à des questions prédéfinies sur les données et les recommandations
- Explique pourquoi un livre est recommandé (basé sur la corrélation)
- Utilise un système de règles simples (pattern matching) — pas de LLM externe requis

---

## 3. Contraintes Techniques

| Contrainte | Détail |
|---|---|
| Langage | Python 3.9+ |
| Framework web | Streamlit |
| Data | pandas |
| ML | scikit-learn, scipy |
| Visualisation | plotly, matplotlib |
| Pas de LLM externe | L'agent IA fonctionne avec des règles/templates |
| Code | Clair, modulaire, commenté |
| Structure | Tout le code dans `app_build/` |
| Artifacts | Documents intermédiaires dans `production_artifacts/` |

---

## 4. Architecture Proposée

```
app_build/
├── app.py                    # Point d'entrée Streamlit
├── requirements.txt          # Dépendances Python
├── README.md                 # Documentation pédagogique
│
├── data/
│   ├── raw/                  # Données CSV brutes (générées par script)
│   └── processed/            # Données nettoyées
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # Chargement des CSV
│   ├── data_cleaner.py       # Nettoyage et fusion
│   ├── recommender.py        # Système de recommandation ML
│   ├── agent.py              # Agent IA conversationnel
│   └── visualizations.py     # Fonctions de graphiques
│
├── pages/
│   ├── 1_🔍_Recherche.py     # Page recherche de livre
│   ├── 2_⭐_Recommandations.py # Page recommandations
│   ├── 3_📊_Dashboard.py     # Page dashboard
│   └── 4_🤖_Agent_IA.py      # Page agent IA
│
└── models/                   # Modèles et matrices sauvegardés
    └── .gitkeep
```

---

## 5. Stack Proposée

| Composant | Technologie | Justification |
|---|---|---|
| Backend/Frontend | Streamlit | Simple, Python-natif, idéal pour data apps |
| Data processing | pandas | Standard pour la manipulation de données |
| ML | scipy (corrélation) | Simple et pédagogique |
| Visualisation | plotly | Graphiques interactifs dans Streamlit |
| Agent IA | Python pur (regex/templates) | Pas de dépendance externe |

---

## 6. Données

### 6.1 Source
Le projet utilise le dataset **Book-Crossing** avec 3 fichiers CSV :

**Books.csv** — Colonnes :
- `ISBN`, `Book-Title`, `Book-Author`, `Year-Of-Publication`, `Publisher`
- `Image-URL-S`, `Image-URL-M`, `Image-URL-L`

**Users.csv** — Colonnes :
- `User-ID`, `Location`, `Age`

**Ratings.csv** — Colonnes :
- `User-ID`, `ISBN`, `Book-Rating`

### 6.2 Stratégie de génération
Comme les fichiers CSV ne sont pas fournis, le projet inclura un script `generate_sample_data.py` qui crée des données d'exemple réalistes (500 livres, 200 utilisateurs, 5000 ratings) pour permettre une exécution immédiate.

---

## 7. Détail des Modules

### 7.1 `data_loader.py`
- `load_books(path)` → DataFrame
- `load_users(path)` → DataFrame
- `load_ratings(path)` → DataFrame
- Gestion d'encodage (latin-1, utf-8)

### 7.2 `data_cleaner.py`
- `clean_books(df)` : supprimer doublons, corriger types, gérer NaN
- `clean_users(df)` : filtrer âges aberrants, gérer NaN
- `clean_ratings(df)` : supprimer ratings invalides
- `merge_datasets(books, users, ratings)` → DataFrame fusionné
- `generate_metrics(merged_df)` → dict de métriques

### 7.3 `recommender.py`
- `build_user_item_matrix(df)` : créer matrice pivot User × Book
- `compute_correlations(matrix, book_title)` : calculer corrélations
- `get_recommendations(book_title, n=5)` : retourner top-N recommandations
- `save_model(matrix, path)` / `load_model(path)`
- `generate_ml_report(metrics)` : créer le rapport ML

### 7.4 `agent.py`
- `BookLensAgent` : classe avec méthodes pour répondre aux questions
- Pattern matching sur mots-clés (recommandation, statistiques, explication)
- `answer(question)` → réponse textuelle
- Templates de réponse pré-définis

### 7.5 `visualizations.py`
- `plot_rating_distribution(df)` → fig plotly
- `plot_top_books(df, n=10)` → fig plotly
- `plot_top_authors(df, n=10)` → fig plotly
- `plot_ratings_per_year(df)` → fig plotly
- `plot_age_distribution(df)` → fig plotly

---

## 8. Étapes de Réalisation

| Étape | Description | Agent |
|---|---|---|
| 1 | Rédiger la spécification technique | @pm |
| 2 | Générer le script de données d'exemple | @engineer |
| 3 | Générer les modules src/ | @engineer |
| 4 | Générer les pages Streamlit | @engineer |
| 5 | Générer app.py, requirements.txt, README.md | @engineer |
| 6 | Auditer le code vs la spec | @qa |
| 7 | Corriger les problèmes trouvés | @qa |
| 8 | Lancer localement et vérifier | @devops |

---

## 9. Critères de Validation

- [ ] Les 3 CSV sont chargés et nettoyés correctement
- [ ] Le dataset fusionné est exploitable
- [ ] Le système de recommandation retourne des résultats cohérents
- [ ] L'application Streamlit se lance sans erreur
- [ ] Les 4 pages sont navigables
- [ ] L'agent IA répond à au moins 5 types de questions
- [ ] Le rapport ML est généré
- [ ] Le README est complet et pédagogique
- [ ] requirements.txt est complet

---

*Spécification rédigée par @pm — BookLens v1.0*
