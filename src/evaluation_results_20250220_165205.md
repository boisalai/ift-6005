# Rapport d'évaluation de l'agent Open Food Facts

Date: 2025-02-20 16:52:05

## Informations d'exécution

| Paramètre | Valeur |
|-----------|--------|
| Langue | en |
| Questions traitées | 1 |
| Modèle LLM | ollama/llama3.1:8b-instruct-q8_0 |
| Temps total | 71.73s |
| Temps moyen par question | 71.73s |

## Description des métriques

- **Exécution SQL** : Évalue si l'agent génère des requêtes SQL valides qui retournent les bons résultats
- **Sémantique** : Mesure si la réponse en langage naturel de l'agent correspond au sens de la réponse attendue
- **Stratégie** : Évalue si l'agent suit une progression logique : d'abord la base de données, puis des approches alternatives, et enfin d'autres sources si nécessaire

## Métriques de Performance

| Métrique | Score (%) | Min | Max | Moyenne | Médiane |
|-----------|-----------|-----|-----|---------|----------|
| Exécution SQL | 50.00 | 0.50 | 0.50 | 0.50 | 0.50 |
| Sémantique | 17.39 | 0.17 | 0.17 | 0.17 | 0.17 |
| Stratégie | 40.00 | 0.40 | 0.40 | 0.40 | 0.40 |
