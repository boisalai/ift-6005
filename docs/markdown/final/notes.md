Tu trouveras ci-joint les fichiers suivants :
- report.pdf et report.tex : le rapport de mi-session du projet, respectivement en version pdf et LaTeX.
- 2410.01066v1.pdf : un article sur l'utilisation des graphes de connaissances pour la recherche sémantique.
- create_nx_graph.py : le script pour créer un graphe NetworkX à partir du fichier parquet de Open Food Facts.
- evaluate_nx.py : le script pour évaluer les performances de l'agent DuckDB et de l'agent NetworkX sur le même ensemble de questions-réponses (qa_pairs.json), en anglais et en français.

Je souhaite que tu rédige en LateX une suite au rapport de mi-session, en ajoutant une partie 2 "Graphe de produits alimentaires avec recherche sémantique" avec un texte qui respecte ces consignes :

<texte>
Pour la seconde partie du projet, j'ai exploré l'utilisation d'un graphe avec recherche sémantique.

TODO: Expliquer pourquoi je pense qu'un graphe de connaissance avec recherche sémantique serait plus efficace qu'une base de données DuckDB
pour interroger les produits alimentaires. 

TODO: Faire un lien avec ce que dit l'article 2410.01066v1.pdf. Est-ce que cet article indique les avantages d'un graphe de connaissance avec recherche sémantique?
Si oui, expliquer en quoi cela est pertinent pour notre projet.

## Choix du graphe

Au début, j'ai utilisé Neo4j, base de données orientée graphe, pour créer un graphe de produits alimentaires à partir du fichier JSONL.
Après plusieurs tentatives avec Neo4j, j'ai constaté que le nombre de relations que je peux créé est limité avec la version gratuite de Neo4j.
Je devais donc limiter le nombre de produits canadiens, ce qui malheureusement rendait les analyses comparatives avec DuckdDB impossible.

J'ai essayé de charger tous les produits canadiens avec une version payante de Neo4j, mais le temps de création du graphe 
était démeusurément long sûrement parce que Neo4j est situé sur un serveur distant. 

Pour contourner les limitations de Neo4j, j'ai choisi NetworkX (https://networkx.org/) au lieu de Neo4j.
NetworkX est une bibliothèque Python open source pour la création, la manipulation et l'étude de la structure, de la dynamique et des fonctions des réseaux complexes.

Voici une comparaison de NetworkX et Neo4j :

TODO: Il faudrait simplifier le texte sur la compasaison de NetworkX et Neo4j
Pour évaluer la popularité de NetworkX et Neo4j, je vais comparer ces deux technologies selon différents critères pertinents dans le domaine des graphes.

## NetworkX

NetworkX est une bibliothèque Python pour la manipulation et l'analyse de graphes.

**Indicateurs de popularité :**
- **Adoption dans la communauté scientifique** : Très utilisé dans la recherche académique et l'analyse de données
- **GitHub** : Plus de 10 000 étoiles et de nombreux forks
- **Intégration** : S'intègre facilement dans l'écosystème Python de data science (NumPy, Pandas, scikit-learn)
- **Domaines d'utilisation** : Analyses de réseaux sociaux, bioinformatique, physique des réseaux, sciences sociales
- **Publication** : Cité dans de nombreux articles scientifiques

NetworkX est particulièrement apprécié pour sa simplicité d'utilisation, sa flexibilité, et son intégration transparente avec d'autres outils Python. Il est idéal pour le prototypage rapide et l'analyse de graphes de taille moyenne.

## Neo4j

Neo4j est une base de données orientée graphe avec son propre langage de requête (Cypher).

**Indicateurs de popularité :**
- **Adoption commerciale** : Leader des bases de données de graphes, utilisé par de nombreuses entreprises
- **Part de marché** : Domine le segment des bases de données de graphes
- **Communauté** : Grande communauté d'utilisateurs et nombreuses conférences dédiées
- **Stack Overflow** : Nombreuses questions et réponses
- **Cas d'utilisation** : Détection de fraude, recommandations, gestion des identités, réseaux sociaux

