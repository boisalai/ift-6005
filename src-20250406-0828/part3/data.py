import pandas as pd
import pyarrow.parquet as pq

# Charger et examiner un petit échantillon pour comprendre la structure
table = pq.read_table('../../data/food.parquet', memory_map=True)
sample = table.slice(0, 10).to_pandas()  # Juste 10 lignes

# Afficher toutes les colonnes
print("Colonnes:", table.column_names)

# Examiner la structure d'une ligne spécifique
print("\nStructure d'une ligne d'exemple:")
for colname in table.column_names:
    value = sample.iloc[0].get(colname, None)
    print(f"- {colname}: {type(value)}, {'iterable' if hasattr(value, '__iter__') and not isinstance(value, (str)) else 'scalar'}, {value}")

# Rechercher les produits canadiens dans le premier fragment
if 'countries_tags' in table.column_names:
    sample_tags = sample['countries_tags']
    print("\nExemple de countries_tags:")
    for i, tags in enumerate(sample_tags):
        print(f"Row {i}: {type(tags)}, {tags}")
        if isinstance(tags, list) and 'en:canada' in tags:
            print("  --> Produit canadien trouvé!")