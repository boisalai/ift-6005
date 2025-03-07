from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

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
        MATCH (p:Product)-[:BELONGS_TO]->(b:Brand {name: $brand})
        RETURN p.name, p.nutriscore, p.quantity
        """
        return self.execute_query(query, {"brand": brand_name})
    
    def get_products_by_category(self, category_name):
        """Trouver tous les produits dans une catégorie"""
        query = """
        MATCH (p:Product)-[:CATEGORIZED_AS]->(c:Category {name: $category})
        RETURN p.name, p.nutriscore
        """
        return self.execute_query(query, {"category": category_name})
    
    def get_products_by_ingredient(self, ingredient_term):
        """Trouver tous les produits qui contiennent un ingrédient spécifique (insensible à la casse)"""
        query = """
        MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
        WHERE toLower(i.name) CONTAINS toLower($ingredient)
        RETURN p.name, p.nutriscore
        """
        return self.execute_query(query, {"ingredient": ingredient_term})
    
    def get_vegan_products(self):
        """Trouver des produits potentiellement végétaliens"""
        query = """
        MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
        WITH p, collect(i.vegan) AS vegan_status
        WHERE ALL(status IN vegan_status WHERE status = 'yes')
        RETURN p.name, p.id
        """
        return self.execute_query(query)
    
    def get_products_without_allergen(self, allergen_name):
        """Trouver des produits sans un allergène spécifique"""
        query = """
        MATCH (p:Product)
        WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {name: $allergen})
        RETURN p.name, p.id
        """
        return self.execute_query(query, {"allergen": allergen_name})
    
    def get_products_by_nutriscore(self, scores):
        """Trouver tous les produits avec des Nutri-Scores spécifiques"""
        query = """
        MATCH (p:Product)
        WHERE p.nutriscore IN $scores
        RETURN p.name, p.nutriscore
        ORDER BY p.nutriscore
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
        WHERE p1.id < p2.id
        WITH p1, p2, count(i) AS common_ingredients
        WHERE common_ingredients > $min_common
        RETURN p1.name, p2.name, common_ingredients
        ORDER BY common_ingredients DESC
        """
        return self.execute_query(query, {"min_common": min_common_ingredients})

    def get_nutrient_info(self, product_id):
        """Obtenir toutes les informations nutritionnelles d'un produit spécifique"""
        query = """
        MATCH (p:Product {id: $id})-[r:HAS_NUTRIENT]->(n:Nutrient)
        RETURN n.name, r.value, r.unit
        """
        return self.execute_query(query, {"id": product_id})

    def get_healthier_alternatives(self, product_id):
        """Trouver des alternatives plus saines dans la même catégorie"""
        query = """
        MATCH (p1:Product {id: $id})-[:CATEGORIZED_AS]->(c:Category)
        MATCH (p2:Product)-[:CATEGORIZED_AS]->(c)
        WHERE p2.id <> p1.id AND p2.nutriscore < p1.nutriscore
        RETURN p1.name, p1.nutriscore, p2.name, p2.nutriscore
        ORDER BY p2.nutriscore
        """
        return self.execute_query(query, {"id": product_id})

    def get_consolidated_ingredients(self, limit=10):
        """Identifier les ingrédients les plus courants en consolidant les variantes"""
        query = """
        MATCH (:Product)-[:CONTAINS]->(i:Ingredient)
        RETURN toLower(i.name) AS ingredient_name, count(*) AS occurrences
        ORDER BY occurrences DESC
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})

# Exemple d'utilisation
def main():
    query_engine = OpenFoodFactsQuery(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # Exemple de requêtes
        print("=== Nombre de nœuds par type ===")
        node_counts = query_engine.get_node_counts()
        for record in node_counts:
            print(f"{record['NodeType']}: {record['Count']}")
        
        print("\n=== Produits de la marque 'Butternut Mountain Farm' ===")
        brand_products = query_engine.get_products_by_brand("Butternut Mountain Farm")
        for product in brand_products:
            print(f"{product['p.name']} - Nutriscore: {product['p.nutriscore']} - Quantité: {product['p.quantity']}")
        
        print("\n=== Top 5 ingrédients les plus courants ===")
        top_ingredients = query_engine.get_top_ingredients(5)
        for ingredient in top_ingredients:
            print(f"{ingredient['i.name']}: {ingredient['occurrences']} occurrences")
        
        print("\n=== Ingrédients les plus courants en consolidant les variantes ===")
        top_ingredients = query_engine.get_consolidated_ingredients(100)
        for ingredient in top_ingredients:
            print(f"{ingredient['ingredient_name']}: {ingredient['occurrences']} occurrences")

    finally:
        query_engine.close()

if __name__ == "__main__":
    main()