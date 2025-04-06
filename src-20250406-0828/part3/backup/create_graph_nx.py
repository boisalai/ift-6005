#!/usr/bin/env python
# coding: utf-8

import os
import json
import time
import pandas as pd
import numpy as np
import networkx as nx
import pickle
from dotenv import load_dotenv
from tqdm import tqdm
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Chargement du modèle SentenceTransformer
print("Chargement du modèle SentenceTransformer...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Modèle SentenceTransformer chargé: all-MiniLM-L6-v2")

# Chemins pour la sauvegarde des graphes
script_dir = os.path.dirname(os.path.abspath(__file__))
GRAPH_DIR = os.path.join(script_dir, "../../data/graphs")
os.makedirs(GRAPH_DIR, exist_ok=True)

# Créer une instance de graphe NetworkX
G = nx.MultiDiGraph()  # Graphe dirigé qui permet des arêtes multiples entre les mêmes nœuds

def create_embedding(text):
    """Génère un embedding pour le texte donné en utilisant SentenceTransformer."""
    try:
        if not text or text.strip() == "":
            return None
            
        # Génération de l'embedding avec SentenceTransformer
        embedding = model.encode(text)
        
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
    if 'product_name' in product and product['product_name']:
        text_parts.append(f"Nom: {product['product_name']}")
    
    if 'generic_name' in product and product['generic_name']:
        text_parts.append(f"Nom générique: {product['generic_name']}")
    
    # Marque
    if 'brands' in product and product['brands']:
        text_parts.append(f"Marque: {product['brands']}")
    
    # Catégories
    if 'categories' in product and product['categories']:
        text_parts.append(f"Catégories: {product['categories']}")
    
    # Ingrédients
    if 'ingredients_text' in product and product['ingredients_text']:
        text_parts.append(f"Ingrédients: {product['ingredients_text']}")
    
    # Caractéristiques nutritionnelles
    if 'nutrient_levels' in product and product['nutrient_levels']:
        nutrient_text = ", ".join([f"{k}: {v}" for k, v in product['nutrient_levels'].items()])
        text_parts.append(f"Niveaux nutritionnels: {nutrient_text}")
    
    # Nutri-score et autres scores
    if 'nutriscore_grade' in product and product['nutriscore_grade']:
        text_parts.append(f"Nutri-Score: {product['nutriscore_grade']}")
    
    # Labels et certifications
    if 'labels' in product and product['labels']:
        text_parts.append(f"Labels: {product['labels']}")
    
    return " ".join(text_parts)

def create_product_nodes(products, batch_size=1000):
    """Crée les nœuds Product dans le graphe avec embeddings."""
    products_count = 0
    batches = [products[i:i + batch_size] for i in range(0, len(products), batch_size)]
    
    for batch in tqdm(batches, desc="Création des nœuds Product"):
        for product in batch:
            # Extraire les propriétés essentielles du produit
            product_data = {
                "code": product.get('code', ''),
                "name": product.get('product_name', ''),  # Valeur par défaut
                "product_name_en": product.get('product_name_en', product.get('product_name', '')),
                "product_name_fr": product.get('product_name_fr', product.get('product_name', '')),
                "generic_name": product.get('generic_name', ''),
                "quantity": product.get('quantity', ''),
                "nutriscore_grade": product.get('nutriscore_grade', ''),
                "nova_group": product.get('nova_group', ''),
                "ecoscore_grade": product.get('ecoscore_grade', ''),
                "type": "Product"  # Type de nœud pour les requêtes
            }
            
            # Générer le texte descriptif pour l'embedding
            embedding_text = get_product_embedding_text(product)
            
            # Générer l'embedding si nous avons un texte descriptif
            if embedding_text:
                embedding = create_embedding(embedding_text)
                if embedding:
                    product_data["embedding"] = embedding
            
            # Ajouter le nœud au graphe avec un identifiant unique basé sur le code
            node_id = f"Product-{product_data['code']}"
            G.add_node(node_id, **product_data)
            products_count += 1
            
    print(f"Ajouté {products_count} produits au total.")
    return products_count

def create_brand_nodes(products):
    """Crée les nœuds Brand et les relations HAS_BRAND."""
    brands_added = set()
    relations_count = 0
    
    for product in tqdm(products, desc="Création des nœuds Brand"):
        if 'brands' in product and product['brands']:
            brands = [brand.strip() for brand in product['brands'].split(',')]
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

