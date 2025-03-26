#!/usr/bin/env python
# coding: utf-8

import os
import json
import time
import pandas as pd
import numpy as np
from neo4j import GraphDatabase
from dotenv import load_dotenv
from tqdm import tqdm
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Chargement du modèle SentenceTransformer
print("Chargement du modèle SentenceTransformer...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Modèle SentenceTransformer chargé: all-MiniLM-L6-v2")

# Chemin vers le répertoire racine du projet (2 niveaux au-dessus de ce script)
root_dir = Path(__file__).parent.parent.parent.absolute()
dotenv_path = os.path.join(root_dir, '.env')
print(f"Chargement des variables d'environnement depuis : {dotenv_path}")

# Chargement des variables d'environnement depuis la racine
load_dotenv(dotenv_path)

# Configuration de l'accès à Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Connexion à la base de données Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def create_embedding(text):
    """Génère un embedding pour le texte donné en utilisant SentenceTransformer."""
    try:
        if not text or text.strip() == "":
            return None
            
        # Génération de l'embedding avec SentenceTransformer
        embedding = model.encode(text)
        
        # Conversion en liste pour la compatibilité avec Neo4j
        return embedding.tolist()
    except Exception as e:
        print(f"Erreur lors de la création d'embedding: {e}")
        return None

def run_query(query, params=None):
    """Exécute une requête Cypher dans Neo4j."""
    with driver.session() as session:
        result = session.run(query, params or {})
        return list(result)

def create_vector_index():
    """Crée un index vectoriel dans Neo4j pour les embeddings des produits alimentaires."""
    # Essayer de supprimer l'index existant
    try:
        drop_index_query = """
        DROP INDEX product_embedding_index IF EXISTS
        """
        run_query(drop_index_query)
        print("Index vectoriel existant supprimé.")
    except Exception as e:
        print(f"Erreur lors de la suppression de l'index vectoriel: {e}")
    
    # Création de l'index vectoriel
    # all-MiniLM-L6-v2 produit des vecteurs de dimension 384
    create_index_query = """
    CREATE VECTOR INDEX product_embedding_index 
    FOR (p:Product) 
    ON (p.embedding)
    OPTIONS {indexConfig: {
      `vector.dimensions`: 384,  // Dimension pour all-MiniLM-L6-v2
      `vector.similarity_function`: 'cosine'
    }}
    """
    
    run_query(create_index_query)
    print("Index vectoriel créé avec succès.")

def clear_database():
    """Efface toutes les données de la base de données."""
    query = """
    MATCH (n)
    DETACH DELETE n
    """
    run_query(query)
    print("Base de données vidée avec succès.")

def create_constraints():
    """Crée les contraintes d'unicité."""
    constraints = [
        "CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.code IS UNIQUE",
        "CREATE CONSTRAINT brand_name IF NOT EXISTS FOR (b:Brand) REQUIRE b.name IS UNIQUE",
        "CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
        "CREATE CONSTRAINT nutriment_name IF NOT EXISTS FOR (n:Nutriment) REQUIRE n.name IS UNIQUE",
        "CREATE CONSTRAINT country_name IF NOT EXISTS FOR (c:Country) REQUIRE c.name IS UNIQUE",
        "CREATE CONSTRAINT ingredient_name IF NOT EXISTS FOR (i:Ingredient) REQUIRE i.name IS UNIQUE",
        "CREATE CONSTRAINT label_name IF NOT EXISTS FOR (l:Label) REQUIRE l.name IS UNIQUE",
        "CREATE CONSTRAINT additif_name IF NOT EXISTS FOR (a:Additif) REQUIRE a.name IS UNIQUE",
        "CREATE CONSTRAINT allergen_name IF NOT EXISTS FOR (a:Allergen) REQUIRE a.name IS UNIQUE"
    ]
    
    for constraint in constraints:
        run_query(constraint)
    
    print("Contraintes créées avec succès.")

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


