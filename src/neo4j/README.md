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

4. **Télécharger le fichier JSONL**
   Téléchargez le fichier `openfoodfacts-products.jsonl` depuis le dépôt OpenFoodFacts 
   ([JSONL data export](https://world.openfoodfacts.org/data)) et placez-le dans le dossier `data/`.

## Composants principaux

Le projet s'articule autour de quatre composants principaux :

1. **Extraction et traitement des données** (`filter.py`, `analyse.py`)
   - Filtrage des données brutes d'OpenFoodFacts
   - Analyse statistique et identification des champs pertinents

2. **Création et population de la base Neo4j** (`create_graph.py`)
   - Création des nœuds et relations
   - Génération d'embeddings pour la recherche sémantique
   - Enrichissement avec les taxonomies d'OpenFoodFacts

3. **Validation et inspection du schéma** (`verify_neo4j_schema.py`)
   - Vérification structurelle de la base Neo4j
   - Identification des types de nœuds et relations existants
   - Comptage des relations par type et validation des propriétés
   - Contrôle de qualité des embeddings et des traductions
   - Confirmation de l'existence et configuration de l'index vectoriel
  
4. **Requêtes et interrogation de la base** (`query.py`, `cypher_queries.py`)
   - Encapsulation des requêtes Cypher
   - Fonctions spécialisées pour différents cas d'usage

5. **Implémentation de l'agent conversationnel** (`agent.py`)
   - Analyse des intentions en langage naturel
   - Traduction en requêtes Cypher
   - Formatage des résultats en réponses naturelles

## Exécution

Excécuter ces scripts dans l'ordre suivant :

```bash
python src/jsonl/filter.py  # Filtrage des données
python src/jsonl/analyse.py  # Analyse des données
python src/jsonl/create_graph.py  # Création de la base Neo4j
python src/jsonl/agent.py  # Lancement de l'agent
```

## Structure des taxonomies

Les taxonomies d'OpenFoodFacts enrichissent notre graphe avec des hiérarchies et des relations entre entités. Issues du [dépôt officiel d'OpenFoodFacts](https://github.com/openfoodfacts/openfoodfacts-server/tree/main/taxonomies), elles sont organisées en graphes acycliques dirigés où chaque nœud peut avoir plusieurs parents.

Les fichiers principaux (`categories.txt`, `ingredients.txt`, etc.) définissent des relations parent-enfant et contiennent des traductions multilingues et des synonymes, suivant ce format :
```
< en:Parent
en: Child name in English
fr: Child name in French
```

## Fonctionnement du script `create_graph.py` 

Ce script crée une base de données graphe dans Neo4j à partir des données alimentaires d'Open Food Facts. Voici son fonctionnement étape par étape:

1. **Préparation** : Il se connecte à votre base de données Neo4j et charge un modèle d'intelligence artificielle (SentenceTransformer) qui permet de transformer du texte en vecteurs numériques.

2. **Création de la structure** : Le script efface d'abord toutes les données existantes puis crée des contraintes pour s'assurer que chaque produit, marque, ingrédient, etc. soit unique.

3. **Importation des produits** : Il lit le fichier JSONL contenant les données alimentaires et crée un nœud dans la base de données pour chaque produit avec ses propriétés (nom, code-barre, nutriscore, etc.).

4. **Génération d'embeddings** : Pour chaque produit, il génère un "embedding" - un vecteur numérique qui représente le produit à partir de sa description, permettant plus tard de trouver des produits similaires.

5. **Création des relations** : Il relie chaque produit à ses:
   - Marques (HAS_BRAND)
   - Catégories (HAS_CATEGORY)
   - Ingrédients (CONTAINS)
   - Étiquettes/labels (HAS_LABEL)
   - Additifs (CONTAINS_ADDITIF)
   - Allergènes (CONTAINS_ALLERGEN)
   - Pays de vente (SOLD_IN)
   - Nutriments (HAS_NUTRIMENT)

6. **Intégration des taxonomies** : Il ajoute des hiérarchies entre les catégories et les ingrédients (par exemple, "pomme" est un enfant de "fruit").

7. **Création d'index vectoriel** : Il crée un index spécial permettant des recherches par similarité sémantique, comme "trouve-moi des produits similaires à X".

8. **Test final** : Il exécute une recherche sémantique pour vérifier que tout fonctionne correctement.

Ce script transforme donc des données "plates" en une riche base de données graphe où tout est connecté, ce qui permet ensuite à un
agent conversationnel de répondre à des questions complexes comme "Trouve-moi des alternatives plus saines au Nutella" ou "Quels snacks sans gluten contiennent du chocolat?".

La force de cette approche est que les relations entre entités (produits, ingrédients, etc.) sont explicitement modélisées, ce 
qui facilite la navigation et les requêtes complexes dans les données.


J'ai examiné le schéma actuel décrit dans le README.md et les résultats de `verify_neo4j_schema.py`. La section du README est globalement correcte, mais il y a quelques informations à ajuster pour qu'elle reflète parfaitement les résultats de la vérification. Voici une version révisée de cette section:

## Schéma du graphe dans Neo4j

La base de données Neo4j créée par `create_graph.py` suit cette structure&nbsp;:

### Nœuds
- **Product**: Produits alimentaires avec propriétés:
  - code (identifiant unique)
  - name (nom du produit)
  - product_name_en, product_name_fr (traductions)
  - generic_name (description générique)
  - quantity (quantité)
  - nutriscore_grade (score nutritionnel)
  - nova_group (classification NOVA)
  - ecoscore_grade (impact environnemental)
  - embedding (vecteur pour la recherche sémantique)

- **Brand**: Marques commerciales (propriété: name)
- **Category**: Catégories de produits (propriété: name)
- **Ingredient**: Ingrédients (propriété: name)
- **Nutriment**: Nutriments et valeurs nutritives (propriété: name)
- **Label**: Labels et certifications (propriété: name)
- **Additif**: Additifs alimentaires (propriété: name)
- **Allergen**: Allergènes potentiels (propriété: name)
- **Country**: Pays de commercialisation (propriété: name)
- **Nutrient**: Informations nutritionnelles complémentaires (propriété: name)

### Relations principales
- **(Product)-[:HAS_BRAND]->(Brand)**: Relie produits et marques
- **(Product)-[:HAS_CATEGORY]->(Category)**: Catégorisation des produits
- **(Product)-[:CONTAINS]->(Ingredient)**: Ingrédients contenus dans un produit
- **(Product)-[:CONTAINS_ADDITIF]->(Additif)**: Additifs présents dans un produit
- **(Product)-[:CONTAINS_ALLERGEN]->(Allergen)**: Allergènes présents dans un produit
- **(Product)-[:HAS_LABEL]->(Label)**: Labels/certifications d'un produit
- **(Product)-[:SOLD_IN]->(Country)**: Pays où le produit est commercialisé
- **(Product)-[:HAS_NUTRIMENT {value, unit}]->(Nutriment)**: Valeurs nutritionnelles avec propriétés indiquant la quantité et l'unité

### Relations hiérarchiques (basées sur les taxonomies d'OpenFoodFacts)
Ces relations sont créées par la fonction `create_taxonomy_structures`:

- **(Category)-[:HAS_CHILD]->(Category)**: Hiérarchie des catégories (10,099 relations)
- **(Ingredient)-[:CONTAINS]->(Ingredient)**: Hiérarchie des ingrédients (4,511 relations)
- **(Additif)-[:PART_OF]->(Additif)**: Hiérarchie des additifs (115 relations)
- **(Label)-[:INCLUDES]->(Label)**: Hiérarchie des labels (2,076 relations)

Notez que la relation `BELONGS_TO` entre Allergen-Allergen et `PART_OF` entre Nutriment-Nutriment sont définies dans le schéma mais ne contiennent actuellement aucune relation.

### Index vectoriel
- **product_embedding_index**: Index vectoriel créé pour les embeddings des produits, permettant des recherches par similarité sémantique (384 dimensions, similarité cosinus)

Le graphe intègre des enrichissements via les taxonomies d'OpenFoodFacts, notamment des traductions et synonymes dans plusieurs langues (principalement français et anglais), stockés comme propriétés des nœuds (translations_en, translations_fr). Cette structure permet des requêtes complexes comme la recherche de produits similaires, l'identification d'alternatives plus saines, ou la navigation dans les hiérarchies d'ingrédients et de catégories.

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