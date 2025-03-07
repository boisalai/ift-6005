import json
import os
import time
from neo4j import GraphDatabase
import logging
from dotenv import load_dotenv
from collections import defaultdict

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
    
    def add_product(self, product_data):
        """Ajouter un produit et ses relations à la base de données"""
        try:
            # Extraction des données du produit
            product_id = self.extract_field(product_data, '_id', '')
            if not product_id:
                logger.warning("Produit sans ID ignoré")
                self.stats["produits_sans_id"] += 1
                return False
                
            # Extraction du nom du produit (priorité à product_name, sinon product_name_en)
            product_name = self.extract_field(product_data, 'product_name', '')
            if not product_name:
                product_name = self.extract_field(product_data, 'product_name_en', '')
            
            if not product_name:
                logger.warning(f"Produit {product_id} sans nom ignoré")
                self.stats["produits_sans_nom"] += 1
                return False
            
            # Données de base du produit
            quantity = self.extract_field(product_data, 'quantity', '')
            nutriscore = self.extract_field(product_data, 'nutriscore_grade', '')
            nova_group = self.extract_field(product_data, 'nova_group', None)
            ecoscore = self.extract_field(product_data, 'ecoscore_grade', '')
            
            # Vérification des données nutritionnelles
            has_nutrition = self.extract_field(product_data, 'nutriments') is not None
            
            # Création du produit
            with self.driver.session() as session:
                session.run("""
                    MERGE (p:Product {id: $id})
                    SET p.name = $name,
                        p.quantity = $quantity,
                        p.nutriscore = $nutriscore,
                        p.nova_group = $nova_group,
                        p.ecoscore = $ecoscore,
                        p.has_nutrition = $has_nutrition
                """, id=product_id, name=product_name, quantity=quantity, 
                    nutriscore=nutriscore, nova_group=nova_group, ecoscore=ecoscore,
                    has_nutrition=has_nutrition)
                
                # Ajouter les marques
                brands = self.extract_field(product_data, 'brands', '').split(',')
                brands = [brand.strip() for brand in brands if brand.strip()]
                
                for brand in brands:
                    session.run("""
                        MERGE (b:Brand {name: $name})
                        WITH b
                        MATCH (p:Product {id: $product_id})
                        MERGE (p)-[:BELONGS_TO]->(b)
                    """, name=brand, product_id=product_id)
                    
                    self.stats["marques"] += 1
                
                # Ajouter les catégories
                categories = self.extract_field(product_data, 'categories', '').split(',')
                categories = [category.strip() for category in categories if category.strip()]
                
                for category in categories:
                    session.run("""
                        MERGE (c:Category {name: $name})
                        WITH c
                        MATCH (p:Product {id: $product_id})
                        MERGE (p)-[:CATEGORIZED_AS]->(c)
                    """, name=category, product_id=product_id)
                    
                    self.stats["categories"] += 1
                
                # Ajouter les pays
                countries = self.extract_field(product_data, 'countries', '').split(',')
                countries = [country.strip() for country in countries if country.strip()]
                
                for country in countries:
                    session.run("""
                        MERGE (c:Country {name: $name})
                        WITH c
                        MATCH (p:Product {id: $product_id})
                        MERGE (p)-[:PRODUCED_IN]->(c)
                    """, name=country, product_id=product_id)
                    
                    self.stats["pays"] += 1
                
                # Ajouter les ingrédients
                ingredients_list = []
                if "ingredients" in product_data and isinstance(product_data["ingredients"], list):
                    for ingr in product_data["ingredients"]:
                        if isinstance(ingr, dict) and "text" in ingr:
                            ingredients_list.append({
                                "name": ingr["text"],
                                "vegan": ingr.get("vegan", "unknown"),
                                "vegetarian": ingr.get("vegetarian", "unknown")
                            })
                
                # Si pas d'ingrédients détaillés, essayer avec ingredients_text
                if not ingredients_list and "ingredients_text" in product_data:
                    text = product_data["ingredients_text"]
                    if text:
                        raw_ingredients = [i.strip() for i in text.split(',') if i.strip()]
                        ingredients_list = [{"name": ingr, "vegan": "unknown", "vegetarian": "unknown"} 
                                           for ingr in raw_ingredients]
                
                for ingredient in ingredients_list:
                    session.run("""
                        MERGE (i:Ingredient {name: $name})
                        SET i.vegan = $vegan,
                            i.vegetarian = $vegetarian
                        WITH i
                        MATCH (p:Product {id: $product_id})
                        MERGE (p)-[:CONTAINS]->(i)
                    """, name=ingredient["name"], vegan=ingredient["vegan"], 
                         vegetarian=ingredient["vegetarian"], product_id=product_id)
                    
                    self.stats["ingredients"] += 1
                
                # Ajouter les allergènes
                allergens = []
                if "allergens_tags" in product_data:
                    allergens = [allergen.replace("en:", "") for allergen in product_data["allergens_tags"]]
                
                for allergen in allergens:
                    session.run("""
                        MERGE (a:Allergen {name: $name})
                        WITH a
                        MATCH (p:Product {id: $product_id})
                        MERGE (p)-[:CONTAINS_ALLERGEN]->(a)
                    """, name=allergen, product_id=product_id)
                    
                    self.stats["allergenes"] += 1
                
                # Ajouter les valeurs nutritionnelles
                if "nutriments" in product_data:
                    nutriments = product_data["nutriments"]
                    
                    # Ajouter les valeurs nutritionnelles de base dans le produit
                    session.run("""
                        MATCH (p:Product {id: $id})
                        SET p.energy = $energy,
                            p.fat = $fat,
                            p.proteins = $proteins,
                            p.carbohydrates = $carbohydrates,
                            p.sugars = $sugars,
                            p.sodium = $sodium,
                            p.salt = $salt,
                            p.fiber = $fiber
                    """, id=product_id, 
                         energy=self.extract_field(nutriments, 'energy', None),
                         fat=self.extract_field(nutriments, 'fat', None),
                         proteins=self.extract_field(nutriments, 'proteins', None),
                         carbohydrates=self.extract_field(nutriments, 'carbohydrates', None),
                         sugars=self.extract_field(nutriments, 'sugars', None),
                         sodium=self.extract_field(nutriments, 'sodium', None),
                         salt=self.extract_field(nutriments, 'salt', None),
                         fiber=self.extract_field(nutriments, 'fiber', None))
                    
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
                            
                            session.run("""
                                MERGE (n:Nutrient {name: $name})
                                WITH n
                                MATCH (p:Product {id: $product_id})
                                MERGE (p)-[r:HAS_NUTRIENT]->(n)
                                SET r.value = $value,
                                    r.unit = $unit
                            """, name=name, product_id=product_id, value=value, unit=unit)
                            
                            self.stats["nutriments"] += 1
                
                # Ajouter les labels (ex: Bio, Sans Gluten, etc.)
                labels = []
                if "labels_tags" in product_data:
                    labels = [label.replace("en:", "") for label in product_data["labels_tags"]]
                
                for label in labels:
                    session.run("""
                        MERGE (l:Label {name: $name})
                        WITH l
                        MATCH (p:Product {id: $product_id})
                        MERGE (p)-[:HAS_LABEL]->(l)
                    """, name=label, product_id=product_id)
                    
                    self.stats["labels"] += 1
                
                self.stats["produits_ajoutes"] += 1
                return True
                
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du produit {product_data.get('_id', 'inconnu')}: {e}")
            self.stats["erreurs"] += 1
            return False
    
    def load_json_products(self, file_path, limit=None):
        """Charge les produits depuis un fichier JSON et les ajoute au graphe"""
        products = []
        
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
        logger.info(f"Chargement de {total_products} produits...")
        
        # Limiter le nombre de produits si spécifié
        if limit and limit < total_products:
            products = products[:limit]
            logger.info(f"Limitation à {limit} produits...")
        
        # Créer les contraintes avant d'ajouter les produits
        self.create_constraints()
        
        # Ajouter chaque produit
        for i, product in enumerate(products, 1):
            success = self.add_product(product)
            
            # Log d'avancement
            if i % 10 == 0 or i == len(products):
                logger.info(f"Progression: {i}/{len(products)} produits traités")
        
        # Afficher les statistiques
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
    limit = 1000  # Limiter le nombre de produits à charger
    clear_db = True  # Paramètre pour contrôler si on efface ou non

    # Initialiser le graphe
    graph = OpenFoodFactsGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    start = time.time()

    try:
        if clear_db:
            graph.clear_database()

        graph.create_constraints()
        
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