def create_product_nodes(products, batch_size=100):
    """Crée les nœuds Product dans la base de données avec embeddings."""
    products_count = 0
    batches = [products[i:i + batch_size] for i in range(0, len(products), batch_size)]
    
    for batch in tqdm(batches, desc="Création des nœuds Product"):
        batch_params = []
        
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
                "ecoscore_grade": product.get('ecoscore_grade', '')
            }
            
            # Générer le texte descriptif pour l'embedding
            embedding_text = get_product_embedding_text(product)
            
            # Générer l'embedding si nous avons un texte descriptif
            if embedding_text:
                embedding = create_embedding(embedding_text)
                if embedding:
                    product_data["embedding"] = embedding
            
            batch_params.append(product_data)
        
        if batch_params:
            # Requête pour créer les nœuds Product
            query = """
            UNWIND $batch AS product
            CREATE (p:Product {
                code: product.code,
                name: product.name,
                product_name_en: product.product_name_en,
                product_name_fr: product.product_name_fr,
                generic_name: product.generic_name,
                quantity: product.quantity,
                nutriscore_grade: product.nutriscore_grade,
                nova_group: product.nova_group,
                ecoscore_grade: product.ecoscore_grade
            })
            """
            
            # Ajouter l'embedding si disponible
            embedding_query = """
            UNWIND $batch AS product
            MATCH (p:Product {code: product.code})
            WHERE product.embedding IS NOT NULL
            SET p.embedding = product.embedding
            """
            
            run_query(query, {"batch": batch_params})
            run_query(embedding_query, {"batch": batch_params})
            
            products_count += len(batch_params)
            
    print(f"Ajouté {products_count} produits au total.")
    return products_count

def create_brand_nodes(products):
    """Crée les nœuds Brand et les relations HAS_BRAND."""
    brand_relations = []
    
    for product in tqdm(products, desc="Préparation des marques"):
        if 'brands' in product and product['brands']:
            brands = [brand.strip() for brand in product['brands'].split(',')]
            
            for brand in brands:
                if brand:
                    brand_relations.append({
                        "product_code": product['code'],
                        "brand_name": brand
                    })
    
    if brand_relations:
        query = """
        UNWIND $relations AS rel
        MERGE (b:Brand {name: rel.brand_name})
        WITH b, rel
        MATCH (p:Product {code: rel.product_code})
        MERGE (p)-[r:HAS_BRAND]->(b)
        """
        
        run_query(query, {"relations": brand_relations})
        print(f"Ajouté {len(brand_relations)} relations HAS_BRAND.")

def create_category_nodes(products):
    """Crée les nœuds Category et les relations HAS_CATEGORY."""
    category_relations = []
    
    for product in tqdm(products, desc="Préparation des catégories"):
        if 'categories' in product and product['categories']:
            categories = [cat.strip() for cat in product['categories'].split(',')]
            
            for category in categories:
                if category:
                    category_relations.append({
                        "product_code": product['code'],
                        "category_name": category
                    })
    
    if category_relations:
        batch_size = 1000
        for i in range(0, len(category_relations), batch_size):
            batch = category_relations[i:i+batch_size]
            
            query = """
            UNWIND $relations AS rel
            MERGE (c:Category {name: rel.category_name})
            WITH c, rel
            MATCH (p:Product {code: rel.product_code})
            MERGE (p)-[r:HAS_CATEGORY]->(c)
            """
            
            run_query(query, {"relations": batch})
            
        print(f"Ajouté {len(category_relations)} relations HAS_CATEGORY.")

def create_ingredient_nodes(products):
    """Crée les nœuds Ingredient et les relations CONTAINS."""
    ingredient_relations = []
    
    for product in tqdm(products, desc="Préparation des ingrédients"):
        if 'ingredients_tags' in product and product['ingredients_tags']:
            ingredients = product['ingredients_tags']
            
            for ingredient in ingredients:
                # Extraction du nom de l'ingrédient (enlever les préfixes comme "en:")
                ingredient_name = ingredient.split(':')[-1].replace('-', ' ').strip()
                
                if ingredient_name:
                    ingredient_relations.append({
                        "product_code": product['code'],
                        "ingredient_name": ingredient_name
                    })
    
    if ingredient_relations:
        batch_size = 1000
        for i in range(0, len(ingredient_relations), batch_size):
            batch = ingredient_relations[i:i+batch_size]
            
            query = """
            UNWIND $relations AS rel
            MERGE (i:Ingredient {name: rel.ingredient_name})
            WITH i, rel
            MATCH (p:Product {code: rel.product_code})
            MERGE (p)-[r:CONTAINS]->(i)
            """
            
            run_query(query, {"relations": batch})
            
        print(f"Ajouté {len(ingredient_relations)} relations CONTAINS.")

