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
import sys
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
                "name": product.get('product_name', ''),
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
    """Crée les nœuds Label et les relations HAS_LABEL."""
    label_relations = []
    
    for product in tqdm(products, desc="Préparation des labels"):
        if 'labels_tags' in product and product['labels_tags']:
            labels = product['labels_tags']
            
            for label in labels:
                # Extraction du nom du label (enlever les préfixes comme "en:")
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
    
    # Fermeture de la connexion
    driver.close()

if __name__ == "__main__":
    main()