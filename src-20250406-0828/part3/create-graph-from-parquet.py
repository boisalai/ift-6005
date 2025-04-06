#!/usr/bin/env python
# coding: utf-8

import os
import time
import pandas as pd
import numpy as np
import networkx as nx
import pickle
from tqdm import tqdm
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Chemins pour les fichiers de données et de sauvegarde
BASE_DIR = Path("../../data")
PARQUET_FILE = BASE_DIR / "food.parquet"
GRAPH_DIR = BASE_DIR / "graphs"
GRAPH_DIR.mkdir(exist_ok=True, parents=True)

# Chargement du modèle SentenceTransformer pour les embeddings
print("Chargement du modèle SentenceTransformer...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Modèle SentenceTransformer chargé: all-MiniLM-L6-v2")

# Créer une instance de graphe NetworkX
G = nx.MultiDiGraph()  # Graphe dirigé qui permet des arêtes multiples entre les mêmes nœuds

def create_embedding(text):
    """Génère un embedding pour le texte donné en utilisant SentenceTransformer."""
    try:
        if not text or str(text).strip() == "":
            return None
            
        # Génération de l'embedding avec SentenceTransformer
        embedding = model.encode(str(text))
        
        # Retourne l'embedding comme liste
        return embedding.tolist()
    except Exception as e:
        print(f"Erreur lors de la création d'embedding: {e}")
        return None

def get_product_embedding_text(product):
    """
    Génère un texte descriptif du produit pour l'embedding.
    Combine des informations pertinentes du produit.
    """
    text_parts = []
    
    # Nom et description du produit
    if 'product_name' in product and pd.notna(product.get('product_name')):
        text_parts.append(f"Nom: {product['product_name']}")
    
    if 'generic_name' in product and pd.notna(product.get('generic_name')):
        text_parts.append(f"Nom générique: {product['generic_name']}")
    
    # Marque
    if 'brands' in product and pd.notna(product.get('brands')):
        text_parts.append(f"Marque: {product['brands']}")
    
    # Catégories
    if 'categories' in product and pd.notna(product.get('categories')):
        text_parts.append(f"Catégories: {product['categories']}")
    
    # Ingrédients
    if 'ingredients_text' in product and pd.notna(product.get('ingredients_text')):
        text_parts.append(f"Ingrédients: {product['ingredients_text']}")
    
    # Caractéristiques nutritionnelles
    if 'nutrient_levels' in product and pd.notna(product.get('nutrient_levels')) and isinstance(product.get('nutrient_levels'), dict):
        nutrient_text = ", ".join([f"{k}: {v}" for k, v in product['nutrient_levels'].items()])
        text_parts.append(f"Niveaux nutritionnels: {nutrient_text}")
    
    # Nutri-score et autres scores
    if 'nutriscore_grade' in product and pd.notna(product.get('nutriscore_grade')):
        text_parts.append(f"Nutri-Score: {product['nutriscore_grade']}")
    
    # Labels et certifications
    if 'labels' in product and pd.notna(product.get('labels')):
        text_parts.append(f"Labels: {product['labels']}")
    
    return " ".join(text_parts)