def create_label_nodes(products):
    """Crée les nœuds Label et les relations HAS_LABEL en intégrant les synonymes.
    
    Pour chaque label extrait (issu de product['labels_tags']), on recherche dans
    label_synonyms (un dictionnaire dont les clés sont le label principal en minuscule)
    la liste des synonymes associés, puis on crée (ou met à jour) le nœud Label.
    La relation HAS_LABEL est ensuite créée entre le produit et ce nœud.
    """
    label_relations = []
    
    for product in tqdm(products, desc="Préparation des labels"):
        if 'labels_tags' in product and product['labels_tags']:
            labels = product['labels_tags']
            for label in labels:
                # Extraction du nom du label en retirant le préfixe "en:" et en normalisant
                label_name = label.split(':')[-1].replace('-', ' ').strip()
                if label_name:
                    label_relations.append({
                        "product_code": product['code'],
                        "label_name": label_name
                    })
    
    if label_relations:
        batch_size = 1000
        for i in range(0, len(label_relations), batch_size):
            batch = label_relations[i:i+batch_size]
            query = """
            UNWIND $relations AS rel
            MERGE (l:Label {name: rel.label_name})
            WITH l, rel
            MATCH (p:Product {code: rel.product_code})
            MERGE (p)-[r:HAS_LABEL]->(l)
            """
            run_query(query, {"relations": batch})
            
        print(f"Ajouté {len(label_relations)} relations HAS_LABEL.")



def create_additif_nodes(products):
    """Crée les nœuds Additif et les relations CONTAINS_ADDITIF."""
    additif_relations = []
    
    for product in tqdm(products, desc="Préparation des additifs"):
        if 'additives_tags' in product and product['additives_tags']:
            additives = product['additives_tags']
            
            for additif in additives:
                # Extraction du nom de l'additif (enlever les préfixes comme "en:")
                additif_name = additif.split(':')[-1].replace('-', ' ').strip()
                
                if additif_name:
                    additif_relations.append({
                        "product_code": product['code'],
                        "additif_name": additif_name
                    })
    
    if additif_relations:
        batch_size = 1000
        for i in range(0, len(additif_relations), batch_size):
            batch = additif_relations[i:i+batch_size]
            
            query = """
            UNWIND $relations AS rel
            MERGE (a:Additif {name: rel.additif_name})
            WITH a, rel
            MATCH (p:Product {code: rel.product_code})
            MERGE (p)-[r:CONTAINS_ADDITIF]->(a)
            """
            
            run_query(query, {"relations": batch})
            
        print(f"Ajouté {len(additif_relations)} relations CONTAINS_ADDITIF.")

def create_allergen_nodes(products):
    """Crée les nœuds Allergen et les relations CONTAINS_ALLERGEN."""
    allergen_relations = []
    
    for product in tqdm(products, desc="Préparation des allergènes"):
        if 'allergens_tags' in product and product['allergens_tags']:
            allergens = product['allergens_tags']
            
            for allergen in allergens:
                # Extraction du nom de l'allergène (enlever les préfixes comme "en:")
                allergen_name = allergen.split(':')[-1].replace('-', ' ').strip()
                
                if allergen_name:
                    allergen_relations.append({
                        "product_code": product['code'],
                        "allergen_name": allergen_name
                    })
    
    if allergen_relations:
        query = """
        UNWIND $relations AS rel
        MERGE (a:Allergen {name: rel.allergen_name})
        WITH a, rel
        MATCH (p:Product {code: rel.product_code})
        MERGE (p)-[r:CONTAINS_ALLERGEN]->(a)
        """
        
        run_query(query, {"relations": allergen_relations})
        print(f"Ajouté {len(allergen_relations)} relations CONTAINS_ALLERGEN.")