def create_category_nodes(products):
    """Crée les nœuds Category et les relations HAS_CATEGORY."""
    categories_added = set()
    relations_count = 0
    
    for product in tqdm(products, desc="Création des nœuds Category"):
        if 'categories' in product and product['categories']:
            categories = [cat.strip() for cat in product['categories'].split(',')]
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

def create_ingredient_nodes(products):
    """Crée les nœuds Ingredient et les relations CONTAINS."""
    ingredients_added = set()
    relations_count = 0
    
    for product in tqdm(products, desc="Création des nœuds Ingredient"):
        if 'ingredients_tags' in product and product['ingredients_tags']:
            ingredients = product['ingredients_tags']
            product_node_id = f"Product-{product['code']}"
            
            for ingredient in ingredients:
                # Extraction du nom de l'ingrédient (enlever les préfixes comme "en:")
                ingredient_name = ingredient.split(':')[-1].replace('-', ' ').strip()
                
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

def create_label_nodes(products):
    """Crée les nœuds Label et les relations HAS_LABEL."""
    labels_added = set()
    relations_count = 0
    
    for product in tqdm(products, desc="Création des nœuds Label"):
        if 'labels_tags' in product and product['labels_tags']:
            labels = product['labels_tags']
            product_node_id = f"Product-{product['code']}"
            
            for label in labels:
                # Extraction du nom du label en retirant le préfixe "en:" et en normalisant
                label_name = label.split(':')[-1].replace('-', ' ').strip()
                
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

def create_additif_nodes(products):
    """Crée les nœuds Additif et les relations CONTAINS_ADDITIF."""
    additifs_added = set()
    relations_count = 0
    
    for product in tqdm(products, desc="Création des nœuds Additif"):
        if 'additives_tags' in product and product['additives_tags']:
            additives = product['additives_tags']
            product_node_id = f"Product-{product['code']}"
            
            for additif in additives:
                # Extraction du nom de l'additif (enlever les préfixes comme "en:")
                additif_name = additif.split(':')[-1].replace('-', ' ').strip()
                
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

def create_allergen_nodes(products):
    """Crée les nœuds Allergen et les relations CONTAINS_ALLERGEN."""
    allergens_added = set()
    relations_count = 0
    
    for product in tqdm(products, desc="Création des nœuds Allergen"):
        if 'allergens_tags' in product and product['allergens_tags']:
            allergens = product['allergens_tags']
            product_node_id = f"Product-{product['code']}"
            
            for allergen in allergens:
                # Extraction du nom de l'allergène (enlever les préfixes comme "en:")
                allergen_name = allergen.split(':')[-1].replace('-', ' ').strip()
                
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

def create_country_nodes(products):
    """Crée les nœuds Country et les relations SOLD_IN."""
    countries_added = set()
    relations_count = 0
    
    for product in tqdm(products, desc="Création des nœuds Country"):
        if 'countries_tags' in product and product['countries_tags']:
            countries = product['countries_tags']
            product_node_id = f"Product-{product['code']}"
            
            for country in countries:
                # Extraction du nom du pays (enlever les préfixes comme "en:")
                country_name = country.split(':')[-1].replace('-', ' ').strip()
                
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

def create_nutriment_nodes(products):
    """Crée les nœuds Nutriment et les relations HAS_NUTRIMENT."""
    nutriments_added = set()
    relations_count = 0
    
    nutriments_of_interest = [
        'energy', 'fat', 'saturated-fat', 'carbohydrates', 'sugars', 
        'fiber', 'proteins', 'salt', 'sodium', 'calcium', 'iron', 
        'vitamin-a', 'vitamin-c', 'vitamin-d'
    ]
    
    for product in tqdm(products, desc="Création des nœuds Nutriment"):
        if 'nutriments' in product and product['nutriments']:
            nutriments = product['nutriments']
            product_node_id = f"Product-{product['code']}"
            
            for nutriment in nutriments_of_interest:
                if nutriment in nutriments and nutriments[nutriment] is not None:
                    value = nutriments[nutriment]
                    unit = nutriments.get(f"{nutriment}_unit", "")
                    
                    if value:
                        # Normalisation du nom du nutriment
                        nutriment_name = nutriment.replace('-', ' ').strip()
                        
                        # Créer un identifiant unique pour le nœud nutriment
                        nutriment_node_id = f"Nutriment-{nutriment_name}"
                        
                        # Ajouter le nœud nutriment s'il n'existe pas déjà
                        if nutriment_node_id not in nutriments_added:
                            G.add_node(nutriment_node_id, name=nutriment_name, type="Nutriment")
                            nutriments_added.add(nutriment_node_id)
                        
                        # Ajouter la relation entre le produit et le nutriment avec la valeur et l'unité
                        G.add_edge(product_node_id, nutriment_node_id, type="HAS_NUTRIMENT", value=value, unit=unit)
                        relations_count += 1
    
    print(f"Ajouté {len(nutriments_added)} nœuds Nutriment et {relations_count} relations HAS_NUTRIMENT.")

