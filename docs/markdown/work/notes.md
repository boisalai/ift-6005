# Document de travail
 
## Phase 1

### Créer l'environnement de développement

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

### Télécharger les données d'Open Food Facts

Télécharger le fichier d'Open Food Facts depuis Hugging Face directement dans le dossier `data/` du projet.

```bash
brew install wget  # si vous n'avez pas wget
wget -P data/ https://huggingface.co/datasets/openfoodfacts/product-database/resolve/main/food.parquet
```

Le fichier `food.parquet` contient les données de Open Food Facts au format Parquet. Ce fichier pèse 5.5 Go.

```bash
$ ls -lh data/food.parquet | awk '{print $5}'
5.5G
```

### Lire les données avec Pandas

Nous pourrions normalement lire les données en utilisant la librairie `pandas` comme ceci.

```python
import pandas as pd
df = pd.read_parquet('food.parquet')
df.describe()
```

Cependant, le code précédent entraîne une erreur de mémoire insuffisante. Nous devons donc utiliser une autre approche.


### Lire les donné.es avec DuckDB

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


### Ollama

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


## Agents

- LlamaIndex, [AgentWorkflow Basic Introduction](https://docs.llamaindex.ai/en/stable/examples/agent/agent_workflow_basic/)
- [Week 10](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/free_courses/Applied_LLMs_Mastery_2024/week10_research_trends.md)
- Elasticsearch?
- [What is Agentic RAG](https://weaviate.io/blog/what-is-agentic-rag)
- [Introduction to LLM Agents](https://developer.nvidia.com/blog/introduction-to-llm-agents/)
- [Agentic RAG 101 Guide](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/resources/agentic_rag_101.md) Ce site est très intéressant!!!
- [Introducing AgentWorkflow: A Powerful System for Building AI Agent Systems](https://www.llamaindex.ai/blog/introducing-agentworkflow-a-powerful-system-for-building-ai-agent-systems)
- [Agents 101 guide](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/resources/agents_101_guide.md)
- [LlamaIndex | Text-To-SQL ( LlamaIndex + DuckDB)](https://www.youtube.com/watch?v=03KFt-XSqVI) on Youtube
- [CrewAI ](https://x.com/akshay_pachaar/status/1882406721974624278)
- [RAG, AI Agents, and Agentic RAG: An In-Depth Review and Comparative Analysis](https://www.digitalocean.com/community/conceptual-articles/rag-ai-agents-agentic-rag-comparative-analysis)
- [Applied LLMs Mastery 2024](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/free_courses/Applied_LLMs_Mastery_2024/README.MD)


## Mistral-7B

- [Function calling](https://docs.mistral.ai/capabilities/function_calling/)

## ElasticSearch

- [ElasticsearchRetriever](https://python.langchain.com/docs/integrations/retrievers/elasticsearch_retriever/)

Je dois décrire brièvement mon projet à réaliser dans le cadre du projet intégrateur d'un cours universitaire IFT-6005.

Je dois notamment expliquer différentes approches à explorer pour interroger une base de données avec un agent conversationnel.
Les différentes approches seraient RAG classique, ou Données SQL soit par représentation textuelle ou requêtes SQI dynamique, ou encore ElasticSearch, via un LLM.

Faut expliquer les avantages et inconvénients de chaque approche.

Aussi, je veux proposer une approche incrémentale pour le développement de l'agent conversationnel.

D'abord, choisir un LLM capable de générer des requêtes SQL à partir de questions en langage naturel, et d'utiliser un outil comme DuckDB pour exécuter ces requêtes.


Ensuite utiliser ElasticSearch pour exploiter à la fois la recherche sémantique et les requêtes structurées.

Reformule tes réponses précédentes pour les rendre plus claires et plus concises, en paragraphes, sur deux pages.


## SQL

- [IA SQL](https://medium.com/@clicbiz/list/ia-sql-73e98bba4daf)
- [SQL Query Engine with LlamaIndex + DuckDB](https://docs.llamaindex.ai/en/stable/examples/index_structs/struct_indices/duckdb_sql_query/)

## LLM Web Crawler 

- [Introducing DeepSeek R1 web crawler](https://x.com/ericciarla/status/1882471683560558870)
- [Browse-use](https://x.com/hwchase17/status/1882502767312531954)

## Autres références

- [LLM-Engineers-Handbook](https://github.com/PacktPublishing/LLM-Engineers-Handbook)

-----





## Requêtes possibles

Voici des requêtes possibles que l'interface pourrait gérer :

- "Show me ready made meals that are NutriScore A sold at Aldi"
- "Show me the repartition of NutriScore for Nestlé in Europe"
- "Make me a graph of all breakfast cereals with NOVA groups, nutrition value and Nutri-Score"

## Références

- [How to Talk to Any Database Using AI – Build Your Own SQL Query Data Extractor](https://www.freecodecamp.org/news/talk-to-databases-using-ai-build-a-sql-query-data-extractor/)
  - Trop compliqué. La solution présentée passe par REST API.
- [Table-Augmented Generation (TAG): A Unified Approach for Enhancing Natural Language Querying over Databases](https://www.marktechpost.com/2024/08/29/table-augmented-generation-tag-a-unified-approach-for-enhancing-natural-language-querying-over-databases/?amp)
  - Ce texte réfère à un article académique.
  - Intéressant.
- [Construisez un chatbot sur vos propres données en 1 heure avec Azure SQL~? Langchain et Chainlit](https://windows-azure.developpez.com/actu/363354/Construisez-un-chatbot-sur-vos-propres-donnees-en-1-heure-avec-Azure-SQL-Langchain-et-Chainlit-par-Davide-Mauri/?amp)
  - Ce texte est trop bref et compliqué à la fois.
  - Utilise Azure SQL pour la prise en charge des vecteurs, LangChain et ChainLit.
- [Reusing Open Food Facts Data](https://wiki.openfoodfacts.org/Reusing_Open_Food_Facts_Data)
  - Cette page explique comment utiliser les données Open Food Facts.
- [search-a-licious](https://github.com/openfoodfacts/search-a-licious)
  - Elasticsearch est au coeur de ce projet.
  - L'équipe Search-a-licious est prête à discuter avec nous.
  - Leur prochaine étape serait d'ajouter plus de NLP dans l'outil de recherche. 
  - https://gitingest.com/openfoodfacts/search-a-licious
  - Ce projet utilise Elasticsearch, FastAPI, TypeScript, Docker et Vega pour les visualisations.
  - Je crains que la courbe d’apprentissage nécessaire pour bien maîtriser ces outils soit trop abrupte pour moi dans le cadre du cours IFT-6005. 
  - Étant donné les délais serrés et les exigences du cours, le risque de ne pas réussir à atteindre les objectifs me semble élevé.

---

## Agents

### Note 20250123-0730

Agents require the ability to remember past actions, security, handle user feedback, and adapt gracefully. In other words, it is a proper software product that happens to use/integrate a large language model with tool usage to accomplish various tasks.

As AI engineers working at the application layer, this is our job building agents: assemble these pieces into a polished and fully realized product.
Voir le livre de Chip Huyen Ai Enginering

### 20250123-1019

Dans ce plan, les composants décrits se situent plutôt entre agents et RAG :

**Vrais agents** :
- Agent principal de conversation : C'est un véritable agent car il coordonne, planifie et prend des décisions complexes.

**Hybrides Agent-RAG** :
- Agent d'enrichissement : C'est plus proche d'un RAG car sa fonction principale est de récupérer et intégrer des informations du Guide alimentaire canadien.
- Agent de génération de requêtes : Pourrait être un agent s'il planifie des séquences complexes de requêtes, mais semble plus proche d'un RAG spécialisé dans la traduction langue naturelle vers SQL.

**Non-agent** :
- Agent de visualisation : C'est plutôt un outil spécialisé qui transforme des données en visualisations, sans réelle capacité de planification ou d'autonomie.

Pour mieux respecter l'architecture agent/RAG, il faudrait :
1. Garder l'agent principal comme vrai agent planificateur
2. Transformer les autres composants en outils/RAG que l'agent principal peut utiliser
3. Clarifier les capacités de planification et d'action autonome de chaque composant

## Données Open Foods Facts

- brands
- categories
- categories_tags
- compared_to_category (BEAUCOUP DE VALEURS NULLES)
- countries_tags
- ecoscore_grade
- ingredients_without_ciqual_codes








## See also

- [Building Effective Agents Cookbook](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents) from Anthropics
- [Introducing AgentWorkflow: A Powerful System for Building AI Agent Systems](https://www.llamaindex.ai/blog/introducing-agentworkflow-a-powerful-system-for-building-ai-agent-systems) from LlamaIndex, and 
  [here](https://docs.llamaindex.ai/en/stable/understanding/agent/multi_agents/)


---

---
sidebar_label: IFT-6005 Projet intégrateur
sidebar_position: 1
custom_edit_url: null
toc_min_heading_level: 2
toc_max_heading_level: 5
---

# IFT-6005 Projet intégrateur

## OpenFoodFacts

[Open Food Facts](https://en.openfoodfacts.org/) is a non-profit organisation that collects and shares information on food products from around the world. It is a collaborative project that relies on volunteers to collect data. Open Food Facts is the largest open food products database in the world, with over 3 million products in 200 countries.

Je comprends que :

- il existe une plateforme pour gérer les projets d'intelligence artificielle d'Open Food Facts = Robotoff

### Robotoff

#### Project Meeting Minutes

These meeting minutes document the development of Robotoff, an AI system for Open Food Facts.  The project focuses on improving data quality through automated tasks such as ingredient spellcheck, nutrition fact extraction, and image analysis.  Discussions cover model training, deployment, and integration with the Open Food Facts website and mobile app.  Significant progress is reported on several features, including object detection, language identification, and barcode normalization.  The team also explores using large language models (LLMs) for tasks like ingredient list correction and taxonomy generation.

#### Q1 

**Question** : Depuis 2023, quels projets impliquant du NLP et des LLMs attirent le plus d'attention?

Since 2023, the Robotoff project at Open Food Facts has focused on several NLP and LLM projects, with particular emphasis on:

- **Ingredient Spellcheck:** This project aims to improve the accuracy of ingredient lists by identifying and correcting misspelled ingredients.  Spellcheck is particularly important for ensuring the quality of data used for nutritional analysis and for improving the user experience.
- **Taxonomy Augmentation:** LLMs are being explored for enhancing Open Food Facts' taxonomies. Several potential use cases include:
  - Proposing translations for taxonomy entries.
  - Scoring existing translations
  - Retrieving properties on ingredients and additives.
  - Finding subcategories for taxonomies.
  - Converting categories to plural form.
  - Completing entries in different languages using Wikidata.
  - Predicting categories to understand correlations.
- **Extracting Ingredient Lists from OCR:** LLMs are being tested to extract ingredient lists directly from the output of Optical Character Recognition (OCR) applied to product images. This would streamline the process of adding ingredient information to the database.

Beyond these specific projects, there is a general interest in leveraging LLMs for various tasks:

- **Lowering Barriers to Entry for New Contributors:** LLMs could help make it easier for people without technical expertise to contribute to Open Food Facts.
- **Core Team/Community Productivity:** LLMs could be used for workflow automation and to increase productivity within the core team and the wider community. This could include tasks such as generating release notes from commits.
- **Generating Descriptions for Categories and Labels:** LLMs could be used to automatically generate descriptions for categories and labels. These descriptions could be aimed at different audiences, such as contributors who need to know which products belong in a category, or users who want to understand what a category represents.
- **Building the Encyclopedic Part of Open Food Facts:** LLMs could be used to generate summaries of food-related information from sources like Wikipedia and Wikidata. This could help build a comprehensive knowledge base about food within Open Food Facts.

There is also discussion about using LLMs for tasks such as:

- **Nutrition Fact Extraction:** This would involve using LLMs to extract nutritional information from images or text.
- **Moderation:** LLMs could potentially assist with moderating content on Open Food Facts, such as identifying inappropriate images or products.

However, there are also concerns about the limitations of LLMs, such as:

- **Hallucinations:** LLMs can sometimes generate incorrect or nonsensical information. This necessitates human oversight to ensure the accuracy of the outputs.
- **Cost:** Using proprietary LLMs like ChatGPT can be expensive, which could be a barrier for a non-profit organization like Open Food Facts.

Overall, there is significant interest in exploring the potential of NLP and LLMs to enhance various aspects of Open Food Facts. The focus is on developing innovative solutions that improve data quality, user experience, and community engagement. The sources emphasize the importance of human oversight and careful evaluation to address the limitations of LLMs and ensure their responsible use. 

#### Q2

**Question** : Parmi ces projets, lesquels semblent encore non résolus?

Several of the NLP and LLM projects discussed in the sources are still in progress or face ongoing challenges. Based on our conversation and the meeting minutes, the following projects seem unresolved:

- **Ingredient Spellcheck:** While this project has shown promising results, it is still under development. The sources mention issues with the training dataset, including limitations in size and language diversity.  There are also technical challenges related to the selection of appropriate LLMs and the need for efficient inference solutions on CPU or GPU. There's also discussion about how to best integrate the spellcheck functionality into the user interface and data processing pipeline.
  - Pretraining then fine-tuning (using LoRA)
  - Increase training dataset reviews to 1852
  - Using DPO (Direct Preference Optimization) on reviewed examples
  - Fine-tune Llama-3.1 on dataset v5.2
  - Estimate the RAM necessary to run fine-tuned Mistral 7B
  - inference time on CPU quantize models (int8, int4)
  - assess impact on performance 
  - Ajouter metadata sur jeu d’entraînement (image ID) et benchmark (barcode + image ID)
- **Extracting Ingredient Lists from OCR:** This project is in the experimental phase, with ongoing tests on fine-tuning LLMs for the task.  The sources highlight challenges in achieving accurate extraction, particularly for ingredient lists with complex formatting or multiple languages.
- **Nutrition Fact Extraction:** While there are existing models for detecting the presence of nutrition tables in images, the accuracy of extracting the actual nutritional data is still considered insufficient. The need for more training data and improved models is emphasized. 
- **Moderation:**  The idea of using LLMs for moderation is still in the discussion phase. The sources mention the need to define a clear workflow for using LLMs to identify and address issues such as inappropriate images or products. Concerns about potential bias and the need for human oversight are also highlighted.

It's important to note that the status of these projects may have evolved since the dates of the meeting minutes.  More recent information may be available on the Open Food Facts website or related project repositories. 

#### See also

- Robotoff OCR (vs GPT Vision)
- [robotoff](https://github.com/openfoodfacts/robotoff)
- [Meeting Minutes](https://docs.google.com/document/d/1RUfmWHjtFVaBcvQ17YfXu6FW6oRFWg-2lncljG0giKI/edit?tab=t.0#heading=h.f0lr73fq2mj8)
- [Tech Teams](https://wiki.openfoodfacts.org/Tech_Team)

### Ingredients spellcheck with LLM

- https://towardsdatascience.com/how-did-open-food-facts-use-open-source-llms-to-enhance-ingredients-extraction-d74dfe02e0e4
- https://www.youtube.com/watch?v=jR7ATF8WS2Q&list=PLjAH-USadsF1iZsIFOhYicWLkwA2Zfj5l&index=11
- https://github.com/openfoodfacts/openfoodfacts-ai/tree/develop/spellcheck
- https://huggingface.co/openfoodfacts/spellcheck-mistral-7b
- [Use large language models (LLM) to perform ingredient list spellcheck #314](https://github.com/openfoodfacts/openfoodfacts-ai/issues/314)
- [feat: Batch job - Spellcheck #1401](https://github.com/openfoodfacts/robotoff/pull/1401)
- [Artificial Intelligence @ Open Food Facts](https://github.com/orgs/openfoodfacts/projects/16)
- [Leveraging LLMs across Open Food Facts](https://github.com/orgs/openfoodfacts/projects/99/views/1)

### See also 

- [Site français Open Food Facts](https://fr.openfoodfacts.org/)
  - [Site canadien](https://ca-fr.openfoodfacts.org/)
- [Site](https://world.openfoodfacts.org/)
  - [Data](https://world.openfoodfacts.org/data)
  - [data-fields.txt](https://static.openfoodfacts.org/data/data-fields.txt)
  - [contribute](https://world.openfoodfacts.org/contribute)
- [Blog](https://blog.openfoodfacts.org/fr/)
- [GitHub Python](https://github.com/openfoodfacts/openfoodfacts-python)
- [Youtube Open Food Facts](https://www.youtube.com/@openfoodfacts1170)
- [Importer OpenFoodFacts dans PostgreSQL](https://blog-postgresql.verite.pro/2018/12/21/import-openfoodfacts.html)
- [Kaggle](https://www.kaggle.com/datasets/openfoodfacts/world-food-facts)
- [HuggingFace](https://huggingface.co/openfoodfacts)
- [FOSDEM 2024: The State of Open Food Facts](https://www.youtube.com/watch?v=uTfHJ9njbv0). Voir à 15h34 pour les liens.

- [Open Prices](https://raphodn.github.io/projects/openfoodfacts-prices)
  - https://prices.openfoodfacts.org
- Nutri-Score v2
- Nutrition ML / AI
- Google Cloud Vision API
- CIQUAL pour calculer la qualité nutritionnelle des aliments et afficher un nutri-score
- OpenFoodsFacts se concentre sur les produits emballés et exclut les produits frais notamment.
- Corriger l'erreur de qualité. Actuellement c'est fait manuellement.
- https://tools.myfooddata.com/nutrition-facts/403579/wt1
- Intelligence artificielle
  - Extraction automatique des listes d'ingrégients et des valeurs nutritionnelles à partir des étiquettes de produits alimentaires
  - Extraction automatique des données nutritionnelles 
- [Hunger Games](https://hunger.openfoodfacts.org/)


## LLM

- Hands-On Large Language Models

### See also

- [Fine-tuning Gemma 2 JPN for Yomigana with LoRA](https://www.kaggle.com/code/iamleonie/fine-tuning-gemma-2-jpn-for-yomigana-with-lora).
- [RAG](https://x.com/Sumanth_077/status/1879916261150491039)

## Projet 

https://x.com/akshay_pachaar/status/1882111426321617183

https://x.com/akshay_pachaar/status/1882111426321617183


----

# Plan 

## Résumé de la discussion concernant des projets étudiants en lien avec OpenFoodFacts

Louis, le représentant d'OpenFoodFacts, présente deux projets principaux aux étudiants du cours IFT-6005 (Projet intégrateur) :

- **Projet LLM/Agent conversationnel**
  - Création d'une interface conversationnelle pour interroger la base de données OpenFoodFacts
  - Permettrait aux utilisateurs de poser des questions en langage naturel sur les produits alimentaires
  - Pourrait potentiellement intégrer d'autres sources comme le Guide alimentaire canadien
  - Deux approches possibles discutées :
    - Connexion directe à la BD avec un agent LLM qui génère des requêtes
    - Entraînement d'un modèle sur les données existantes
  - Les étudiants Alain et Grégoire-Marie sont intéressés à travailler sur ce projet séparément, avec des approches potentiellement différentes
- **Projet Vision/Étiquettes**
  - Adaptation des modèles de reconnaissance d'étiquettes au contexte canadien
  - Particulièrement pertinent avec les changements de lois sur l'étiquetage en 2025
  - L'étudiant Dominique est potentiellement intéressé si son premier choix de projet (avec François) ne fonctionne pas
  
La discussion aborde également d'autres aspects :

- La possibilité d'utiliser la plateforme Valeria pour les expérimentations
- L'organisation pratique du cours (dates de remise, rencontres individuelles)
- L'accès à un Slack dédié pour la collaboration
- L'importance de l'autonomie des étudiants dans la réalisation de leurs projets

Le professeur Luc souligne que les étudiants ont la liberté d'explorer différentes approches techniques, 
même s'ils travaillent sur des projets similaires, comparant cela à différents artistes peignant le même sujet de manières distinctes.

## Description du projet LLM/Agent conversationnel

Dans le cadre du cours IFT-6005 Projet intégrateur, je dois réaliser un projet en intelligence artificielle.

Le projet que je souhaite faire concerne la création d'un agent conversationnel pour interroger la base de données Open Food Facts.

Je dois rédiger un rapport de description et de planification de projet.
Ce rapport doit décrire le mandat à réaliser
et l'approche que nous envisageons adopter pour effectuer votre mandat.  De plus, le rapport doit
nous donner une idée très claire des tâches à effectuer et de l'effort nécessaire pour les accomplir. 

Voir la document "Livrables du projet" en annexe pour plus
d'informations concernant cette évaluation. 

Le mandat est le suivant:

- Je veux pouvoir faire des requêtes en langage naturel sur ces données pour obtenir des informations sur les produits.
- Les requêtes peuvent être écrites en anglais ou en français ou tout autre langue.
- Les types de questions peuvent être variés, par exemple:
  - Quels sont les produits qui contiennent du sucre?
  - Quels produits comparables à celui-ci (disons Nutella) sont moins sucrés?
  - Quels sont les meilleurs produits pour une certaine catégorie de produits (ex. les meilleures céréales pour le petit déjeuner)?
  - Comparer les produits de deux marques différentes.
- Pour compléter la réponse, ou si la réponse n'est pas disponible dans la base de données Open Food Facts, le système pourrait 
  interroger d'autres sources comme le Guide alimentaire canadien qui est disponible sous la forme 
  d'un site Web (https://guide-alimentaire.canada.ca/fr/)
- Pour ce projet, j'utiliserai un système de type Agents RAG utilisant ollama et un ou plusieurs LLMs (dont mistral:7b).
- Un agent LLM générerait des requêtes à partir des questions posées par l'utilisateur.
- Idéalement, j'utiliserai [smolagents](https://huggingface.co/docs/smolagents/index) de HuggingFace.
- Le système peut répondre en texte (français, anglais...), en tableaux, en listes, et en utilisant des visualisations sur les données
- Le livrable au professeur prendrait la forme d'un dépôt github et d'un document pédagogique qui explique les différents types d'agents, comment le système a été construit et comment il fonctionne.
- On débuterait avec un cas simple et on ajouterait des fonctionnalités au fur et à mesure.
- On doit aussi pouvoir évaluer la qualité des réponses fournies par le système.

Le projet doit être réalisé en Python et exiger environ 100 heures de travail.

Proposes un rapport de description et de planification de projet entre 4 et 5 pages.

## Réponse


## Jeux de tests

Je vais détailler la stratégie de tests qui sera mise en place pour ce projet d'agent conversationnel.

Les jeux de tests seront organisés en plusieurs catégories :

1. **Tests unitaires**
   - Tests des fonctions de transformation des questions en requêtes SQL
   - Tests de parsing des résultats DuckDB
   - Tests de génération des visualisations
   - Tests de traduction/multilinguisme
   - Tests des agents individuels

2. **Tests d'intégration**
   - Communication entre les agents
   - Flux complet de traitement d'une requête
   - Intégration avec DuckDB
   - Intégration avec les LLMs via ollama

3. **Tests fonctionnels** avec un jeu de questions prédéfinies couvrant :
   - Questions simples sur un produit spécifique
     ```
     "Quelle est la teneur en sucre des céréales Cheerios?"
     "Combien y a-t-il de calories dans le Nutella?"
     ```
   - Questions de comparaison
     ```
     "Compare la teneur en sel des chips Lay's et Ruffles"
     "Quel yogourt nature contient le moins de gras?"
     ```
   - Questions d'analyse
     ```
     "Quels sont les 5 céréales pour petit déjeuner avec le meilleur ratio protéines/sucre?"
     "Classe les marques de pain selon leur teneur en fibres"
     ```
   - Questions multilingues
     ```
     "What is the sugar content of Cheerios cereal?"
     "¿Cuál es el contenido de azúcar de los cereales Cheerios?"
     ```
   - Questions complexes combinant plusieurs aspects
     ```
     "Parmi les barres de céréales contenant moins de 200 calories, 
      lesquelles ont le plus de protéines? Fais un graphique comparatif."
     ```

4. **Tests de robustesse**
   - Gestion des questions mal formulées
   - Gestion des données manquantes
   - Gestion des timeouts
   - Gestion des erreurs de connexion aux LLMs
   - Gestion des produits inconnus

5. **Tests de performance**
   - Temps de réponse pour différents types de requêtes
   - Utilisation de la mémoire
   - Tests de charge (plusieurs requêtes simultanées)

6. **Tests d'évaluation de la qualité des réponses**
   - Exactitude des informations fournies
   - Pertinence des visualisations proposées
   - Cohérence des réponses en différentes langues
   - Utilité des informations complémentaires du Guide alimentaire

Pour chaque catégorie, nous créerons :
- Un fichier YAML de cas de tests
- Des données de test spécifiques
- Des métriques d'évaluation
- Un script d'exécution automatique
- Un rapport de couverture de tests

Structure du dossier de tests :
```
tests/
  ├── unit/               # Tests unitaires
  ├── integration/        # Tests d'intégration
  ├── functional/         # Tests fonctionnels
  │   ├── queries/       # Jeux de questions
  │   └── expected/      # Réponses attendues
  ├── robustness/        # Tests de robustesse
  ├── performance/       # Tests de performance
  └── evaluation/        # Tests d'évaluation qualité
      ├── metrics/       # Définition des métriques
      └── results/       # Résultats des évaluations
```

Les résultats des tests seront :
- Intégrés dans le processus de CI/CD sur GitHub
- Documentés dans le rapport final
- Utilisés pour valider les critères de succès du projet
- Exploités pour identifier les points d'amélioration

Voulez-vous que je développe un aspect particulier de cette stratégie de tests ?

**Questions** : Mais les questions prédéfinis devront-elles avoir des réponses prédéfinies?

C'est une excellente question qui soulève un point important sur la validation des agents LLM. Il y a plusieurs approches possibles :

1. **Tests avec réponses exactes prédéfinies**
   - Pour les questions factuelles simples et directes
   - Ex: "Combien y a-t-il de calories dans 100g de Nutella?"
   - La réponse doit correspondre exactement à la valeur dans la base de données
   - Avantage : Validation automatique facile
   - Inconvénient : Très restrictif, ne teste pas la capacité de synthèse du LLM

2. **Tests avec validation structurelle**
   - On ne vérifie pas le texte exact mais plutôt que :
     - Les bonnes tables ont été interrogées
     - Les calculs sont corrects
     - Les produits mentionnés sont pertinents
     - La visualisation contient les bons éléments
   - Ex: Pour "Compare la teneur en sel des chips Lay's et Ruffles"
     - On vérifie que les deux marques sont présentes
     - Que les valeurs de sel sont correctes
     - Que la comparaison est logique
   - Plus flexible que la première approche

3. **Tests avec "Ground Truth" multiple**
   - Plusieurs réponses valides sont acceptables
   - On définit des critères de validation :
     - Informations obligatoires à inclure
     - Formats acceptables
     - Plages de valeurs correctes
   - Ex: Pour "Quelles sont les meilleures céréales pour le petit déjeuner?"
     - La réponse doit mentionner des critères nutritionnels
     - Inclure au moins 3-5 exemples de produits
     - Citer des valeurs nutritives correctes

4. **Tests par évaluation humaine**
   - Pour les questions complexes nécessitant du jugement
   - Utile pour valider :
     - La pertinence des recommandations
     - La qualité des explications
     - L'utilité des visualisations
   - Plus coûteux en temps mais nécessaire pour certains aspects

Je recommande une approche hybride :
- Tests automatiques avec réponses exactes pour les questions factuelles
- Tests structurels pour les comparaisons et analyses
- Validation humaine pour un sous-ensemble représentatif de questions complexes

Cette stratégie permet de :
- Assurer la fiabilité des informations de base
- Permettre une certaine flexibilité dans la formulation des réponses
- Valider la qualité globale du système
- Maintenir un équilibre entre automatisation et contrôle qualité

Qu'en pensez-vous ? Préféreriez-vous mettre l'accent sur un type particulier de validation ?

## Question 22 janvier 11h23

Ah, vous soulevez des points très pertinents ! Je comprends mieux maintenant la nécessité d'une approche avec agents.

En effet, selon le document "Introduction to Agents.pdf", un agent est défini comme "un programme où les sorties du LLM contrôlent le workflow". Il présente différents niveaux d'agentivité :

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

Donc vous avez raison - dès qu'un LLM a besoin d'accéder à des outils externes (comme une base de données) et de prendre des décisions sur le workflow, c'est effectivement un agent.

Je retire donc ma suggestion précédente. L'approche multi-agents initialement proposée est plus appropriée car :
1. Elle permet au LLM de prendre des décisions à chaque étape
2. Elle sépare logiquement les différentes responsabilités
3. Elle suit les patterns recommandés pour les systèmes LLM avec accès aux outils externes

Est-ce que cette explication clarifie la notion d'agent et justifie mieux l'approche multi-agents pour votre projet ?

## Question Multi-Agent

**Question** : Est-ce que l'agent principal de conversation serait un multi-agent qui coordonne les 3 autres agents?

Oui, exactement ! Selon le document "Introduction to Agents.pdf", c'est ce qu'on appelle un "Multi-Agent" de niveau ★★★, où "un workflow agentique peut en démarrer un autre".

L'agent principal de conversation serait un agent multi-étapes qui, selon la requête, déciderait :
1. S'il faut générer une requête SQL (appel à l'agent de génération de requêtes)
2. Si des informations complémentaires sont nécessaires (appel à l'agent d'enrichissement)
3. Si une visualisation aiderait à mieux comprendre (appel à l'agent de visualisation)

Le flux pourrait ressembler à ceci :

```python
class MainConversationAgent:
    def __init__(self):
        self.memory = []
        self.query_agent = QueryGenerationAgent()
        self.enrichment_agent = EnrichmentAgent()
        self.visualization_agent = VisualizationAgent()
        
    def process_query(self, user_query):
        self.memory = [user_query]
        
        while self.should_continue():
            # Le LLM décide de la prochaine action
            next_action = self.determine_next_action()
            
            if next_action.type == "GENERATE_SQL":
                result = self.query_agent.run(next_action.params)
            elif next_action.type == "ENRICH":
                result = self.enrichment_agent.run(next_action.params)
            elif next_action.type == "VISUALIZE":
                result = self.visualization_agent.run(next_action.params)
                
            self.memory.append((next_action, result))
        
        return self.format_final_response()
```

C'est donc une implémentation du pattern "Multi-Agent" où l'agent principal coordonne des agents spécialisés, chacun étant lui-même un "Tool Caller" de niveau ★★☆ qui peut utiliser des outils spécifiques (DuckDB, Guide alimentaire, matplotlib).

Cette hiérarchie d'agents permet de maintenir une séparation claire des responsabilités tout en gardant la flexibilité nécessaire pour gérer des requêtes complexes et imprévisibles. Le LLM principal peut adapter le workflow selon la nature de la question et les résultats intermédiaires obtenus.


-----

# Projet 

- https://x.com/svpino/status/1881336934418755862
- https://off.mieuxchoisir.org/defis
- https://github.com/DannyMac180/mirror-agent/blob/main/tools/deepseek_r1.py
- https://github.com/Doriandarko/deepseek-engineer/blob/main/r1.py
- https://gitingest.com/Doriandarko/deepseek-engineer
- https://guide-alimentaire.canada.ca/fr/



## Data



## Démarrer MongoDB sur macOS

Pour démarrer le service MongoDB, faire ceci :

```bash
brew tap mongodb/brew  # ajoutez le "tap" MongoDB :
brew install mongodb-community  # installez MongoDB Community Edition
brew services start mongodb-community  # démarrer le service
```
Vous devriez obtenir ceci :

```bash
$ brew services list                   
Name              Status  User  File
mongodb-community started alain ~/Library/LaunchAgents/homebrew.mxcl.mongodb-community.plist
unbound           none          
```

Le statut "started" pour mongodb-community indique que MongoDB est maintenant correctement démarré et fonctionne sur votre système.

Vous pouvez maintenant réessayer votre code Python initial. Il devrait fonctionner maintenant puisque le serveur MongoDB est en cours d'exécution.

Exécuter votre code Python initial

```python
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['test_db']
collection = db['test_collection']

# Insérer des données fictives
data = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "San Francisco"},
    {"name": "Charlie", "age": 35, "city": "Los Angeles"}
]

collection.insert_many(data)
print("Données insérées dans MongoDB")
```

Puis vérifier que les données sont bien insérées avec le shell MongoDB :

```bash
mongosh  
```

Puis dans le shell :

```javascript
use test_db
db.test_collection.find()
```


```txt
test> use test_db
switched to db test_db
test_db> db.test_collection.find()
[
  {
    _id: ObjectId('678aadcd4c2833f08652d133'),
    name: 'Alice',
    age: 30,
    city: 'New York'
  },
  {
    _id: ObjectId('678aadcd4c2833f08652d134'),
    name: 'Bob',
    age: 25,
    city: 'San Francisco'
  },
  {
    _id: ObjectId('678aadcd4c2833f08652d135'),
    name: 'Charlie',
    age: 35,
    city: 'Los Angeles'
  }
]
test_db> 
```

Cela devrait vous montrer les documents que vous avez insérés (Alice, Bob et Charlie).

Pour quitter le shell MongoDB, faire `quit()`.


## Agents

- [Introduction to Agents](https://huggingface.co/docs/smolagents/conceptual_guides/intro_agents)
- [smolagents](https://huggingface.co/docs/smolagents/index)
- [Beginner's Guide to RAG Agents with Prof. Tom Yeh](https://www.youtube.com/watch?v=181Esb2Ba8w)
- https://github.com/bodaay/HuggingFaceModelDownloader
- mlx-examples/llms/mlx_lm/LORA.md
- [Is MLX the best Fine Tuning Framework?](https://www.youtube.com/watch?v=BCfCdTp-fdM)
    
## Questions et réponses

### Q1 Question à DeepSeek

J'ai une base de données contenant des données sur 10000 produits alimentaires.
Je veux pouvoir faire des requêtes sur ces données pour obtenir des informations sur les produits.
Les requêtes peuvent être écrites en langage naturel, en anglais ou en français ou tout autre langue.
Les types de questions peuvent être variés, par exemple:
- Quels sont les produits qui contiennent du sucre?
- Quels produits comparables à celui-ci (disons Nutella) sont moins sucrés?
- Quels sont les meilleurs produits pour une certaine catégorie de produits (ex. les meilleures céréales pour le petit déjeuner)?
- Comparer les produits de deux marques différentes.
J'ai pensé à un système de type RAG utilisant ollama et mistral:7b.
Les données sont dans une base de données MongoDB.
Qu'en penses-tu?

**Réponse**

Votre idée d'utiliser un système de type RAG (Retrieval-Augmented Generation) avec **ollama** et **mistral:7b** pour interroger une base de données MongoDB contenant des informations sur des produits alimentaires est tout à fait pertinente. Voici une analyse détaillée de votre approche et quelques suggestions pour l'améliorer :

**1. Pourquoi RAG est une bonne solution**

Le modèle RAG combine deux éléments clés :
- **Retrieval (Recherche)** : Il permet d'extraire des informations pertinentes à partir d'une base de données structurée (comme MongoDB) en fonction de la requête de l'utilisateur.
- **Generation (Génération)** : Il utilise un modèle de langage (comme **mistral:7b**) pour formuler une réponse naturelle et cohérente à partir des données récupérées.

Cela convient parfaitement à votre cas d'utilisation, car :
- Les requêtes en langage naturel peuvent être complexes et variées.
- Vous avez besoin de réponses précises basées sur des données structurées.
- Le modèle peut générer des réponses fluides et adaptées au contexte.

**2. Intégration avec MongoDB**

MongoDB est une base de données NoSQL flexible, ce qui est idéal pour stocker des données sur des produits alimentaires, car :
- Les produits peuvent avoir des attributs variés (ingrédients, marque, catégorie, nutriments, etc.).
- Vous pouvez facilement ajouter ou modifier des champs sans restructurer toute la base de données.

Pour interroger MongoDB, vous pouvez utiliser des requêtes classiques (par exemple, avec `pymongo` en Python) pour extraire les données pertinentes avant de les passer au modèle de génération.

**3. Utilisation de mistral:7b avec ollama**

**mistral:7b** est un modèle de langage performant et léger, adapté pour des tâches de génération de texte. En l'utilisant avec **ollama**, vous pouvez :
- Charger le modèle localement ou sur un serveur.
- Lui fournir les données extraites de MongoDB pour générer des réponses en langage naturel.
- Personnaliser le modèle pour qu'il comprenne le contexte des produits alimentaires (par exemple, en le fine-tunant sur des données spécifiques).

**4. Défis potentiels et solutions**

**a. Complexité des requêtes en langage naturel**

Les utilisateurs peuvent poser des questions complexes, comme des comparaisons ou des recommandations. Pour gérer cela :
- Utilisez un système de **parsing** pour décomposer la requête en sous-requêtes (par exemple, identifier les filtres comme "moins sucré" ou "meilleures céréales").
- Enrichissez les données dans MongoDB avec des métadonnées (par exemple, des scores nutritionnels ou des catégories) pour faciliter les comparaisons.

**b. Qualité des réponses générées**

Le modèle peut parfois générer des réponses inexactes ou hallucinées. Pour améliorer cela :
- Limitez la génération à des données factuelles extraites de MongoDB.
- Ajoutez une étape de vérification pour valider les réponses avant de les retourner à l'utilisateur.

**c. Performance**

Avec 10 000 produits, les requêtes peuvent devenir lentes si elles ne sont pas optimisées. Pour cela :
- Indexez les champs fréquemment interrogés (par exemple, `ingrédients`, `marque`, `catégorie`).
- Utilisez des agrégations MongoDB pour prétraiter les données et accélérer les requêtes.

**5. Architecture proposée**

Voici une architecture possible pour votre système :

- **Interface utilisateur** : Permet à l'utilisateur de saisir des requêtes en langage naturel.
- **Module de parsing** : Analyse la requête pour en extraire les filtres et les intentions (par exemple, "moins sucré" → filtre sur le sucre).
- **Base de données MongoDB** : Stocke les données des produits alimentaires.
- **Module de retrieval** : Interroge MongoDB en fonction des filtres extraits.
- **Modèle mistral:7b** : Génère une réponse naturelle à partir des données récupérées.
- **Validation** : Vérifie la réponse avant de la retourner à l'utilisateur.

**6. Améliorations possibles**

- **Fine-tuning** : Fine-tunez **mistral:7b** sur des données spécifiques aux produits alimentaires pour améliorer sa compréhension du domaine.
- **Intégration de données externes** : Enrichissez vos données avec des informations provenant de sources externes (par exemple, des scores nutritionnels ou des avis clients).
- **Interface conviviale** : Ajoutez une interface graphique ou un chatbot pour faciliter l'interaction avec les utilisateurs.

**7. Outils et technologies recommandés**

- **Python** : Pour l'intégration entre MongoDB, le parsing des requêtes et le modèle de génération.
- **LangChain** : Un framework pour construire des applications RAG avec des modèles de langage.
- **FastAPI** ou **Flask** : Pour créer une API permettant d'interroger le système.
- **Docker** : Pour containeriser l'application et faciliter le déploiement.

**Conclusion**

Votre approche est solide et bien adaptée à votre cas d'utilisation. En combinant MongoDB pour le stockage des données, un modèle de langage comme **mistral:7b** pour la génération de réponses, et un système RAG pour lier les deux, vous pouvez créer un outil puissant et flexible pour interroger vos données. Avec quelques optimisations et une architecture bien pensée, vous obtiendrez un système performant et convivial.

### Q2 Peut-on envisager un tel système s'exécutant sur un téléphone cellulaire?

Faire fonctionner un système de type RAG (Retrieval-Augmented Generation) sur un téléphone cellulaire est techniquement possible, mais cela présente des défis importants, notamment en termes de performance, de mémoire et de puissance de calcul. Voici une analyse détaillée des possibilités et des limitations, ainsi que des suggestions pour rendre cela réalisable :

**1. Défis techniques**

**a. Taille du modèle**

- **mistral:7b** est un modèle de langage de 7 milliards de paramètres, ce qui nécessite une quantité importante de mémoire (plusieurs Go de RAM) et de puissance de calcul.
- Les téléphones cellulaires modernes ont des capacités limitées en termes de mémoire et de processeur, ce qui rend l'exécution de modèles de cette taille difficile.

**b. Base de données MongoDB**

- MongoDB est conçu pour fonctionner sur des serveurs ou des environnements cloud, pas directement sur des appareils mobiles.
- Interroger une base de données de 10 000 produits nécessite des ressources significatives, ce qui peut ralentir un téléphone.

**c. Latence et expérience utilisateur**

- Les modèles de langage et les requêtes de base de données peuvent introduire une latence importante, ce qui peut rendre l'expérience utilisateur peu fluide.

**2. Solutions possibles**

Pour rendre ce système réalisable sur un téléphone, voici quelques approches :

**a. Utiliser un modèle plus léger**

- Au lieu de **mistral:7b**, envisagez d'utiliser un modèle plus petit et optimisé pour les appareils mobiles, comme :
  - **Mistral-small** ou **Mistral-tiny** (versions réduites de Mistral).
  - **GPT-NeoX** ou **GPT-J** (versions légères).
  - **MobileBERT** ou **DistilBERT** (modèles spécialement conçus pour les appareils mobiles).
- Ces modèles sont moins gourmands en ressources tout en conservant une bonne capacité de génération.

**b. Utiliser une base de données embarquée**

- Au lieu de MongoDB, utilisez une base de données légère et embarquée comme **SQLite** ou **Realm**.
- Ces bases de données sont conçues pour fonctionner sur des appareils mobiles et peuvent stocker des données structurées de manière efficace.

**c. Délégation au cloud**

- Une approche plus réaliste consiste à déléguer les tâches intensives (comme l'exécution du modèle de langage et les requêtes de base de données) à un serveur cloud.
- Le téléphone enverrait les requêtes en langage naturel au serveur, qui renverrait les réponses générées.
- Cela permet de conserver une expérience utilisateur fluide tout en exploitant la puissance du cloud.

**d. Optimisation des données**

- Prétraitez et indexez les données pour minimiser la charge de traitement sur le téléphone.
- Par exemple, précalculez des scores nutritionnels ou des catégories pour accélérer les requêtes.

**3. Architecture pour un système mobile**

Voici une architecture possible pour un système mobile :

**a. Option 1 : Tout sur le téléphone**

1. **Base de données embarquée** : Utilisez SQLite ou Realm pour stocker les données des produits.
2. **Modèle léger** : Chargez un modèle de langage optimisé pour mobile (par exemple, MobileBERT).
3. **Interface utilisateur** : Une application mobile qui interroge la base de données et le modèle localement.

**Avantages** :

- Fonctionne hors ligne.
- Aucune dépendance à un serveur externe.

**Inconvénients** :

- Limité par les ressources du téléphone.
- Nécessite une optimisation poussée.

**b. Option 2 : Hybride (téléphone + cloud)**

1. **Téléphone** :
   - Interface utilisateur pour saisir les requêtes.
   - Envoi des requêtes au serveur cloud.
2. **Cloud** :
   - Base de données MongoDB.
   - Modèle de langage (mistral:7b ou autre).
   - Génération des réponses et renvoi au téléphone.

**Avantages** :

- Exploite la puissance du cloud.
- Expérience utilisateur fluide.

**Inconvénients** :

- Nécessite une connexion Internet.
- Coûts liés à l'utilisation du cloud.

**4. Technologies recommandées**

**Pour le téléphone** :

- **Flutter** ou **React Native** : Pour développer une application mobile multiplateforme.
- **SQLite** ou **Realm** : Pour une base de données embarquée.
- **TensorFlow Lite** ou **ONNX Runtime** : Pour exécuter des modèles de langage légers sur mobile.

**Pour le cloud** :

- **FastAPI** ou **Flask** : Pour créer une API de traitement des requêtes.
- **MongoDB Atlas** : Pour une base de données cloud.
- **Hugging Face Transformers** : Pour charger et exécuter des modèles de langage.

**5. Exemple de workflow hybride**

1. L'utilisateur saisit une requête en langage naturel dans l'application mobile.
2. L'application envoie la requête à une API cloud.
3. Le serveur cloud :
   - Analyse la requête.
   - Interroge la base de données MongoDB.
   - Génère une réponse avec le modèle de langage.
4. La réponse est renvoyée à l'application mobile et affichée à l'utilisateur.

**6. Conclusion**

Faire fonctionner un système RAG entièrement sur un téléphone cellulaire est possible, mais cela nécessite des compromis en termes de performance et de fonctionnalités. Une approche hybride, où les tâches intensives sont déléguées au cloud, est souvent la plus réaliste et la plus efficace. Si vous souhaitez une solution entièrement mobile, optez pour des modèles légers et des bases de données embarquées, mais soyez conscient des limitations.

### Q3 Développement en 3 étapes?

D'accord. Considérant la complexité du projet, crois-tu qu'on devrait développer une solution selon ces étapes :

1. D'abord, développer un premier prototype fonctionnant sur mon macbook pro
2. Ensuite développper une application en mode Hybride (téléphone + cloud)
3. Ensuite seulement, examiner comment faire sur téléphone seulement.

**Réponse**

Absolument, votre approche en trois étapes est très judicieuse et reflète une bonne pratique en développement de projets complexes. Voici pourquoi cette méthode est excellente, ainsi que des conseils pour chaque étape :

**Étape 1 : Prototype sur MacBook Pro**

**Pourquoi commencer par là ?**

- **Rapidité de développement** : Sur un MacBook Pro, vous avez accès à toutes les ressources nécessaires (CPU, GPU, mémoire) pour tester et itérer rapidement.
- **Validation du concept** : Cela vous permet de valider l'idée et de vérifier que le système RAG fonctionne comme prévu avant d'investir dans des solutions plus complexes.
- **Apprentissage** : Vous pouvez vous familiariser avec les technologies (MongoDB, mistral:7b, RAG) sans les contraintes d'un environnement mobile.

**Conseils pour cette étape :**

1. **Utilisez des outils simples** :
   - **LangChain** : Pour intégrer facilement MongoDB et mistral:7b dans un système RAG.
   - **Jupyter Notebook** : Pour prototyper rapidement et tester des requêtes.
2. **Commencez avec un sous-ensemble de données** :
   - Utilisez un échantillon de 100 à 1 000 produits pour accélérer les tests.
3. **Validez les cas d'utilisation** :
   - Testez les types de requêtes que vous souhaitez prendre en charge (recherche, comparaison, recommandation).
4. **Documentez les résultats** :
   - Notez les performances, les limites et les améliorations nécessaires.

**Étape 2 : Application hybride (téléphone + cloud)**

**Pourquoi passer à une application hybride ?**

- **Expérience utilisateur** : Une application mobile est plus accessible et pratique pour les utilisateurs finaux.
- **Scalabilité** : En déléguant le traitement au cloud, vous pouvez gérer des charges de travail plus importantes et des modèles plus complexes.
- **Flexibilité** : Vous pouvez mettre à jour le backend (cloud) sans avoir à modifier l'application mobile.

**Conseils pour cette étape :**

1. **Développez une API cloud** :
   - Utilisez **FastAPI** ou **Flask** pour créer une API qui gère les requêtes et interagit avec MongoDB et mistral:7b.
   - Déployez l'API sur un service cloud comme **AWS**, **Google Cloud** ou **Heroku**.
2. **Créez une application mobile** :
   - Utilisez **Flutter** ou **React Native** pour développer une application multiplateforme.
   - Intégrez l'API cloud pour envoyer des requêtes et recevoir des réponses.
3. **Optimisez les performances** :
   - Utilisez la mise en cache pour réduire la latence.
   - Limitez la taille des données échangées entre le téléphone et le cloud.
4. **Testez avec des utilisateurs réels** :
   - Recueillez des feedbacks pour améliorer l'interface et les fonctionnalités.

**Étape 3 : Examiner une solution entièrement mobile**

**Pourquoi attendre cette étape ?**

- **Complexité technique** : Faire fonctionner un système RAG entièrement sur un téléphone nécessite une optimisation poussée et des compromis.
- **Ressources limitées** : Les téléphones ont des contraintes de mémoire, de CPU et de batterie.
- **Priorisation** : Il est plus important de valider le concept et de fournir une première version fonctionnelle avant d'optimiser pour un environnement entièrement mobile.

**Conseils pour cette étape :**

1. **Évaluez les besoins** :
   - Est-ce que les utilisateurs ont vraiment besoin d'une solution hors ligne ?
   - Quelles sont les fonctionnalités essentielles à inclure dans la version mobile ?
2. **Optimisez le modèle et les données** :
   - Utilisez des modèles légers comme **MobileBERT** ou **DistilBERT**.
   - Compressez et prétraitez les données pour réduire leur taille.
3. **Testez sur plusieurs appareils** :
   - Assurez-vous que l'application fonctionne bien sur différents modèles de téléphones (iOS et Android).
4. **Explorez des alternatives** :
   - Si une solution entièrement mobile s'avère trop complexe, envisagez des solutions hybrides améliorées (par exemple, un mode hors ligne limité).

**Avantages de cette approche en trois étapes**

1. **Réduction des risques** :
   - Vous validez le concept et les technologies avant d'investir dans des solutions plus complexes.
2. **Apprentissage progressif** :
   - Vous acquérez de l'expérience à chaque étape, ce qui facilite le passage à l'étape suivante.
3. **Flexibilité** :
   - Si une étape ne fonctionne pas comme prévu, vous pouvez ajuster votre approche sans avoir tout à refaire.
4. **Livraison rapide d'une première version** :
   - Vous pouvez fournir une application hybride fonctionnelle rapidement, tout en travaillant sur une version entièrement mobile en parallèle.

**Conclusion**

Votre plan en trois étapes est une excellente stratégie pour développer un système RAG complexe. En commençant par un prototype sur MacBook Pro, en passant à une application hybride, puis en explorant une solution entièrement mobile, vous minimisez les risques et maximisez vos chances de succès. Chaque étape vous apportera des insights précieux pour améliorer le système et répondre aux besoins des utilisateurs. Bonne chance avec votre projet ! 🚀

### Q4 Quelles informations avant de débuter?

Excellent! Pour faire l'étape 1, tu as besoin de quelles informations avant de créer le code?

**Réponse**

Je suis ravi que vous trouviez l'approche utile ! Pour créer le prototype de l'**étape 1** (système RAG sur MacBook Pro), voici les informations dont j'aurais besoin pour vous proposer une solution sur mesure :

**1. Structure des données dans MongoDB**

- **Schéma de la base de données** :
  - Quels sont les champs stockés pour chaque produit (par exemple, `nom`, `marque`, `ingrédients`, `nutriments`, `catégorie`, etc.) ?
  - Y a-t-il des champs imbriqués ou des tableaux (par exemple, une liste d'ingrédients ou de nutriments) ?
- **Exemples de documents** :
  - Pouvez-vous fournir 2-3 exemples de documents JSON représentatifs de votre base de données ? Cela aidera à comprendre la structure et le contenu.

**2. Types de requêtes à supporter**

- **Cas d'utilisation principaux** :
  - Quels types de questions ou de requêtes souhaitez-vous prendre en charge ? Par exemple :
    - Recherche de produits par ingrédient (ex. "Quels produits contiennent du sucre ?").
    - Comparaison de produits (ex. "Comparer Nutella et une alternative moins sucrée").
    - Recommandations (ex. "Quelles sont les meilleures céréales pour le petit déjeuner ?").
- **Exemples de requêtes** :
  - Pouvez-vous fournir 3-5 exemples de requêtes en langage naturel que vous aimeriez que le système puisse gérer ?

**3. Technologies et outils préférés**

- **Langage de programmation** :
  - Avez-vous une préférence pour un langage (par exemple, Python) ?
- **Framework ou bibliothèques** :
  - Souhaitez-vous utiliser des outils spécifiques comme **LangChain**, **Hugging Face Transformers**, ou **PyMongo** ?
- **Environnement** :
  - Utilisez-vous un environnement de développement spécifique (par exemple, VS Code, Jupyter Notebook) ?

**4. Accès aux données et au modèle**

- **Accès à MongoDB** :
  - Comment puis-je accéder à votre base de données MongoDB ? Est-ce local (sur votre MacBook) ou dans le cloud (MongoDB Atlas) ?
  - Avez-vous des informations de connexion (URI, nom de la base de données, nom de la collection) ?
- **Modèle de langage** :
  - Souhaitez-vous utiliser **mistral:7b** ou un autre modèle (par exemple, GPT, LLaMA) ?
  - Avez-vous déjà installé et configuré le modèle localement, ou faut-il le faire ?

**5. Objectifs du prototype**

- **Fonctionnalités prioritaires** :
  - Quelles fonctionnalités doivent absolument être incluses dans le prototype ?
  - Y a-t-il des fonctionnalités secondaires que nous pouvons ajouter plus tard ?
- **Critères de succès** :
  - Comment saurez-vous que le prototype est réussi ? Par exemple :
    - Capacité à répondre à des requêtes spécifiques.
    - Performance (temps de réponse, précision des réponses).

**6. Contraintes techniques**

- **Ressources disponibles** :
  - Quelles sont les spécifications de votre MacBook Pro (RAM, CPU, GPU) ?
  - Avez-vous des contraintes de mémoire ou de puissance de calcul ?
- **Limites de temps** :
  - Avez-vous un délai pour la réalisation du prototype ?

**7. Autres informations utiles**

- **Données supplémentaires** :
  - Avez-vous des métadonnées ou des scores prédéfinis (ex. score nutritionnel, popularité) qui pourraient faciliter les requêtes ?
- **Intégrations futures** :
  - Avez-vous des plans pour intégrer ce système avec d'autres outils ou plateformes (ex. application mobile, site web) ?

**Exemple de résumé des informations nécessaires**

Pour vous donner une idée, voici un exemple de ce que je pourrais attendre comme informations :
1. **Structure des données** :
   - Collection : `produits`
   - Champs : `nom` (string), `marque` (string), `ingrédients` (liste de strings), `nutriments` (objet avec `sucre`, `graisse`, etc.), `catégorie` (string).
   - Exemple de document :
     ```json
     {
       "nom": "Nutella",
       "marque": "Ferrero",
       "ingrédients": ["sucre", "huile de palme", "noisettes", "cacao"],
       "nutriments": {
         "sucre": 56.3,
         "graisse": 30.9
       },
       "catégorie": "pâte à tartiner"
     }
     ```
2. **Types de requêtes** :
   - "Quels produits contiennent du sucre ?"
   - "Quelles pâtes à tartiner sont moins sucrées que Nutella ?"
   - "Quelles sont les meilleures céréales pour le petit déjeuner ?"
3. **Technologies** :
   - Langage : Python
   - Outils : LangChain, PyMongo, Hugging Face Transformers
4. **Accès aux données** :
   - MongoDB local sur MacBook Pro, collection `produits`.
5. **Objectifs** :
   - Répondre à des requêtes simples en langage naturel.
   - Afficher les résultats sous forme de liste de produits.

**Prochaines étapes**

Une fois que j'aurai ces informations, je pourrai :
1. Vous proposer une architecture détaillée pour le prototype.
2. Écrire le code initial pour interroger MongoDB et générer des réponses avec mistral:7b.
3. Vous guider dans l'installation et la configuration des outils nécessaires.

N'hésitez pas à me fournir ces détails, et nous pourrons commencer à construire le prototype ensemble ! 🚀


## See also 

- [Open Issues Canada](https://github.com/openfoodfacts/openfoodfacts-server/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22%F0%9F%87%A8%F0%9F%87%A6%20Canada%22%20)
- [Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Building Effective Agents Cookbook](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents) and [here](https://github.com/intellectronica/building-effective-agents-with-pydantic-ai) using Pydantic
- [PhiData](https://github.com/phidatahq/phidata)
- [Multi-Agent Order Management System with MongoDB](https://huggingface.co/learn/cookbook/mongodb_smolagents_multi_micro_agents)

## Trucs

### Medium 

Si je cherche un article Medium 

```txt
https://ai.gopubby.com/running-llms-locally-using-ollama-f17197f60450
https://archive.is/https://ai.gopubby.com/running-llms-locally-using-ollama-f17197f60450
```


## Agent LLM Studio

Ce texte vient de LLM Studio...

Some models (e.g. Llama 3.1/3.2, Mistral, Qwen and more) were trained to use tools.

What this means in practice is: you provide an array of 'tools' (function signatures) to the LLM in a very particular format, and the LLM can decide whether to 'call' them based on the user's prompt.

You can imagine use cases such as querying an API, running code, or really anything that can be expressed as a function call.

Models that were trained for tool use will perform better than others, but you can try to use tools with any model whatsoever. Read the 
to learn more. Models that were trained for tool use will be marked with a new badge:

LLMStudio me suggère Qwen2.5 14B Instruct MLX pour ce cas d'utilisation.

See: https://lmstudio.ai/docs/advanced/tool-use

https://github.com/PacktPublishing/LLM-Engineers-Handbook

https://github.com/microsoft/generative-ai-for-beginners

## Références 


### Article Speech-to-SQL

@article{song2024speech,
  title={Speech-to-SQL: toward speech-driven SQL query generation from natural language question},
  author={Song, Yuanfeng and Wong, Raymond Chi-Wing and Zhao, Xuefang},
  journal={The VLDB Journal},
  pages={1--23},
  year={2024},
  publisher={Springer}
}

Question: 

Pour un travail dans un cours universitaire, je dois trouver des articles académiques qui s'intéressent à ll'utilisation de LLM pour la génération de requêtes SQL à partir de questions en langage naturel.  J'ai besoin de 8 articles pertinents. Classe les articles suivants en ordre de pertinence pour mon projet :






Ces 5 articles sont pertinents. Ces articles réfèrent à d'autres articles cités en bibliographie qui peuvent être pertinents pour mon projet.

Passe en revue ces articles et identifie 10 autres articles qui pourraient être pertinents pour mon projet.



Cet article publié en 2022 présente un nouveau système nommé "Speech-to-SQL" qui permet de convertir directement la parole en requêtes SQL, sans passer par une transcription textuelle intermédiaire. Les points clés pertinents pour votre projet sont :

1. Architecture :
- Deux approches possibles : en cascade (parole → texte → SQL) ou directe (parole → SQL)
- L'approche en cascade souffre d'erreurs qui se propagent entre les composants
- L'approche directe obtient de meilleures performances en évitant ces erreurs

1. Composants principaux :
- Un encodeur de parole basé sur CNN
- Un encodeur de schéma de base de données utilisant des réseaux de neurones graphiques (GNN)
- Un décodeur SQL qui génère les requêtes
- Des mécanismes d'attention pour lier la parole aux éléments du schéma

1. Performances :
- Précision de 54,15% sur les requêtes générées 
- Gain de ~12% par rapport aux approches en cascade
- Plus rapide que la saisie manuelle de requêtes

Les enseignements pour votre projet :
- L'importance d'une architecture bien intégrée pour gérer le langage naturel et les requêtes SQL
- La nécessité de modéliser explicitement les relations entre les entrées en langage naturel et le schéma de la base de données
- L'intérêt des mécanismes d'attention pour lier les éléments du langage naturel aux éléments de la base de données

Est-ce que cet article utilise un LLM?

Non, cet article de 2022 n'utilise pas de LLM. Il emploie une architecture basée sur des réseaux de neurones plus traditionnels (CNN, GNN, LSTM) et des mécanismes d'attention. Cela s'explique par le fait que les LLM n'étaient pas encore largement utilisés pour ce type de tâche au moment de la recherche.




Oui exactement ! Le LLM devra analyser les données disponibles et raisonner sur la meilleure façon de fournir une réponse utile même en présence de données manquantes.

Par exemple, prenons une requête demandant "Quels sont les céréales avec un bon Nutri-Score ?" :

1. Le LLM générera d'abord une requête SQL pour obtenir les céréales avec leur Nutri-Score
2. En analysant les résultats, s'il constate que de nombreux produits n'ont pas de Nutri-Score, il devra :
   - Reconnaître que les données sont incomplètes
   - Déterminer quelles autres colonnes pourraient aider à estimer la qualité nutritionnelle (sucres, graisses saturées, fibres, protéines, etc.)
   - Générer une nouvelle requête SQL pour obtenir ces informations complémentaires
   - Utiliser ces données pour estimer la qualité nutritionnelle des produits sans Nutri-Score
3. Enfin, générer une réponse qui :
   - Présente les produits avec un Nutri-Score connu
   - Propose une estimation pour les autres produits
   - Explique clairement la méthode utilisée

Pour implémenter cela, il faudra :
1. Inclure dans le prompt des instructions sur la gestion des données manquantes
2. Donner au LLM accès à des informations sur les relations entre les différentes colonnes (par exemple, la formule du Nutri-Score)
3. Permettre au LLM de faire plusieurs requêtes SQL successives pour explorer les données disponibles

Cette approche rejoint les techniques mentionnées dans la littérature sur la robustesse des systèmes text-to-SQL face aux données incomplètes.