def create_country_nodes(products):
    """Crée les nœuds Country et les relations SOLD_IN."""
    country_relations = []
    
    for product in tqdm(products, desc="Préparation des pays"):
        if 'countries_tags' in product and product['countries_tags']:
            countries = product['countries_tags']
            
            for country in countries:
                # Extraction du nom du pays (enlever les préfixes comme "en:")
                country_name = country.split(':')[-1].replace('-', ' ').strip()
                
                if country_name:
                    country_relations.append({
                        "product_code": product['code'],
                        "country_name": country_name
                    })
    
    if country_relations:
        query = """
        UNWIND $relations AS rel
        MERGE (c:Country {name: rel.country_name})
        WITH c, rel
        MATCH (p:Product {code: rel.product_code})
        MERGE (p)-[r:SOLD_IN]->(c)
        """
        
        run_query(query, {"relations": country_relations})
        print(f"Ajouté {len(country_relations)} relations SOLD_IN.")

def create_nutriment_nodes(products):
    """Crée les nœuds Nutriment et les relations HAS_NUTRIMENT."""
    nutriment_relations = []
    
    nutriments_of_interest = [
        'energy', 'fat', 'saturated-fat', 'carbohydrates', 'sugars', 
        'fiber', 'proteins', 'salt', 'sodium', 'calcium', 'iron', 
        'vitamin-a', 'vitamin-c', 'vitamin-d'
    ]
    
    for product in tqdm(products, desc="Préparation des nutriments"):
        if 'nutriments' in product and product['nutriments']:
            nutriments = product['nutriments']
            
            for nutriment in nutriments_of_interest:
                if nutriment in nutriments and nutriments[nutriment] is not None:
                    value = nutriments[nutriment]
                    unit = nutriments.get(f"{nutriment}_unit", "")
                    
                    if value:
                        nutriment_relations.append({
                            "product_code": product['code'],
                            "nutriment_name": nutriment.replace('-', ' '),
                            "value": value,
                            "unit": unit
                        })
    
    if nutriment_relations:
        batch_size = 1000
        for i in range(0, len(nutriment_relations), batch_size):
            batch = nutriment_relations[i:i+batch_size]
            
            query = """
            UNWIND $relations AS rel
            MERGE (n:Nutriment {name: rel.nutriment_name})
            WITH n, rel
            MATCH (p:Product {code: rel.product_code})
            MERGE (p)-[r:HAS_NUTRIMENT {value: rel.value, unit: rel.unit}]->(n)
            """
            
            run_query(query, {"relations": batch})
            
        print(f"Ajouté {len(nutriment_relations)} relations HAS_NUTRIMENT.")

# Ajouter ces fonctions au script create_graph_v5.py

def load_taxonomy_files(base_path):
    """
    Charge tous les fichiers de taxonomie disponibles et retourne un dictionnaire
    où la clé est le nom de la taxonomie et la valeur est le chemin du fichier.
    """
    taxonomies = {}
    taxonomy_files = {
        "categories": "categories.txt",
        "ingredients": "ingredients.txt",
        "additives": "additives.txt",
        "allergens": "allergens.txt",
        "countries": "countries.txt",
        "nutrients": "nutrients.txt"
    }
    
    for taxonomy_name, file_name in taxonomy_files.items():
        file_path = os.path.join(base_path, file_name)
        if os.path.exists(file_path):
            taxonomies[taxonomy_name] = file_path
            print(f"Fichier de taxonomie trouvé: {taxonomy_name} -> {file_path}")
        else:
            print(f"Fichier de taxonomie non trouvé: {taxonomy_name} -> {file_path}")
    
    return taxonomies