def create_product_nodes(df):
    """Crée les nœuds Product dans le graphe avec embeddings."""
    products_count = 0
    
    for _, product in tqdm(df.iterrows(), desc="Création des nœuds Product", total=len(df)):
        # Extraire le nom du produit
        product_name = ""
        if isinstance(product.get('product_name'), np.ndarray) and len(product.get('product_name')) > 0:
            # Chercher d'abord le texte en français
            fr_names = [item.get('text', '') for item in product.get('product_name') if item.get('lang') == 'fr']
            if fr_names:
                product_name = fr_names[0]
            else:
                # Sinon prendre le premier texte disponible
                main_names = [item.get('text', '') for item in product.get('product_name') if item.get('lang') == 'main']
                if main_names:
                    product_name = main_names[0]
                elif len(product.get('product_name')) > 0 and 'text' in product.get('product_name')[0]:
                    product_name = product.get('product_name')[0]['text']
        
        # Propriétés du produit
        product_data = {
            "code": str(product.get('code', '')),
            "name": product_name,
            "generic_name": str(product.get('generic_name', '')) if not isinstance(product.get('generic_name'), np.ndarray) else "",
            "quantity": str(product.get('quantity', '')),
            "nutriscore_grade": str(product.get('nutriscore_grade', '')),
            "nova_group": float(product.get('nova_group')) if pd.notna(product.get('nova_group')) else -1,
            "ecoscore_grade": str(product.get('ecoscore_grade', '')),
            "additives_n": float(product.get('additives_n')) if pd.notna(product.get('additives_n')) else -1,
            "type": "Product"
        }
        
        # Générer un texte simple pour l'embedding
        text_parts = []
        
        # Ajouter le nom du produit
        if product_name:
            text_parts.append(f"Nom: {product_name}")
        
        # Ajouter la marque si disponible
        if pd.notna(product.get('brands')):
            text_parts.append(f"Marque: {product.get('brands')}")
        
        # Ajouter les catégories si disponibles
        if pd.notna(product.get('categories')):
            text_parts.append(f"Catégories: {product.get('categories')}")
        
        embedding_text = " ".join(text_parts)
        
        # Générer l'embedding si nous avons un texte descriptif
        if embedding_text:
            embedding = create_embedding(embedding_text)
            if embedding:
                product_data["embedding"] = embedding
        
        # Marquer explicitement les produits sans additifs
        if pd.notna(product.get('additives_n')) and product.get('additives_n') == 0:
            product_data["has_additives"] = False
        elif pd.notna(product.get('additives_n')) and product.get('additives_n') > 0:
            product_data["has_additives"] = True
        
        # Ajouter le nœud au graphe
        node_id = f"Product-{product_data['code']}"
        G.add_node(node_id, **product_data)
        products_count += 1
    
    print(f"Ajouté {products_count} produits au total.")
    return products_count

def create_brand_nodes(df):
    """Crée les nœuds Brand et les relations HAS_BRAND."""
    brands_added = set()
    relations_count = 0
    
    for _, product in tqdm(df.iterrows(), desc="Création des nœuds Brand", total=len(df)):
        if pd.notna(product.get('brands')) and product['brands']:
            brands = [brand.strip() for brand in str(product['brands']).split(',')]
            product_node_id = f"Product-{product['code']}"
            
            for brand in brands:
                if brand:
                    # Créer un identifiant unique pour le nœud marque
                    brand_node_id = f"Brand-{brand}"
                    
                    # Ajouter le nœud marque s'il n'existe pas déjà
                    if brand_node_id not in brands_added:
                        G.add_node(brand_node_id, name=brand, type="Brand")
                        brands_added.add(brand_node_id)
                    
                    # Ajouter la relation entre le produit et la marque
                    G.add_edge(product_node_id, brand_node_id, type="HAS_BRAND")
                    relations_count += 1
    
    print(f"Ajouté {len(brands_added)} nœuds Brand et {relations_count} relations HAS_BRAND.")

def create_category_nodes(df):
    """Crée les nœuds Category et les relations HAS_CATEGORY."""
    categories_added = set()
    relations_count = 0
    
    for _, product in tqdm(df.iterrows(), desc="Création des nœuds Category", total=len(df)):
        if pd.notna(product.get('categories')) and product['categories']:
            categories = [cat.strip() for cat in str(product['categories']).split(',')]
            product_node_id = f"Product-{product['code']}"
            
            for category in categories:
                if category:
                    # Créer un identifiant unique pour le nœud catégorie
                    category_node_id = f"Category-{category}"
                    
                    # Ajouter le nœud catégorie s'il n'existe pas déjà
                    if category_node_id not in categories_added:
                        G.add_node(category_node_id, name=category, type="Category")
                        categories_added.add(category_node_id)
                    
                    # Ajouter la relation entre le produit et la catégorie
                    G.add_edge(product_node_id, category_node_id, type="HAS_CATEGORY")
                    relations_count += 1
    
    print(f"Ajouté {len(categories_added)} nœuds Category et {relations_count} relations HAS_CATEGORY.")