"""
// 1. Vue d'ensemble du graphe
// Nombre total de nœuds par type
MATCH (n)
RETURN labels(n) AS NodeType, count(*) AS Count
ORDER BY Count DESC;

// 2. Produits par marque
// Trouver tous les produits d'une marque spécifique
MATCH (p:Product)-[:BELONGS_TO]->(b:Brand {name: "Butternut Mountain Farm"})
RETURN p.name, p.nutriscore, p.quantity;

// 3. Produits par catégorie
// Trouver tous les produits dans une catégorie
MATCH (p:Product)-[:CATEGORIZED_AS]->(c:Category {name: "Syrups"})
RETURN p.name, p.nutriscore;

// 4. Recherche par ingrédient
// Trouver tous les produits qui contiennent un ingrédient spécifique
MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
WHERE i.name CONTAINS 'sugar'
RETURN p.name, p.nutriscore;

// 5. Produits végétaliens
// Trouver des produits potentiellement végétaliens
MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
WITH p, collect(i.vegan) AS vegan_status
WHERE ALL(status IN vegan_status WHERE status = 'yes')
RETURN p.name, p.id;

// 6. Produits sans allergènes spécifiques
// Trouver des produits sans lait
MATCH (p:Product)
WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {name: 'milk'})
RETURN p.name, p.id;

// 7. Produits par Nutri-Score
// Trouver tous les produits avec un bon Nutri-Score (A ou B)
MATCH (p:Product)
WHERE p.nutriscore IN ['a', 'b', 'A', 'B']
RETURN p.name, p.nutriscore
ORDER BY p.nutriscore;

// 8. Produits par NOVa (traitement)
// Trouver des produits peu transformés (NOVA 1 ou 2)
MATCH (p:Product)
WHERE p.nova_group IN [1, 2]
RETURN p.name, p.nova_group;

// 9. Produits avec de bons scores environnementaux
// Trouver des produits avec un bon Eco-Score
MATCH (p:Product)
WHERE p.ecoscore IN ['a', 'b', 'A', 'B']
RETURN p.name, p.ecoscore;

// 10. Comparaison nutritionnelle
// Comparer les valeurs nutritionnelles entre produits similaires
MATCH (p1:Product)-[:CATEGORIZED_AS]->(c:Category {name: 'Maple syrups'})
MATCH (p2:Product)-[:CATEGORIZED_AS]->(c)
WHERE p1.id < p2.id // Pour éviter les doublons
RETURN p1.name, p1.sugars, p2.name, p2.sugars;

// 11. Recherche de produits par pays
// Trouver des produits fabriqués dans un pays spécifique
MATCH (p:Product)-[:PRODUCED_IN]->(c:Country {name: "Canada"})
RETURN p.name;

// 12. Produits avec un label spécifique
// Trouver des produits bio
MATCH (p:Product)-[:HAS_LABEL]->(:Label {name: "organic"})
RETURN p.name;

// 13. Top ingrédients
// Identifier les ingrédients les plus courants
MATCH (:Product)-[:CONTAINS]->(i:Ingredient)
RETURN i.name, count(*) AS occurrences
ORDER BY occurrences DESC
LIMIT 10;

// 14. Allergènes les plus courants
// Identifier les allergènes les plus fréquents
MATCH (:Product)-[:CONTAINS_ALLERGEN]->(a:Allergen)
RETURN a.name, count(*) AS occurrences
ORDER BY occurrences DESC;

// 15. Graphe de relations entre produits similaires
// Trouver des produits similaires basés sur des ingrédients communs
MATCH (p1:Product)-[:CONTAINS]->(i:Ingredient)<-[:CONTAINS]-(p2:Product)
WHERE p1.id < p2.id // Pour éviter les doublons
WITH p1, p2, count(i) AS common_ingredients
WHERE common_ingredients > 3 // Au moins 3 ingrédients communs
RETURN p1.name, p2.name, common_ingredients
ORDER BY common_ingredients DESC;

// 16. Produits contenant des ingrédients controversés (ex: huile de palme)
MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
WHERE i.name CONTAINS 'palm oil'
RETURN p.name;

// 17. Informations nutritionnelles détaillées
// Obtenir toutes les informations nutritionnelles d'un produit spécifique
MATCH (p:Product {id: "0008577002786"})-[r:HAS_NUTRIENT]->(n:Nutrient)
RETURN n.name, r.value, r.unit;

// 18. Produits avec les meilleures valeurs nutritionnelles dans une catégorie
// Par exemple, les produits avec le moins de sucre dans une catégorie
MATCH (p:Product)-[:CATEGORIZED_AS]->(:Category {name: "Syrups"})
WHERE p.sugars IS NOT NULL
RETURN p.name, p.sugars
ORDER BY p.sugars ASC
LIMIT 5;

// 19. Relations entre catégories et allergènes
// Identifier les catégories de produits les plus susceptibles de contenir certains allergènes
MATCH (p:Product)-[:CATEGORIZED_AS]->(c:Category)
MATCH (p)-[:CONTAINS_ALLERGEN]->(a:Allergen)
WITH c, a, count(p) AS product_count
RETURN c.name, a.name, product_count
ORDER BY product_count DESC;

// 20. Produits avec recommandations alternatives plus saines
// Trouver des alternatives plus saines dans la même catégorie
MATCH (p1:Product {id: "0008577002786"})-[:CATEGORIZED_AS]->(c:Category)
MATCH (p2:Product)-[:CATEGORIZED_AS]->(c)
WHERE p2.id <> p1.id AND p2.nutriscore < p1.nutriscore
RETURN p1.name, p1.nutriscore, p2.name, p2.nutriscore
ORDER BY p2.nutriscore;
"""