def enhance_nodes_with_taxonomy_data(node_type, taxonomy_data, driver, batch_size=100):
    """
    Améliore les nœuds existants avec les données de taxonomie (synonymes, traductions).
    
    Args:
        node_type (str): Type de nœud à améliorer (Category, Ingredient, etc.)
        taxonomy_data (dict): Dictionnaire contenant les données de taxonomie
        driver: Connexion Neo4j
        batch_size (int): Taille des lots pour les opérations batch
    """
    print(f"Amélioration des nœuds {node_type} avec les données de taxonomie...")
    
    # Récupérer tous les nœuds du type spécifié
    with driver.session() as session:
        result = session.run(f"MATCH (n:{node_type}) RETURN n.name as name")
        existing_nodes = [record["name"] for record in result]
    
    print(f"Nombre de nœuds {node_type} existants: {len(existing_nodes)}")
    
    # Préparer les mises à jour pour chaque nœud
    updates = []
    
    for node_name in existing_nodes:
        # Rechercher dans la taxonomie (noms canoniques et synonymes)
        translations_en = []
        translations_fr = []
        
        # Chercher dans les noms canoniques
        for parent, children in taxonomy_data.items():
            for child in children:
                if child["name"].lower() == node_name.lower():
                    # Ajouter les traductions si disponibles
                    if "translations" in child:
                        if "en" in child["translations"]:
                            translations_en.extend(child["translations"]["en"])
                        if "fr" in child["translations"]:
                            translations_fr.extend(child["translations"]["fr"])
        
        # Ajouter uniquement si on a trouvé des traductions
        if translations_en or translations_fr:
            updates.append({
                "name": node_name,
                "translations_en": list(set(translations_en)),
                "translations_fr": list(set(translations_fr))
            })
    
    # Appliquer les mises à jour par lots
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i+batch_size]
        if batch:
            with driver.session() as session:
                query = f"""
                UNWIND $batch AS update
                MATCH (n:{node_type} {{name: update.name}})
                SET n.translations_en = update.translations_en,
                    n.translations_fr = update.translations_fr
                """
                session.run(query, {"batch": batch})
    
    print(f"Amélioré {len(updates)} nœuds {node_type} avec des traductions.")

def create_hierarchical_relationships(relations, node_type, relation_type, driver, batch_size=100):
    """
    Crée des relations hiérarchiques entre les nœuds d'un type spécifié.
    
    Args:
        relations (list): Liste de dictionnaires {parent, child} définissant les relations
        node_type (str): Type de nœud (Category, Ingredient, etc.)
        relation_type (str): Type de relation (HAS_CHILD, PART_OF, etc.)
        driver: Connexion Neo4j
        batch_size (int): Taille des lots pour les opérations batch
    """
    if not relations:
        return
    
    print(f"Création de {len(relations)} relations {relation_type} en lots de {batch_size}...")
    
    # Traitement par lots avec tqdm pour suivre la progression
    for i in tqdm(range(0, len(relations), batch_size), desc=f"Relations {relation_type}", unit="lot"):
        batch = relations[i:i+batch_size]
        success = False
        retries = 0
        max_retries = 3
        
        while not success and retries < max_retries:
            try:
                with driver.session() as session:
                    # Assurer que les nœuds parent et enfant existent avant de créer la relation
                    create_nodes_query = f"""
                    UNWIND $relations AS rel
                    MERGE (p:{node_type} {{name: rel.parent}})
                    MERGE (c:{node_type} {{name: rel.child}})
                    """
                    session.run(create_nodes_query, {"relations": batch})
                    
                    # Créer la relation entre les nœuds
                    create_rel_query = f"""
                    UNWIND $relations AS rel
                    MATCH (p:{node_type} {{name: rel.parent}}), (c:{node_type} {{name: rel.child}})
                    MERGE (p)-[:{relation_type}]->(c)
                    """
                    session.run(create_rel_query, {"relations": batch})
                success = True
            except Exception as e:
                retries += 1
                print(f"Erreur lors du traitement du lot {i} à {i+batch_size} : {e}. Réessai {retries}/{max_retries} dans 5 secondes...")
                time.sleep(5)
                
        if not success:
            print(f"Échec après {max_retries} réessais pour le lot {i} à {i+batch_size}.")
    
    print(f"Ajouté {len(relations)} relations {relation_type}.")

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

