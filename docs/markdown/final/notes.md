# Notes pour le rapport final

Pour la seconde partie du projet, j'ai exploré l'utilisation d'un graphe Neo4j avec recherche sémantique.

Après des expérimentations avec Neo4j, j'ai constaté que le nombre de relations que je peux créé est limité et le temps de création du graph 
est démeusurément long sûrement parce que Neo4j est situé sur un serveur distant. 

Alors j'ai choisi NetworkX (https://networkx.org/) au lieu de Neo4j.
Cette modification permet de créer et manipuler un graph de produits alimentaires entièrement en mémoire avec Python.

## Création du graph

Je vais compléter le code pour créer un graphe avec NetworkX au lieu de Neo4j.

J'ai créé un script `create-graph-from-parquet.py` pour créer un graphe NetworkX à partir du fichier parquet. Ce script reprend la même logique que votre script existant, mais l'adapte pour fonctionner entièrement en mémoire avec Python.

Voici quelques chiffres sur le graphe créé :




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



## Avantages principaux de cette solution

1. **Tout en Python** : Aucune dépendance externe à un serveur de base de données
2. **Léger et portable** : Fonctionne sur n'importe quelle machine avec Python
3. **Simple à utiliser** : Pas besoin de configurer des connexions ou des identifiants
4. **Persistance via pickle** : Sauvegarde et chargement simples du graphe entier

## Fonctionnalités clés

Le script offre les mêmes fonctionnalités que votre version Neo4j :

- Création de tous les types de nœuds (Product, Brand, Category, etc.)
- Établissement de toutes les relations (HAS_BRAND, CONTAINS, etc.)
- Support des taxonomies hiérarchiques
- Génération et utilisation d'embeddings pour les recherches sémantiques

J'ai exécuté le script et j'ai obtenus les messages suivants :

```txt
python create_graph_nx.py 
Chargement du modèle SentenceTransformer...
Modèle SentenceTransformer chargé: all-MiniLM-L6-v2
Chargement des données depuis /Users/alain/Workspace/GitHub/ift-6005/src/part3/../../data/openfoodfacts-canadian-products.jsonl...
Lecture du fichier: 97439it [00:35, 2739.50it/s]
Nombre de produits chargés: 97439
Nombre de produits sélectionnés pour le traitement: 97439
Création des nœuds Product: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 98/98 [15:19<00:00,  9.39s/it]
Ajouté 97439 produits au total.
Création des nœuds Brand: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 97439/97439 [00:01<00:00, 93412.81it/s]
Ajouté 11452 nœuds Brand et 46483 relations HAS_BRAND.
Création des nœuds Category: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 97439/97439 [00:00<00:00, 241214.23it/s]
Ajouté 8193 nœuds Category et 106268 relations HAS_CATEGORY.
Création des nœuds Ingredient: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 97439/97439 [00:01<00:00, 59392.30it/s]
Ajouté 45352 nœuds Ingredient et 442811 relations CONTAINS.
Création des nœuds Label: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 97439/97439 [00:01<00:00, 57369.13it/s]
Ajouté 1941 nœuds Label et 65917 relations HAS_LABEL.
Création des nœuds Additif: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 97439/97439 [00:00<00:00, 199451.84it/s]
Ajouté 352 nœuds Additif et 42711 relations CONTAINS_ADDITIF.
Création des nœuds Allergen: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 97439/97439 [00:00<00:00, 181229.56it/s]
Ajouté 128 nœuds Allergen et 20124 relations CONTAINS_ALLERGEN.
Création des nœuds Country: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 97439/97439 [00:00<00:00, 146461.39it/s]
Ajouté 126 nœuds Country et 104443 relations SOLD_IN.
Création des nœuds Nutriment: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 97439/97439 [00:02<00:00, 32933.86it/s]
Ajouté 14 nœuds Nutriment et 587996 relations HAS_NUTRIMENT.
Traitement de la taxonomie categories...
Ajouté 10099 relations HAS_CHILD pour Category.
Traitement de la taxonomie ingredients...
Ajouté 4516 relations CONTAINS pour Ingredient.
Traitement de la taxonomie additives...
Ajouté 115 relations PART_OF pour Additif.
Traitement de la taxonomie allergens...
Ajouté 0 relations BELONGS_TO pour Allergen.
Traitement de la taxonomie labels...
Ajouté 2078 relations INCLUDES pour Label.
Graphe sauvegardé dans /Users/alain/Workspace/GitHub/ift-6005/src/part3/../../data/graphs/food_graph_20250404_121527.pkl

Statistiques du graphe:
Nombre de nœuds: 177694
Nombre d'arêtes: 1433561

Nombre de nœuds par type:
- Product: 97439
- Brand: 11452
- Category: 15565
- Ingredient: 48393
- Label: 4065
- Additif: 512
- Allergen: 128
- Country: 126
- Nutriment: 14

Nombre d'arêtes par type:
- HAS_BRAND: 46483
- HAS_CATEGORY: 106268
- CONTAINS: 447327
- HAS_LABEL: 65917
- SOLD_IN: 104443
- HAS_NUTRIMENT: 587996
- CONTAINS_ADDITIF: 42711
- CONTAINS_ALLERGEN: 20124
- HAS_CHILD: 10099
- INCLUDES: 2078
- PART_OF: 115

Test de recherche sémantique:
Produit: Mélange pour produits de boulangerie proteinés, Score: 0.7016
Description: 
Nutri-Score: unknown

Produit: Proteine de Riz brun fermenté, Score: 0.6761
Description: 
Nutri-Score: unknown

Produit: Boisson fouetter source de protein, Score: 0.6645
Description: 
Nutri-Score: unknown

Produit: Barre de proteine, Score: 0.6559
Description: 
Nutri-Score: unknown

Produit: Poudre protéines de soya, Score: 0.6518
Description: 
Nutri-Score: unknown


Information détaillée sur le produit 0628055145318:
Nom: Mélange pour produits de boulangerie proteinés
Description: 
Nutriscore: unknown
Allergènes: Aucun
```




