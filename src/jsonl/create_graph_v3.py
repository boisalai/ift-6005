import json
import os
from neo4j import GraphDatabase
import logging
from dotenv import load_dotenv
from collections import defaultdict, Counter
import time
from concurrent.futures import ThreadPoolExecutor

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("openfoodfacts_loader.log"),
                             logging.StreamHandler()])
logger = logging.getLogger()

# Charger les variables d'environnement
load_dotenv()

# Configuration Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class OpenFoodFactsGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.stats = defaultdict(int)
    
    def clear_database(self):
        """Effacer toutes les données du graphe"""
        with self.driver.session() as session:
            try:
                # Supprimer d'abord toutes les contraintes et index
                session.run("CALL apoc.schema.assert({}, {})")
                # Supprimer toutes les données
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Base de données Neo4j effacée avec succès")
                return True
            except Exception as e:
                logger.error(f"Erreur lors de l'effacement de la base de données: {e}")
                return False
        
    def close(self):
        """Fermer la connexion au driver Neo4j"""
        self.driver.close()
        
    def create_constraints(self):
        """Créer les contraintes d'unicité pour les nœuds principaux"""
        with self.driver.session() as session:
            # Exécuter chaque contrainte séparément
            constraints = [
                "CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT brand_name IF NOT EXISTS FOR (b:Brand) REQUIRE b.name IS UNIQUE",
                "CREATE CONSTRAINT ingredient_name IF NOT EXISTS FOR (i:Ingredient) REQUIRE i.name IS UNIQUE",
                "CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
                "CREATE CONSTRAINT country_name IF NOT EXISTS FOR (c:Country) REQUIRE c.name IS UNIQUE",
                "CREATE CONSTRAINT allergen_name IF NOT EXISTS FOR (a:Allergen) REQUIRE a.name IS UNIQUE",
                "CREATE CONSTRAINT nutrient_name IF NOT EXISTS FOR (n:Nutrient) REQUIRE n.name IS UNIQUE",
                "CREATE CONSTRAINT label_name IF NOT EXISTS FOR (l:Label) REQUIRE l.name IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Contrainte créée: {constraint}")
                except Exception as e:
                    logger.error(f"Erreur lors de la création de la contrainte: {e}")
    
    def clean_field(self, value):
        """Nettoyer une valeur pour éviter les problèmes de formatage"""
        if isinstance(value, str):
            return value.strip()
        return value
    
    def clean_ingredient_name(self, name):
        """Normaliser le nom des ingrédients"""
        if isinstance(name, str):
            # Convertir en minuscules
            name = name.lower().strip()
            
            # Dictionnaire de traduction (à compléter selon vos besoins)
            translations = {
                "sel": "salt",
                "sucre": "sugar",
                "eau": "water",
                # Ajouter d'autres traductions...
            }
            
            # Remplacer par la version standardisée si elle existe
            return translations.get(name, name)
        return name

    def extract_field(self, data, field, default=None):
        """Extraire un champ des données, avec support pour la notation pointée"""
        if '.' in field:
            parts = field.split('.')
            current = data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            return current
        else:
            return data.get(field, default)
    
    def preprocess_products(self, products):
        """Prétraiter les produits pour extraire les entités uniques et les données"""
        valid_products = []
        brands_set = set()
        categories_set = set()
        countries_set = set()
        ingredients_set = set()
        allergens_set = set()
        labels_set = set()
        
        for product_data in products:
            # Vérification et extraction de l'ID du produit
            product_id = self.extract_field(product_data, '_id', '')
            if not product_id:
                self.stats["produits_sans_id"] += 1
                continue
            
            # Extraction du nom du produit
            product_name = self.extract_field(product_data, 'product_name', '')
            if not product_name:
                product_name = self.extract_field(product_data, 'product_name_en', '')
            
            if not product_name:
                self.stats["produits_sans_nom"] += 1
                continue

            # Données de base du produit
            quantity = self.extract_field(product_data, 'quantity', '')
            nutriscore = self.extract_field(product_data, 'nutriscore_grade', '')
            nova_group = self.extract_field(product_data, 'nova_group', None)
            ecoscore = self.extract_field(product_data, 'ecoscore_grade', '')
            
            # Vérification des données nutritionnelles
            has_nutrition = self.extract_field(product_data, 'nutriments') is not None
            
            # Produire un dictionnaire contenant les données pour le nœud du produit
            product_node = {
                'id': product_id,
                'name': product_name,
                'quantity': quantity,
                'nutriscore': nutriscore,
                'nova_group': nova_group,
                'ecoscore': ecoscore,
                'has_nutrition': has_nutrition
            }
            
            # Extraire les marques
            brands = self.extract_field(product_data, 'brands', '').split(',')
            product_brands = [brand.strip() for brand in brands if brand.strip()]
            brands_set.update(product_brands)
            
            # Extraire les catégories
            categories = self.extract_field(product_data, 'categories', '').split(',')
            product_categories = [category.strip() for category in categories if category.strip()]
            categories_set.update(product_categories)
            
            # Extraire les pays
            countries = self.extract_field(product_data, 'countries', '').split(',')
            product_countries = [country.strip() for country in countries if country.strip()]
            countries_set.update(product_countries)
            
            # Extraire les ingrédients
            product_ingredients = []
            if "ingredients" in product_data and isinstance(product_data["ingredients"], list):
                for ingr in product_data["ingredients"]:
                    if isinstance(ingr, dict) and "text" in ingr:
                        ingredient_name = self.clean_ingredient_name(ingr["text"])
                        ingredient = {
                            "name": ingredient_name,
                            "vegan": ingr.get("vegan", "unknown"),
                            "vegetarian": ingr.get("vegetarian", "unknown")
                        }
                        product_ingredients.append(ingredient)
                        ingredients_set.add((ingr["text"], ingr.get("vegan", "unknown"), ingr.get("vegetarian", "unknown")))
            
            # Si pas d'ingrédients détaillés, essayer avec ingredients_text
            if not product_ingredients and "ingredients_text" in product_data:
                text = product_data["ingredients_text"]
                if text:
                    raw_ingredients = [i.strip() for i in text.split(',') if i.strip()]
                    for ingr in raw_ingredients:
                        product_ingredients.append({
                            "name": ingr,
                            "vegan": "unknown",
                            "vegetarian": "unknown"
                        })
                        ingredients_set.add((ingr, "unknown", "unknown"))
            
            # Extraire les allergènes
            product_allergens = []
            if "allergens_tags" in product_data:
                allergens = [allergen.replace("en:", "") for allergen in product_data["allergens_tags"]]
                product_allergens = allergens
                allergens_set.update(allergens)
            
            # Extraire les données nutritionnelles
            product_nutrients = []
            if "nutriments" in product_data:
                nutriments = product_data["nutriments"]
                
                # Ajouter les valeurs nutritionnelles de base dans le produit
                product_node['energy'] = self.extract_field(nutriments, 'energy', None)
                product_node['fat'] = self.extract_field(nutriments, 'fat', None)
                product_node['proteins'] = self.extract_field(nutriments, 'proteins', None)
                product_node['carbohydrates'] = self.extract_field(nutriments, 'carbohydrates', None)
                product_node['sugars'] = self.extract_field(nutriments, 'sugars', None)
                product_node['sodium'] = self.extract_field(nutriments, 'sodium', None)
                product_node['salt'] = self.extract_field(nutriments, 'salt', None)
                product_node['fiber'] = self.extract_field(nutriments, 'fiber', None)
                
                # Créer une liste de nutriments à ajouter comme nœuds
                key_nutrients = {
                    'energy': 'Énergie',
                    'fat': 'Matières grasses',
                    'proteins': 'Protéines',
                    'carbohydrates': 'Glucides',
                    'sugars': 'Sucres',
                    'sodium': 'Sodium',
                    'salt': 'Sel',
                    'fiber': 'Fibres'
                }
                
                for key, name in key_nutrients.items():
                    if key in nutriments and nutriments[key] is not None:
                        value = nutriments[key]
                        unit = nutriments.get(f"{key}_unit", "")
                        product_nutrients.append({
                            'name': name,
                            'value': value,
                            'unit': unit
                        })
            
            # Extraire les labels
            product_labels = []
            if "labels_tags" in product_data:
                labels = [label.replace("en:", "") for label in product_data["labels_tags"]]
                product_labels = labels
                labels_set.update(labels)
            
            # Ajouter le produit avec toutes ses relations à la liste
            valid_products.append({
                'node': product_node,
                'brands': product_brands,
                'categories': product_categories,
                'countries': product_countries,
                'ingredients': product_ingredients,
                'allergens': product_allergens,
                'nutrients': product_nutrients,
                'labels': product_labels
            })
            
        return {
            'products': valid_products,
            'unique_brands': list(brands_set),
            'unique_categories': list(categories_set),
            'unique_countries': list(countries_set),
            'unique_ingredients': list(ingredients_set),
            'unique_allergens': list(allergens_set),
            'unique_labels': list(labels_set)
        }
    
    def create_entity_nodes_batch(self, session, entity_type, entities, batch_size=1000):
        """Créer des nœuds d'entité en lots"""
        start_time = time.time()
        total = len(entities)
        
        if not entities:
            return
        
        logger.info(f"Création de {total} nœuds de type {entity_type}")
        
        for i in range(0, total, batch_size):
            batch = entities[i:i+batch_size]
            
            if entity_type == "Brand":
                session.run("""
                    UNWIND $batch AS item
                    MERGE (b:Brand {name: item})
                """, batch=batch)
                
            elif entity_type == "Category":
                session.run("""
                    UNWIND $batch AS item
                    MERGE (c:Category {name: item})
                """, batch=batch)
                
            elif entity_type == "Country":
                session.run("""
                    UNWIND $batch AS item
                    MERGE (c:Country {name: item})
                """, batch=batch)
                
            elif entity_type == "Label":
                session.run("""
                    UNWIND $batch AS item
                    MERGE (l:Label {name: item})
                """, batch=batch)
                
            elif entity_type == "Allergen":
                session.run("""
                    UNWIND $batch AS item
                    MERGE (a:Allergen {name: item})
                """, batch=batch)
                
            elif entity_type == "Ingredient":
                session.run("""
                    UNWIND $batch AS item
                    MERGE (i:Ingredient {name: item[0]})
                    SET i.vegan = item[1],
                        i.vegetarian = item[2]
                """, batch=batch)
                
            elif entity_type == "Nutrient":
                session.run("""
                    UNWIND $batch AS item
                    MERGE (n:Nutrient {name: item})
                """, batch=batch)
                
            logger.info(f"Progrès {entity_type}: {min(i+batch_size, total)}/{total}")
            
        elapsed = time.time() - start_time
        logger.info(f"Création des nœuds {entity_type} terminée en {elapsed:.2f} secondes")
    
    def create_product_nodes_batch(self, session, products, batch_size=500):
        """Créer des nœuds de produits en lots"""
        start_time = time.time()
        total = len(products)
        
        if not products:
            return
        
        logger.info(f"Création de {total} nœuds de produits")
        
        for i in range(0, total, batch_size):
            batch = products[i:i+batch_size]
            product_nodes = [p['node'] for p in batch]
            
            session.run("""
                UNWIND $batch AS product
                MERGE (p:Product {id: product.id})
                ON CREATE SET 
                    p.name = product.name,
                    p.quantity = product.quantity,
                    p.nutriscore = product.nutriscore,
                    p.nova_group = product.nova_group,
                    p.ecoscore = product.ecoscore,
                    p.has_nutrition = product.has_nutrition,
                    p.energy = product.energy,
                    p.fat = product.fat,
                    p.proteins = product.proteins,
                    p.carbohydrates = product.carbohydrates,
                    p.sugars = product.sugars,
                    p.sodium = product.sodium,
                    p.salt = product.salt,
                    p.fiber = product.fiber
            """, batch=product_nodes)
            
            logger.info(f"Progrès produits: {min(i+batch_size, total)}/{total}")
            
        elapsed = time.time() - start_time
        logger.info(f"Création des nœuds de produits terminée en {elapsed:.2f} secondes")
    
    def create_relationships_batch(self, session, products, relationship_type, batch_size=500):
        """Créer des relations en lots"""
        start_time = time.time()
        total = len(products)
        
        if not products:
            return
        
        logger.info(f"Création des relations de type {relationship_type}")
        
        for i in range(0, total, batch_size):
            batch = products[i:i+batch_size]
            
            if relationship_type == "BELONGS_TO":
                brand_relations = []
                for p in batch:
                    for brand in p['brands']:
                        brand_relations.append({
                            'product_id': p['node']['id'],
                            'brand_name': brand
                        })
                
                if brand_relations:
                    session.run("""
                        UNWIND $relations AS rel
                        MATCH (p:Product {id: rel.product_id})
                        MATCH (b:Brand {name: rel.brand_name})
                        MERGE (p)-[:BELONGS_TO]->(b)
                    """, relations=brand_relations)
                    
                    self.stats["marques"] += len(brand_relations)
            
            elif relationship_type == "CATEGORIZED_AS":
                category_relations = []
                for p in batch:
                    for category in p['categories']:
                        category_relations.append({
                            'product_id': p['node']['id'],
                            'category_name': category
                        })
                
                if category_relations:
                    session.run("""
                        UNWIND $relations AS rel
                        MATCH (p:Product {id: rel.product_id})
                        MATCH (c:Category {name: rel.category_name})
                        MERGE (p)-[:CATEGORIZED_AS]->(c)
                    """, relations=category_relations)
                    
                    self.stats["categories"] += len(category_relations)
            
            elif relationship_type == "PRODUCED_IN":
                country_relations = []
                for p in batch:
                    for country in p['countries']:
                        country_relations.append({
                            'product_id': p['node']['id'],
                            'country_name': country
                        })
                
                if country_relations:
                    session.run("""
                        UNWIND $relations AS rel
                        MATCH (p:Product {id: rel.product_id})
                        MATCH (c:Country {name: rel.country_name})
                        MERGE (p)-[:PRODUCED_IN]->(c)
                    """, relations=country_relations)
                    
                    self.stats["pays"] += len(country_relations)
            
            elif relationship_type == "CONTAINS":
                ingredient_relations = []
                for p in batch:
                    for ingredient in p['ingredients']:
                        ingredient_relations.append({
                            'product_id': p['node']['id'],
                            'ingredient_name': ingredient['name']
                        })
                
                if ingredient_relations:
                    session.run("""
                        UNWIND $relations AS rel
                        MATCH (p:Product {id: rel.product_id})
                        MATCH (i:Ingredient {name: rel.ingredient_name})
                        MERGE (p)-[:CONTAINS]->(i)
                    """, relations=ingredient_relations)
                    
                    self.stats["ingredients"] += len(ingredient_relations)
            
            elif relationship_type == "CONTAINS_ALLERGEN":
                allergen_relations = []
                for p in batch:
                    for allergen in p['allergens']:
                        allergen_relations.append({
                            'product_id': p['node']['id'],
                            'allergen_name': allergen
                        })
                
                if allergen_relations:
                    session.run("""
                        UNWIND $relations AS rel
                        MATCH (p:Product {id: rel.product_id})
                        MATCH (a:Allergen {name: rel.allergen_name})
                        MERGE (p)-[:CONTAINS_ALLERGEN]->(a)
                    """, relations=allergen_relations)
                    
                    self.stats["allergenes"] += len(allergen_relations)
            
            elif relationship_type == "HAS_LABEL":
                label_relations = []
                for p in batch:
                    for label in p['labels']:
                        label_relations.append({
                            'product_id': p['node']['id'],
                            'label_name': label
                        })
                
                if label_relations:
                    session.run("""
                        UNWIND $relations AS rel
                        MATCH (p:Product {id: rel.product_id})
                        MATCH (l:Label {name: rel.label_name})
                        MERGE (p)-[:HAS_LABEL]->(l)
                    """, relations=label_relations)
                    
                    self.stats["labels"] += len(label_relations)
            
            elif relationship_type == "HAS_NUTRIENT":
                nutrient_relations = []
                for p in batch:
                    for nutrient in p['nutrients']:
                        nutrient_relations.append({
                            'product_id': p['node']['id'],
                            'nutrient_name': nutrient['name'],
                            'value': nutrient['value'],
                            'unit': nutrient['unit']
                        })
                
                if nutrient_relations:
                    session.run("""
                        UNWIND $relations AS rel
                        MATCH (p:Product {id: rel.product_id})
                        MATCH (n:Nutrient {name: rel.nutrient_name})
                        MERGE (p)-[r:HAS_NUTRIENT]->(n)
                        SET r.value = rel.value,
                            r.unit = rel.unit
                    """, relations=nutrient_relations)
                    
                    self.stats["nutriments"] += len(nutrient_relations)
            
            logger.info(f"Progrès relations {relationship_type}: {min(i+batch_size, total)}/{total}")
            
        elapsed = time.time() - start_time
        logger.info(f"Création des relations {relationship_type} terminée en {elapsed:.2f} secondes")
    
    def load_json_products(self, file_path, limit=None):
        """Charge les produits depuis un fichier JSON et les ajoute au graphe"""
        start_time = time.time()
        products = []
        
        logger.info(f"Chargement du fichier {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Pour un fichier JSONL (une ligne JSON par produit)
            lines = f.readlines()
            for line in lines:
                if line.strip():  # Ignorer les lignes vides
                    try:
                        product = json.loads(line)
                        products.append(product)
                    except json.JSONDecodeError:
                        logger.error(f"Erreur de décodage JSON: {line[:50]}...")
                        self.stats["erreurs_json"] += 1
        
        total_products = len(products)
        logger.info(f"Fichier chargé: {total_products} produits trouvés")
        
        # Limiter le nombre de produits si spécifié
        if limit and limit < total_products:
            products = products[:limit]
            logger.info(f"Limitation à {limit} produits...")
        
        # Créer les contraintes avant d'ajouter les produits
        self.create_constraints()
        
        # Prétraiter les produits pour extraire toutes les entités uniques
        logger.info("Prétraitement des produits...")
        preprocessed = self.preprocess_products(products)
        logger.info(f"Prétraitement terminé: {len(preprocessed['products'])} produits valides")
        
        # Créer tous les nœuds d'entité en premier
        with self.driver.session() as session:
            # Créer les nutriments (entités fixes)
            key_nutrients = ['Énergie', 'Matières grasses', 'Protéines', 'Glucides', 'Sucres', 'Sodium', 'Sel', 'Fibres']
            self.create_entity_nodes_batch(session, "Nutrient", key_nutrients)
            
            # Créer les entités uniques
            self.create_entity_nodes_batch(session, "Brand", preprocessed['unique_brands'])
            self.create_entity_nodes_batch(session, "Category", preprocessed['unique_categories'])
            self.create_entity_nodes_batch(session, "Country", preprocessed['unique_countries'])
            self.create_entity_nodes_batch(session, "Ingredient", preprocessed['unique_ingredients'])
            self.create_entity_nodes_batch(session, "Allergen", preprocessed['unique_allergens'])
            self.create_entity_nodes_batch(session, "Label", preprocessed['unique_labels'])
            
            # Créer les nœuds de produits
            self.create_product_nodes_batch(session, preprocessed['products'])
            
            # Créer les relations
            self.create_relationships_batch(session, preprocessed['products'], "BELONGS_TO")
            self.create_relationships_batch(session, preprocessed['products'], "CATEGORIZED_AS")
            self.create_relationships_batch(session, preprocessed['products'], "PRODUCED_IN")
            self.create_relationships_batch(session, preprocessed['products'], "CONTAINS")
            self.create_relationships_batch(session, preprocessed['products'], "CONTAINS_ALLERGEN")
            self.create_relationships_batch(session, preprocessed['products'], "HAS_LABEL")
            self.create_relationships_batch(session, preprocessed['products'], "HAS_NUTRIENT")
        
        self.stats["produits_ajoutes"] = len(preprocessed['products'])
        
        # Afficher les statistiques
        elapsed = time.time() - start_time
        logger.info(f"Chargement terminé en {elapsed:.2f} secondes ({elapsed/60:.2f} minutes)")
        logger.info("=== Statistiques de chargement ===")
        for key, value in self.stats.items():
            logger.info(f"{key}: {value}")
        
        return self.stats["produits_ajoutes"]

    def add_indexes(self):
        """Ajouter des index pour améliorer les performances des requêtes"""
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX product_name_index IF NOT EXISTS FOR (p:Product) ON (p.name)",
                "CREATE INDEX brand_name_index IF NOT EXISTS FOR (b:Brand) ON (b.name)",
                "CREATE INDEX category_name_index IF NOT EXISTS FOR (c:Category) ON (c.name)",
                "CREATE INDEX ingredient_name_index IF NOT EXISTS FOR (i:Ingredient) ON (i.name)",
                "CREATE INDEX product_nutriscore_index IF NOT EXISTS FOR (p:Product) ON (p.nutriscore)",
                "CREATE INDEX product_nova_index IF NOT EXISTS FOR (p:Product) ON (p.nova_group)",
                "CREATE INDEX product_ecoscore_index IF NOT EXISTS FOR (p:Product) ON (p.ecoscore)"
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                    logger.info(f"Index créé: {index}")
                except Exception as e:
                    logger.error(f"Erreur lors de la création de l'index: {e}")

def main():
    # Chemin vers le fichier de données
    file_path = "../../data/openfoodfacts-canadian-products.jsonl"

    # neo4j.exceptions.ClientError: {code: Neo.ClientError.Transaction.TransactionHookFailed} 
    # {message: You have exceeded the logical size limit of 400000 relationships in your database 
    # (attempt to add 575 relationships would reach 400498 relationships). Please consider 
    # upgrading to the next tier.}
    # With limit=1000, elapsed time: 46 seconds
    limit = 1000
    clear_db = True  # Paramètre pour contrôler si on efface ou non

    # Initialiser le graphe
    graph = OpenFoodFactsGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    start = time.time()

    try:
        if clear_db:
            graph.clear_database()

        # Charger les produits
        num_products = graph.load_json_products(file_path, limit)
        logger.info(f"{num_products} produits ont été chargés dans le graphe Neo4j.")
        
        # Ajouter des index pour améliorer les performances
        graph.add_indexes()
        
    finally:
        # Fermer la connexion
        graph.close()
        
    end = time.time()
    logger.info(f"Temps d'exécution: {end - start:.2f} secondes")


if __name__ == "__main__":
    main()