def create_ingredient_nodes(df):
    """Crée les nœuds Ingredient et les relations CONTAINS."""
    ingredients_added = set()
    relations_count = 0
    
    for _, product in tqdm(df.iterrows(), desc="Création des nœuds Ingredient", total=len(df)):
        # Vérifier si le champ ingredients_tags existe et est une liste numpy
        if ('ingredients_tags' in df.columns and 
            product.get('ingredients_tags') is not None and  # Vérification d'existence
            not pd.isna(product.get('ingredients_tags')).all() and  # Vérification que tout n'est pas NaN
            isinstance(product['ingredients_tags'], np.ndarray)):
            
            ingredients = product['ingredients_tags']
            product_node_id = f"Product-{product['code']}"
            
            for ingredient in ingredients:
                # Extraction du nom de l'ingrédient (enlever les préfixes comme "en:")
                ingredient_name = str(ingredient).split(':')[-1].replace('-', ' ').strip()
                
                if ingredient_name:
                    # Créer un identifiant unique pour le nœud ingrédient
                    ingredient_node_id = f"Ingredient-{ingredient_name}"
                    
                    # Ajouter le nœud ingrédient s'il n'existe pas déjà
                    if ingredient_node_id not in ingredients_added:
                        G.add_node(ingredient_node_id, name=ingredient_name, type="Ingredient")
                        ingredients_added.add(ingredient_node_id)
                    
                    # Ajouter la relation entre le produit et l'ingrédient
                    G.add_edge(product_node_id, ingredient_node_id, type="CONTAINS")
                    relations_count += 1
    
    print(f"Ajouté {len(ingredients_added)} nœuds Ingredient et {relations_count} relations CONTAINS.")

def create_label_nodes(df):
    """Crée les nœuds Label et les relations HAS_LABEL."""
    labels_added = set()
    relations_count = 0
    
    for _, product in tqdm(df.iterrows(), desc="Création des nœuds Label", total=len(df)):
        # Vérifier si le champ labels_tags existe et est une liste numpy
        if ('labels_tags' in df.columns and 
            product.get('labels_tags') is not None and 
            not pd.isna(product.get('labels_tags')).all() and 
            isinstance(product['labels_tags'], np.ndarray)):
            
            labels = product['labels_tags']
            product_node_id = f"Product-{product['code']}"
            
            for label in labels:
                # Extraction du nom du label en retirant le préfixe "en:" et en normalisant
                label_name = str(label).split(':')[-1].replace('-', ' ').strip()
                
                if label_name:
                    # Créer un identifiant unique pour le nœud label
                    label_node_id = f"Label-{label_name}"
                    
                    # Ajouter le nœud label s'il n'existe pas déjà
                    if label_node_id not in labels_added:
                        G.add_node(label_node_id, name=label_name, type="Label")
                        labels_added.add(label_node_id)
                    
                    # Ajouter la relation entre le produit et le label
                    G.add_edge(product_node_id, label_node_id, type="HAS_LABEL")
                    relations_count += 1
    
    print(f"Ajouté {len(labels_added)} nœuds Label et {relations_count} relations HAS_LABEL.")

