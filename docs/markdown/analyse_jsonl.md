# Fichier JSONL 

```bash
$ wget https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz
$ gunzip openfoodfacts-products.jsonl.gz
$ ls -la *.jsonl
-rw-r--r--  1 alain  staff  58667548367 Mar  3 11:04 openfoodfacts-products.jsonl
```

## Analyse du fichier JSONL

Le script `analyse_jsonl.py` génère un fichier log contenant une analyse détaillée de la structure 
du fichier JSONL `openfoodfacts-products.jsonl`. Voici comment interpréter les principales sections de ce log :

### Informations générales

- **Taille du fichier** : 54.64 Go, ce qui confirme qu'il s'agit d'un fichier volumineux
- **Échantillon analysé** : 10 objets (défini par le paramètre `sample_size=10`)
- **Date et heure d'analyse** : 3 mars 2025 à 11:16:05

### Structure des données

Le log organise les clés trouvées par niveaux de profondeur :

- **Niveau de profondeur 0** : Ce sont les clés de premier niveau de chaque objet JSON
  - Il y a environ 120 clés au niveau 0, comme "_id", "code", "brands", "product_name", etc.
  - Pour chaque clé, le log indique :
    - Sa fréquence dans l'échantillon (ex: "10/10" signifie présente dans tous les objets)
    - Son type de données (str, int, float, list, dict, etc.)
- **Niveau de profondeur 1, 2, 3, etc.** : Ce sont les clés imbriquées
  - Par exemple, "nutriments.salt", "nutriscore.2023.grade" sont des clés de profondeur 1 et 2
  - La structure hiérarchique est clairement visible

### Contenu du jeu de données

Ce fichier contient des informations sur des produits alimentaires (Open Food Facts) avec :

- Informations générales sur les produits (nom, marque, code-barres)
- Données nutritionnelles (nutriments, scores nutritionnels)
- Ingrédients et allergènes
- Emballages et impact environnemental
- Classifications et catégories de produits
- Données sur les pays et langues

### Observations importantes

- **Données très structurées** : Le jeu de données présente une structure cohérente avec des champs standardisés
- **Richesse des champs** : Certains objets ont plus de 200 attributs quand on compte les champs imbriqués
- **Niveaux de profondeur** : Jusqu'à 6 niveaux d'imbrication dans certains cas (ex: scores environnementaux par pays)
- **Variabilité des données** : Toutes les clés ne sont pas présentes dans tous les objets (certaines sont marquées "9/10" ou moins)
- **Exemple d'objet** : À la fin du log, on trouve un exemple complet d'un objet du fichier (une pâte à tartiner Bovetti)

## Filtre 

Création d'un fichier JSONL filtré pour les produits canadiens.

```txt
Taille du fichier: 54.64 Go
Filtrage des produits: 3730362produits [08:03, 7720.61produits/s, total=3,730,000, filtrés=97,432, ratio=2.61%] 

Filtrage terminé!
Produits traités: 3,730,362
Produits canadiens: 97,439 (2.61%)
Fichier de sortie: ../../data/openfoodfacts-canadian-products.jsonl
```