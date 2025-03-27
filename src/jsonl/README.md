# Agent conversationnel pour interroger un graphe Neo4j sur les produits alimentaires d'OpenFoodFacts

## Vue d'ensemble

Ce système permet aux utilisateurs d'interroger en langage naturel une base de données Neo4j contenant des informations sur des produits alimentaires provenant d'OpenFoodFacts. L'objectif est de fournir une interface conversationnelle intelligente qui comprend les requêtes en français et en anglais, et qui peut extraire des informations pertinentes sur les produits, leurs ingrédients, valeurs nutritionnelles, allergènes, etc.

## Architecture du système

```
┌──────────────┐    ┌───────────┐    ┌────────────────┐
│ Données      │    │ Scripts de│    │ Base de données│
│ OpenFoodFacts├───►  traitement├───►  Neo4j          │
└──────────────┘    └───────────┘    └───────┬────────┘
                                             │
                                             ▼
                   ┌───────────────────────────────────┐
                   │         Agent conversationnel     │
                   │  (Embeddings + Requêtes Cypher)   │
                   └───────────────────┬───────────────┘
                                       │
                                       ▼
                   ┌───────────────────────────────────┐
                   │         Interface utilisateur     │
                   └───────────────────────────────────┘
```


## Installation

1. **Créer et activer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer les variables d'environnement**
   Créez un fichier `.env` à la racine du projet :
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   NEO4J_URI=neo4j+s://...
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=...
   ```


## Composants principaux

Le projet s'articule autour de quatre composants principaux :

1. **Extraction et traitement des données** (`filter.py`, `analyse.py`)
   - Filtrage des données brutes d'OpenFoodFacts
   - Analyse statistique et identification des champs pertinents

2. **Création et population de la base Neo4j** (`create_graph.py`)
   - Création des nœuds et relations
   - Génération d'embeddings pour la recherche sémantique
   - Enrichissement avec les taxonomies d'OpenFoodFacts

3. **Requêtes et interrogation de la base** (`query.py`, `cypher_queries.py`)
   - Encapsulation des requêtes Cypher
   - Fonctions spécialisées pour différents cas d'usage

4. **Implémentation de l'agent conversationnel** (`agent.py`)
   - Analyse des intentions en langage naturel
   - Traduction en requêtes Cypher
   - Formatage des résultats en réponses naturelles


## Structure des taxonomies

Les taxonomies d'OpenFoodFacts enrichissent notre graphe avec des hiérarchies et des relations entre entités. Issues du [dépôt officiel d'OpenFoodFacts](https://github.com/openfoodfacts/openfoodfacts-server/tree/main/taxonomies), elles sont organisées en graphes acycliques dirigés où chaque nœud peut avoir plusieurs parents.

Les fichiers principaux (`categories.txt`, `ingredients.txt`, etc.) définissent des relations parent-enfant et contiennent des traductions multilingues et des synonymes, suivant ce format :
```
< en:Parent
en: Child name in English
fr: Child name in French
```

## Schéma de la base de données Neo4j

Notre base de données Neo4j créé par `create_graph.py` suit cette structure :

### Nœuds
- **Product** : Produits alimentaires (code, name, nutriscore_grade, embedding...)
- **Brand** : Marques commerciales
- **Category** : Catégories de produits (hiérarchisées)
- **Ingredient** : Ingrédients (hiérarchisés)
- **Nutriment** : Nutriments et valeurs nutritives
- **Label** : Labels et certifications (bio, commerce équitable...)
- **Additif** : Additifs alimentaires
- **Allergen** : Allergènes potentiels
- **Country** : Pays de commercialisation

### Relations principales
- **(Product)-[:HAS_BRAND]->(Brand)** : Relie produits et marques
- **(Product)-[:HAS_CATEGORY]->(Category)** : Catégorisation des produits
- **(Product)-[:CONTAINS]->(Ingredient)** : Ingrédients contenus dans un produit
- **(Product)-[:CONTAINS_ADDITIF]->(Additif)** : Additifs présents dans un produit
- **(Product)-[:CONTAINS_ALLERGEN]->(Allergen)** : Allergènes présents dans un produit
- **(Product)-[:HAS_LABEL]->(Label)** : Labels/certifications d'un produit
- **(Product)-[:SOLD_IN]->(Country)** : Pays où le produit est commercialisé
- **(Product)-[:HAS_NUTRIMENT {value, unit}]->(Nutriment)** : Valeurs nutritionnelles

### Relations hiérarchiques
- **(Category)-[:HAS_CHILD]->(Category)** : Hiérarchie des catégories
- **(Ingredient)-[:CONTAINS]->(Ingredient)** : Hiérarchie des ingrédients
- **(Additif)-[:PART_OF]->(Additif)** : Hiérarchie des additifs
- **(Allergen)-[:BELONGS_TO]->(Allergen)** : Hiérarchie des allergènes
- **(Country)-[:CONTAINS_REGION]->(Country)** : Hiérarchie géographique
- **(Nutriment)-[:PART_OF]->(Nutriment)** : Hiérarchie des nutriments
- **(Label)-[:INCLUDES]->(Label)** : Hiérarchie des labels

## Configuration des modèles pour l'agent

L'agent peut utiliser deux types de modèles de langage :

### Claude d'Anthropic (recommandé)
```python
llm = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-20240620")
```
**Avantages :** Meilleure compréhension des requêtes complexes, gestion supérieure des nuances linguistiques  
**Inconvénients :** Nécessite une clé API, coût associé, dépendance internet

### Llama 3.2 via Ollama (local)
```python
llm = LiteLLMModel(model_id="ollama/llama3.2:latest", api_base="http://localhost:11434")
```
**Avantages :** Fonctionnement local, aucun coût, confidentialité  
**Inconvénients :** Performances inférieures, installation d'Ollama requise


## Lancement et test de l'agent

1. **Vérifier les prérequis**
   - Base Neo4j accessible
   - Variables d'environnement configurées
   - (Optionnel) Ollama installé pour Llama local

2. **Configurer le modèle LLM**
   Dans `agent.py`, choisissez :
   ```python
   engine = "sonnet"  # Pour Claude
   # OU
   engine = "ollama/llama3.2:latest"  # Pour Llama
   ```

3. **Lancer l'agent**
   ```bash
   python src/jsonl/agent.py
   ```


## Exemples de requêtes

```
Quels produits sont fabriqués par Kellogg's?
Quels produits contiennent du sucre?
Montre-moi des produits sans gluten.
Parle-moi du Nutella.
Compare Coca-Cola et Pepsi.
Donne-moi des produits végétaliens.
```

## Prochaines étapes

- Analyser les performances de l'agent interrogeant la base Neo4j par rapport à l'agent qui interroge la base DuckDB créé dans la première partie du projet.

## Développements futurs

1. **Interface web** : Implementation via Streamlit ou Flask avec visualisation du graphe
2. **Détection d'intention avancée** : Classification fine-tunée pour le domaine alimentaire
3. **Recommandations personnalisées** : Système de profils et de préférences utilisateurs
4. **Enrichissement de données** : Intégration de sources nutritionnelles supplémentaires
5. **Analyse avancée des requêtes** : Correction orthographique et suggestions
6. **Optimisation des performances** : Mise en cache et requêtes optimisées

## Conclusion

Ce projet démontre comment combiner une base de données graphe Neo4j avec des techniques d'IA conversationnelle pour créer un agent capable de répondre à des questions complexes sur les produits alimentaires. La structure du graphe, enrichie par des taxonomies et des embeddings vectoriels, permet des recherches sémantiques puissantes qui dépassent les simples correspondances de mots-clés.