## Utilisation avec un agent LLM

Ce graphe peut facilement être utilisé avec un agent LLM. Vous pourriez créer un outil personnalisé comme celui-ci :

```python
class GraphQueryTool(Tool):
    name = "graph_query"
    description = "Interroge le graphe de produits alimentaires"
    
    def __init__(self, graph_path):
        self.graph = load_graph(graph_path)
        
    def forward(self, query: str) -> str:
        """Interprète une requête en langage naturel et recherche dans le graphe"""
        # Recherche sémantique
        if "similar" in query.lower() or "like" in query.lower():
            results = search_similar_products(self.graph, query, limit=5)
            return format_results(results)
            
        # Autres types de requêtes...
        # (recherche par marque, catégorie, etc.)
```

On doit faire pip install "networkx[default]"

## Comparaison avec Neo4j

| Aspect | NetworkX | Neo4j |
|--------|----------|-------|
| **Performance** | Excellente pour les petits-moyens graphes (<1M nœuds) | Meilleure pour très grands graphes |
| **Facilité** | Simple, tout en Python | Nécessite configuration serveur |
| **Requêtes** | API Python (pas de Cypher) | Langage Cypher |
| **Mémoire** | Tout en RAM | Stockage sur disque |
| **Déploiement** | Simple (fichier pickle) | Plus complexe |

## Améliorations possibles

Pour optimiser davantage, vous pourriez:

1. Ajouter des index en mémoire pour accélérer les recherches par attributs
2. Implémenter un mini-langage de requête inspiré de Cypher
3. Utiliser des formats plus efficaces que pickle (Arrow, Parquet)
4. Créer un chargement partiel/paresseux pour les très grands graphes

Vous pourrez maintenant créer et interroger un graphe complexe de produits alimentaires directement dans votre code Python, ce qui simplifiera grandement l'intégration avec votre agent LLM existant.


## 4 avril 16h50

Le graphe NetworkX est bien chargé et contient toutes les données nécessaires pour répondre aux questions sur les additifs alimentaires. Voici une analyse détaillée :

### Structure du graphe
- **Total de nœuds** : 177,694
- **Total d'arêtes** : 1,433,561
- **Additifs** : 512 nœuds de type Additif
- **Relations CONTAINS_ADDITIF** : 42,711 relations entre produits et additifs

## 4 avril 8h00

L'approche que vous utilisez actuellement (évaluation par LLM) et les métriques BLEU/ROUGE sont deux méthodes différentes pour évaluer la similarité des réponses, chacune ayant ses avantages et inconvénients.

### Comparaison des méthodes

**Votre méthode actuelle (évaluation par LLM):**
- **Avantages**:
  - Comprend le contexte sémantique et le sens profond
  - Peut identifier les informations équivalentes même si elles sont formulées très différemment
  - Tolère les variations de structure, d'ordre et de formulation
  - Évalue la justesse factuelle, pas juste la similarité lexicale
  
- **Inconvénients**:
  - Dépend de la qualité du modèle LLM utilisé
  - Peut être subjective ou inconsistante
  - Coûteuse en ressources et en temps
  - Binaire (oui/non) plutôt que nuancée

**Scores BLEU/ROUGE:**
- **Avantages**:
  - Métriques standard et reproductibles
  - Rapides à calculer
  - Ne nécessitent pas de modèle additionnel
  - Fournissent un score numérique continu (0-1)
  
- **Inconvénients**:
  - Basés principalement sur le recouvrement lexical (mots ou n-grammes communs)
  - Sensibles à l'ordre des mots et à la formulation exacte
  - Peuvent manquer des équivalences sémantiques
  - Ne considèrent pas la justesse factuelle

