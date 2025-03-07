# Documentation de l'Agent Conversationnel OpenFoodFacts

## Vue d'ensemble

Ce système permet aux utilisateurs d'interroger en langage naturel une base de données Neo4j contenant des informations sur des produits alimentaires provenant d'OpenFoodFacts. Le système est composé de trois modules principaux:

1. **Agent OpenFoodFacts** (`food_agent.py`) - Gère les interactions avec la base de données Neo4j et traite les requêtes
2. **Gestionnaire d'intentions** (`intent_handler.py`) - Identifie le type de demande et l'entité concernée
3. **Interface utilisateur** (`app.py`) - Interface conversationnelle en Streamlit

## Architecture du système

```
                 ┌───────────────────┐
                 │                   │
                 │    Interface      │
                 │    Streamlit      │
                 │                   │
                 └─────────┬─────────┘
                           │
                           ▼
┌────────────────────────────────────────────┐
│                                            │
│            Agent OpenFoodFacts             │
│                                            │
│  ┌───────────────┐       ┌──────────────┐  │
│  │ GraphCypherQA │       │  Gestionnaire │  │
│  │    Chain      │◄─────►│  d'intentions │  │
│  └───────────────┘       └──────────────┘  │
│                                            │
└────────────────────┬───────────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │             │
              │   Neo4j     │
              │ OpenFoodFacts│
              │             │
              └─────────────┘
```

## Installation et configuration

### Prérequis

- Python 3.8+
- Neo4j Database
- OpenAI API key (pour LangChain)

### Variables d'environnement

Créez un fichier `.env` avec les variables suivantes:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
OPENAI_API_KEY=votre_clé_api
```

### Installation des dépendances

```bash
pip install neo4j langchain openai streamlit pandas python-dotenv
```

### Démarrage

Lancez l'interface utilisateur Streamlit avec la commande:

```bash
streamlit run app.py
```

## Composants du système

### 1. Agent OpenFoodFacts

L'agent principal qui gère les interactions avec Neo4j et traite les requêtes en langage naturel.

**Fonctionnalités principales:**
- Connexion à la base de données Neo4j
- Conversion des questions en requêtes Cypher
- Gestion des erreurs et des cas spéciaux
- Fonctions spécialisées (recherche de produits, analyse nutritionnelle, etc.)

### 2. Gestionnaire d'intentions

Analyse les requêtes en langage naturel pour identifier leur intention et extraire les entités pertinentes.

**Types d'intentions reconnus:**
- Information sur un produit
- Recherche par marque
- Recherche par ingrédient
- Vérification d'allergènes
- Information nutritionnelle
- Recommandations de produits
- Requêtes sur les régimes alimentaires
- Comparaison de produits

### 3. Interface utilisateur Streamlit

Interface conversationnelle permettant aux utilisateurs d'interagir avec l'agent.

**Fonctionnalités:**
- Chat interactif
- Onglets pour des fonctions spécialisées
- Affichage de données tabulaires
- Statistiques de la base de données

## Exemples d'utilisation

### Requêtes générales
- "Quels sont les produits de la marque Kroger?"
- "Quels produits contiennent du sucre?"
- "Montre-moi des produits sans gluten"

### Requêtes nutritionnelles
- "Quelle est la teneur en calories du lait 1%?"
- "Quelles sont les informations nutritionnelles du sirop d'érable?"

### Requêtes sur les régimes alimentaires
- "Je suis végétalien, quels produits puis-je manger?"
- "Montre-moi des produits biologiques"

### Requêtes comparatives
- "Compare le lait 1% et le sirop d'érable"
- "Lequel est plus sain entre le sirop d'érable et le sirop d'imitation vanille?"

## Extension du système

### Ajout de nouvelles intentions
Pour ajouter de nouveaux types d'intentions, modifiez `intent_handler.py`:
1. Ajoutez un nouveau type dans `IntentType`
2. Créez des patterns RegEx pour détecter cette intention
3. Implémentez le traitement dans `handle_intent()`

### Amélioration des requêtes Cypher
Pour affiner les requêtes Cypher, modifiez les exemples dans:
- Le template `cypher_generation_template` dans `food_agent.py`
- Les requêtes prédéfinies dans `handle_intent()` de `intent_handler.py`

### Extension de l'interface utilisateur
Pour ajouter de nouvelles fonctionnalités à l'interface:
1. Créez de nouveaux onglets dans l'application Streamlit
2. Implémentez les fonctions correspondantes dans l'agent
3. Reliez l'interface aux nouvelles fonctionnalités

## Limitations actuelles et améliorations futures

### Limitations:
- Compréhension limitée des synonymes et variantes linguistiques
- Pas de gestion des conversations multi-tours complexes
- Performances limitées sur des grands volumes de données

### Améliorations potentielles:
- Intégration d'un modèle d'embeddings pour la recherche sémantique
- Implémentation d'un système de suivi de contexte pour les conversations
- Enrichissement de la base de connaissances avec d'autres sources
- Optimisation des requêtes Cypher pour de meilleures performances
- Ajout de visualisations (graphiques nutritionnels, comparaisons visuelles)