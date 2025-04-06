from neo4j import GraphDatabase
import os
import json
from dotenv import load_dotenv
import logging

logging.basicConfig(
    filename="query.log",  # Nom du fichier log
    filemode="w",          # "a" pour ajouter à la fin du fichier ou "w" pour écraser à chaque exécution
    level=logging.INFO,    # Niveau de log (INFO, DEBUG, ERROR, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Charger les variables d'environnement
load_dotenv()

# Configuration Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class OpenFoodFactsQuery:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        """Fermer la connexion au driver Neo4j"""
        self.driver.close()
        
    def execute_query(self, query, params=None):
        """Exécuter une requête Cypher et retourner les résultats"""
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
    
    def get_node_counts(self):
        """Obtenir le nombre de nœuds par type"""
        query = """
        MATCH (n)
        RETURN labels(n) AS NodeType, count(*) AS Count
        ORDER BY Count DESC
        """
        return self.execute_query(query)
    
    def get_products_by_brand(self, brand_name):
        """Trouver tous les produits d'une marque spécifique"""
        query = """
        MATCH (p:Product)-[:HAS_BRAND]->(b:Brand {name: $brand})
        RETURN p.name, p.nutriscore_grade AS nutriscore, p.quantity
        """
        return self.execute_query(query, {"brand": brand_name})
    
    def get_products_by_category(self, category_name):
        """Trouver tous les produits dans une catégorie"""
        query = """
        MATCH (p:Product)-[:HAS_CATEGORY]->(c:Category {name: $category})
        RETURN p.name, p.nutriscore_grade AS nutriscore
        """
        return self.execute_query(query, {"category": category_name})
    
    def get_products_by_ingredient(self, ingredient_term):
        """Trouver tous les produits qui contiennent un ingrédient spécifique (insensible à la casse)"""
        query = """
        MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
        WHERE toLower(i.name) CONTAINS toLower($ingredient)
        RETURN p.name, p.nutriscore_grade AS nutriscore
        """
        return self.execute_query(query, {"ingredient": ingredient_term})
    
    def get_vegan_products(self):
        """Trouver des produits potentiellement végétaliens"""
        query = """
        MATCH (p:Product)
        WHERE NOT (p)-[:CONTAINS]->(:Ingredient)<-[:HAS_CHILD*]-(i:Ingredient {name: 'Animal products'})
        RETURN p.name, p.code AS id
        LIMIT 10
        """
        return self.execute_query(query)
    
    def get_products_without_allergen(self, allergen_name):
        """Trouver des produits sans un allergène spécifique"""
        query = """
        MATCH (p:Product)
        WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {name: $allergen})
        RETURN p.name, p.code AS id
        LIMIT 10
        """
        return self.execute_query(query, {"allergen": allergen_name})
    
    def get_products_by_nutriscore(self, scores):
        """Trouver tous les produits avec des Nutri-Scores spécifiques"""
        query = """
        MATCH (p:Product)
        WHERE p.nutriscore_grade IN $scores
        RETURN p.name, p.nutriscore_grade AS nutriscore
        ORDER BY p.nutriscore_grade
        LIMIT 10
        """
        return self.execute_query(query, {"scores": scores})
    
    def get_top_ingredients(self, limit=10):
        """Identifier les ingrédients les plus courants"""
        query = """
        MATCH (:Product)-[:CONTAINS]->(i:Ingredient)
        RETURN i.name, count(*) AS occurrences
        ORDER BY occurrences DESC
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})

    def get_similar_products(self, min_common_ingredients=3):
        """Trouver des produits similaires basés sur des ingrédients communs"""
        query = """
        MATCH (p1:Product)-[:CONTAINS]->(i:Ingredient)<-[:CONTAINS]-(p2:Product)
        WHERE p1.code < p2.code
        WITH p1, p2, count(i) AS common_ingredients
        WHERE common_ingredients > $min_common
        RETURN p1.name, p2.name, common_ingredients
        ORDER BY common_ingredients DESC
        LIMIT 10
        """
        return self.execute_query(query, {"min_common": min_common_ingredients})

    def get_nutriment_info(self, product_code):
        """Obtenir toutes les informations nutritionnelles d'un produit spécifique"""
        query = """
        MATCH (p:Product {code: $code})-[r:HAS_NUTRIMENT]->(n:Nutriment)
        RETURN n.name, r.value, r.unit
        """
        return self.execute_query(query, {"code": product_code})

    def get_healthier_alternatives(self, product_code):
        """Trouver des alternatives plus saines dans la même catégorie"""
        query = """
        MATCH (p1:Product {code: $code})-[:HAS_CATEGORY]->(c:Category)
        MATCH (p2:Product)-[:HAS_CATEGORY]->(c)
        WHERE p2.code <> p1.code 
          AND p2.nutriscore_grade IS NOT NULL 
          AND p1.nutriscore_grade IS NOT NULL
          AND p2.nutriscore_grade < p1.nutriscore_grade
        RETURN p1.name, p1.nutriscore_grade AS p1_nutriscore, 
               p2.name, p2.nutriscore_grade AS p2_nutriscore
        ORDER BY p2.nutriscore_grade
        LIMIT 5
        """
        return self.execute_query(query, {"code": product_code})

    def get_consolidated_ingredients(self, limit=10):
        """Identifier les ingrédients les plus courants en consolidant les variantes"""
        query = """
        MATCH (:Product)-[:CONTAINS]->(i:Ingredient)
        RETURN toLower(i.name) AS ingredient_name, count(*) AS occurrences
        ORDER BY occurrences DESC
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})

    def visualize_product_relationships(self, product_code):
        """
        Visualise un produit et ses relations sans afficher les embeddings.
        Retourne le code, le nom et le nom générique du produit,
        le type de relation et le nom du nœud relié.
        """
        query = """
        MATCH (p:Product {code: $code})-[r]->(n)
        RETURN p.code AS code, p.name AS name, p.generic_name AS generic_name,
               type(r) AS relation, n.name AS related_name
        """
        return self.execute_query(query, {"code": product_code})

    
    def visualize_category_hierarchy(self, limit=20):
        """
        Visualise la hiérarchie des catégories.
        Retourne chaque relation HAS_CHILD entre les nœuds Category, triée par nom de catégorie parent.
        """
        query = """
        MATCH (c:Category)-[r:HAS_CHILD]->(child:Category)
        RETURN c.name AS parent, child.name AS child
        ORDER BY c.name
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})
    
    def find_products_by_natural_language(self, query_text, limit=5):
        """
        Recherche des produits en utilisant une requête en langage naturel.
        Exploite la recherche par taxonomie.
        """
        # Version simplifiée qui évite les problèmes de syntaxe
        query = """
        MATCH (p:Product)
        WHERE 
        EXISTS {
            MATCH (p)-[:HAS_CATEGORY]->(c:Category)
            WHERE any(keyword IN $keywords WHERE toLower(c.name) CONTAINS keyword)
        }
        OR 
        EXISTS {
            MATCH (p)-[:CONTAINS]->(i:Ingredient)
            WHERE any(keyword IN $keywords WHERE toLower(i.name) CONTAINS keyword) 
        }
        OR
        EXISTS {
            MATCH (p)-[:HAS_LABEL]->(l:Label)
            WHERE any(keyword IN $keywords WHERE toLower(l.name) CONTAINS keyword)
        }
        RETURN p.code AS code, p.name AS name, p.generic_name AS generic_name, 
            p.nutriscore_grade AS nutriscore, 1.0 AS score
        ORDER BY score DESC
        LIMIT $limit
        """
        
        # Traitement simple des mots-clés
        keywords = query_text.lower().split()
        
        return self.execute_query(query, {
            "keywords": keywords,
            "limit": limit
        })

