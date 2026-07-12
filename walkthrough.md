# 📘 BookLens — Projet Terminé !

Félicitations, l'application **BookLens** a été entièrement développée, corrigée, et vérifiée avec succès. Le MVP est prêt à être utilisé comme projet pédagogique et ajouté à un portfolio Data/IA.

## 🌟 Ce qui a été accompli

L'équipe d'agents a traversé avec succès toutes les phases du cycle de développement :

1. **Phase de Spécification (@pm)** : Définition des besoins, de l'architecture, et rédaction de la documentation (`Technical_Specification.md`).
2. **Phase de Développement (@engineer)** : Écriture de tout le code backend (Data Engineering, Machine Learning) et frontend (Application Streamlit).
3. **Phase d'Audit et de Correction (@qa)** : 
   - Résolution de bugs complexes liés à Pandas (agrégations manquantes).
   - Fix de problèmes d'encodage Windows CP1252 causés par les emojis.
   - Résolution du dépassement de limite de `int32` dans Numpy lors de la génération des numéros ISBN.
4. **Phase de Déploiement Local (@devops)** : Vérification complète via un sub-agent web naviguant sur toutes les pages pour s'assurer que l'application Streamlit fonctionnait parfaitement.

## 📸 Aperçu de l'Application (Vérifié)

Voici quelques captures d'écran prises en temps réel lors du test de l'application en arrière-plan :

````carousel
![Page d'accueil chargée avec succès](/C:/Users/eliot/.gemini/antigravity-ide/brain/41eee5e9-a9d7-477f-abe9-f25a0ec6cf75/homepage_loaded_1783518940628.png)
<!-- slide -->
![Filtres et recherche sur les données](/C:/Users/eliot/.gemini/antigravity-ide/brain/41eee5e9-a9d7-477f-abe9-f25a0ec6cf75/recherche_page_loaded_1783518952741.png)
<!-- slide -->
![Dashboard de visualisations interactif](/C:/Users/eliot/.gemini/antigravity-ide/brain/41eee5e9-a9d7-477f-abe9-f25a0ec6cf75/dashboard_page_loaded_1783519020596.png)
<!-- slide -->
![Interaction avec l'Agent IA (Règles NLP)](/C:/Users/eliot/.gemini/antigravity-ide/brain/41eee5e9-a9d7-477f-abe9-f25a0ec6cf75/agent_ia_response_1783519052884.png)
````

## 🛠️ Fonctionnalités Développées

* **Data Pipeline Intégré** : Génération de données synthétiques, nettoyage des CSV, gestion des doublons et des valeurs manquantes.
* **Système de Recommandation** : Modèle de filtrage collaboratif basé sur la similarité cosinus (Items/Livres). Rapport ML disponible dans `production_artifacts/ml_report.md`.
* **Frontend Interactif** : UI soignée construite avec Streamlit, permettant d'explorer les métriques, rechercher des livres, obtenir des recommandations visuelles (avec barres de similarité), et consulter des graphiques Plotly dynamiques.
* **Agent IA basé sur des Règles** : Un bot conversationnel didactique sans LLM pour guider l'utilisateur.

## 🚀 Comment Lancer l'Application

Tout est installé et l'application s'exécute actuellement en arrière-plan (sur le port 8501).
Pour la lancer manuellement plus tard, ouvrez votre terminal (depuis `c:\Users\eliot\Desktop\appli book intro data ia\app_build`), et exécutez simplement :

```bash
streamlit run app.py
```