def create_taxonomy_structures(script_dir, driver):
    """
    Crée les structures hiérarchiques pour toutes les taxonomies supportées.
    
    Args:
        script_dir (str): Chemin du répertoire du script
        driver: Connexion Neo4j
    """
    # Configuration des taxonomies
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
            "name": "countries",
            "file_name": "countries.txt",
            "node_type": "Country",
            "relation_type": "CONTAINS_REGION"
        },
        {
            "name": "nutrients",
            "file_name": "nutrients.txt",
            "node_type": "Nutriment",
            "relation_type": "PART_OF"
        },
        {
            "name": "labels",
            "file_name": "labels.txt",
            "node_type": "Label",
            "relation_type": "INCLUDES"
        }
    ]
    
    taxonomy_dir = os.path.join(script_dir, "../../data/taxonomies")
    
    for taxonomy in taxonomies:
        file_path = os.path.join(taxonomy_dir, taxonomy["file_name"])
        
        if not os.path.exists(file_path):
            print(f"Fichier de taxonomie non trouvé: {file_path}")
            continue
        
        print(f"Traitement de la taxonomie {taxonomy['name']}...")
        
        # 1. Parser le fichier de taxonomie
        taxonomy_data = parse_taxonomy(file_path)
        
        # 2. Créer les relations hiérarchiques
        relations = []
        for parent, children in taxonomy_data.items():
            for child in children:
                relations.append({"parent": parent, "child": child["name"]})
        
        if relations:
            print(f"Création de {len(relations)} relations {taxonomy['relation_type']} pour {taxonomy['node_type']}...")
            create_hierarchical_relationships(
                relations, 
                taxonomy["node_type"], 
                taxonomy["relation_type"], 
                driver
            )
        
        # 3. Ajouter les traductions et synonymes aux nœuds
        enhance_nodes_with_taxonomy_data(
            taxonomy["node_type"], 
            taxonomy_data, 
            driver
        )

def enhanced_search_similar_products(query_text, limit=5, lang="fr"):
    """
    Recherche des produits similaires à partir d'une requête textuelle,
    en exploitant les taxonomies et les relations hiérarchiques.
    
    Args:
        query_text (str): Texte de la requête en langage naturel
        limit (int): Nombre maximum de résultats à retourner
        lang (str): Langue de la requête ('fr' ou 'en')
    
    Returns:
        list: Liste des produits correspondants avec scores
    """
    # 1. Générer l'embedding pour la requête
    query_embedding = create_embedding(query_text)
    
    if not query_embedding:
        print("Impossible de générer l'embedding pour la requête.")
        return []
    
    # 2. Recherche vectorielle de base (comme avant)
    vector_query = """
    CALL db.index.vector.queryNodes('product_embedding_index', $limit * 2, $embedding)
    YIELD node, score
    RETURN node.code AS code, node.name AS name, node.generic_name AS generic_name, 
           node.nutriscore_grade AS nutriscore, score
    """
    
    vector_results = run_query(vector_query, {
        "limit": limit * 2,  # On récupère plus de résultats pour filtrage ultérieur
        "embedding": query_embedding
    })
    
    # 3. Analyser la requête pour extraire les concepts clés
    # Ici, une approche simple: extraire des mots-clés
    keywords = query_text.lower().split()
    
    # 4. Recherche basée sur les taxonomies pour ces concepts
    # On cherche dans les catégories, ingrédients, labels, etc. en utilisant aussi les synonymes
    taxonomy_query = f"""
    MATCH (p:Product)
    WHERE 
    // Recherche dans les catégories et leurs traductions
    EXISTS(
        (p)-[:HAS_CATEGORY]->(c:Category) 
        WHERE ANY(keyword IN $keywords WHERE 
            LOWER(c.name) CONTAINS keyword OR
            ANY(syn IN c.translations_{lang} WHERE LOWER(syn) CONTAINS keyword)
        )
    )
    OR 
    // Recherche dans les ingrédients et leurs traductions
    EXISTS(
        (p)-[:CONTAINS]->(i:Ingredient) 
        WHERE ANY(keyword IN $keywords WHERE 
            LOWER(i.name) CONTAINS keyword OR
            ANY(syn IN i.translations_{lang} WHERE LOWER(syn) CONTAINS keyword)
        )
    )
    OR
    // Recherche dans les labels et leurs synonymes
    EXISTS(
        (p)-[:HAS_LABEL]->(l:Label) 
        WHERE ANY(keyword IN $keywords WHERE 
            LOWER(l.name) CONTAINS keyword OR
            ANY(syn IN l.synonyms WHERE LOWER(syn) CONTAINS keyword)
        )
    )
    RETURN p.code AS code, p.name AS name, p.generic_name AS generic_name, 
           p.nutriscore_grade AS nutriscore, 1.0 AS taxonomy_score
    LIMIT $limit
    """
    
    taxonomy_results = run_query(taxonomy_query, {
        "keywords": keywords,
        "limit": limit
    })
    
    # 5. Fusion et ordonnancement des résultats
    combined_results = {}
    
    # Ajouter les résultats de recherche vectorielle
    for result in vector_results:
        code = result["code"]
        combined_results[code] = {
            "code": code,
            "name": result["name"],
            "generic_name": result["generic_name"],
            "nutriscore": result["nutriscore"],
            "vector_score": result["score"],
            "taxonomy_score": 0.0,
            "final_score": result["score"]
        }
    
    # Ajouter ou mettre à jour avec les résultats de taxonomie
    for result in taxonomy_results:
        code = result["code"]
        if code in combined_results:
            # Mettre à jour un résultat existant
            combined_results[code]["taxonomy_score"] = result["taxonomy_score"]
            combined_results[code]["final_score"] = (
                combined_results[code]["vector_score"] * 0.7 + 
                combined_results[code]["taxonomy_score"] * 0.3
            )
        else:
            # Ajouter un nouveau résultat
            combined_results[code] = {
                "code": code,
                "name": result["name"],
                "generic_name": result["generic_name"],
                "nutriscore": result["nutriscore"],
                "vector_score": 0.0,
                "taxonomy_score": result["taxonomy_score"],
                "final_score": result["taxonomy_score"] * 0.3
            }
    
    # Trier par score final et limiter le nombre de résultats
    results = list(combined_results.values())
    results.sort(key=lambda x: x["final_score"], reverse=True)
    
    return results[:limit]


