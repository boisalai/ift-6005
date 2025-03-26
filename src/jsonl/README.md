# Agent conversationnel pour interroger un graphe Neo4j sur les produits alimentaires d'OpenFoodFacts

## Vue d'ensemble

Ce système permet aux utilisateurs d'interroger en langage naturel une base de données Neo4j contenant des informations sur des produits alimentaires provenant d'OpenFoodFacts. 

## Installation des bibliothèques

Pour installer l’ensemble des bibliothèques nécessaires au fonctionnement du système, procédez comme suit :

1. **Créer un environnement virtuel**  
   Dans le répertoire racine du projet, exécutez :
   ```bash
   python -m venv venv
   ```
2. **Activer l’environnement virtuel**  
   - Sous Linux/macOS :
     ```bash
     source venv/bin/activate
     ```
   - Sous Windows :
     ```bash
     venv\Scripts\activate
     ```
3. **Installer les dépendances**  
   Installez les bibliothèques listées dans le fichier requirements.txt en lançant :
   ```bash
   pip install -r requirements.txt
   ```
   Cela installera notamment les packages pour la recherche vectorielle (faiss-cpu, duckdb), le traitement du langage (sentence-transformers, langchain), ainsi que les outils de développement (smolagents, streamlit, etc.).
4. **Configurer les variables d'environnement**
   Créez un fichier `.env` à la racine du projet et ajoutez-y les variables d'environnement nécessaires.
   ```
   ANTHROPIC_API_KEY=sk-ant-...

   # Wait 60 seconds before connecting using these details, or login to https://console.neo4j.io to validate the Aura Instance is available
   NEO4J_URI=neo4j+s://a3d3e8c5.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=...
   AURA_INSTANCEID=...
   AURA_INSTANCENAME=Instance01
   ```
5. **Démarrer l'interface Streamlit**
   Lancez l'interface utilisateur Streamlit avec la commande:
   ```bash
   streamlit run app.py
   ```

## Description sommaires des fichiers

- **Préparation des données**
  - `filter.py` : Filtre un fichier JSONL pour ne garder que les produits du Canada.
- **Exploration des données**
  - `analyse.py` : Analyser la structure des données JSON pour identifier les champs pertinents.
- **Création de la base de données vectorielle**
  - `create_graph.py` : Crée un graphe Neo4j à partir des données JSONL. Ce script créé le fichier `openfoodfacts_loader.log`.
  - `query.py` : Code pour interroger le graphe Neo4j avec des requêtes Cypher.
- **Construction de l'agent conversationnel**
  - `agent_*.py` : L'agent principal qui gère les interactions avec Neo4j et traite les requêtes en langage naturel.
  - `intent_handler.py` et `llm_intent_handler.py` : Gestionnaires d'intentions pour l'agent principal, utilisés par `agent_*.py`.
- **Interface utilisateur**
  - `app.py` : Point d'entrée alternatif basé sur Streamlit pour lancer une interface web permettant d'interagir avec l'agent. L'interface permet d’entrer nos questions en anglais ou en français et d’obtenir les résultats en temps réel.
- **Documentation**
  - `README.md`et `notes.md` : Fichiers de documentation

## Fichier filter.py

Ce script filtre les produits d'un fichier JSONL pour ne garder que les 97&nbsp;439&nbsp;produits canadiens.

## Fichier create_graph.py

