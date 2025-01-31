# Document de travail

Document de travail pour le projet intégrateur du cours IFT-6005.
À la fin de ce projet, je devrais réécrire le texte de façon structurée.

## Description du projet 

Le projet consiste à créer un agent conversationnel pour interroger la base de données Open Food Facts.

- Création d'une interface conversationnelle pour interroger la base de données OpenFoodFacts
- Permettrait aux utilisateurs de poser des questions en langage naturel sur les produits alimentaires
- Les requêtes peuvent être écrites en anglais ou en français ou tout autre langue.
  - Les types de questions peuvent être variés, par exemple:
  - Quels sont les produits qui contiennent du sucre?
  - Quels produits comparables à celui-ci (disons Nutella) sont moins sucrés?
  - Quels sont les meilleurs produits pour une certaine catégorie de produits (ex. les meilleures céréales pour le petit déjeuner)?
  - Comparer les produits de deux marques différentes.
- Pour compléter la réponse, ou si la réponse n'est pas disponible dans la base de données Open Food Facts,
  le système pourrait interroger d'autres sources comme le Guide alimentaire canadien qui est disponible sous la forme d'un site Web (https://guide-alimentaire.canada.ca/fr/)
- Deux approches possibles discutées :
  - Connexion directe à la BD avec un agent LLM qui génère des requêtes
  - Entraînement d'un modèle sur les données existantes
- Pour ce projet, j'envisage :
  - un système de type Agents RAG utilisant ollama et un ou plusieurs LLMs (dont mistral:7b).
  - un agent LLM générerait des requêtes à partir des questions posées par l'utilisateur.
  - d'utiliser [smolagents](https://huggingface.co/docs/smolagents/index) de HuggingFace.
- Le livrable au professeur prendrait la forme d'un dépôt github et d'un document pédagogique qui explique les différents types d'agents, comment le système a été construit et comment il fonctionne.
- On débuterait avec un cas simple et on ajouterait des fonctionnalités au fur et à mesure.
- On doit aussi pouvoir évaluer la qualité des réponses fournies par le système.

Je prévois développer ce projet sur mon ordinateur personnel, un MacBook Pro M1 avec 16 Go de RAM.

## Tâches à faire selon le plan 

### Préparation et configuration (30h)

#### Mise en place de l’environnement de développement (5h)

Dans le terminal, créez et accédez au répertoire où vous voulez placer le projet.

```bash
mkdir ~/Projects  # si ce n'est pas déjà fait
cd ~/Projects
```

Clonez le dépôt GitHub.

```bash
git clone git@github.com:boisalai/ift-6005.git
cd ift-6005
```

Créez un environnement virtuel Python et installer les dépendances.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Les librairies utilisées sont les suivantes :

- `ollama` pour l'agent conversationnel
- `sqlglot[rs]` pour la conversion texte-SQL


Voici la structure du projet :

```
votre-repo/
├── LICENSE
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   └── agents/
├── tests/
├── data/
├── docs/
│   ├── latex/
│   └── markdown/
└── notebooks/
```

Pour la documentation Markdown :

```
docs/markdown/
├── README.md              # Vue d'ensemble
├── installation.md        # Guide d'installation
├── architecture.md        # Architecture du système
├── agents/               
│   ├── main_agent.md     # Agent principal
│   ├── query_agent.md    # Agent de requêtes
│   ├── enrichment_agent.md # Agent d'enrichissement
│   └── viz_agent.md      # Agent de visualisation
└── database/
    ├── schema.md         # Structure de la base de données
    └── queries.md        # Exemples de requêtes
```

Pour la documentation LaTeX :

```
docs/latex/
├── main.tex              # Document principal
├── chapters/
│   ├── introduction.tex
│   ├── architecture.tex
│   ├── implementation.tex
│   ├── evaluation.tex
│   └── conclusion.tex
├── images/               # Figures et diagrammes
├── appendices/           # Code source, exemples
└── bibliography.bib      # Références
```

##### Qualité du code

Pour maintenir la qualité du code Python selon les standards, voici les outils essentiels :

1. **Linters et formatters principaux** :
```bash
# Installation
pip install black flake8 pylint pre-commit

# Configuration pre-commit
pre-commit install
```

2. Créer un fichier `.pre-commit-config.yaml` à la racine :
```yaml
repos:
-   repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
    -   id: black
-   repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
    -   id: flake8
-   repo: https://github.com/pycqa/pylint
    rev: v3.0.3
    hooks:
    -   id: pylint
```

3. Créer un fichier `setup.cfg` pour la configuration :
```ini
[flake8]
max-line-length = 88
extend-ignore = E203

[pylint]
max-line-length = 88
disable = C0111
```

Ces hooks s'exécuteront automatiquement lors de chaque commit, vérifiant le formatage (black), le style (flake8) et la qualité du code (pylint).

Pour ignorer temporairement les validations pre-commit, utilisez :

```bash
git commit -m "message" --no-verify
```

Ou l'option courte :
```bash
git commit -m "message" -n
```


#### Préparation de la base de données Open Food Facts canadienne (5h)

[Open Food Facts](https://en.openfoodfacts.org/) is a non-profit organisation that collects and shares information on food products from around the world. It is a collaborative project that relies on volunteers to collect data. Open Food Facts is the largest open food products database in the world, with over 3 million products in 200 countries.

Pour plus d'information sur Open Food Facts, voir :

- [Site français Open Food Facts](https://fr.openfoodfacts.org/)
  - [Site canadien](https://ca-fr.openfoodfacts.org/)
- [Site](https://world.openfoodfacts.org/)
  - [Data](https://world.openfoodfacts.org/data)
  - [data-fields.txt](https://static.openfoodfacts.org/data/data-fields.txt)
  - [contribute](https://world.openfoodfacts.org/contribute)
- [Blog](https://blog.openfoodfacts.org/fr/)
- [GitHub Python](https://github.com/openfoodfacts/openfoodfacts-python)
- [Open Issues Canada](https://github.com/openfoodfacts/openfoodfacts-server/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22%F0%9F%87%A8%F0%9F%87%A6%20Canada%22%20)
- [Youtube Open Food Facts](https://www.youtube.com/@openfoodfacts1170)
- [Importer OpenFoodFacts dans PostgreSQL](https://blog-postgresql.verite.pro/2018/12/21/import-openfoodfacts.html)
- [Kaggle](https://www.kaggle.com/datasets/openfoodfacts/world-food-facts)
- [HuggingFace](https://huggingface.co/openfoodfacts)
- [FOSDEM 2024: The State of Open Food Facts](https://www.youtube.com/watch?v=uTfHJ9njbv0). Voir à 15h34 pour les liens.

J'ai téléchargé le fichier d'Open Food Facts depuis Hugging Face directement dans le dossier `data/` du projet.

```bash
brew install wget  # si vous n'avez pas wget
wget -P data/ https://huggingface.co/datasets/openfoodfacts/product-database/resolve/main/food.parquet
```

Le fichier `food.parquet` contient les données de Open Food Facts au format Parquet. Ce fichier pèse 5.5 Go.

```bash
$ ls -lh data/food.parquet | awk '{print $5}'
5.5G
```


Nous pourrions normalement lire les données en utilisant la librairie `pandas` comme ceci.

```python
import pandas as pd
df = pd.read_parquet('food.parquet')
df.describe()
```

Cependant, le code précédent entraîne une erreur de mémoire insuffisante sur mon ordinateur personnel (un MaxcBook Pro M1 16 Go RAM). Nous devons donc utiliser une autre approche.

DuckDB offre plusieurs avantages majeurs par rapport à Pandas pour la manipulation de fichiers volumineux. Son traitement "out-of-core" permet d'analyser des fichiers plus grands que la RAM disponible, contrairement à Pandas qui doit charger l'intégralité des données en mémoire. 

De plus, DuckDB permet l'exécution vectorisée et la parallélisation automatique, ce qui offre des performances nettement supérieures, avec des requêtes jusqu'à 100 fois plus rapides que Pandas pour les agrégations. Sa syntaxe SQL native facilite également l'analyse des fichiers Parquet avec des requêtes ciblées.

Un autre avantage clé est l'accès partiel aux données : DuckDB ne lit que les colonnes nécessaires à la requête, optimisant ainsi l'utilisation des ressources. L'intégration transparente avec Pandas permet de basculer facilement entre les deux outils selon les besoins spécifiques.

Pandas reste toutefois préférable pour les manipulations fines nécessitant des opérations personnalisées sur les lignes, le prototypage rapide et l'intégration directe avec l'écosystème de visualisation et d'apprentissage automatique. La solution optimale consiste souvent à combiner les deux approches : utiliser DuckDB pour le prétraitement des données volumineuses, puis convertir le résultat en DataFrame Pandas pour les analyses détaillées.

Donc, voici comment lire le fichier Parquet avec DuckDB.

```python
import duckdb

DATA_PATH = "../data/food.parquet"

# Pour afficher les 5 premières lignes
with duckdb.connect() as con:
    query = f"SELECT * FROM '{DATA_PATH}' LIMIT 5"
    result = con.execute(query).fetchall()
    print(result)
```

Le script `data_01.py` lit le fichier parquet et crée une table DuckDB contenant l'ensemble des données 
et une table DuckDB contenant que les produits alimentaires canadiens.

Voir aussi :

- [Parquet Data Export on Hugging Face](https://world.openfoodfacts.org/data).
- [Parquet file hosted on Hugging Face (beta)](https://wiki.openfoodfacts.org/Reusing_Open_Food_Facts_Data#Parquet_file_hosted_on_Hugging_Face_.28beta.29)
- [Data field](https://wiki.openfoodfacts.org/Data_fields)
- [DuckDB Cheatsheet](https://wiki.openfoodfacts.org/DuckDB_Cheatsheet)
- [DuckDB](https://duckdb.org/)
- [GitHub](https://github.com/duckdb/duckdb)
- [awesome-duckdb](https://github.com/davidgasquez/awesome-duckdb)
- [DuckDB: Crunching Data Anywhere, From Laptops to Servers • Gabor Szarnyas • GOTO 2024](https://www.youtube.com/watch?v=9Rdwh0rNaf0)
- [Books](https://learning.oreilly.com/search/?q=duckdb&rows=100&language=en)
- [DuckDB](https://blog.openfoodfacts.org/en/news/food-transparency-in-the-palm-of-your-hand-explore-the-largest-open-food-database-using-duckdb-%f0%9f%a6%86x%f0%9f%8d%8a)
- [Explore the Largest Open Food Database using DuckDB](https://blog.openfoodfacts.org/en/news/food-transparency-in-the-palm-of-your-hand-explore-the-largest-open-food-database-using-duckdb-%f0%9f%a6%86x%f0%9f%8d%8a)

#### Créer un dictionnaire des données Open Food Facts en format JSON (2h)

Le modèle de langage (LLM) devra comprendre la structure de la base de données Open Food Facts pour générer des requêtes SQL pertinentes. 
Or, après plusieurs recherches, j'ai constaté qu'il n'existait pas de dictionnaire de données officiel et facilement accessible. 
Pour résoudre ce problème, j'ai entrepris de créer mon propre dictionnaire de données en format JSON.

Ma démarche s'est appuyée sur quatres sources principales d'information. Tout d'abord, j'ai utilisé un fichier 
texte disponible sur le site d'Open Food Facts (https://static.openfoodfacts.org/data/data-fields.txt), qui fournit 
des descriptions basiques des champs. Ensuite, j'ai exploité une page wiki d'Open Food 
Facts (https://wiki.openfoodfacts.org/Data_fields) qui explique en détail les différents champs de données.
Puis, une autre page wiki (https://wiki.openfoodfacts.org/DuckDB_Cheatsheet) présente le schéma Parquet. 
Enfin, j'ai analysé directement la structure de ma base de données DuckDB pour obtenir des informations 
techniques et statistiques sur chacune des colonnes de la base de données.

Pour combiner ces sources d'information, j'ai développé un script Python (`dictionary.py`) qui génère automatiquement
un dictionnaire de données au format JSON (`data_dictionary.json`). Ce script analyse chaque champ de la base de données et 
rassemble des informations essentielles : le nom du champ, sa description, son type de données, le pourcentage 
de données manquantes, et des exemples concrets de valeurs. Pour les champs contenant des données complexes 
comme des objets JSON (par exemple, les champs `ecoscore_data` et `image`), j'ai mis en place un système 
qui simplifie l'affichage des exemples tout en conservant leur structure.

Ensuite, j'ai ajusté manuellement la description de chacun des champs et 
j'ai ajouté des termes comparables dans différentes langues

Pour chaque champ de la base de données, le dictionnaire fournit les informations suivantes :

- `description` : une description textuelle du champ
- `terms`: les termes associés au champ dans différentes langues
- `type` : le type de données (STRING, INTEGER, etc.)
- `is_nullable` : indique si le champ peut contenir des valeurs nulles
- `unique_values_count` : nombre de valeurs uniques distinctes
- `completeness_score` : pourcentage de valeurs non nulles
- `known_issues` : problèmes identifiés dans les données
- `examples` : échantillon de valeurs représentatives

Voici un exemple pour le champ "categories" :

```json
"categories_tags": {
  "description": "Description of categories_tags",
  "type": "VARCHAR[]",
  "format": "",
  "is_nullable": true,
  "unique_values_count": 5829,
  "completeness_score": 24.1,
  "known_issues": [
    "High percentage of null values: 75.9%"
  ],
  "examples": [
    "[en:sweeteners, en:syrups, en:simple-syrups, en:maple-syrups]",
    "[]",
    "[en:plant-based-foods-and-beverages, en:plant-based-foods, en:cereals-and-potatoes, en:spreads, e...",
    "[en:sweeteners, en:syrups, en:simple-syrups, en:agave-syrups]",
    "[en:snacks, en:sweet-snacks, en:biscuits-and-cakes, en:cakes, en:chocolate-cakes]"
  ]
}
```

Cette approche permet d'avoir une vision plus claire et complète de la structure des 
données d'Open Food Facts, qui facilitera ainsi l'interaction entre le modèle de langage et la base de données.

<!--
Ce fichier est très volumineux et contient des informations sur les catégories.
Que faire avec cela...
https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/refs/heads/main/taxonomies/food/categories.txt



-->

#### Créer un jeu de test de 100 questions de référence (10h)

Le benchmark BIRD (Big Bench for Large-Scale Database Grounded Text-to-SQLs) est conçu pour évaluer
les modèles de langage dans la tâche de conversion du langage naturel en requêtes SQL sur de grandes
bases de données issues de divers domaines professionnels. Il comprend plus de 12 751 paires
question-SQL uniques et 95 bases de données totalisant 33,4 Go, couvrant plus de 37 domaines
professionnels tels que la blockchain, le hockey, la santé et l'éducation.

Les questions du benchmark BIRD sont formulées en langage naturel et sont accompagnées de requêtes
SQL correspondantes. Les bases de données associées contiennent des données volumineuses et
parfois "bruyantes", reflétant des scénarios réels où les données peuvent être incomplètes ou mal
formatées. Cela oblige les modèles à comprendre et à traiter ces valeurs de base de données pour
générer des requêtes SQL précises.

Pour créer un ensemble de 100 questions-réponses similaire à BIRD, il faut formuler des
questions en langage naturel couvrant divers domaines professionnels et fournir les requêtes 
SQL correspondantes. Assurez-vous que les bases de données associées contiennent des données
réalistes, y compris des valeurs manquantes ou mal formatées, pour simuler des scénarios du
monde réel. Cela permettra d'évaluer la capacité des modèles à comprendre et à interroger
efficacement des bases de données complexes et imparfaites.




Voici des requêtes possibles que l'interface pourrait gérer :

- "Show me ready made meals that are NutriScore A sold at Aldi"
- "Show me the repartition of NutriScore for Nestlé in Europe"
- "Make me a graph of all breakfast cereals with NOVA groups, nutrition value and Nutri-Score"

See also :

- [BIRD-SQL](https://bird-bench.github.io/)
- [Bird-SQL: A Benchmark for Text-to-SQL](https://arxiv.org/abs/2202.10700)

#### Implémentation des scripts d’évaluation des trois métriques (10h)

### Développement du système de base (75h)

#### Implémentation du module de dialogue avec Qwen2-7B-Instruct (20h)

Pour débuter, j'utilise `mistral:7b` avec `Ollama`. 
Pour la liste des paramètres possibles, voir [Ollama Model File](https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values).


```bash
brew install ollama
```

Ensuite, vous devrez aussi télécharger le modèle mistral-7b :

```bash
ollama pull mistral:7b
```

Pour vérifier si Ollama est démarré sur Linux/Mac :

```bash
ps aux | grep ollama
```

Sur Windows, vérifiez dans le Task Manager ou exécutez :

```powershell
Get-Process | Where-Object {$_.Name -like "*ollama*"}
```

Vous pouvez aussi tester la connexion directement avec curl :

```bash
curl http://localhost:11434/api/tags
```

Si Ollama n'est pas démarré, lancez-le avec :

```bash
ollama serve
```

Pour arrêter le serveur Ollama, faire ceci sur Linux/Mac :

```bash
sudo pkill -9 ollama Ollama
```

J'utilise le modèle `mistral:7b` (ou `qwen2-7b-instruct` à vérifier) pour ses capacités natives d’appel de fonctions.
À ce sujet, voir [Function calling](https://docs.mistral.ai/capabilities/function_calling/)


Pour plus d'information sur Ollama, voir :

- [Running LLMs Locally using Ollama](https://ai.gopubby.com/running-llms-locally-using-ollama-f17197f60450)
- [Même article sur Archive.is](https://archive.is/https://ai.gopubby.com/running-llms-locally-using-ollama-f17197f60450)
- https://lmstudio.ai/docs/advanced/tool-use

Pour plus d'information sur les LLM, voir :

- [Tool Usage with Qwen](https://github.com/QwenLM/Qwen/blob/main/README.md#tool-usage)



#### Développement de la conversion texte-SQL de base (25h)

Le script implémente les principaux composants du modèle TAG, mais avec quelques différences et limitations. Voici l'analyse :

Points alignés avec TAG :

1. Structure en 3 étapes :
- `syn`: Méthode TAGSystem.syn() convertit la requête en SQL
- `exec`: Méthode TAGSystem.exec() exécute la requête sur la base
- `gen`: Méthode TAGSystem.gen() génère la réponse en langage naturel

2. Utilisation de LLMs via une interface abstraite `BaseLLM` supportant différents modèles (Ollama, OpenAI, Anthropic)

3. Gestion du contexte conversationnel via `conversation_history`

Différences/limitations :

1. Moins flexible que le TAG décrit dans l'article :
- Limité aux requêtes SQL uniquement
- Pas de support pour les opérateurs sémantiques complexes
- Pas d'implémentation des patterns LLM itératifs/récursifs

2. Pas d'optimisation des performances comme suggéré dans l'article pour le traitement de grands volumes de données

3. Architecture plus simple que celle proposée dans l'article pour les cas d'utilisation avancés (raisonnement sémantique, connaissance du monde)

Le script fournit une implémentation fonctionnelle mais simplifiée du modèle TAG, adaptée principalement aux requêtes SQL basiques plutôt qu'à l'ensemble des capacités décrites dans l'article.

Pour plus d'information, voir :

- [IA SQL](https://medium.com/@clicbiz/list/ia-sql-73e98bba4daf)
- [SQL Query Engine with LlamaIndex + DuckDB](https://docs.llamaindex.ai/en/stable/examples/index_structs/struct_indices/duckdb_sql_query/)
- [Awesome-Text2SQL](https://github.com/eosphoros-ai/Awesome-Text2SQL)
- [Table-Augmented Generation (TAG): A Unified Approach for Enhancing Natural Language Querying over Databases](https://www.marktechpost.com/2024/08/29/table-augmented-generation-tag-a-unified-approach-for-enhancing-natural-language-querying-over-databases/?amp)
  - Ce texte réfère à un article académique.
  - Intéressant.
  
#### Création du connecteur de base de données DuckDB (5h)
#### Implémentation du générateur de réponses simples (25h)



### Rapport de mi-session (25h)
#### Analyse des résultats (10h)
#### Rédaction du rapport de mi-session (15h)
### Optimisations et fonctionnalités avancées (60h)
#### Amélioration de la gestion des données manquantes (15h)
#### Implémentation du one-shot et few-shot learning (20h)
#### Optimisation des prompts et des requêtes SQL (15h)

Voir aussi :

- [Doriandarko deepseek-engineer](https://github.com/Doriandarko/deepseek-engineer/tree/main) : ce projet m'intrigue et pourrait être intéressant pour la suite.
- Claude offre un outil pour améliorer les prompts, mais je crois qu'il faut acheter des crédits pour l'utiliser.

#### Sélection dynamique de LLM pour accroître la performace et réduire les coûts (10h)

#### Agents 

Selon le document "Introduction to Agents.pdf", un agent est défini comme "un programme où les sorties du LLM contrôlent le workflow". Il présente différents niveaux d'agentivité :

1. ☆☆☆ Simple processeur : Le LLM n'a pas d'impact sur le flux du programme
2. ★☆☆ Routeur : Le LLM détermine un switch if/else 
3. ★★☆ Appelant d'outils (Tool Caller) : Le LLM choisit quelles fonctions exécuter
4. ★★★ Agent multi-étapes : Le LLM contrôle l'itération et la continuation du programme
5. ★★★ Multi-agents : Un workflow agentique peut en démarrer un autre

Dans notre cas, nous avons besoin d'un agent car :
- L'entrée est en langage naturel et imprévisible
- Le LLM doit décider quelle action prendre (générer du SQL, faire une visualisation, etc.)
- Le LLM doit pouvoir accéder à des outils (DuckDB, matplotlib, etc.)
- Le workflow n'est pas linéaire et dépend de la compréhension de la requête

La structure de base d'un agent multi-étapes selon la documentation est :

```python
memory = [user_defined_task]
while llm_should_continue(memory):
    action = llm_get_next_action(memory)
    observations = execute_action(action)
    memory += [action, observations]
```

Dès qu'un LLM a besoin d'accéder à des outils externes (comme une base de données) et de prendre des décisions sur le workflow, c'est effectivement un agent.

L'approche multi-agents initialement proposée est plus appropriée car :

- Elle permet au LLM de prendre des décisions à chaque étape
- Elle sépare logiquement les différentes responsabilités
- Elle suit les patterns recommandés pour les systèmes LLM avec accès aux outils externes

L'agent principal de conversation serait un agent multi-étapes qui, selon la requête, déciderait :

- S'il faut générer une requête SQL (appel à l'agent de génération de requêtes)
- Si des informations complémentaires sont nécessaires (appel à l'agent d'enrichissement)
- Si une visualisation aiderait à mieux comprendre (appel à l'agent de visualisation)

Cette hiérarchie d'agents permet de maintenir une séparation claire des responsabilités tout en gardant la flexibilité nécessaire pour gérer des requêtes complexes et imprévisibles. Le LLM principal peut adapter le workflow selon la nature de la question et les résultats intermédiaires obtenus.

Voir le livre de Chip Huyen Ai Enginering

- Agents require the ability to remember past actions, security, handle user feedback, and adapt gracefully. In other words, it is a proper software product that happens to use/integrate a large language model with tool usage to accomplish various tasks.
- As AI engineers working at the application layer, this is our job building agents: assemble these pieces into a polished and fully realized product.


Pour plus d'information sur les agents, voir :


- [Building Effective Agents Cookbook](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents) from Anthropics
- [Introducing AgentWorkflow: A Powerful System for Building AI Agent Systems](https://www.llamaindex.ai/blog/introducing-agentworkflow-a-powerful-system-for-building-ai-agent-systems) from LlamaIndex, and 
  [here](https://docs.llamaindex.ai/en/stable/understanding/agent/multi_agents/)
- [Introduction to Agents](https://huggingface.co/docs/smolagents/conceptual_guides/intro_agents)
- [smolagents](https://huggingface.co/docs/smolagents/index)
- [Beginner's Guide to RAG Agents with Prof. Tom Yeh](https://www.youtube.com/watch?v=181Esb2Ba8w)
- [Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Building Effective Agents Cookbook](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents) and [here](https://github.com/intellectronica/building-effective-agents-with-pydantic-ai) using Pydantic
- [PhiData](https://github.com/phidatahq/phidata)
- [Multi-Agent Order Management System with MongoDB](https://huggingface.co/learn/cookbook/mongodb_smolagents_multi_micro_agents)
- LlamaIndex, [AgentWorkflow Basic Introduction](https://docs.llamaindex.ai/en/stable/examples/agent/agent_workflow_basic/)
- [Week 10](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/free_courses/Applied_LLMs_Mastery_2024/week10_research_trends.md)
- Elasticsearch?
- [What is Agentic RAG](https://weaviate.io/blog/what-is-agentic-rag)
- [Introduction to LLM Agents](https://developer.nvidia.com/blog/introduction-to-llm-agents/)
- [Agentic RAG 101 Guide](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/resources/agentic_rag_101.md) Ce site est très intéressant!!!
- [Introducing AgentWorkflow: A Powerful System for Building AI Agent Systems](https://www.llamaindex.ai/blog/introducing-agentworkflow-a-powerful-system-for-building-ai-agent-systems)
- [Agents 101 guide](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/resources/agents_101_guide.md)
- [LlamaIndex | Text-To-SQL ( LlamaIndex + DuckDB)](https://www.youtube.com/watch?v=03KFt-XSqVI) on Youtube
- [RAG, AI Agents, and Agentic RAG: An In-Depth Review and Comparative Analysis](https://www.digitalocean.com/community/conceptual-articles/rag-ai-agents-agentic-rag-comparative-analysis)
- [Applied LLMs Mastery 2024](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/free_courses/Applied_LLMs_Mastery_2024/README.MD)

#### CrewAI


- Mental framework for agent creation
  - What is the goal
  - What is the process
  - Think like a manager
  - What kind of individuals would I need to hire to get this done?
  - Which processes and tasks do I expect the individuals on my teams to do?
- Tools
  - Versatile, Fault-tolerant, Caching
  - Search the internet, Scrape a website, Connect to a database, LangChain tools
- Les agents peuvent déléguer des tâches à d'autres agents
- Les agents peuvent aussi collaborer entre eux

Voir aussi :

- [Post X](https://x.com/akshay_pachaar/status/1882111286127038926) 
- [CrewAI ](https://x.com/akshay_pachaar/status/1882406721974624278)
- [CrewAI](https://www.crewai.com/) A cutting-edge framework for orchestrating role-playing, autonomous AI agents that work together seamlessly to tackle complex tasks.
  - Le code source est hébergé sur GitHub : joaomdmoura/crewAI
  - Il existe même un cours gratuit sur [DeepLearning.AI](https://learn.deeplearning.ai/courses/multi-ai-agent-systems-with-crewai/lesson/1/introduction)
- [How to Build an Agentic RAG Recommendation Engine (Step-by-Step)](https://www.youtube.com/watch?v=2Fu_GgS-Q4s)
- DeepLearning.AI [Multi AI Agents systems with crewAI](https://learn.deeplearning.ai/courses/multi-ai-agent-systems-with-crewai)
- DeepLearning.AI [Practical Multi AI Agents and Advanced Use Cases with crewAI](https://learn.deeplearning.ai/courses/practical-multi-ai-agents-and-advanced-use-cases-with-crewai/lesson/1/introduction)
- [CrewAI for Local AI Agents with Ollama: A Hands-On Tutorial](https://medium.com/@indradumnabanerjee/crewai-for-local-ai-agents-with-ollama-a-hands-on-tutorial-for-local-ai-agents-a59b6ba32fd1)

#### Guide alimentaire canadien

Il s'agit de la source d'information officielle du gouvernement du Canada sur la nutrition et la santé. Le Guide alimentaire canadien fournit des recommandations sur les aliments et les habitudes alimentaires pour une alimentation saine. Il est conçu pour aider les Canadiens à faire des choix alimentaires éclairés et à adopter des habitudes alimentaires saines.

Pour exploiter les informations du Guide alimentaire canadien, nous pourrions envisager plusieurs approches :

- [Browse-use](https://x.com/hwchase17/status/1882502767312531954)
- utilisation de [browser-use](https://github.com/browser-use/browser-use)
- utilisation de [firecrawl](https://github.com/mendableai/firecrawl) Turn entire websites into
  LLM-ready markdown or structured data. Scrape, crawl and extract with a single API.
- voir ce [post](https://x.com/akshay_pachaar/status/1883860089037369587) sur X
- [Introducing DeepSeek R1 web crawler](https://x.com/ericciarla/status/1882471683560558870)

#### Food Data Central

Le Food Data Central (FDC) est une base de données de l'USDA qui fournit des informations détaillées sur les valeurs nutritionnelles des aliments. Il contient des données sur les nutriments, les ingrédients, les portions, les marques et les étiquettes nutritionnelles des aliments. Le FDC est une ressource précieuse pour les professionnels de la santé, les chercheurs, les développeurs d'applications et le grand public.

Les données du Food Data Central sont disponibles [ici](https://fdc.nal.usda.gov/download-datasets).

#### ElasticSearch

- [ElasticsearchRetriever](https://python.langchain.com/docs/integrations/retrievers/elasticsearch_retriever/)

Je dois décrire brièvement mon projet à réaliser dans le cadre du projet intégrateur d'un cours universitaire IFT-6005.

Je dois notamment expliquer différentes approches à explorer pour interroger une base de données avec un agent conversationnel.
Les différentes approches seraient RAG classique, ou Données SQL soit par représentation textuelle ou requêtes SQI dynamique, ou encore ElasticSearch, via un LLM.

Faut expliquer les avantages et inconvénients de chaque approche.

Aussi, je veux proposer une approche incrémentale pour le développement de l'agent conversationnel.

D'abord, choisir un LLM capable de générer des requêtes SQL à partir de questions en langage naturel, et d'utiliser un outil comme DuckDB pour exécuter ces requêtes.


Ensuite utiliser ElasticSearch pour exploiter à la fois la recherche sémantique et les requêtes structurées.

Reformule tes réponses précédentes pour les rendre plus claires et plus concises, en paragraphes, sur deux pages.

- [search-a-licious](https://github.com/openfoodfacts/search-a-licious)
  - Elasticsearch est au coeur de ce projet.
  - L'équipe Search-a-licious est prête à discuter avec nous.
  - Leur prochaine étape serait d'ajouter plus de NLP dans l'outil de recherche. 
  - https://gitingest.com/openfoodfacts/search-a-licious
  - Ce projet utilise Elasticsearch, FastAPI, TypeScript, Docker et Vega pour les visualisations.
  - Je crains que la courbe d’apprentissage nécessaire pour bien maîtriser ces outils soit trop abrupte pour moi dans le cadre du cours IFT-6005. 
  - Étant donné les délais serrés et les exigences du cours, le risque de ne pas réussir à atteindre les objectifs me semble élevé.


#### Ingredients spellcheck with LLM

**Ingredient Spellcheck:** While this project has shown promising results, it is still under development. The sources mention issues with the training dataset, including limitations in size and language diversity.  There are also technical challenges related to the selection of appropriate LLMs and the need for efficient inference solutions on CPU or GPU. There's also discussion about how to best integrate the spellcheck functionality into the user interface and data processing pipeline.

- Pretraining then fine-tuning (using LoRA)
- Increase training dataset reviews to 1852
- Using DPO (Direct Preference Optimization) on reviewed examples
- Fine-tune Llama-3.1 on dataset v5.2
- Estimate the RAM necessary to run fine-tuned Mistral 7B
- inference time on CPU quantize models (int8, int4)
- assess impact on performance 
- Ajouter metadata sur jeu d’entraînement (image ID) et benchmark (barcode + image ID)

See also:

- https://towardsdatascience.com/how-did-open-food-facts-use-open-source-llms-to-enhance-ingredients-extraction-d74dfe02e0e4
- https://www.youtube.com/watch?v=jR7ATF8WS2Q&list=PLjAH-USadsF1iZsIFOhYicWLkwA2Zfj5l&index=11
- https://github.com/openfoodfacts/openfoodfacts-ai/tree/develop/spellcheck
- https://huggingface.co/openfoodfacts/spellcheck-mistral-7b
- [Use large language models (LLM) to perform ingredient list spellcheck #314](https://github.com/openfoodfacts/openfoodfacts-ai/issues/314)
- [feat: Batch job - Spellcheck #1401](https://github.com/openfoodfacts/robotoff/pull/1401)
- [Artificial Intelligence @ Open Food Facts](https://github.com/orgs/openfoodfacts/projects/16)
- [Leveraging LLMs across Open Food Facts](https://github.com/orgs/openfoodfacts/projects/99/views/1)

#### Fine-Tuning

Fine-tunez **mistral:7b** sur des données spécifiques aux produits alimentaires pour améliorer sa compréhension du domaine.

- [Is MLX the best Fine Tuning Framework?](https://www.youtube.com/watch?v=BCfCdTp-fdM)

#### Recherche vectorielle

La recherche vectorielle, potentiellement intéressant :

- https://github.com/lorenzejay/agentic-rag-recommendation-engine
- https://www.youtube.com/watch?v=2Fu_GgS-Q4s
- https://x.com/helloiamleonie/status/1884554441514459435
- 

### Documentation et finalisation (25h)
#### Rédaction du rapport final (15h)
#### Préparation de la présentation orale (5h)
#### Nettoyage du code et de la documentation du dépôt GitHub (5h)

## Versions

### `chatbot_01.py`

- Première version du chatbot.

### `chatbot_02.py`

- Deuxième version du chatbot avec des améliorations.

### `chatbot_03.py`

- Troisième version du chatbot, la première version fonctionnelle.

### `chatbot_04.py`

Quatrième version du chatbot en intégrant les 3 étapes suggérées par l'article de Biswal et al..

D'après l'article de Biswal et al., le modèle TAG (Table-Augmented Generation) se décompose en 3 étapes principales. 

Le code est restructuré le code pour mieux refléter cette architecture.

Les principales modifications apportées au code pour implémenter l'approche TAG sont :

- Création d'une nouvelle classe `TAGSystem` qui implémente explicitement les trois étapes du modèle TAG :
  - `syn()` : Query Synthesis - Convertit la question en langage naturel en une requête SQL
  - `exec()` : Query Execution - Exécute la requête sur la base de données 
  - `gen()` : Answer Generation - Génère la réponse finale en langage naturel
- Simplification de la classe `FoodDatabaseBot` qui devient une simple interface utilisateur s'appuyant sur le système TAG.
- Amélioration des différentes étapes selon les recommandations de l'article :
  - La synthèse de requête (syn) a été améliorée pour mieux déduire les données pertinentes
  - L'exécution de requête (exec) exploite plus efficacement le moteur de base de données
  - La génération de réponse (gen) combine maintenant la requête originale et les données obtenues
- Les principaux avantages de cette nouvelle architecture sont :
  - Une meilleure séparation des responsabilités entre les différentes étapes
  - Une plus grande flexibilité pour optimiser chaque étape indépendamment
  - Une meilleure correspondance avec l'architecture TAG décrite dans l'article
- Pour utiliser ce nouveau code, il suffit de créer une instance de `FoodDatabaseBot` comme avant :

```python
llm = create_llm(**config)  
bot = FoodDatabaseBot(db_path, llm)
response = bot.process_user_input("Quels sont les produits avec un Nutri-score A?")
```

Cette implémentation permet une meilleure maintenance et évolution du code tout en suivant les bonnes pratiques décrites dans l'article de Biswal et al.





## Idées à explorer

- DeepLearning.AI [Practical Multi AI Agents and Advanced Use Cases with crewAI](https://learn.deeplearning.ai/courses/practical-multi-ai-agents-and-advanced-use-cases-with-crewai/lesson/1/introduction) à écouter
- [motherduckdb/DuckDB-NSQL-7B-v0.1](https://huggingface.co/motherduckdb/DuckDB-NSQL-7B-v0.1/blob/main/README.md?code=true#L17) et [ici](https://huggingface.co/motherduckdb/DuckDB-NSQL-7B-v0.1) et [ici](https://github.com/NumbersStationAI/DuckDB-NSQL)
- Voir [ici](https://huggingface.co/spaces/cfahlgren1/duckdb-nsql-hard/blob/main/app.py#L2)
- [Fine-tune SmolLM's on custom synthetic data](https://huggingface.co/blog/prithivMLmods/smollm2-ft) qui prévoit du 
  fine-tuning et du Deepthink-Reasoning.

## Améliorations court terme 

- Intégrer TAG dans le chatbot pour améliorer la génération de requêtes SQL.
- Générer un ensemble de 100 questions réponses pour tester le chatbot. S'inspirer de BIRD pour cela.
- Peut-on évaluer ce code avec le benchmark BIRD? 
- Implanter des agents avec crewAI pour gérer les différentes étapes du processus.
- Bonifier le code pour que le LLM détermine lui-même si les données sont complètes ou non, s'il a besoin de consulter le Guide alimentaire canadien (https://guide-alimentaire.canada.ca/fr/ ou https://food-guide.canada.ca/en/) pour compléter les données et/ou formuler une réponse plus satisfaisante.
- Bonifier le code pour converser dans la langue de l'utilisateur (français ou anglais).


## Références académiques

### [1] Text2SQL is Not Enough : Unifying AI and Databases with TAG

[1] Asim Biswal, Liana Patel, Siddarth Jha, Amog Kamsetty, Shu Liu, Joseph E Gonzalez, Carlos
Guestrin, and Matei Zaharia. Text2SQL is Not Enough : Unifying AI and Databases with
TAG. arXiv preprint arXiv :2408.14717, 2024.

Mots clés : domain knowledge, exact computation, semantic reasoning, world knowledge

Messages clés : 

- While Text2SQL methods 
  are suitable for the subset of natural language queries that have
  direct relational equivalents, they cannot handle the vast array of
  user queries that require semantic reasoning or world knowledge
- On the other hand, the RAG model is limited to simple relevancebased point lookups to a few data records, followed by a single LM
  invocation
- The authors instead propose table-augmented generation (TAG) as a unified paradigm for systems that answer natural language questions over databases. 
- Specifically, TAG defines three key steps : Query synthesis, Query Execution, and Answer Generation
- We select BIRD [17], a widely used Text2SQL benchmark on which LMs have been evaluated, for its large scale tables along with its variety of domains and query types.
- Baselines
  - **Text2SQL** In this baseline, the LM generates SQL code which is run to obtain an answer. However, this
direction does not utilize model capabilities beyond SQL generation, keeping queries that require reasoning or knowledge beyond
a static data source out of scope.
  - **Retrieval Augmented Generation (RAG)** RAG style methods have been explored for table retrieval [6, 25], where tabular data is embedded into an index for search.
    For our baseline, we use rowlevel embeddings. A given row is serialized as "- col: val" for each
    column before being embedded into a FAISS [7] index.
  - **Retrieval + LM Rank** We extend the RAG baseline by utilizing an
    LM to assign a score between 0 and 1 for retrieved rows to rerank
    rows before input to the model, as is done in the STaRK work [25].
  - **Text2SQL + LM** In this baseline, our model is first asked to generate
    SQL to retrieve a set of relevant rows to answer a given NL query.
    This is an important distinction from the Text2SQL baseline, where
    the model is asked to directly generate SQL code that alone provides
    an answer to the query when executed. Similar to the RAG baseline,
    relevant rows are fed in context to the model once retrieved.
  - **Hand-written TAG** We also evaluate hand-written TAG pipelines, which leverage expert knowledge of the table schema 
    rather than automatic query synthesis from the natural language request to the database query. We implement
    our hand-written TAG pipelines with LOTUS [21]. The LOTUS API allows programmers to declaratively specify
    query pipelines with standard relational operators as well as semantic operators, such as LM-based filtering,
    ranking, and aggregations. LOTUS also provides an optimized semantic query execution engine, which we use
    to implement the query execution and answer generation steps of our hand-written TAG pipelines.
- L'article montre clairement que l'approche Hand-written TAG a donné les meilleurs résultats comparés aux autres méthodes. 

### LOTUS: Enabling Semantic Queries with LLMs Over Tables of Unstructured and Structured Data.

Patel, L., Jha, S., Guestrin, C., & Zaharia, M. (2024). "LOTUS: Enabling Semantic Queries with LLMs Over Tables of Unstructured and Structured Data." arXiv:2407.11418

LOTUS (Looking Over Tables Using Semantics) est un système qui permet d'effectuer des opérations sémantiques sur des données en
utilisant les capacités des modèles de langage (LLMs) de manière optimisée et déclarative.

Termes clés : semantic operators.

Voir [GitHub](https://github.com/guestrin-lab/lotus).

### [2] Text-to-SQL Empowered by Large Language Models : A Benchmark Evaluation

[2] Dawei Gao, Haibin Wang, Yaliang Li, Xiuyu Sun, Yichen Qian, Bolin Ding, and Jingren
Zhou. Text-to-SQL Empowered by Large Language Models : A Benchmark Evaluation.
arXiv preprint arXiv :2308.15363, 2023.

### [3] Next-Generation Database Interfaces : A Survey of LLM-based Text-to-SQL

[3] Zijin Hong, Zheng Yuan, Qinggang Zhang, Hao Chen, Junnan Dong, Feiran Huang, and Xiao
Huang. Next-Generation Database Interfaces : A Survey of LLM-based Text-to-SQL. arXiv
preprint arXiv :2406.08426, 2024.

### [4] Can LLM Already Serve as A Database Interface ? A Big Bench for Large-Scale Database Grounded Text-to-SQLs

[4] Jinyang Li, Binyuan Hui, Ge Qu, Jiaxi Yang, Binhua Li, Bowen Li, Bailin Wang, Bowen Qin,
Ruiying Geng, Nan Huo, et al. Can LLM Already Serve as A Database Interface ? A Big
Bench for Large-Scale Database Grounded Text-to-SQLs. Advances in Neural Information
Processing Systems, 36, 2024.

### [5] Towards Optimizing SQL Generation via LLM Routing

[5] Mohammadhossein Malekpour, Nour Shaheen, Foutse Khomh, and Amine Mhedhbi. Towards
Optimizing SQL Generation via LLM Routing. arXiv preprint arXiv :2411.04319, 2024.

### [6] From Natural Language to SQL : Review of LLM-based Text-to-SQL Systems

[6] Ali Mohammadjafari, Anthony S Maida, and Raju Gottumukkala. From Natural Language
to SQL : Review of LLM-based Text-to-SQL Systems. arXiv preprint arXiv :2410.01066,
2024.

### [7] Large Language Model Enhanced Text-to-SQL Generation : A Survey

[7] Xiaohu Zhu, Qian Li, Lizhen Cui, and Yongkang Liu. Large Language Model Enhanced
Text-to-SQL Generation : A Survey. arXiv preprint arXiv :2410.06011, 2024.

## Autres ressources 

- [Generative AI for beginners](https://github.com/microsoft/generative-ai-for-beginners)
- [Anthropic has a pretty useful prompt generator](https://x.com/kregenrek/status/1881422133659840911)
- [Hands-On Large Language Models](https://learning.oreilly.com/library/view/hands-on-large-language/9781098150952/)
  - [https://github.com/HandsOnLLM/Hands-On-Large-Language-Models](https://github.com/HandsOnLLM/Hands-On-Large-Language-Models)