Neo4j est reconnu pour ses performances avec de grands graphes, sa robustesse en production, et ses capacités de visualisation intégrées.

## Comparaison

- **Cas d'usage** : NetworkX est privilégié pour l'analyse, l'expérimentation et la recherche, tandis que Neo4j est choisi pour les applications d'entreprise et les environnements de production
- **Échelle** : NetworkX convient aux graphes de petite à moyenne taille (mémoire limitée), Neo4j peut gérer des graphes beaucoup plus volumineux
- **Courbe d'apprentissage** : NetworkX est plus accessible pour les débutants maîtrisant Python, Neo4j nécessite l'apprentissage de Cypher
- **Écosystème** : NetworkX s'intègre à l'écosystème Python, Neo4j constitue son propre écosystème

Ces deux technologies sont complémentaires plutôt que concurrentes directes, car elles répondent à des besoins différents dans l'univers des graphes. NetworkX est plus présent dans le monde académique et l'analyse exploratoire, tandis que Neo4j domine dans les applications d'entreprise nécessitant une persistance et des performances à grande échelle.






J'ai créé un graphe de produits alimentaires en mémoire avec NetworkX, en utilisant le fichier parquet de Open Food Facts.
En utilisant la même source de données, les analyses comparatives de performance avec DuckDB seront possible.

Cette modification permet de créer et manipuler un graph de produits alimentaires entièrement en mémoire avec Python.

## Création du graphe

J'ai créé un script `create-graph-from-parquet.py` pour créer un graphe NetworkX à partir du même fichier parquet qui a été utilisé pour créer la base DuckDB. 

Les grandes étapes du fonctionnement du script sont les suivantes :

TODO: Corrige les étapes
1. Chargement du modèle SentenceTransformer pour la recherche sémantique
2. Chargement des données depuis le fichier parquet
3. Création des nœuds pour chaque type (Product, Brand, Category, etc.)
4. Établissement des relations entre les nœuds (HAS_BRAND, CONTAINS, etc.)
5. Traitement des taxonomies hiérarchiques (categories, ingredients, etc.)
6. Sauvegarde du graphe au format pickle pour une utilisation ultérieure
7. Affichage des statistiques du graphe


Voici quelques chiffres sur le graphe créé :


Le graphe NetworkX est bien chargé et contient toutes les données nécessaires pour répondre aux questions sur les additifs alimentaires. Voici une analyse détaillée :

Résumé du traitement:
Nombre total de produits canadiens: 94802
Produits sans additifs (additives_n = 0): 5843
Produits avec additifs (additives_n > 0): 10313
Produits sans info sur additifs: 78646
Graphe sauvegardé dans ../../data/graphs/food_graph_parquet_20250405_164654.pkl

Statistiques du graphe:
Nombre de nœuds: 160136
Nombre d'arêtes: 1499475

Nombre de nœuds par type:
- Product: 94802
- Brand: 10478
- Category: 7801
- Ingredient: 44617
- Label: 1827
- Additif: 347
- Allergen: 120
- Country: 130
- Nutriment: 14

Nombre d'arêtes par type:
- HAS_BRAND: 43149
- HAS_CATEGORY: 104451
- CONTAINS: 426820
- HAS_LABEL: 65159
- SOLD_IN: 101491
- HAS_NUTRIMENT: 697936
- CONTAINS_ADDITIF: 41146
- CONTAINS_ALLERGEN: 19323

Nombre de produits explicitement marqués sans additifs dans le graphe: 5843

## Évaluation de la performance des agents sur DuckDB et NetworkX

J'ai créé un script `evaluate_nx.py` pour évaluer les performances de l'agent DuckDB et de l'agent NetworkX sur le même ensemble de questions-réponses (qa_pairs.json), en anglais et en français.
Le script utilise le modèle LLM Claude Haiku (claude-3-5-haiku-20241022) de Anthropic pour évaluer les réponses des deux agents. 