### Implémentation alternative avec BLEU/ROUGE

Voici comment vous pourriez implémenter une évaluation avec BLEU et ROUGE:

```python
def evaluate_agent_response_with_metrics(expected: str, actual: str) -> dict:
    """
    Évalue la réponse de l'agent en utilisant les métriques BLEU et ROUGE.
    
    Args:
        expected: Réponse attendue
        actual: Réponse de l'agent
        
    Returns:
        Dictionnaire contenant les scores BLEU et ROUGE
    """
    try:
        from nltk.translate.bleu_score import sentence_bleu
        from rouge import Rouge
        
        # Prétraitement des textes
        expected_tokens = expected.lower().split()
        actual_tokens = actual.lower().split()
        
        # Calcul du score BLEU
        # BLEU considère différentes longueurs de n-grammes (1, 2, 3, 4)
        weights_unigrams = (1, 0, 0, 0)  # Uniquement les unigrammes
        weights_bigrams = (0.5, 0.5, 0, 0)  # Unigrammes et bigrammes
        
        bleu_score_1 = sentence_bleu([expected_tokens], actual_tokens, weights=weights_unigrams)
        bleu_score_2 = sentence_bleu([expected_tokens], actual_tokens, weights=weights_bigrams)
        
        # Calcul des scores ROUGE
        rouge = Rouge()
        rouge_scores = rouge.get_scores(actual, expected)
        
        return {
            "bleu_1": bleu_score_1,
            "bleu_2": bleu_score_2,
            "rouge_1": rouge_scores[0]["rouge-1"]["f"],
            "rouge_2": rouge_scores[0]["rouge-2"]["f"],
            "rouge_l": rouge_scores[0]["rouge-l"]["f"]
        }
    except ImportError:
        print("Modules NLTK et/ou Rouge non installés. Exécutez: pip install nltk rouge")
        return {"error": "Modules requis non disponibles"}
```

### Approche hybride recommandée

Une solution idéale serait d'utiliser une approche hybride:

```python
def evaluate_agent_response_hybrid(expected: str, actual: str, model: LiteLLMModel, threshold: float = 0.5) -> dict:
    """Combine évaluation LLM et métriques automatiques."""
    
    # 1. Calcul des métriques automatiques
    metrics = evaluate_agent_response_with_metrics(expected, actual)
    
    # 2. Évaluation par LLM
    evaluator = CodeAgent(model=model, tools=[])
    prompt = f"""
    Compare ces deux réponses et détermine si la Réponse B contient l'information 
    factuelle principale de la Réponse A, même si la formulation est différente.

    Réponse A (référence): {expected}
    
    Réponse B (à évaluer): {actual}
    
    Évalue la correspondance sur une échelle de 0 à 5, où:
    0 = Complètement incorrect ou non pertinent
    1 = Minimal, manque la plupart des informations clés
    2 = Partiellement correct, avec des omissions importantes
    3 = Majoritairement correct, avec quelques omissions mineures
    4 = Presque parfait, informations complètes avec formulation différente
    5 = Parfait, toutes les informations clés sont présentes et correctes
    
    Réponds uniquement par un chiffre entre 0 et 5.
    """
    
    llm_score_str = evaluator.run(prompt)
    
    # Extraire le score numérique
    try:
        llm_score = float(llm_score_str.strip())
        llm_normalized = llm_score / 5.0  # Normaliser entre 0 et 1
    except ValueError:
        llm_normalized = 0.0
        
    # 3. Combiner les scores
    combined_score = (metrics.get("rouge_l", 0) * 0.3) + (metrics.get("bleu_2", 0) * 0.2) + (llm_normalized * 0.5)
    
    # 4. Déterminer si la réponse est correcte selon un seuil
    is_correct = combined_score >= threshold
    
    return {
        "is_correct": is_correct,
        "combined_score": combined_score,
        "llm_score": llm_normalized,
        "metrics": metrics
    }
```

Cette approche hybride:
1. Utilise à la fois les forces des métriques automatiques et de l'évaluation LLM
2. Fournit un score nuancé plutôt qu'une évaluation binaire
3. Permet une analyse plus détaillée des réponses
4. Offre plus de visibilité sur pourquoi une réponse est considérée correcte ou non

L'approche hybride serait supérieure aux deux méthodes individuelles car elle offre à la fois la rigueur des métriques statistiques et la compréhension sémantique des LLMs.

## 4 avril 8h52

Bien sûr, voici l'explication détaillée de chaque métrique dans votre tableau récapitulatif :

### Métriques de base

1. **Taux de réussite (%)** : 
   - Pourcentage de questions pour lesquelles l'agent a fourni une réponse jugée correcte.
   - Dans votre cas, 0% pour les deux agents signifie qu'aucune réponse n'a atteint le seuil de qualité fixé.

