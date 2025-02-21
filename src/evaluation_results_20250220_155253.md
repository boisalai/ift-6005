# Rapport d'Évaluation de l'Agent Open Food Facts

Date: 2025-02-20 15:52:53

## Métriques Globales

| Métrique | Valeur |
|----------|--------|
| Précision d'Exécution (EX) | 50.00% |
| Couverture Données Manquantes (TCM) | 40.00% |
| Précision Sémantique | 80.00% |
| Temps de Réponse Moyen | 11.52s |

### Distribution des Scores

| Métrique | Min | Max | Moyenne | Médiane |
|----------|-----|-----|---------|----------|
| SQL | 0.50 | 0.50 | 0.50 | 0.50 |
| Sémantique | 0.80 | 0.80 | 0.80 | 0.80 |
| TCM | 0.40 | 0.40 | 0.40 | 0.40 |

## Résultats Détaillés

### Question 1 (en)

#### Question et Réponses
**Question:** What food products without additives are available in the database?

**Réponse Attendue:** The database contains 5843 products without additives, including items such as organic Vermont maple syrup, low-fat milk, organic blue agave, and coconut milk.

**Réponse de l'Agent:** There are many food products without additives available in the database. Some examples include: Organic Vermont Maple Syrup, 1% low-fat milk, Seto fumi furikake, Organic Blue Agave, Coconut Milk, Coconut Water, Teriyaki Beef Jerky, Ginger Teriyaki Chicken Breast, Whole Wheat Cinnamon Harvest, and Coconut Cream. These products have empty additives_tags, indicating they don't contain any additives.
**Source:** Open Food Facts

#### Métriques
```
Temps de réponse: 11.52s

Précision SQL:
- query_present: 1.00
- execution_success: 1.00
- results_match: 0.00
- combined: 0.50

Précision sémantique: 0.80
Score TCM: 0.40
```

#### Requête SQL
```sql

SELECT 
    unnest(list_filter(product_name, x -> x.lang == 'en'))['text'] AS name,
    additives_tags
FROM products
WHERE additives_tags = '[]'
LIMIT 10

```

#### Résultats de la Requête
```
Lignes correspondantes: 0
Total des lignes: 5853
Lignes de référence: 5843
Lignes de l'agent: 10
```

#### Étapes de Recherche
**Étape 1** (database_query)
- Description: Queried the database for products with empty additives_tags
- Succès: True
- Résultat: Retrieved 10 products without additives

---