Les grandes étapes de fonctionnement du script sont les suivantes :

TODO: Corrige, sinon bonifie les étapes suivantes
1. Créer et configurer les deux agents (DuckDB et NetworkX)
2. Tester les deux agents sur chaque question du jeu de test
3. Évaluer les réponses avec une combinaison de métriques automatiques (BLEU, ROUGE) et LLM
4. Générer un rapport comparatif détaillé avec :
   - Taux de réussite
   - Temps de réponse
   - Métriques détaillées de qualité des réponses

Cette évaluation vous permettra de déterminer si l'approche NetworkX offre des avantages en termes de performance ou de précision par rapport à l'approche DuckDB, vous aidant ainsi à choisir la meilleure solution pour votre projet final.

Ce script évalue les performances des deux agents sur un ensemble de questions-réponses prédéfini. Il mesure le temps de réponse, le taux de réussite et d'échec, ainsi que la qualité des réponses générées par chaque agent.
Il compare les réponses générées par chaque agent avec une référence et calcule des métriques de qualité (BLEU, ROUGE) ainsi qu'un score LLM.

Le script a été exécuté sur un MacBook Pro M1 avec 16 Go de RAM.

Les métriques d'évaluation sont les suivantes :

- **Taux de réussite (%)** : Pourcentage de questions pour lesquelles l'agent a fourni une réponse jugée correcte.
- **Taux d'échec (%)** : Pourcentage de questions pour lesquelles l'agent a rencontré une erreur technique ou n'a pas pu produire une réponse.
- **Temps moyen (s)** : Temps moyen en secondes pour répondre à chaque question.
- **Temps médian (s)** : Valeur médiane des temps de réponse (plus robuste aux valeurs extrêmes que la moyenne).
- **Score combiné moyen** : Moyenne des scores combinés (pondération de scores LLM, BLEU, ROUGE). Formule : ??? × score LLM + ??? × score BLEU-2 + ??? × score ROUGE-L
- **Score LLM moyen** : Score moyen attribué par le modèle de langage lors de l'évaluation des réponses.
- **BLEU-2 moyen** : Mesure de la précision des n-grammes (séquences de mots) entre la réponse générée et la référence. BLEU-2 utilise des unigrammes et bigrammes (séquences de 1 et 2 mots).
- **ROUGE-L moyen** : Mesure du rappel des plus longues sous-séquences communes entre la réponse et la référence. Évalue la fluidité et la couverture du contenu de référence.

## Résultats 

Les résultats de l'évaluation sont les suivants :

TODO: À compléter plus tard...

J'ai exécuté la commande `python evaluate_nx.py --limit 100 --lang fr --model claude`. Voici les résultats obtenus sur 100 questions-réponses en français :

TABLEAU RÉCAPITULATIF DES MÉTRIQUES
+----------------------+----------+------------+--------------+
| Métrique             |   DuckDB |   NetworkX | Différence   |
+======================+==========+============+==============+
| Taux de réussite (%) |  43      |    17      | 26.00        |
+----------------------+----------+------------+--------------+
| Taux d'échec (%)     |  21      |    48      | 27.00        |
+----------------------+----------+------------+--------------+
| Temps moyen (s)      |  26.37   |    26.69   | 0.32         |
+----------------------+----------+------------+--------------+
| Temps médian (s)     |  26.21   |    27.65   |              |
+----------------------+----------+------------+--------------+
| Score combiné moyen  |   0.34   |     0.19   | 0.15         |
+----------------------+----------+------------+--------------+
| Score LLM moyen      |   0.42   |     0.23   | 0.19         |
+----------------------+----------+------------+--------------+
| BLEU-2 moyen         |   0.0815 |     0.0398 | 0.0417       |
+----------------------+----------+------------+--------------+
| ROUGE-L moyen        |   0.1767 |     0.1144 | 0.0624       |
+----------------------+----------+------------+--------------+