2. **Taux d'échec (%)** : 
   - Pourcentage de questions pour lesquelles l'agent a rencontré une erreur technique ou n'a pas pu produire une réponse.
   - 100% signifie que toutes les questions ont soit généré des erreurs, soit produit des réponses sous le seuil d'acceptation.

3. **Temps moyen (s)** : 
   - Temps moyen en secondes pour répondre à chaque question.
   - DuckDB (11.54s) est nettement plus rapide que Neo4j (42.96s), mais attention aux erreurs qui peuvent fausser cette métrique.

4. **Temps médian (s)** : 
   - Valeur médiane des temps de réponse (plus robuste aux valeurs extrêmes que la moyenne).
   - 34.62s pour DuckDB et 37.3s pour Neo4j, ce qui est plus proche et suggère des performances plus similaires que ce qu'indique la moyenne.

### Métriques d'évaluation hybride

5. **Score combiné moyen** : 
   - Moyenne des scores combinés (pondération de scores LLM, BLEU, ROUGE).
   - Formule : 0.5 × score LLM + 0.2 × score BLEU-2 + 0.3 × score ROUGE-L
   - DuckDB (0.10) obtient un meilleur score que Neo4j (0.02), mais les deux sont faibles.

6. **Score LLM moyen** : 
   - Score moyen attribué par le modèle de langage lors de l'évaluation des réponses.
   - 0 pour les deux agents signifie que le LLM a jugé toutes les réponses comme totalement incorrectes.

7. **BLEU-2 moyen** : 
   - Mesure de la précision des n-grammes (séquences de mots) entre la réponse générée et la référence.
   - BLEU-2 utilise des unigrammes et bigrammes (séquences de 1 et 2 mots).
   - DuckDB (0.1368) est supérieur à Neo4j (0.0273), indiquant un meilleur recouvrement lexical.

8. **ROUGE-L moyen** : 
   - Mesure du rappel des plus longues sous-séquences communes entre la réponse et la référence.
   - Évalue la fluidité et la couverture du contenu de référence.
   - DuckDB (0.2545) est meilleur que Neo4j (0.045).

### Interprétation globale

Ces résultats suggèrent que :

1. **Aucun agent n'atteint le seuil de qualité** défini (probablement 0.6 pour le score combiné).

2. **DuckDB surpasse Neo4j sur tous les aspects de qualité** (BLEU, ROUGE, score combiné), bien que les deux obtiennent des scores faibles.

3. **Neo4j est significativement plus lent** que DuckDB, ce qui pourrait indiquer des problèmes de connexion ou une complexité accrue des requêtes Cypher par rapport à SQL.

4. **Le score LLM de 0** suggère que le modèle LLM (Openchat) pourrait ne pas être adapté à l'évaluation ou que les réponses sont très éloignées de la référence.

Ces métriques vous permettent d'avoir une vision complète des performances et de la qualité des réponses générées par les deux agents, bien que dans ce cas précis, elles indiquent principalement des problèmes à résoudre.




Voici la suite du script d'évaluation :

Voilà ! Le script `evaluate_nx.py` est maintenant complet. Ce script vous permettra de comparer les performances entre votre agent DuckDB et votre nouvel agent NetworkX sur le même ensemble de questions-réponses.

## Comment utiliser le script

1. **Prérequis** :
   - Avoir déjà exécuté `create_graph_nx.py` pour générer un graphe NetworkX
   - Avoir un fichier de paires questions-réponses (`qa_pairs.json`)
   - Avoir les dépendances installées : duckdb, networkx, sentence-transformers, nltk, rouge, etc.

2. **Lancement** :
   ```bash
   python evaluate_nx.py --limit 10 --lang fr --model claude
   ```

3. **Options** :
   - `--limit N` : Limite le nombre de questions (utile pour les tests rapides)
   - `--lang [fr|en]` : Langue des questions et réponses
   - `--model [claude|openchat|mistral-openorca|openhermes]` : Choix du modèle LLM
   - `--output chemin/rapport.txt` : Sauvegarde le rapport de résultats

## Résultats attendus

Le script va :

1. Créer et configurer les deux agents (DuckDB et NetworkX)
2. Tester les deux agents sur chaque question du jeu de test
3. Évaluer les réponses avec une combinaison de métriques automatiques (BLEU, ROUGE) et LLM
4. Générer un rapport comparatif détaillé avec :
   - Taux de réussite
   - Temps de réponse
   - Métriques détaillées de qualité des réponses
5. Créer des visualisations pour faciliter la comparaison

Cette évaluation vous permettra de déterminer si l'approche NetworkX offre des avantages en termes de performance ou de précision par rapport à l'approche DuckDB, vous aidant ainsi à choisir la meilleure solution pour votre projet final.