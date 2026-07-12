# 💼 Fiche Portfolio & Synthèse CV — BookLens

Ce résumé est directement prêt à être copié/collé sur votre site portfolio, votre profil LinkedIn, votre CV ou vos publications de projets.

---

## 📌 Accroche (LinkedIn / Site Web)
> **BookLens v3.0** : Un système de recommandation hybride multimédia (Livres, Films, Jeux Vidéo) doté d'un agent IA conversationnel avec RAG local et d'un laboratoire d'évaluation complet, conçu pour fonctionner de manière autonome sur CPU/Laptop. 

---

## 🛠️ Compétences Démontrées
- **Data Engineering & Architecture** : Pipelines ETL, validation de données (diagnostics de doublons, d'anomalies et d'intégrité de schémas), intégration et enrichissement d'APIs externes (Open Library, TMDB, RAWG, Semantic Scholar) avec cache local.
- **Machine Learning & Recommandations** : Algorithme hybride associant le filtrage collaboratif (similarité cosinus user-item) et la similarité de contenu (TF-IDF sur métadonnées textuelles). Implémentation d'un profil de préférences utilisateur dynamique et reranking en temps réel.
- **IA Générative & RAG** : Modèles d'embeddings multilingues locaux (`sentence-transformers`), base vectorielle ChromaDB, et orchestrateur multi-agents (NVIDIA Nemotron / Hugging Face Llama) avec fallbacks dégradés offline.
- **MLOps & Evaluation Lab** : Cycle de vie des modèles, détection de dérive (data drift sur distributions de notes/genres), et suite d'évaluation déterministe avec scoring automatisé de 36 scénarios complexes (sécurité, injections, RAG).
- **CI/CD & DevOps** : Intégration continue (GitHub Actions, tests automatisés avec Python 3.12), support multilingue natif (FR/EN/ZH) et gestion sécurisée des secrets.

---

## 🏆 Réalisations Clés
1. **Zéro-Cloud par défaut (Confidentialité)** : L'application fait tourner son RAG PDF, ses embeddings et sa recherche sémantique en local sur CPU, garantissant la protection de la vie privée.
2. **Robustesse & Fallbacks** : L'agent IA et le moteur multimédia sont capables de s'adapter dynamiquement si l'utilisateur est déconnecté du réseau ou sans clés API, en basculant sur des algorithmes et corpus locaux.
3. **AI Evaluation Lab** : Mesure automatisée de la qualité des réponses (score de 0 à 100), du respect de la langue, de l'exfiltration de clés secrètes, et de l'adéquation du routage multi-agents.
4. **Interface Premium** : Design System CSS personnalisé sombre de type "glassmorphic" offrant une expérience utilisateur fluide et moderne.