J'ai exécuté la commande `python evaluate_nx.py --limit 100 --lang en --model claude`. Voici les résultats obtenus sur 100 questions-réponses en anglais :

TABLEAU RÉCAPITULATIF DES MÉTRIQUES
+----------------------+----------+------------+--------------+
| Métrique             |   DuckDB |   NetworkX | Différence   |
+======================+==========+============+==============+
| Taux de réussite (%) |  50      |    26      | 24.00        |
+----------------------+----------+------------+--------------+
| Taux d'échec (%)     |  17      |    49      | 32.00        |
+----------------------+----------+------------+--------------+
| Temps moyen (s)      |  26.58   |    29.94   | 3.36         |
+----------------------+----------+------------+--------------+
| Temps médian (s)     |  25.03   |    28.6    |              |
+----------------------+----------+------------+--------------+
| Score combiné moyen  |   0.37   |     0.25   | 0.13         |
+----------------------+----------+------------+--------------+
| Score LLM moyen      |   0.46   |     0.3    | 0.16         |
+----------------------+----------+------------+--------------+
| BLEU-2 moyen         |   0.0426 |     0.0331 | 0.0095       |
+----------------------+----------+------------+--------------+
| ROUGE-L moyen        |   0.1077 |     0.1023 | 0.0054       |
+----------------------+----------+------------+--------------+

## Interprétation des résultats

Les résultats montrent que l'agent DuckDB a un taux de réussite supérieur à celui de l'agent NetworkX, tant en français qu'en anglais. Cependant, le taux d'échec de l'agent NetworkX est plus élevé, ce qui indique qu'il a rencontré plus de problèmes techniques ou n'a pas pu produire de réponse.

Mais les résultats sont extrêmement faibles pour les deux agents. Lorsqu'on regarde les fichiers log, on constate que les deux agents ont souvent échoué à répondre à des questions pourtant simples. 
Il arrive aussi que les agents répondent avec une requête Cypher ou un script Python, ce qui n'est pas le but recherché.

Pour régler ce problème, il aurait fallu probablement utiliser un modèle encore plus performance que Claude Haiku, comme Claude 3.7 ou GPT-4.
Il aurait peut-être fallu augmenter le paramètre `max_steps` actuellement fixé à 5.

Mais les résulats NetworkX sont encore plus décevants.
L'agent NetworkX n'a pas été capable de répondre à la plupart des questions posées.
Ils semblent inférieurs à ceux nous aurions pu obtenir avec Neo4j. Lors des expérimentations précédentes, l'agent semblait capable de générer des requêtes Cypher sans trop de difficulté.

Contrairement à Neo4j où nous avons permis à l'agent de générer ses propres requêtes Cypher,
l'agent NetworkX doit utiliser une méthode parmi un ensemble de méthodes que nous avons préparée pour chaque type de question de l'utilisateur.
Nous n'avons pas laissé la liberté à l'agent écrire ses propres requêtes, lesquelles devaient être écrites en Python avec la bibliothèque `networkx`. 

Ainsi, il est probablement préférable de laisser l'agent écrire ses propres requêtes à la base de données 
plutôt que de lui imposer un ensemble de méthodes prédéfinies, lesquelles ne couvrent pas tous les cas d'utilisation possibles.

Dans d'autres cas, les agents ont fournis des réponses très élaborées, avec des informations pertinentes, mais le script d'évaluation ne les considèrerait pas comme correctes.
Dans ces cas, il aurait peut-être fallu préciser aux agents la structure de la réponse attendue, en donnant quelques exemples de réponses.
Il aurait fallu aussi procéder à une évaluation manuelle des réponses pour mieux comprendre les forces et les faiblesses de chaque agent.

Il est donc difficile de tirer des conclusions définitives sur la performance de l'agent NetworkX par rapport à l'agent DuckDB.

## Conclusion
TODO: À compléter 
</texte>

Je te laisse le soin de corriger et d'améliorer le texte.
Le style de cette seconde partie doit être similaire à celui de la première partie du rapport de mi-session.