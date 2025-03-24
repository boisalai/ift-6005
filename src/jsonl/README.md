# Répertoire SRC/JSONL

## Vue d'ensemble

Ce système permet aux utilisateurs d'interroger en langage naturel une base de données Neo4j contenant des informations sur des produits alimentaires provenant d'OpenFoodFacts. Le système est composé de trois modules principaux:

TODO: À compléter.

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
  - `extract.py` : Extrait les n premiers produits d'un fichier JSONL et les écrire dans un nouveau fichier.
- **Exploration des données**
  - `taxonomy.py` : Explore la taxonomie des catégories de produits. 
  - `analyse.py` : Analyser la structure des données JSON pour identifier les champs pertinents.
- **Création de la base de données vectorielle**
  - `create_graph_*.py` : Crée un graphe Neo4j à partir des données JSONL. Ce script créé le fichier `openfoodfacts_loader.log`.
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

## Fichier extract.py

Ce script extrait les n premiers produits canadiens et les écrit dans un nouveau fichier nommé `data/openfoodfacts-canadian-products-first-n.jsonl`. 
Il est utile pour créer un sous-ensemble de données à partir d'un fichier JSONL plus grand, facilitant ainsi le traitement et l'analyse.

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



