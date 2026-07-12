# 📊 BookLens — Rapport Machine Learning

## 1. Vue d'ensemble du modèle

| Paramètre | Valeur |
|---|---|
| Type de modèle | Filtrage collaboratif basé sur les items |
| Mesure de similarité | Similarité cosinus |
| Seuil min. de ratings | 2 |
| Livres dans le modèle | 468 |
| Taille de la matrice | 200 users × 468 books |

## 2. Données utilisées

| Métrique | Valeur |
|---|---|
| Total ratings | 4383 |
| Livres uniques | 523 |
| Utilisateurs uniques | 200 |
| Note moyenne | 5.67 |
| Livre le mieux noté | A Door into Ocean |

## 3. Comment ça marche ?

### Étape 1 : La Matrice User-Item
On crée un tableau où :
- Chaque **ligne** représente un utilisateur
- Chaque **colonne** représente un livre
- Chaque **cellule** contient la note donnée (0 si pas de note)

### Étape 2 : Similarité Cosinus
Pour chaque paire de livres, on calcule un score de similarité :
- **1.0** = les deux livres reçoivent exactement les mêmes notes
- **0.0** = aucune corrélation entre les notes
- Plus le score est élevé, plus les livres sont "similaires"

### Étape 3 : Recommandation
Quand un utilisateur sélectionne un livre :
1. On cherche les livres avec le score de similarité le plus élevé
2. On retourne les N meilleurs résultats
3. On explique pourquoi chaque livre est recommandé

## 4. Limites et améliorations possibles

### Limites actuelles
- **Cold start** : impossible de recommander pour un nouveau livre sans ratings
- **Sparsité** : avec peu de ratings, la matrice est très creuse
- **Pas de contenu** : le modèle ne regarde pas le genre ou la description

### Améliorations possibles
- Filtrage hybride (collaboratif + contenu)
- Matrix Factorization (SVD)
- Deep Learning (autoencoders)
- Ajout de features textuelles (NLP sur les titres/descriptions)

## 5. Exemple de recommandation

**Livre sélectionné** : A Door into Ocean

| Rang | Livre recommandé | Score de similarité |
|---|---|---|
| 1 | Ancient River | 0.3986 |
| 2 | Lost Kingdom | 0.3230 |
| 3 | Forgotten Legacy: Tale of Tale | 0.3229 |

---
*Rapport généré automatiquement par BookLens*