def parse_taxonomy(file_path):
    """
    Parse un fichier de taxonomie pour extraire les relations parent-enfant
    et les traductions/synonymes (anglais et français).
    
    Args:
        file_path (str): Chemin vers le fichier de taxonomie
    
    Returns:
        dict: Dictionnaire où chaque clé est le nom de la catégorie parent (en anglais)
              et la valeur est une liste de dictionnaires pour les catégories enfants
    """
    taxonomy = {}
    block_lines = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line == "":
                    if block_lines:
                        process_taxonomy_block(block_lines, taxonomy)
                        block_lines = []
                elif not line.startswith("#"):  # Ignorer les commentaires
                    block_lines.append(line)
            
            # Traiter le dernier bloc s'il n'est pas terminé par une ligne vide
            if block_lines:
                process_taxonomy_block(block_lines, taxonomy)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier de taxonomie {file_path}: {e}")
    
    return taxonomy

def process_taxonomy_block(lines, taxonomy):
    """
    Traite un bloc de lignes correspondant à un ensemble de définitions pour une catégorie enfant.
    
    Args:
        lines (list): Liste de lignes à traiter
        taxonomy (dict): Dictionnaire de taxonomie à mettre à jour
    """
    parents = []
    child_canonical = None
    translations = {"en": [], "fr": []}
    synonyms = {"en": [], "fr": []}
    
    # Extraire d'abord tous les parents
    for line in lines:
        if line.startswith("< en:"):
            parent = line[len("< en:"):].strip()
            parents.append(parent)
    
    # Ensuite extraire le nom canonique et les traductions
    for line in lines:
        if ":" in line and not line.startswith("<") and not line.startswith("synonyms:") and not line.startswith("stopwords:"):
            lang, value = line.split(":", 1)
            lang = lang.strip()
            value = value.strip()
            
            # On ne conserve que les traductions anglaises et françaises
            if lang in ["en", "fr"]:
                # Pour l'anglais, la première occurrence sera le nom canonique
                if lang == "en" and child_canonical is None:
                    child_canonical = value
                
                # Ajouter à la liste des traductions
                if value not in translations[lang]:
                    translations[lang].append(value)
        
        # Extraire les synonymes
        elif line.startswith("synonyms:"):
            parts = line.split(":", 2)
            if len(parts) >= 3:
                lang = parts[1].strip()
                if lang in ["en", "fr"]:
                    syns = [s.strip() for s in parts[2].split(",")]
                    for syn in syns:
                        if syn and syn not in synonyms[lang]:
                            synonyms[lang].append(syn)
    
    # Ajouter les traductions à chaque parent
    if child_canonical and parents:
        # Combiner les traductions et les synonymes
        for lang in ["en", "fr"]:
            translations[lang].extend([s for s in synonyms[lang] if s not in translations[lang]])
        
        # Créer l'entrée pour chaque parent
        for parent in parents:
            entry = {"name": child_canonical, "translations": translations}
            taxonomy.setdefault(parent, []).append(entry)