def create_additif_nodes(df):
    """Crée les nœuds Additif et les relations CONTAINS_ADDITIF."""
    additifs_added = set()
    relations_count = 0
    
    for _, product in tqdm(df.iterrows(), desc="Création des nœuds Additif", total=len(df)):
        # Important: ajouter une vérification explicite pour additives_n = 0
        has_additives = pd.notna(product.get('additives_n')) and product['additives_n'] > 0
        
        # Vérifier si le champ additives_tags existe et est une liste numpy
        if ('additives_tags' in df.columns and 
            product.get('additives_tags') is not None and 
            not pd.isna(product.get('additives_tags')).all() and 
            isinstance(product['additives_tags'], np.ndarray) and 
            has_additives):
            
            additives = product['additives_tags']
            product_node_id = f"Product-{product['code']}"
            
            for additif in additives:
                # Extraction du nom de l'additif (enlever les préfixes comme "en:")
                additif_name = str(additif).split(':')[-1].replace('-', ' ').strip()
                
                if additif_name:
                    # Créer un identifiant unique pour le nœud additif
                    additif_node_id = f"Additif-{additif_name}"
                    
                    # Ajouter le nœud additif s'il n'existe pas déjà
                    if additif_node_id not in additifs_added:
                        G.add_node(additif_node_id, name=additif_name, type="Additif")
                        additifs_added.add(additif_node_id)
                    
                    # Ajouter la relation entre le produit et l'additif
                    G.add_edge(product_node_id, additif_node_id, type="CONTAINS_ADDITIF")
                    relations_count += 1
    
    print(f"Ajouté {len(additifs_added)} nœuds Additif et {relations_count} relations CONTAINS_ADDITIF.")
    
    # Ajouter une relation explicite pour les produits sans additifs
    zero_additives_count = 0
    for _, product in tqdm(df.iterrows(), desc="Marquage des produits sans additifs", total=len(df)):
        if pd.notna(product.get('additives_n')) and product['additives_n'] == 0:
            product_node_id = f"Product-{product['code']}"
            # Vérifier si le nœud existe
            if G.has_node(product_node_id):
                # Marquer explicitement comme produit sans additifs
                G.nodes[product_node_id]['has_additives'] = False
                zero_additives_count += 1
    
    print(f"Marqué {zero_additives_count} produits sans additifs (additives_n = 0).")

def create_allergen_nodes(df):
    """Crée les nœuds Allergen et les relations CONTAINS_ALLERGEN."""
    allergens_added = set()
    relations_count = 0
    
    for _, product in tqdm(df.iterrows(), desc="Création des nœuds Allergen", total=len(df)):
        # Vérifier si le champ allergens_tags existe et est une liste numpy
        if ('allergens_tags' in df.columns and 
            product.get('allergens_tags') is not None and 
            not pd.isna(product.get('allergens_tags')).all() and 
            isinstance(product['allergens_tags'], np.ndarray)):
            
            allergens = product['allergens_tags']
            product_node_id = f"Product-{product['code']}"
            
            for allergen in allergens:
                # Extraction du nom de l'allergène (enlever les préfixes comme "en:")
                allergen_name = str(allergen).split(':')[-1].replace('-', ' ').strip()
                
                if allergen_name:
                    # Créer un identifiant unique pour le nœud allergène
                    allergen_node_id = f"Allergen-{allergen_name}"
                    
                    # Ajouter le nœud allergène s'il n'existe pas déjà
                    if allergen_node_id not in allergens_added:
                        G.add_node(allergen_node_id, name=allergen_name, type="Allergen")
                        allergens_added.add(allergen_node_id)
                    
                    # Ajouter la relation entre le produit et l'allergène
                    G.add_edge(product_node_id, allergen_node_id, type="CONTAINS_ALLERGEN")
                    relations_count += 1
    
    print(f"Ajouté {len(allergens_added)} nœuds Allergen et {relations_count} relations CONTAINS_ALLERGEN.")

def create_country_nodes(df):
    """Crée les nœuds Country et les relations SOLD_IN."""
    countries_added = set()
    relations_count = 0
    
    for _, product in tqdm(df.iterrows(), desc="Création des nœuds Country", total=len(df)):
        # Vérifier si le champ countries_tags existe et est une liste numpy
        if ('countries_tags' in df.columns and 
            product.get('countries_tags') is not None and 
            not pd.isna(product.get('countries_tags')).all() and 
            isinstance(product['countries_tags'], np.ndarray)):
            
            countries = product['countries_tags']
            product_node_id = f"Product-{product['code']}"
            
            for country in countries:
                # Extraction du nom du pays (enlever les préfixes comme "en:")
                country_name = str(country).split(':')[-1].replace('-', ' ').strip()
                
                if country_name:
                    # Créer un identifiant unique pour le nœud pays
                    country_node_id = f"Country-{country_name}"
                    
                    # Ajouter le nœud pays s'il n'existe pas déjà
                    if country_node_id not in countries_added:
                        G.add_node(country_node_id, name=country_name, type="Country")
                        countries_added.add(country_node_id)
                    
                    # Ajouter la relation entre le produit et le pays
                    G.add_edge(product_node_id, country_node_id, type="SOLD_IN")
                    relations_count += 1
    
    print(f"Ajouté {len(countries_added)} nœuds Country et {relations_count} relations SOLD_IN.")