Allez à la [console Neo4j](https://console.neo4j.io) et cliquez sur **Create instance**. Sélectionnez **AuraDB Free**.
Éventuellement, je pourrais utiliser la version **Pro** mais gratuite 14 jours.

Attendez que l'instance soit prête (indiqué RUNNING en vert).

Ensuite, exécutez le script `create_graph.py` pour créer un graphe Neo4j à partir des données JSONL.

Ce script crée les noeuds et les relations dans la base de données Neo4j. 

Ce script crée également les relations parents–enfants dans le graphe des noeuds qui font l'objet d'une taxonomie documentée. Par exemple, dans 
`create_category_nodes()`, après avoir créé tous les nœuds de catégories, le code itére sur le fichier de taxonomie `categories.txt` 
et exécuter des requêtes Cypher pour ajouter des relations entre chaque parent et chacun de ses enfants. 
Les fichiers de taxonomie sont disponibles [ici](https://github.com/openfoodfacts/openfoodfacts-server/tree/main/taxonomies).

Voici les points importants à noter dans la sortie :

1. **Chargement initial** : Le script a correctement chargé 1000 produits sur les 97439 disponibles (échantillon limité pour le test).

2. **Création des nœuds et relations de base** :
   - 1000 produits avec leurs embeddings
   - 1040 relations HAS_BRAND
   - 4363 relations HAS_CATEGORY
   - 16471 relations CONTAINS pour les ingrédients
   - 1717 relations HAS_LABEL
   - 1522 relations CONTAINS_ADDITIF
   - 970 relations CONTAINS_ALLERGEN
   - 1486 relations SOLD_IN pour les pays
   - 6778 relations HAS_NUTRIMENT

3. **Intégration des taxonomies hiérarchiques** :
   - Taxonomie des catégories : 10099 relations HAS_CHILD créées, 8214 nœuds enrichis avec des traductions
   - Taxonomie des ingrédients : 4516 relations CONTAINS créées, 4019 nœuds enrichis
   - Taxonomie des additifs : 115 relations PART_OF créées, 115 nœuds enrichis
   - Taxonomie des labels : 2078 relations INCLUDES créées, 2037 nœuds enrichis

4. **Recherche sémantique** :
   - Le test de recherche pour "Produit sans gluten riche en protéines" a retourné 5 résultats, montrant que l'index vectoriel fonctionne.


Cette structure de graphe enrichie permettra désormais des requêtes sophistiquées, exploitant à la fois :
- Les relations entre produits et leurs attributs (ingrédients, marques, etc.)
- Les relations hiérarchiques au sein de chaque taxonomie
- Les synonymes et traductions en français et en anglais

Nous avons maintenant une base solide pour développer des applications qui peuvent répondre à des requêtes en langage naturel sur les produits alimentaires, tenant compte des relations sémantiques et hiérarchiques.

## Fichier query.py





## Fichier agent.py

Le fichier `agent.py` est un composant central du système qui fournit une interface entre les utilisateurs et la base de données Neo4j contenant les données d'Open Food Facts.

La classe `OpenFoodFactsAgent` implémente plusieurs fonctionnalités clés :

- **Initialisation et connexion à Neo4j**
  - Utilise LangChain pour se connecter à la base de données Neo4j
  - Configure un modèle de génération de requêtes Cypher
  - Initialise un modèle de langage (GPT-3.5-turbo) pour comprendre les requêtes
- **Prompt de génération Cypher**
  - Un template détaillé pour guider le LLM à générer des requêtes Cypher correctes
  - Comprend des instructions, des exemples et le schéma de la base de données
  - Les exemples couvrent divers cas d'usage : recherche par marque, ingrédients, allergènes, etc.
- **Fonctions utilitaires**
  - `refresh_schema()` : Met à jour le schéma de la base de données
  - `get_schema()` : Récupère le schéma actuel
  - `execute_custom_cypher()` : Exécute des requêtes Cypher personnalisées
- **Fonctions spécialisées**
  - `get_product_recommendations()` : Recommande des produits similaires ou plus sains
  - `get_nutritional_analysis()` : Analyse nutritionnelle d'un produit
  - `get_dietary_info()` : Information sur les produits adaptés à un régime spécifique
- **Traitement des requêtes**
  - `query()` : Point d'entrée principal qui utilise un gestionnaire d'intentions

### Problèmes connus

- Problème de regroupement sémantique observé précédemment pourrait affecter la qualité des résultats. Par exemple, chercher des produits contenant du "sel" pourrait ne pas trouver ceux avec "salt" si le regroupement n'est pas optimal.
- Je n'aime pas la façon dont est déterminé les intentions avec `IntentHandler`. Je souhaite que le LLM le détermine lui-même.



