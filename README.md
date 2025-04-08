# Agent conversationnel pour l'interrogation de la base de données Open Food Facts

Un agent conversationnel intelligent permettant l'interrogation en langage naturel de la base de données alimentaire Open Food Facts. Développé dans le cadre du cours IFT-6005 - Projet intégrateur à l'Université Laval.

## Présentation du projet

L'objectif de ce projet est de faciliter l'accès aux informations nutritionnelles en permettant aux utilisateurs d'interroger la base de données Open Food Facts via des questions en langage naturel (français ou anglais). L'agent utilise des grands modèles de langage pour convertir ces questions en requêtes SQL ou en parcours de graphe.

Le projet s'articule autour de trois approches complémentaires :
1. **Interrogation par DuckDB** - Un agent qui transforme les questions en requêtes SQL
2. **Graphe de connaissances avec NetworkX** - Un agent qui exploite un graphe de produits alimentaires
3. **Analyse comparative** - Une évaluation rigoureuse des performances des deux approches

## Fonctionnalités

- ✅ Interrogation par SQL de la base Open Food Facts (via DuckDB)
- ✅ Recherche sémantique des colonnes pertinentes (FAISS)
- ✅ Conversion automatique des questions en requêtes SQL (Text-to-SQL)
- ✅ Interrogation d'un graphe de connaissances (NetworkX)
- ✅ Recherche vectorielle par similarité sémantique
- ✅ Source d'information complémentaire (Guide alimentaire canadien)
- ✅ Support multilingue (français et anglais)
- ✅ Framework d'évaluation comparative

## Architecture du système

L'architecture modulaire du système comprend les composants suivants :

- **Module de dialogue** : Gère les conversations avec l'utilisateur en utilisant un LLM
- **Convertisseur texte-SQL** : Transforme les questions en requêtes SQL adaptées
- **Connecteur de base de données** : Communique avec DuckDB pour exécuter les requêtes
- **Graphe de connaissances** : Représente les produits et leurs relations dans NetworkX
- **Recherche sémantique** : Exploite des embeddings vectoriels pour la recherche avancée
- **Recherche sur le Web** : Consulte le Guide alimentaire canadien quand les informations manquent
- **Générateur de réponses** : Transforme les résultats en réponses naturelles et précises

## Structure du projet

```
ift-6005/
├── data/                   # Données utilisées dans le projet
│   ├── cache/              # Cache pour les embeddings et index FAISS
│   ├── graphs/             # Graphes NetworkX sérialisés
│   ├── taxonomies/         # Taxonomies Open Food Facts
│   ├── columns_documentation.json   # Documentation des colonnes
│   ├── food.parquet        # Base de données source (format Parquet)
│   ├── food_canada.duckdb  # Base de données DuckDB (produits canadiens)
│   └── qa_pairs.json       # Paires question-réponse pour évaluation
├── docs/                   # Documentation du projet
│   ├── latex/              # Rapports LaTeX
│   └── markdown/           # Documentation technique
├── src/                    # Code source
│   ├── duckdb/             # Agent basé sur DuckDB
│   │   ├── chatbot_19.py   # Agent conversationnel principal
│   │   ├── data.py         # Préparation des données
│   │   ├── docoff.py       # Génération de documentation
│   │   ├── evaluate_04.py  # Framework d'évaluation
│   │   └── question_answer.py # Génération de paires Q&A
│   ├── neo4j/              # Tentative avec Neo4j
│   │   ├── create_graph.py # Création du graphe
│   │   └── agent.py        # Agent d'interrogation
│   └── networkx/           # Agent basé sur NetworkX
│       ├── create_nx_graph.py  # Création du graphe NetworkX
│       └── evaluate_nx.py      # Évaluation comparative
└── README.md
```

## Technologies utilisées

- **DuckDB** : Base de données analytique rapide et légère
- **NetworkX** : Bibliothèque Python pour la création et manipulation de graphes
- **FAISS** : Bibliothèque pour la recherche vectorielle efficace
- **SentenceTransformer** : Génération d'embeddings pour la recherche sémantique
- **Smolagents** : Framework pour la création d'agents conversationnels
- **Claude 3.5/3.7 Sonnet** : Modèle de langage principal pour les agents
- **Llama 3.1, Qwen 2.5** : Modèles de langage alternatifs pour les tests locaux

## Installation

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

Configuration des variables d'environnement dans un fichier `.env` :

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Préparation des données

1. Télécharger le fichier Parquet d'Open Food Facts :
   ```bash
   wget -P data/ https://huggingface.co/datasets/openfoodfacts/product-database/resolve/main/food.parquet
   ```

2. Créer la base de données DuckDB :
   ```bash
   python src/duckdb/data.py
   ```

3. Générer la documentation des colonnes :
   ```bash
   python src/duckdb/docoff.py
   ```

4. Créer le graphe NetworkX :
   ```bash
   python src/networkx/create_nx_graph.py
   ```

## Utilisation

### Agent DuckDB

```python
from src.duckdb.chatbot_19 import run

# Poser une question à l'agent
run("Quels sont les produits sans gluten qui ont un bon score nutritionnel?")
```

### Évaluation comparative

```bash
# Évaluer les performances des agents (français)
python src/networkx/evaluate_nx.py --lang fr --limit 20 --model claude

# Évaluer les performances des agents (anglais)
python src/networkx/evaluate_nx.py --lang en --limit 20 --model openchat
```

## Résultats des évaluations

L'évaluation comparative des deux approches (DuckDB vs NetworkX) a montré :

| Métrique | DuckDB | NetworkX | Différence |
|----------|--------|----------|------------|
| Taux de réussite (%) | 43.00 | 17.00 | 26.00 |
| Taux d'échec (%) | 21.00 | 48.00 | 27.00 |
| Temps moyen (s) | 26.37 | 26.69 | 0.32 |
| Score combiné moyen | 0.34 | 0.19 | 0.15 |

L'approche DuckDB s'est montrée significativement plus performante, avec un taux de réussite supérieur et un taux d'échec inférieur à l'approche NetworkX.

## Exemples de requêtes

```
Quels sont les produits sans additifs disponibles dans la base de données?
Quels produits ont le meilleur Nutri-Score?
Combien de produits contiennent du sucre comme ingrédient?
Quels sont les allergènes les plus courants dans les produits?
Y a-t-il des produits végétaliens avec un bon Nutri-Score?
```

## Limitations

- Difficulté à gérer les structures de données complexes d'Open Food Facts
- Performance limitée des modèles de langage légers pour la génération SQL
- Nécessité d'une documentation précise des colonnes
- Approche NetworkX moins performante que prévue

## Contributeurs

- Alain Boisvert (@boisalai)

## Licence

MIT License - Voir le fichier LICENSE pour plus de détails.