def create_taxonomy_structures(script_dir):
    """
    Crée les structures hiérarchiques pour toutes les taxonomies supportées.
    
    Args:
        script_dir (str): Chemin du répertoire du script
    """
    # Configuration des taxonomies et types de relations
    taxonomies = [
        {
            "name": "categories",
            "file_name": "categories.txt",
            "node_type": "Category",
            "relation_type": "HAS_CHILD"
        },
        {
            "name": "ingredients",
            "file_name": "ingredients.txt",
            "node_type": "Ingredient",
            "relation_type": "CONTAINS"
        },
        {
            "name": "additives",
            "file_name": "additives.txt",
            "node_type": "Additif",
            "relation_type": "PART_OF"
        },
        {
            "name": "allergens",
            "file_name": "allergens.txt",
            "node_type": "Allergen",
            "relation_type": "BELONGS_TO"
        },
        {
            "name": "labels",
            "file_name": "labels.txt",
            "node_type": "Label",
            "relation_type": "INCLUDES"
        }
    ]
    
    taxonomy_dir = os.path.join(script_dir, "../../data/taxonomies")
    
    for taxonomy_info in taxonomies:
        file_path = os.path.join(taxonomy_dir, taxonomy_info["file_name"])
        
        if not os.path.exists(file_path):
            print(f"Fichier de taxonomie non trouvé: {file_path}")
            continue
        
        print(f"Traitement de la taxonomie {taxonomy_info['name']}...")
        
        # 1. Parser le fichier de taxonomie
        taxonomy_data = parse_taxonomy(file_path)
        
        # 2. Créer les relations hiérarchiques et ajouter les traductions
        node_type = taxonomy_info["node_type"]
        relation_type = taxonomy_info["relation_type"]
        relations_count = 0
        
        for parent, children in taxonomy_data.items():
            parent_node_id = f"{node_type}-{parent}"
            
            # S'assurer que le nœud parent existe
            if not G.has_node(parent_node_id):
                G.add_node(parent_node_id, name=parent, type=node_type)
            
            # Ajouter les traductions au nœud parent
            G.nodes[parent_node_id]['translations_en'] = []
            G.nodes[parent_node_id]['translations_fr'] = []
            
            for child in children:
                child_name = child["name"]
                child_node_id = f"{node_type}-{child_name}"
                
                # S'assurer que le nœud enfant existe
                if not G.has_node(child_node_id):
                    G.add_node(child_node_id, name=child_name, type=node_type)
                
                # Ajouter les traductions au nœud enfant
                if "translations" in child:
                    G.nodes[child_node_id]['translations_en'] = child["translations"].get("en", [])
                    G.nodes[child_node_id]['translations_fr'] = child["translations"].get("fr", [])
                
                # Créer la relation parent-enfant
                G.add_edge(parent_node_id, child_node_id, type=relation_type)
                relations_count += 1
        
        print(f"Ajouté {relations_count} relations {relation_type} pour {node_type}.")

def save_graph(graph, filename):
    """Sauvegarde le graphe dans un fichier pickle."""
    filepath = os.path.join(GRAPH_DIR, filename)
    
    with open(filepath, 'wb') as f:
        pickle.dump(graph, f)
        # NetworkX avec compression
        # pickle.dump(graph, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"Graphe sauvegardé dans {filepath}")

def load_graph(filename):
    """Charge un graphe depuis un fichier pickle."""
    filepath = os.path.join(GRAPH_DIR, filename)
    
    with open(filepath, 'rb') as f:
        graph = pickle.load(f)
    
    print(f"Graphe chargé depuis {filepath}")
    return graph

def search_similar_products(graph, query_text, limit=5):
    """
    Recherche des produits similaires à partir d'une requête textuelle.
    Utilise les embeddings pour trouver les produits sémantiquement proches.
    
    Args:
        graph: Graphe NetworkX contenant les produits
        query_text: Texte de la requête
        limit: Nombre maximum de résultats à retourner
        
    Returns:
        list: Liste des produits les plus similaires avec leurs scores
    """
    # Générer l'embedding pour la requête
    query_embedding = create_embedding(query_text)
    
    if not query_embedding:
        print("Impossible de générer l'embedding pour la requête.")
        return []
    
    # Convertir en numpy array pour les calculs de similarité
    query_embedding_np = np.array(query_embedding)
    
    # Parcourir tous les nœuds produits et calculer la similarité
    similarities = []
    for node_id, node_data in graph.nodes(data=True):
        if node_data.get('type') == 'Product' and 'embedding' in node_data:
            product_embedding = np.array(node_data['embedding'])
            
            # Calculer la similarité cosinus
            norm_q = np.linalg.norm(query_embedding_np)
            norm_p = np.linalg.norm(product_embedding)
            
            if norm_q > 0 and norm_p > 0:
                similarity = np.dot(query_embedding_np, product_embedding) / (norm_q * norm_p)
                
                # Stocker le résultat avec l'identifiant du produit
                similarities.append({
                    'id': node_id,
                    'code': node_data.get('code', ''),
                    'name': node_data.get('name', 'Nom inconnu'),
                    'generic_name': node_data.get('generic_name', ''),
                    'nutriscore_grade': node_data.get('nutriscore_grade', ''),
                    'score': float(similarity)
                })
    
    # Trier les résultats par score et limiter le nombre
    similarities.sort(key=lambda x: x['score'], reverse=True)
    return similarities[:limit]

