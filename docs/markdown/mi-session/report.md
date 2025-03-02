# Rapport de mi-session

> Version du 1er mars 2025

## 1. Introduction

L'accès aux informations nutritionnelles reste souvent limité par des interfaces techniques nécessitant des compétences en langages de requête comme SQL. Cette barrière empêche de nombreux utilisateurs d'exploiter pleinement des bases de données comme Open Food Facts, qui contient des informations détaillées sur des milliers de produits alimentaires. 

Ce projet vise à développer un agent conversationnel utilisant des grands modèles de langage (LLM) pour permettre aux utilisateurs de poser des questions en langage naturel comme "Quelles collations sans allergènes ont un Nutri-score A ?". Cette approche démocratise l'accès aux données nutritionnelles tout en améliorant la qualité des réponses grâce à l'exploitation directe de sources structurées. 

Ce rapport de mi-session présente l'état d'avancement du projet à la mi-session, les défis rencontrés et les solutions implémentées.

## 2. Rappel de l'objectif du projet

L'objectif de ce projet est de développer un agent conversationnel permettant aux utilisateurs d'interroger la base de données [Open Food Facts](https://world.openfoodfacts.org/) en langage naturel. Le système doit comprendre les questions des utilisateurs sur les produits alimentaires, les convertir en requêtes SQL, et fournir des réponses claires et précises. Les données manquantes ou incomplètes doivent être compensées par une recherche alternative dans le [Guide alimentaire canadien](https://guide-alimentaire.canada.ca/fr/).

## 3. Approche proposée

### 3.1 Architecture du système

Mon approche utilise une architecture avec les composants suivants :

- **Module de dialogue**: Gère les conversations avec l'utilisateur en utilisant un LLM pré-entraîné.
- **Convertisseur texte-SQL**: Transforme les questions en requêtes SQL adaptées à Open Food Facts. Il utilise d'abord une recherche dans un dictionnaire de données pour trouver les colonnes pertinentes.
- **Connecteur de base de données**: Communique avec DuckDB pour exécuter les requêtes. Les requêtes SQL sont vérifiées avant exécution pour garantir leur sécurité.
- **Recherche sur le Web**: Consulte le [Guide alimentaire canadien](https://guide-alimentaire.canada.ca/fr/) quand les informations manquent dans la base de données.
- **Générateur de réponses**: Transforme les résultats bruts en réponses naturelles, en précisant les sources.

### 3.2 Sélection des technologies

J'ai choisi ces technologies pour mon projet :

- **DuckDB** comme base de données, car :
  - Elle est rapide pour les requêtes analytiques
  - Elle gère bien la mémoire
  - Elle supporte les fichiers Parquet et les requêtes SQL complexes
  - Elle s'intègre facilement avec Python
- **Smolagents de Hugging Face** comme framework d'agent car :
  - Il est simple à utiliser
  - Il est conçu pour les "agents de code"
  - Il permet d'intégrer différents LLMs et outils
  - Il est bien documenté et supporté
- **Modèles de langage** :
  - Pour le développement: `ollama/llama3.1:8b-instruct-q8_0` (modèle local)
  - Pour les tests: `ollama/llama3.1:8b-instruct-q8_0`, `ollama/qwen2.5:7b-instruct` et `anthropic/claude-3-5-sonnet` (modèle commercial)
  - Cette approche limite les coûts d'API
- **FAISS** pour la recherche sémantique :
  - Il identifie rapidement les colonnes pertinentes pour chaque question
  - Il transforme la documentation des colonnes en vecteurs faciles à comparer

## 4. État d'avancement et tâches réalisées

Le développement de l'agent conversationnel a progressé significativement durant cette première phase du projet. Cette section détaille les différentes tâches accomplies et leur état d'avancement, en suivant le plan initial.

### 4.1 Mise en place de l'environnement de développement

J'ai d'abord créé un environnement de développement complet:

- **Infrastructure et outils**
  - Un [dépôt GitHub](https://github.com/boisalai/ift-6005) pour le code et la documentation
  - Un environnement virtuel Python avec les bonnes dépendances
  - Des outils comme Black pour le formatage et Pylint pour l'analyse de code
  - Des hooks pre-commit pour maintenir la qualité du code
- **Dépendances principales**
  - DuckDB (v1.2.0) pour les requêtes SQL
  - Smolagents (v1.9.2) comme framework d'agent
  - FAISS (v1.10.0) pour la recherche sémantique
  - Des bibliothèques pour l'analyse de données et le traitement du langage
- **Configuration des API**
  - Des variables d'environnement pour les clés API dans un fichier `.env`
  - L'accès à l'API d'Anthropic pour Claude 3.5 Sonnet
  - L'interface avec Ollama pour les tests locaux


### 4.2 Préparation de la base de données

J'ai téléchargé le fichier Parquet d'Open Food Facts (3,6 millions de produits) et l'ai converti en base DuckDB:

```bash
wget -P data/ https://huggingface.co/datasets/openfoodfacts/product-database/resolve/main/food.parquet
```

```python
DATA_DIR = Path("../data")
PARQUET_PATH = DATA_DIR / "food.parquet"
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"

con = duckdb.connect(str(FULL_DB_PATH), config={'memory_limit': '8GB'})
con.execute(f"CREATE TABLE products AS SELECT * FROM '{PARQUET_PATH}'")
con.close()
```

Pour accélérer les requêtes, j'ai créé une version avec seulement les 94 802 produits canadiens :

```python
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

con = duckdb.connect(str(FILTERED_DB_PATH))
con.execute(f"ATTACH DATABASE '{FULL_DB_PATH}' AS full_db")
con.execute(f"""
    CREATE TABLE products AS 
    SELECT * FROM full_db.products
    WHERE array_contains(countries_tags, 'en:canada')
""")
```

J'ai aussi analysé les données et découvert que certaines colonnes sont très complètes (>95%) alors que d'autres sont peu renseignées (<30%).

![missing-values](../img/missing_values.png)

J'ai également remarqué que certaines colonnes ont des structures complexes. 

Par exemple, "categories" contient du texte libre séparé par des virgules, alors que "categories_tags" contient des identifiants standardisés incluant des préfixes de langue.

Exemple de données pour la colonne "categories" :

```
"Sweeteners,Syrups,Simple syrups,Agave syrups"
"Plant-based beverages,Fruit-based,Juices and nectars,Fruit juices,Lemon juice"
"Snacks,Sweet snacks,Biscuits and cakes,Cakes"
```

Exemple de données pour la colonne "categories_tags" :

```
["en:plant-based-foods-and-beverages", "en:beverages", "en:plant-based-beverages", "en:coconut-milks"]
["en:snacks", "en:sweet-snacks", "en:cocoa-and-chocolate-products", "en:chocolates"]
["en:dairies", "en:milk", "en:whole-milk"]
```

Ces tâches s'effectuent via le script `data.py`.

### 4.3 Documentation des données

J'ai créé un dictionnaire détaillé en JSON (`columns_documentation.json`) pour aider l'agent à générer des requêtes SQL. Il contient des informations sur chacune des 109 colonnes.
La documentation pour chaque colonne ressemble à ceci:

```python
"nova_groups_tags": {
    "type": "VARCHAR[]",
    "description": "Array containing NOVA food classification group tags. NOVA...
    "examples": [
      "['en:1-unprocessed-or-minimally-processed-foods']",
      "['en:4-ultra-processed-food-and-drink-products']",
      "['en:3-processed-foods']"
    ],
    "is_nullable": true,
    "common_queries": [
    {
        "description": "Distribution of products across NOVA groups",
        "sql": "SELECT nova_groups_tags, COUNT(*) as product_count FROM products..."
    },
    {
        "description": "Find products in a specific NOVA group (e.g., ultra-pro...","
        "sql": "SELECT code, product_name, nova_groups_tags FROM products WHERE..."
    },
    {
        "description": "Products with unknown or missing NOVA classification",
        "sql": "SELECT code, product_name, nova_groups_tags FROM products WHERE..."
    }
  ]
},
```

Cette documentation est générée par un agent qui :

- Interroge la colonne dans la base de données
- Recherche des informations sur le site Open Food Facts
- Propose une description de la colonne
- Génère des requêtes SQL typiques
- Ajoute la documentation au fichier JSON

Ces tâches s'effectuent via le script `docoff.py`.

### 4.4 Création du jeu de test

J'ai créé un jeu de questions-réponses en utilisant les requêtes SQL documentées. Pour chaque requête SQL, un agent:

Évalue si la requête répond à une question pertinente pour un consommateur
Génère des questions en français et en anglais
Crée des réponses claires correspondant à la requête SQL
Vérifie que les résultats de la requête permettent de répondre à la question

Les paires sont stockées dans `qa_pairs.json` avec cette structure:

```json
{
    "column": "nutriscore_grade",
    "sql": "SELECT code, product_name FROM products WHERE...",
    "questions": {
        "fr": "Quels produits ont un Nutri-Score A?",
        "en": "Which products have a Nutri-Score A?"
    },
    "answers": {
        "fr": "Les produits suivants ont un Nutri-Score A...",
        "en": "The following products have a Nutri-Score A..."
    }
}
# ... plus de paires Q&A
```

Le processus est implémenté dans le script `question_answer.py`.

### 4.5 Développement de la recherche sémantique

J'ai implémenté une recherche sémantique avec FAISS et le modèle `all-MiniLM-L6-v2` pour identifier les colonnes pertinentes dans la base de données :

- Préparation des embeddings :
  - La documentation des 109 colonnes est convertie en vecteurs
  - Le modèle MiniLM génère des embeddings de dimension 384
  - Ce modèle fonctionne en français et en anglais
- Indexation FAISS :
  - Un index est créé pour les recherches rapides par similarité
  - Les embeddings sont sauvegardés dans des fichiers pour éviter de recalculer l'index
- Processus de recherche :
  - Pour chaque question, l'embedding de la question est comparé à ceux des colonnes
  - Les 5 colonnes les plus similaires sont retournées avec un score
  - Seules les colonnes avec un score > 0.5 sont utilisées

Les résultats de cette recherche sont ajoutés au prompt de l'agent pour l'aider à générer de meilleures requêtes SQL.

### 4.6 Création des outils d'agent

Un agent d'intelligence artificielle (IA) est un logiciel qui peut interagir avec son environnement, collecter des données et les utiliser pour effectuer des tâches autodéterminées afin d'atteindre des objectifs prédéterminés.

J'ai choisi Smolagents pour son approche simple et flexible.  Cet outil est idéal pour expérimenter rapidement avec la logique d'agent, 
particulièrement lorsque l'application est relativement simple.

J'ai développé deux outils principaux :

- **Exécution SQL sécurisée**: Permet à l'agent de générer et d'exécuter des requêtes SQL sur DuckDB avec des vérifications de sécurité
- **Recherche sur le Web**: Permet à l'agent de consulter le Guide alimentaire canadien quand les informations ne sont pas dans Open Food Facts

Ces outils sont orchestrés par Smolagents, qui aide l'agent à choisir le bon outil selon la question.

### 4.7 Stratégie d'évaluation

J'évalue l'agent avec quatre métriques principales:

- **Précision d'exécution (EX)** : Mesure si l'agent génère des requêtes SQL correctes (20% pour avoir une requête, 30% pour l'exécution sans erreur, 50% pour des résultats corrects)
- **Précision sémantique (PS)** : Compare la similarité entre les réponses de l'agent et les réponses attendues
- **Respect de séquence (RS)** : Vérifie si l'agent suit une stratégie de recherche cohérente (d'abord la base de données, puis les sources externes)
- **Temps de réponse moyen (TRM)** : Mesure la rapidité du traitement

## 4.8 Avancement par rapport à la planification initiale

Voici un tableau comparatif entre la **planification initiale** et l’**état actuel du projet** :

| **Tâche**                                      | **Planification initiale (plan.pdf)**     | **État actuel (report.pdf)**           | **Statut**  |
|-----------------------------------------------|-----------------------------------------|--------------------------------------|------------|
| **Mise en place de l’environnement**         | 5h – Environnement Python, GitHub      | Environnement configuré, GitHub prêt, Black & Pylint utilisés | ✅ Terminé  |
| **Préparation de la base de données**        | 5h – Création d’une base DuckDB        | Base DuckDB créée avec filtrage des produits canadiens | ✅ Terminé  |
| **Création du jeu de test (100 questions)**  | 10h – Générer des questions et requêtes SQL | 100 questions-réponses créées en français et anglais | ✅ Terminé  |
| **Documentation des données**                | Prévoir un dictionnaire des colonnes   | Documentation détaillée (109 colonnes, exemples, SQL) | ✅ Terminé  |
| **Développement de la conversion texte-SQL** | 25h – Approche texte-SQL avec LLM      | Implémentation avec FAISS pour recherche sémantique | ✅ Terminé  |
| **Développement du module de dialogue**      | 20h – Utilisation de Qwen2-7B-Instruct | Utilisation de Llama3.1:8B, Qwen2.5:7B, Claude 3.5 | ✅ Terminé  |
| **Implémentation du générateur de réponses** | 25h – Transformer résultats SQL en texte | Fonctionnel avec SmolAgents et intégration Guide alimentaire canadien | ✅ Terminé  |
| **Stratégie d’évaluation (métriques EX, PS, RS, TRM)** | 10h – Définir et tester les métriques | Métriques définies et tests réalisés sur plusieurs modèles | ✅ Terminé  |
| **Optimisation des requêtes SQL et prompts** | 15h – Améliorer la génération SQL      | Ajustements des prompts et meilleure gestion des colonnes SQL | ✅ Terminé  |
| **Gestion des données manquantes**           | 15h – Trouver des stratégies alternatives | Approche hybride avec Guide alimentaire canadien intégrée | ✅ Terminé  |
| **Sélection dynamique de LLM**               | 10h – Tester plusieurs modèles pour équilibre coût/performance | Tests réalisés sur plusieurs modèles, résultats documentés | ✅ Terminé  |
| **Exploration de nouvelles méthodes (ex. RAG, Neo4j)** | Optionnelle en phase avancée          | Mentionnée comme piste future | ⏳ À explorer |
| **Finalisation et rapport final**            | Rapport mi-session : 15h, final : 15h  | Rapport mi-session rédigé, reste le rapport final | ⏳ En cours |

🔹 **Résumé :**  
Toutes les tâches **principales sont terminées** selon la planification. Les optimisations avancées et l’exploration de nouvelles approches (ex. RAG) sont **à explorer**. La **rédaction du rapport final** est en cours.


## 5. Résultats et discussion

Le tableau suivant résume les résultats des tests effectués sur l'agent conversationnel en utilisant différents modèles de langage et en évaluant les métriques EX, PS, RS et TRM
sur 20 questions pour chaque modèle, en français et en anglais.



|                          |Llama3.1:8b-Instruct (en)|Qwen2.5:7b-Instruct (en)|Claude 3.5 Sonnet (en)|Llama3.1:8b-Instruct (fr)|Qwen2.5:7b-Instruct (fr)|Claude 3.5 Sonnet (fr)| 
|--------------------------|---:|---:|---:|---:|---:|---:|
|Nombre de questions       |20|20|20|20|20|20|
|Précision d'exécution (EX) (%)             |31.1|28.6|42.5|25.0|40.0|47.5|
|Précision sémantique (PS) (%)      |16.7|66.5|62.3|20.0|49.5|54.7|
|Respect de séquence (RS) (%)       |100.0|100.0|100.0|100.0|100.0|100.0|
|Temps de réponse moyen (TRM)|432s|239s|37s|273s|201|41s|

Ici Llama3.1:8b-Instruct réfère au modèle `ollama/llama3.1:8b-instruct-q8_0`, Qwen2.5:7b-Instruct au modèle `ollama/qwen2.5:7b-instruct` et Claude 3.5 Sonnet au modèle `anthropic/claude-3-5-sonnet-20241022`. Les tests ont été réalisés sur un MacBook Pro M1 16 Go de RAM.

Les principales observations sont les suivantes :

- **Performance des modèles** : Claude 3.5 Sonnet surpasse significativement les modèles Llama3.1 et Qwen2.5 sur presque toutes les métriques, particulièrement en précision d'exécution (EX) et en temps de réponse moyen (TRM).
- **Différences linguistiques** : Les performances varient selon la langue. Les résultats en français montrent généralement une bonne précision d'exécution pour Claude et Qwen par rapport à l'anglais, suggérant une bonne capacité de traitement multilingue.
- **Respect de séquence** : Tous les modèles obtiennent un score parfait (100%) sur le respect de séquence (RS), indiquant que la stratégie de recherche définie est bien suivie indépendamment du modèle utilisé.
- **Précision sémantique** : Qwen2.5 surpasse remarquablement Llama3.1 en précision sémantique, particulièrement en anglais (66.5% contre 16.7%), suggérant peut-être une meilleure compréhension du domaine des produits alimentaires.

Ces résultats démontrent clairement l'avantage d'utiliser un modèle commercial comme Claude 3.5 Sonnet pour des applications pratiques, bien que Qwen2.5 offre une alternative gratuite intéressante avec des performances acceptables, particulièrement pour la compréhension sémantique.

Ces évaluations s'effectuent dans le script `evaluation_04.py`.

## 6. Problèmes rencontrés et solutions

### 6.1 Complexité structurelle des données

Un défi majeur a été de comprendre les structures complexes d'Open Food Facts. Sans documentation officielle complète, j'ai dû explorer la base en détail pour comprendre les relations entre les colonnes.

La base contient des structures hétérogènes, comme les colonnes "categories" (texte libre avec virgules) et "categories_tags" (tableaux avec préfixes de langue). Cette complexité rend difficile la génération de bonnes requêtes SQL.

Pour résoudre ce problème, j'ai créé une documentation détaillée avec :

- Le type de données et sa description
- Des exemples de valeurs
- Des modèles de requêtes SQL adaptées

Je pense qu'on peut encore améliorer cette documentation, peut-être avec plus d'exemples annotés.

### 6.2 Limitations des modèles de langage légers

L'utilisation de modèles gratuits (ex. `ollama/llama3.1:8b-instruct-q8_0`) pendant le développement a permis d'avancer sans coûts d'API, mais a montré des limites :

- Difficulté à comprendre des instructions complexes
- Problèmes pour maintenir un format de réponse cohérent
- Génération SQL parfois incorrecte
- Difficulté à suivre des séquences d'actions

Pour résoudre ces problèmes, j'ai :

- Amélioré les prompts: Instructions plus simples et directes, avec plus d'exemples
- Modifié l'architecture: Utilisé les mécanismes de MultiStepAgent de Smolagents pour mieux suivre la progression

Des tests avec `anthropic/claude-3-5-sonnet` montrent des résultats bien meilleurs, confirmant l'intérêt d'une approche hybride: développement avec des modèles légers, puis déploiement avec des modèles plus puissants.

## 7. Prochaines étapes

Si je continue ce projet sur cette voie, je peux :

- **Mieux documenter la structure de la base de données** : Créer une meilleure carte des relations entre colonnes, ajouter des exemples pour les structures difficiles, et enrichir la documentation avec des informations sur la distribution des données.
- **Optimiser la recherche sémantique** : Ajouter une recherche vectorielle sur les fiches produits en plus de l'approche SQL. Cela aiderait à trouver des produits similaires quand les requêtes SQL sont limitées.

Je pourrais aussi explorer une approche différente avec **RAG sur un graphe de connaissances** en utilisant Neo4j et Langchain. Cette méthode 
pourrait mieux représenter les relations complexes entre produits et informations nutritionnelles.

## 8. Références

Gao, D., Wang, H., Li, Y., Sun, X., Qian, Y., Ding, B., & Zhou, J. (2023). Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation. *arXiv preprint arXiv:2308.15363*. https://arxiv.org/abs/2308.15363

## Annexe A: Exemple d'évaluation d'une requête utilisateur

**Question utilisateur** : "What food products without additives are available in the database?"

### Étape 1: Définition de la question et référence dans le jeu de test

Cette question correspond à la première entrée dans le fichier `qa_pairs.json`, structurée comme suit:

```txt
[
  {
    "column": "additives_n",
    "sql": "SELECT code, product_name FROM products WHERE additives_n = 0",
    "questions": {
      "fr": "Quels sont les produits alimentaires sans additifs disponibles dans la base de données?",
      "en": "What food products without additives are available in the database?"
    },
    "answers": {
      "fr": """La base de données contient 5843 produits sans additifs, incluant des produits comme 
               le sirop d'érable biologique du Vermont, le lait faible en gras, l'agave bleu biologique, 
               et le lait de coco.""",
      "en": """The database contains 5843 products without additives, including items such as organic 
               Vermont maple syrup, low-fat milk, organic blue agave, and coconut milk."""
    }
  },
  ...
]
```

### Étape 2: Analyse sémantique des colonnes pertinentes

Le système utilise FAISS pour comparer l'embedding de la question avec ceux des descriptions de colonnes :

```python
relevant_columns = self._search_relevant_columns(question)
```

Cette recherche identifie 5 colonnes potentiellement pertinentes avec leurs scores de similarité :
- `unknown_ingredients_n` (score : 0,656)
- `additives_tags` (score : 0,638)
- `ingredients_original_tags` (score : 0,622)
- `ingredients_without_ciqual_codes` (score : 0,612)
- `data_quality_info_tags` (score : 0,563)

### Étape 3: Préparation du prompt pour l'agent

Les informations sur ces colonnes sont préparées et stockées dans `columns_info` :

```python
columns_info = []
for col in relevant_columns:
    if col['similarity'] > 0.5:
        column_section = [
            f"Column: {col['name']}\n"
            f"Type: {col['type']}\n"
            f"Description: {col['description']}\n"
            f"Examples of values: {', '.join(map(str, col['examples'][:3]))}"
        ]
        
        if 'common_queries' in col and col['common_queries']:
            column_section.append(f"Query examples:")
            for query in col['common_queries']:
                column_section.append(
                    f"# {query.get('description', '')}:\n"
                    f"{query.get('sql', '')}"
                )
        
        columns_info.append("\n".join(column_section))
```

Ces informations sur les colonnes pertinentes sont insérées des notes additionnelles pour l'agent
comme ceci :

```python
additional_notes = dedent(
    """\
    You are a helpful assistant that answers questions about food products 
    using the Open Food Facts database.

    POTENTIALLY RELEVANT COLUMNS:
    The following columns have been identified through semantic search as potentially relevant, 
    with their similarity scores (higher means more likely relevant):
    
    {columns_text}

    SEARCH SEQUENCE RULES:
    1. ALWAYS start with database queries using the most relevant columns
    2. If initial query fails, try alternative database queries with different columns or approaches
    3. Only if database queries are unsuccessful, search the Canada Food Guide
    4. Document EVERY attempt in the steps array, including failures
    5. Never skip straight to Food Guide without trying database first
    6. Always include the source of the information in the answer ("Open Food Facts" or "Canada Food Guide")
    7. Always respond in the same language as the question (French or English)
    
    RESPONSE FORMAT REQUIREMENTS:
    1. Provide ONLY the natural language answer to the user's question
    2. Maximum response length: 200 characters
    3. DO NOT include SQL queries, code snippets, or technical details
    4. DO NOT explain your reasoning or methodology
    5. Respond in the same language as the question (French or English)
    6. DO mention the source of information ("Open Food Facts" or "Canada Food Guide")
    
    Please follow these rules to ensure a consistent and effective search strategy.
    """
).format(columns_text=columns_text)
```

### Étape 4: Exécution de l'agent

L'agent est appelé avec le prompt enrichi :

```python
start_time = time.time()
agent_response = agent.run(
    question,
    additional_args={"additional_notes": additional_notes},
)
response_time = time.time() - start_time
```

### Étape 5: Génération de la réponse

L'agent analyse les informations et génère une réponse :

"According to Open Food Facts database, additive-free products include natural 
foods like blueberries and pistachios, basic staples like spaghetti and rice, 
and beverages like coconut water and coffee."

### Étape 6: Traçage des étapes de l'agent

Le système enregistre toutes les étapes suivies par l'agent :

```python
# Extrait les étapes depuis la mémoire de l'agent
if hasattr(agent, 'memory') and hasattr(agent.memory, 'steps'):
    steps_sequence = []
    
    for step in agent.memory.steps:
        # Analyse chaque étape et outil utilisé
        if not hasattr(step, 'tool_calls') or not step.tool_calls:
            continue
            
        tool_call = step.tool_calls[0]
        
        # Enregistre les requêtes SQL, recherches web et autres actions
        if tool_call.name == "python_interpreter" and isinstance(tool_call.arguments, str):
            code = tool_call.arguments
            step_data = {}
            
            # Détermine le type d'action (requête SQL, recherche web, etc.)
            if "query_db" in code:
                sql_query = self._extract_sql_from_code(code)
                # Enregistre l'information sur la requête SQL
            elif "search_food_guide" in code:
                # Enregistre l'information sur la recherche web
```

Ces étapes permettent de suivre la séquence de recherche (d'abord la base de données, puis le guide alimentaire si nécessaire).

### Étape 7: Évaluation des métriques

Trois métriques principales sont calculées :

**1. Précision d'exécution (EX)** : Comparer la requête générée avec la référence

```python
def _calculate_sql_accuracy(self, response_data: dict, qa_pair: Dict[str, Any]) -> float:
    agent_sql = response_data.get('sql_query')
    
    # Exécuter les requêtes
    reference_results = self.execute_query(qa_pair['sql'])
    agent_results = self.execute_query(agent_sql)

    # Calculer les métriques individuelles
    query_present = 1.0 if agent_sql else 0.0
    execution_success = float(agent_results.success)
    results_match = 0.0

    # Comparer les résultats
    if reference_results.success and agent_results.success:
        # Calcul de la similarité entre les deux ensembles de résultats
```

**2. Précision sémantique (PS) : Comparer la réponse générée avec la référence**

Je demande à un modèle LLM de comparer les deux réponses pour évaluer leur similarité sémantique.

Les deux réponses sont : 

- **Réponse attendue** : "The database contains 5843 products without additives, including items such as organic Vermont maple syrup, low-fat milk, organic blue agave, and coconut milk."
- **Réponse de l'agent** : "According to Open Food Facts database, additive-free products include natural foods like blueberries and pistachios, basic staples like spaghetti and rice, and beverages like coconut water and coffee."

```python
def _calculate_semantic_accuracy(self, response_data: dict, qa_pair: Dict, lang: str) -> float:
    # Utiliser un LLM pour évaluer la similarité sémantique
    prompt = dedent(f"""\
    Compare these two responses and rate their semantic similarity from 0 to 1:
    Response #1: {qa_pair['answers'][lang]}
    Response #2: {agent_response}
    """)
    
    # Le modèle LLM évalue et retourne un score de similarité
```

**3. Respect de séquence (RS)** : Vérifier que l'agent a suivi le bon ordre des sources

```python
def _evaluate_search_sequence(self, response_data: dict) -> dict:
    steps = response_data.get('steps', [])
    
    # Initialiser les compteurs
    db_attempts = []
    web_attempt = None
    sequence_respected = True
    
    # Vérifier l'ordre des étapes
    for step in steps:
        if step['action'] in ['database_query', 'alternative_query']:
            db_attempts.append(step)
            # Vérifier si une recherche web a déjà eu lieu (violation)
            if web_attempt is not None:
                sequence_respected = False
                break
        elif step['action'] == 'food_guide_search':
            web_attempt = step
```

### Étape 8: Compilation des résultats

Les résultats de l'évaluation sont compilés :

```python
# Créer un objet EvaluationResult contenant toutes les informations
return EvaluationResult(
    question_id=qa_pair.get('id', 0),
    language=lang,
    question=question,
    expected_answer=qa_pair['answers'][lang],
    agent_answer=agent_answer,
    metrics=metrics,
    expected_sql=qa_pair.get('sql', ''),
    agent_sql=agent_sql
)
```

### Résultats finaux

L'évaluation finale montre :

- Précision d'exécution (EX) : 0,00% (l'agent n'a pas généré de requête SQL valide)
- Précision sémantique (PS) : 80,00% (forte similarité entre les réponses)
- Respect de séquence (RS) : 100,00% (protocole de recherche respecté)
- Temps de réponse moyen (TR) : 45,95 secondes

Cet exemple illustre le parcours complet, démontrant comment l'agent analyse la question, génère une réponse et comment le système
évalue objectivement cette réponse selon plusieurs dimensions.
