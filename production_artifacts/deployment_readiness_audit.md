# Audit de Préparation au Déploiement Public — BookLens

Ce document dresse l'état des lieux complet du projet BookLens avant son déploiement public sur Streamlit Community Cloud.

---

## 1. Fiche Technique de l'Audit

| Paramètre | Valeur / Constat | Statut / Risque |
|---|---|---|
| **Entrypoint Streamlit** | [app.py](file:///c:/Users/eliot/Desktop/appli%20book%20intro%20data%20ia/app_build/app.py) | ✅ Correct |
| **Version Python cible** | `3.12` | ✅ Recommandé |
| **Total Pages de navigation** | 18 pages dans [pages/](file:///c:/Users/eliot/Desktop/appli%20book%20intro%20data%20ia/app_build/pages) | ✅ Unique Emojis |
| **Limites mémoire (RAM)** | sentence-transformers (PyTorch CPU) | ⚠️ Modéré (surveillance RAM cloud) |
| **Base Vectorielle** | ChromaDB locale persistante | ✅ Configurée CPU/Laptop |

---

## 2. Dépendances & requirements.txt

L'audit des dépendances dans [requirements.txt](file:///c:/Users/eliot/Desktop/appli%20book%20intro%20data%20ia/app_build/requirements.txt) confirme l'absence de bibliothèques standard (`os`, `sys`, `json`, etc.) et de doublons :
- **Streamlit** >= 1.28.0 (Interface web)
- **OpenAI / python-dotenv / requests** (Interactions APIs)
- **Pandas / Numpy / Scikit-learn / Scipy** (Pipeline Data / ML Cosine Similarity)
- **Plotly** (Visualisations dynamiques)
- **ChromaDB / PyPDF / PyMuPDF / Sentence-transformers** (RAG PDF Local)

---

## 3. Analyse des Chemins & Persistance Locale (Risques Cloud)

Dans un environnement éphémère comme Streamlit Community Cloud, le stockage disque local est temporaire. Voici les risques identifiés et les garde-fous correspondants :

1. **`data/uploads/` et `data/chroma_db/`** (RAG PDF) :
   - *Risque* : Perte des documents importés lors du redémarrage du conteneur.
   - *Garde-fou* : Création automatique des dossiers si absents au runtime. Si aucun document n'est indexé, avertissement clair traduit expliquant qu'il faut en uploader un.
2. **`data/mlops/runs.json`** et **`models/`** (Modèles & MLOps) :
   - *Risque* : Perte de l'historique des entraînements.
   - *Garde-fou* : Démarrage garanti avec des modèles fallbacks et tracker local robuste.
3. **`data/user_profile/feedbacks.json`** (Personnalisation) :
   - *Risque* : Réinitialisation des favoris de l'utilisateur à chaque arrêt du conteneur.
   - *Garde-fou* : Chargement avec fallback vide silencieux si absent. Avertissement dans la page Confidentialité et Sécurité.
4. **`logs/`** :
   - *Risque* : Perte de persistance des logs techniques.
   - *Garde-fou* : Logging local sécurisé sans crash en cas d'inaccessibilité en écriture.

---

## 4. Gestion des Secrets & API Keys

L'application accède aux secrets dans l'ordre de priorité suivant :
1. `st.secrets` (Streamlit Cloud Dashboard)
2. `os.environ` (Variables d'environnement locales / `.env`)
3. Absence de clé (Mode fallback dégradé automatique)

### Clés attendues :
- `NVIDIA_API_KEY` (Assistant Nemotron principal)
- `HF_TOKEN` (Génération d'images / Voix)
- `TMDB_API_KEY` (Métadonnées de films)
- `RAWG_API_KEY` (Métadonnées de jeux vidéo)

---

## 5. Démarrage sans Clé API & Fallbacks

L'audit confirme le comportement robuste de BookLens en l'absence de clés :
- **Accueil & Recherche** : 100% opérationnels avec les datasets locaux générés de démonstration.
- **Recommandations** : Reranking et algorithme hybride 100% locaux.
- **Agent IA** : Détection d'intentions locale avec réponses statiques issues du corpus et des statistiques réelles du dataset, évitant toute erreur de connexion.
- **Bibliothèque RAG** : Indexation locale opérationnelle.