def afficher_produit(code_recherche, logging):
    file_path = "../../data/openfoodfacts-canadian-products.jsonl"
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                produit = json.loads(line)
                if produit.get("code") == code_recherche:
                    logging.info("Produit trouvé :")
                    logging.info(json.dumps(produit, indent=4, ensure_ascii=False))
                    return
            except json.JSONDecodeError:
                continue
    logging.info(f"Aucun produit trouvé avec le code {code_recherche}.")

def main():
    query_engine = OpenFoodFactsQuery(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        logging.info("=== Nombre de nœuds par type ===")
        node_counts = query_engine.get_node_counts()
        for record in node_counts:
            logging.info(f"{record['NodeType']}: {record['Count']}")
        
        logging.info("\n=== Produits de la marque 'Butternut Mountain Farm' ===")
        brand_products = query_engine.get_products_by_brand("Butternut Mountain Farm")
        for product in brand_products:
            logging.info(f"{product['p.name']} - Nutriscore: {product['nutriscore']} - Quantité: {product['p.quantity']}")
        
        logging.info("\n=== Top 5 ingrédients les plus courants ===")
        top_ingredients = query_engine.get_top_ingredients(5)
        for ingredient in top_ingredients:
            logging.info(f"{ingredient['i.name']}: {ingredient['occurrences']} occurrences")
        
        logging.info("\n=== Ingrédients les plus courants en consolidant les variantes ===")
        top_ingredients = query_engine.get_consolidated_ingredients(10)
        for ingredient in top_ingredients:
            logging.info(f"{ingredient['ingredient_name']}: {ingredient['occurrences']} occurrences")

        # Visualiser les relations d'un produit spécifique
        product_code = "0008577002786"
        logging.info(f"\n=== Visualisation des relations du produit '{product_code}' ===")
        afficher_produit(product_code, logging)
        prod_rel = query_engine.visualize_product_relationships(product_code)
        for record in prod_rel:
            logging.info(record)
        
        # Visualiser la hiérarchie des catégories
        logging.info("\n=== Visualisation de la hiérarchie des catégories ===")
        cat_hierarchy = query_engine.visualize_category_hierarchy()
        for record in cat_hierarchy:
            logging.info(record)
            
        # Recherche de produits sans gluten
        logging.info("\n=== Recherche de produits sans gluten ===")
        gluten_free = query_engine.find_products_by_natural_language("sans gluten")
        for product in gluten_free:
            logging.info(f"{product['name']} - {product['generic_name']} - Nutriscore: {product['nutriscore']}")
            
        # Recherche de produits avec alternative plus saine
        logging.info("\n=== Alternatives plus saines pour le produit ===")
        healthier = query_engine.get_healthier_alternatives(product_code)
        for alt in healthier:
            logging.info(f"Original: {alt['p1.name']} (Nutriscore: {alt['p1_nutriscore']}) → Alternative: {alt['p2.name']} (Nutriscore: {alt['p2_nutriscore']})")
            
        # Informations nutritionnelles d'un produit
        logging.info("\n=== Informations nutritionnelles ===")
        nutrients = query_engine.get_nutriment_info(product_code)
        for nutrient in nutrients:
            logging.info(f"{nutrient['n.name']}: {nutrient['r.value']} {nutrient['r.unit']}")

    finally:
        query_engine.close()


if __name__ == "__main__":
    main()