def create_nutriment_nodes(df):
    """Crée les nœuds Nutriment et les relations HAS_NUTRIMENT."""
    nutriments_added = set()
    relations_count = 0
    
    nutriments_of_interest = [
        'energy', 'fat', 'saturated-fat', 'carbohydrates', 'sugars', 
        'fiber', 'proteins', 'salt', 'sodium', 'calcium', 'iron', 
        'vitamin-a', 'vitamin-c', 'vitamin-d'
    ]
    
    for _, product in tqdm(df.iterrows(), desc="Création des nœuds Nutriment", total=len(df)):
        # Vérifier si le champ nutriments existe et est un tableau numpy
        if ('nutriments' in df.columns and 
            product.get('nutriments') is not None and 
            not pd.isna(product.get('nutriments')).all() and 
            isinstance(product['nutriments'], np.ndarray)):
            
            nutriments_list = product['nutriments']
            product_node_id = f"Product-{product['code']}"
            
            # Convertir la liste de nutriments en dictionnaire pour faciliter l'accès
            nutriments_dict = {}
            for nutriment_obj in nutriments_list:
                if isinstance(nutriment_obj, dict) and 'name' in nutriment_obj:
                    name = nutriment_obj['name']
                    nutriments_dict[name] = nutriment_obj
            
            for nutriment_name in nutriments_of_interest:
                if nutriment_name in nutriments_dict:
                    nutriment_obj = nutriments_dict[nutriment_name]
                    value = nutriment_obj.get('100g')
                    unit = nutriment_obj.get('unit', '')
                    
                    if pd.notna(value):
                        # Normalisation du nom du nutriment
                        normalized_name = nutriment_name.replace('-', ' ').strip()
                        
                        # Créer un identifiant unique pour le nœud nutriment
                        nutriment_node_id = f"Nutriment-{normalized_name}"
                        
                        # Ajouter le nœud nutriment s'il n'existe pas déjà
                        if nutriment_node_id not in nutriments_added:
                            G.add_node(nutriment_node_id, name=normalized_name, type="Nutriment")
                            nutriments_added.add(nutriment_node_id)
                        
                        # Ajouter la relation entre le produit et le nutriment avec la valeur et l'unité
                        G.add_edge(product_node_id, nutriment_node_id, 
                                   type="HAS_NUTRIMENT", 
                                   value=value, 
                                   unit=unit)
                        relations_count += 1
    
    print(f"Ajouté {len(nutriments_added)} nœuds Nutriment et {relations_count} relations HAS_NUTRIMENT.")

def save_graph(graph, filename):
    """Sauvegarde le graphe dans un fichier pickle."""
    filepath = GRAPH_DIR / filename
    
    with open(filepath, 'wb') as f:
        pickle.dump(graph, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"Graphe sauvegardé dans {filepath}")