def search_similar_products(query_text, limit=5):
    """
    Recherche des produits similaires à partir d'une requête textuelle.
    Utilise les embeddings pour trouver les produits sémantiquement proches.
    """
    # Génération de l'embedding pour la requête
    query_embedding = create_embedding(query_text)
    
    if not query_embedding:
        print("Impossible de générer l'embedding pour la requête.")
        return []
    
    # Recherche des produits similaires dans Neo4j
    search_query = """
    CALL db.index.vector.queryNodes('product_embedding_index', $limit, $embedding)
    YIELD node, score
    RETURN node.code AS code, node.name AS name, node.generic_name AS generic_name, 
           node.nutriscore_grade AS nutriscore, score
    ORDER BY score DESC
    """
    
    results = run_query(search_query, {
        "limit": limit,
        "embedding": query_embedding
    })
    
    return results

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
    products = products[:1000]  # Limiter à 1000 produits pour le test
    print(f"Nombre de produits sélectionnés pour le traitement: {len(products)}")
    
    try:
        # Nettoyage de la base de données
        clear_database()
        
        # Création des contraintes
        create_constraints()
        
        # Création des nœuds de produits avec embeddings
        create_product_nodes(products)
        
        # Création de l'index vectoriel
        create_vector_index()
        
        # Création des autres nœuds et relations
        create_brand_nodes(products)
        create_category_nodes(products)
        create_ingredient_nodes(products)
        create_label_nodes(products)
        create_additif_nodes(products)
        create_allergen_nodes(products)
        create_country_nodes(products)
        create_nutriment_nodes(products)

        # Crée des relations hiérarchiques pour chaque type de taxonomie
        create_taxonomy_structures(script_dir, driver)
        
        # Test de recherche sémantique
        print("\nTest de recherche sémantique:")
        results = search_similar_products("Produit sans gluten riche en protéines", 5)
        for result in results:
            # Vérifier si result est un dictionnaire ou un objet Record de Neo4j
            if hasattr(result, "get"):  # Pour les objets de type Record
                name = result.get("name", "Nom inconnu")
                score = result.get("score", 0.0)
                generic_name = result.get("generic_name", "")
                nutriscore = result.get("nutriscore", "")
            else:  # Pour les dictionnaires
                name = result["name"] if "name" in result else "Nom inconnu"
                score = result["score"] if "score" in result else 0.0
                generic_name = result["generic_name"] if "generic_name" in result else ""
                nutriscore = result["nutriscore"] if "nutriscore" in result else ""
                
            print(f"Produit: {name}, Score: {score:.4f}")
            print(f"Description: {generic_name}")
            print(f"Nutri-Score: {nutriscore}\n")
    finally:
        # Fermeture de la connexion
        driver.close()

if __name__ == "__main__":
    main()