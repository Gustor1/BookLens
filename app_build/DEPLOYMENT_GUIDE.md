# 🚀 Guide de Déploiement Manuel sur Streamlit Community Cloud

Ce guide pas-à-pas vous accompagne dans le déploiement public et manuel de l'application BookLens sur **Streamlit Community Cloud**.

---

## Étape 1 : Validation Locale Initiale
Avant de déployer, assurez-vous que tous les tests unitaires et d'intégration passent avec succès en local :
```bash
cd app_build
python -m pytest
```
Tous les tests doivent être au vert (`PASSED`).

---

## Étape 2 : Préparation du Repository GitHub
1. Créez un nouveau dépôt public sur GitHub (ex: `BookLens`).
2. S'assurer qu'aucun fichier sensible ou clé n'est suivi par Git en vérifiant le statut :
```bash
git status
```
*Note : Le fichier `.gitignore` a été pré-configuré pour exclure tous les secrets (`.env`, `secrets.toml`), caches, uploads locaux, bases ChromaDB et rapports d'évaluation.*

3. Poussez votre code local vers votre dépôt distant :
```bash
git add .
git commit -m "Prepare BookLens for cloud deployment"
git branch -M main
git remote add origin https://github.com/VOTRE_NOM/BookLens.git
git push -u origin main
```

---

## Étape 3 : Déploiement sur Streamlit Community Cloud
1. Rendez-vous sur [share.streamlit.io](https://share.streamlit.io/) et connectez-vous avec votre compte GitHub.
2. Cliquez sur le bouton **"New app"** (ou **"Create app"**).
3. Renseignez les paramètres de déploiement :
   - **Repository** : Sélectionnez votre dépôt (ex: `VOTRE_NOM/BookLens`).
   - **Branch** : `main` (ou `master`).
   - **Main file path** : `app.py` (assurez-vous d'être dans le bon dossier parent si applicable, par exemple `app.py` ou `app_build/app.py`).
4. Cliquez sur **"Advanced settings..."** (Paramètres avancés) en bas du formulaire :
   - **Python version** : Sélectionnez **3.12**.

---

## Étape 4 : Injection des Secrets Applicatifs
Dans le champ texte **Secrets** de Streamlit Community Cloud, copiez et collez la configuration suivante en remplaçant les valeurs fictives par vos clés d'API personnelles :

```toml
# Configuration des Secrets de Production BookLens

# Clé API NVIDIA Build (Agent IA Nemotron)
# Obtenez-la gratuitement sur : https://build.nvidia.com
NVIDIA_API_KEY = "votre_cle_nvidia_api_ici"

# Token Hugging Face (Génération d'images FLUX & MMS-TTS)
# Créez-en un dans Settings > Access Tokens : https://huggingface.co
HF_API_KEY = "votre_token_hugging_face_ici"

# Clé API TMDB (Films)
# Obtenez-la gratuitement dans les paramètres TMDB > API : https://themoviedb.org
TMDB_API_KEY = "votre_cle_tmdb_ici"

# Clé API RAWG (Jeux Vidéo)
# Obtenez-la en créant un compte développeur : https://rawg.io/apidocs
RAWG_API_KEY = "votre_cle_rawg_ici"
```

Cliquez sur **"Save"** pour enregistrer les secrets.

---

## Étape 5 : Lancement & Validation du Déploiement
1. Cliquez sur **"Deploy!"**.
2. Suivez le chargement des logs d'installation des dépendances dans le panneau latéral droit.
3. Une fois l'application chargée :
   - Allez sur l'onglet **🔒 Confidentialité & Sécurité** pour vérifier le statut `"✅ Connecté"` de tous vos fournisseurs.
   - Visitez les pages **Films** et **Jeux Vidéo** et faites une recherche pour tester la récupération d'API réelles.
   - Entrez dans l'**Agent IA**, activez le chat et vérifiez que les requêtes fonctionnent avec le LLM en ligne.

---

## 🛠️ Résolution des Problèmes les Plus Fréquents

| Problème | Cause Possible | Solution |
|---|---|---|
| **Erreur d'import lors du déploiement** | Dépendance manquante dans `requirements.txt`. | Vérifiez que le package est listé. Streamlit Cloud réinstalle automatiquement à chaque push sur `main`. |
| **Dossiers d'uploads/cache manquants** | Le cloud n'a pas les dossiers pré-créés. | L'application BookLens crée automatiquement `data/uploads/`, `data/chroma_db/`, et `logs/` au runtime. |
| **Limitation mémoire (RAM crash)** | Le modèle d'embedding RAG consomme trop. | Nous utilisons `paraphrase-multilingual-MiniLM-L12-v2` (~80 Mo), très économe en RAM, qui tourne sans problème sur le tier gratuit de Streamlit. |
| **Modifications non persistées** | Le conteneur du cloud a redémarré. | C'est le comportement attendu sur Streamlit Cloud (stockage éphémère). Pour persister, exécutez localement. |