def main():
    # Charger les données du fichier parquet par morceaux
    print(f"Chargement des données depuis {PARQUET_FILE}...")
    try:
        # Utiliser PyArrow pour plus d'efficacité en mémoire
        import pyarrow.parquet as pq
        
        # Lire les métadonnées sans charger toutes les données
        table = pq.read_table(PARQUET_FILE, memory_map=True)
        print(f"Fichier parquet chargé avec succès. Nombre de lignes: {table.num_rows}")
        
        # Afficher les informations sur les colonnes
        print("Colonnes disponibles:")
        for col in table.column_names:
            print(f"- {col}")
        
        # Définir la taille des fragments pour le traitement
        chunk_size = 5000  # Ajuster selon la RAM disponible
        total_rows = table.num_rows
        chunks = total_rows // chunk_size + (1 if total_rows % chunk_size != 0 else 0)
        
        print(f"Traitement du fichier en {chunks} fragments de {chunk_size} lignes...")
        
        # Vérifier la présence des colonnes importantes
        critical_columns = ['countries_tags', 'additives_n', 'additives_tags']
        for col in critical_columns:
            if col not in table.column_names:
                print(f"ATTENTION: La colonne '{col}' n'existe pas dans le fichier parquet.")
        
        # Statistiques pour les additifs
        products_with_additives = 0
        products_without_additives = 0
        products_no_info = 0
        total_canadian = 0
        
        # Traiter le fichier par fragments
        for i in range(chunks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, total_rows)
            print(f"\nTraitement du fragment {i+1}/{chunks} (lignes {start}-{end})...")
            
            # Lire un fragment
            df_chunk = table.slice(start, end - start).to_pandas()
            
            # Filtrer pour les produits canadiens
            if 'countries_tags' in df_chunk.columns:
                # Créer une fonction pour vérifier si le Canada est dans la liste des pays
                def has_canada(countries):
                    if isinstance(countries, np.ndarray) and countries.size > 0:
                        return np.any([str(country) == 'en:canada' for country in countries])
                    return False
                
                # Appliquer la fonction aux pays de chaque produit
                canada_chunk = df_chunk[df_chunk['countries_tags'].apply(has_canada)]
                
                if len(canada_chunk) > 0:
                    print(f"  Trouvé {len(canada_chunk)} produits canadiens dans ce fragment")
                    total_canadian += len(canada_chunk)
                    
                    # Analyser les additifs dans ce fragment
                    if 'additives_n' in canada_chunk.columns:
                        products_without_additives += len(canada_chunk[canada_chunk['additives_n'] == 0])
                        products_with_additives += len(canada_chunk[canada_chunk['additives_n'] > 0])
                        products_no_info += len(canada_chunk[canada_chunk['additives_n'].isna()])
                    
                    # Ajouter ce fragment au graphe
                    print("  Création des nœuds product...")
                    create_product_nodes(canada_chunk)
                    print("  Création des relations...")
                    create_brand_nodes(canada_chunk)
                    create_category_nodes(canada_chunk)
                    create_ingredient_nodes(canada_chunk)
                    create_label_nodes(canada_chunk)
                    create_additif_nodes(canada_chunk)
                    create_allergen_nodes(canada_chunk)
                    create_country_nodes(canada_chunk)
                    create_nutriment_nodes(canada_chunk)
            
            # Libérer explicitement la mémoire
            del df_chunk
            if 'canada_chunk' in locals():
                del canada_chunk
            import gc
            gc.collect()
        
        # Résumé des statistiques d'additifs
        print("\nRésumé du traitement:")
        print(f"Nombre total de produits canadiens: {total_canadian}")
        if 'additives_n' in table.column_names:
            print(f"Produits sans additifs (additives_n = 0): {products_without_additives}")
            print(f"Produits avec additifs (additives_n > 0): {products_with_additives}")
            print(f"Produits sans info sur additifs: {products_no_info}")
        
        # Sauvegarder le graphe
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_graph(G, f"food_graph_parquet_{timestamp}.pkl")
        
        # Afficher quelques statistiques
        print("\nStatistiques du graphe:")
        print(f"Nombre de nœuds: {G.number_of_nodes()}")
        print(f"Nombre d'arêtes: {G.number_of_edges()}")
        
        # Compter les nœuds par type
        node_types = {}
        for _, data in G.nodes(data=True):
            node_type = data.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print("\nNombre de nœuds par type:")
        for node_type, count in node_types.items():
            print(f"- {node_type}: {count}")
        
        # Compter les arêtes par type
        edge_types = {}
        for _, _, data in G.edges(data=True):
            edge_type = data.get('type', 'unknown')
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        print("\nNombre d'arêtes par type:")
        for edge_type, count in edge_types.items():
            print(f"- {edge_type}: {count}")
            
        # Vérifier combien de produits sont marqués sans additifs
        no_additives_count = sum(1 for _, data in G.nodes(data=True) 
                               if data.get('type') == 'Product' and data.get('has_additives') is False)
        print(f"\nNombre de produits explicitement marqués sans additifs dans le graphe: {no_additives_count}")
        
    except Exception as e:
        print(f"Erreur lors du traitement: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()