def get_product_info(graph, product_id):
    """
    Récupère toutes les informations d'un produit, y compris ses relations.
    
    Args:
        graph: Graphe NetworkX
        product_id: ID du produit (code)
        
    Returns:
        dict: Informations complètes sur le produit
    """
    node_id = f"Product-{product_id}"
    
    if not graph.has_node(node_id):
        return {"error": f"Produit avec ID {product_id} non trouvé."}
    
    # Récupérer les propriétés du produit
    product_info = dict(graph.nodes[node_id])
    product_info["relations"] = {}
    
    # Récupérer toutes les relations sortantes
    for _, target, edge_data in graph.out_edges(node_id, data=True):
        relation_type = edge_data.get("type", "unknown")
        target_type = graph.nodes[target].get("type", "")
        target_name = graph.nodes[target].get("name", "")
        
        # Ajouter cette relation au dictionnaire des relations
        if relation_type not in product_info["relations"]:
            product_info["relations"][relation_type] = []
        
        relation_info = {
            "type": target_type,
            "name": target_name
        }
        
        # Ajouter les propriétés de la relation (comme value et unit pour les nutriments)
        for key, value in edge_data.items():
            if key != "type":
                relation_info[key] = value
        
        product_info["relations"][relation_type].append(relation_info)
    
    return product_info

def main():
    # Déterminer le chemin du fichier de données relatif au script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, "../../data/openfoodfacts-canadian-products.jsonl")
    
    print(f"Chargement des données depuis {data_file}...")
    products = []
    
    # Lire le fichier JSONL ligne par ligne
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Lecture du fichier"):
            try:
                product = json.loads(line)
                if 'code' in product and product['code']:
                    products.append(product)
            except json.JSONDecodeError:
                continue
    
    print(f"Nombre de produits chargés: {len(products)}")
    
    # Sélection d'un échantillon de produits pour le test (décommenter pour traiter tous les produits)
    # products = products[:1000]  # Limiter à 1000 produits pour le test
    print(f"Nombre de produits sélectionnés pour le traitement: {len(products)}")
    
    try:
        # Création des nœuds de produits avec embeddings
        create_product_nodes(products)
        
        # Création des autres nœuds et relations
        create_brand_nodes(products)
        create_category_nodes(products)
        create_ingredient_nodes(products)
        create_label_nodes(products)
        create_additif_nodes(products)
        create_allergen_nodes(products)
        create_country_nodes(products)
        create_nutriment_nodes(products)
        
        # Créer les relations hiérarchiques pour chaque type de taxonomie
        create_taxonomy_structures(script_dir)
        
        # Sauvegarder le graphe
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_graph(G, f"food_graph_{timestamp}.pkl")
        
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
        
        # Test de recherche sémantique
        print("\nTest de recherche sémantique:")
        results = search_similar_products(G, "Produit sans gluten riche en protéines", 5)
        for result in results:
            print(f"Produit: {result['name']}, Score: {result['score']:.4f}")
            print(f"Description: {result['generic_name']}")
            print(f"Nutri-Score: {result['nutriscore_grade']}\n")
            
        # Exemple d'utilisation pour récupérer des informations complètes sur un produit
        if results:
            first_result = results[0]
            product_code = first_result['code']
            print(f"\nInformation détaillée sur le produit {product_code}:")
            product_details = get_product_info(G, product_code)
            
            # Afficher quelques informations clés
            print(f"Nom: {product_details.get('name', 'N/A')}")
            print(f"Description: {product_details.get('generic_name', 'N/A')}")
            print(f"Nutriscore: {product_details.get('nutriscore_grade', 'N/A')}")
            
            # Afficher les marques associées
            if 'HAS_BRAND' in product_details.get('relations', {}):
                brands = [brand['name'] for brand in product_details['relations']['HAS_BRAND']]
                print(f"Marques: {', '.join(brands)}")
            
            # Afficher les catégories
            if 'HAS_CATEGORY' in product_details.get('relations', {}):
                categories = [cat['name'] for cat in product_details['relations']['HAS_CATEGORY']]
                print(f"Catégories: {', '.join(categories[:5])}" + ("..." if len(categories) > 5 else ""))
            
            # Afficher les allergènes s'il y en a
            if 'CONTAINS_ALLERGEN' in product_details.get('relations', {}):
                allergens = [allergen['name'] for allergen in product_details['relations']['CONTAINS_ALLERGEN']]
                print(f"Allergènes: {', '.join(allergens)}")
            else:
                print("Allergènes: Aucun")
            
    except Exception as e:
        print(f"Erreur lors du traitement: {e}")

if __name__ == "__main__":
    main()