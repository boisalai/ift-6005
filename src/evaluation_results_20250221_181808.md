# Rapport d'évaluation de l'agent Open Food Facts

Date: 2025-02-21 18:18:08

## Informations d'exécution

| Paramètre | Valeur |
|-----------|--------|
| Langue | en |
| Questions traitées | 1 |
| Modèle LLM | anthropic/claude-3-5-sonnet-20240620 |
| Temps total | 19.40s |
| Temps moyen par question | 19.40s |

## Description des métriques

- **Exécution SQL** : Évalue si l'agent génère des requêtes SQL valides qui retournent les bons résultats
- **Sémantique** : Mesure si la réponse en langage naturel de l'agent correspond au sens de la réponse attendue
- **Séquence de recherche** : Évalue si l'agent suit une progression logique dans sa recherche d'information
  - Respect de la séquence : Vérifie si l'agent commence par la base de données avant d'utiliser d'autres sources
  - Nombre d'étapes : Compte le nombre total d'étapes de recherche effectuées

## Métriques de Performance

| Métrique | Score (%) | Min | Max | Moyenne | Médiane |
|-----------|-----------|-----|-----|---------|----------|
| Exécution SQL | 50.00 | 50.00 | 50.00 | 50.00 | 50.00 |
| Sémantique | 70.00 | 70.00 | 70.00 | 70.00 | 70.00 |
| Respect séquence | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |

## Statistiques des étapes de recherche

| Statistique | Valeur |
|-------------|--------|
| Nombre minimum d'étapes | 2 |
| Nombre maximum d'étapes | 2 |
| Nombre moyen d'étapes | 2.0 |
| Nombre médian d'étapes | 2 |

## Temps de réponse

| Statistique | Valeur (secondes) |
|-------------|-------------------|
| Minimum | 19.40 |
| Maximum | 19.40 |
| Moyenne | 19.40 |
| Médiane | 19.40 |

## Statistiques des requêtes

| Métrique | Nombre | Pourcentage |
|-----------|---------|-------------|
| Requêtes avec SQL | 1 | 100.0% |
| Exécutions réussies | 1 | 100.0% |
