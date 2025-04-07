import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

def verify_neo4j_schema():
    """
    Ce script vérifie que le schéma du graphe dans Neo4j correspond à ce qui est 
    décrit dans le README.md. Il exécute une série de requêtes Cypher pour 
    valider l'existence des nœuds, relations et index.
    """
    # Chargement des variables d'environnement
    load_dotenv()
    
    # Configuration de la connexion à Neo4j
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    
    # Connexion à la base de données Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        with driver.session() as session:
            # 1. Vérification des types de nœuds
            print("\n=== TYPES DE NŒUDS ===")
            query_node_types = """
            CALL db.labels() YIELD label
            RETURN label AS NodeType, count(*) AS Count
            ORDER BY Count DESC;
            """
            print("Vérification de tous les types de nœuds existants...")
            result = session.run(query_node_types)
            for record in result:
                print(f"{record['NodeType']}: {record['Count']}")
                
            # 2. Vérification des propriétés des nœuds Product
            print("\n=== PROPRIÉTÉS DES NŒUDS PRODUCT ===")
            query_product_props = """
            MATCH (p:Product) 
            RETURN 
                count(p) AS TotalProducts,
                count(p.code) AS code_count,
                count(p.name) AS name_count,
                count(p.product_name_en) AS product_name_en_count,
                count(p.product_name_fr) AS product_name_fr_count,
                count(p.generic_name) AS generic_name_count,
                count(p.quantity) AS quantity_count,
                count(p.nutriscore_grade) AS nutriscore_grade_count,
                count(p.nova_group) AS nova_group_count,
                count(p.ecoscore_grade) AS ecoscore_grade_count,
                count(p.embedding) AS embedding_count
            LIMIT 1;
            """
            print("Vérification des propriétés des nœuds Product (nombre de nœuds avec chaque propriété)...")
            result = session.run(query_product_props)
            for record in result:
                for key, value in record.items():
                    print(f"{key}: {value}")
            
            # 3. Vérification de tous les types de relations
            print("\n=== TYPES DE RELATIONS ===")
            query_relation_types = """
            CALL db.relationshipTypes() YIELD relationshipType
            RETURN relationshipType
            ORDER BY relationshipType;
            """
            print("Vérification de tous les types de relations existants...")
            result = session.run(query_relation_types)
            for record in result:
                print(record["relationshipType"])
                
            # 4. Comptage des relations de chaque type
            print("\n=== NOMBRE DE RELATIONS PAR TYPE ===")
            query_relation_counts = """
            MATCH ()-[r]->()
            RETURN type(r) AS RelationType, count(r) AS Count
            ORDER BY Count DESC;
            """
            print("Comptage du nombre de relations par type...")
            result = session.run(query_relation_counts)
            for record in result:
                print(f"{record['RelationType']}: {record['Count']}")
            
            # 5. Vérification des relations principales mentionnées dans le README
            print("\n=== VÉRIFICATION DES RELATIONS PRINCIPALES ===")
            query_main_relations = """
            MATCH (:Product)-[r:HAS_BRAND]->(:Brand) RETURN 'HAS_BRAND' AS Relation, COUNT(r) AS Count
            UNION ALL
            MATCH (:Product)-[r:HAS_CATEGORY]->(:Category) RETURN 'HAS_CATEGORY' AS Relation, COUNT(r) AS Count
            UNION ALL
            MATCH (:Product)-[r:CONTAINS]->(:Ingredient) RETURN 'Product-CONTAINS->Ingredient' AS Relation, COUNT(r) AS Count
            UNION ALL
            MATCH (:Product)-[r:CONTAINS_ADDITIF]->(:Additif) RETURN 'CONTAINS_ADDITIF' AS Relation, COUNT(r) AS Count
            UNION ALL
            MATCH (:Product)-[r:CONTAINS_ALLERGEN]->(:Allergen) RETURN 'CONTAINS_ALLERGEN' AS Relation, COUNT(r) AS Count
            UNION ALL
            MATCH (:Product)-[r:HAS_LABEL]->(:Label) RETURN 'HAS_LABEL' AS Relation, COUNT(r) AS Count
            UNION ALL
            MATCH (:Product)-[r:SOLD_IN]->(:Country) RETURN 'SOLD_IN' AS Relation, COUNT(r) AS Count
            UNION ALL
            MATCH (:Product)-[r:HAS_NUTRIMENT]->(:Nutriment) RETURN 'HAS_NUTRIMENT' AS Relation, COUNT(r) AS Count;
            """
            print("Vérification des relations principales entre produits et autres entités...")
            result = session.run(query_main_relations)
            for record in result:
                print(f"{record['Relation']}: {record['Count']}")
            
            # 6. Vérification des relations hiérarchiques
            print("\n=== VÉRIFICATION DES RELATIONS HIÉRARCHIQUES ===")
            print("Vérification des relations hiérarchiques une par une pour éviter les avertissements...")
            
            hierarchical_relations = [
                ("Category", "HAS_CHILD", "Category"),
                ("Ingredient", "CONTAINS", "Ingredient"),
                ("Additif", "PART_OF", "Additif"),
                ("Allergen", "BELONGS_TO", "Allergen"),
                ("Nutriment", "PART_OF", "Nutriment"),
                ("Label", "INCLUDES", "Label")
            ]
            
            for source, rel_type, target in hierarchical_relations:
                try:
                    query = f"""
                    MATCH (:{source})-[r:{rel_type}]->(:{target})
                    RETURN '{source}-{rel_type}->{target}' AS Hierarchy, COUNT(r) AS Count
                    """
                    result = session.run(query)
                    record = result.single()
                    if record:
                        print(f"{record['Hierarchy']}: {record['Count']}")
                    else:
                        print(f"{source}-{rel_type}->{target}: 0")
                except Exception as e:
                    print(f"{source}-{rel_type}->{target}: Relation non trouvée ou erreur: {str(e)}")
            
            # 7. Vérification des propriétés de la relation HAS_NUTRIMENT
            print("\n=== VÉRIFICATION DES PROPRIÉTÉS DE HAS_NUTRIMENT ===")
            query_nutriment_props = """
            MATCH (:Product)-[r:HAS_NUTRIMENT]->(:Nutriment)
            WITH COUNT(r) AS total,
                 SUM(CASE WHEN r.value IS NOT NULL THEN 1 ELSE 0 END) AS value_count,
                 SUM(CASE WHEN r.unit IS NOT NULL THEN 1 ELSE 0 END) AS unit_count
            RETURN total AS total_relations,
                   value_count AS relations_with_value,
                   unit_count AS relations_with_unit,
                   CASE WHEN total > 0 THEN 100.0 * value_count / total ELSE 0 END AS percent_with_value,
                   CASE WHEN total > 0 THEN 100.0 * unit_count / total ELSE 0 END AS percent_with_unit
            """
            print("Vérification des propriétés value et unit sur les relations HAS_NUTRIMENT...")
            result = session.run(query_nutriment_props)
            for record in result:
                print(f"Total relations: {record['total_relations']}")
                print(f"Relations avec propriété value: {record['relations_with_value']} ({record['percent_with_value']:.2f}%)")
                print(f"Relations avec propriété unit: {record['relations_with_unit']} ({record['percent_with_unit']:.2f}%)")
            
            # 8. Vérification de l'existence de l'index vectoriel
            print("\n=== VÉRIFICATION DE L'INDEX VECTORIEL ===")
            # Mise à jour pour Neo4j 5 et versions ultérieures : utiliser SHOW INDEXES au lieu de CALL db.indexes()
            query_vector_index = """
            SHOW INDEXES 
            YIELD name, type, entityType, labelsOrTypes, properties
            WHERE name = 'product_embedding_index'
            RETURN name, type, entityType, labelsOrTypes, properties
            """
            print("Vérification de l'existence de l'index vectoriel product_embedding_index...")
            result = session.run(query_vector_index)
            records = list(result)
            if records:
                print("L'index vectoriel product_embedding_index existe.")
                for record in records:
                    print(f"Nom: {record.get('name', 'N/A')}")
                    print(f"Type: {record.get('type', 'N/A')}")
                    print(f"Type d'entité: {record.get('entityType', 'N/A')}")
                    print(f"Labels/Types: {record.get('labelsOrTypes', 'N/A')}")
                    print(f"Propriétés: {record.get('properties', 'N/A')}")
                    print(f"Provider: {record.get('provider', 'N/A')}")
            else:
                print("Attention: L'index vectoriel product_embedding_index n'existe pas!")
                
            # 9. Vérifier quelques exemples de produits avec des embeddings
            print("\n=== EXEMPLES DE PRODUITS AVEC EMBEDDINGS ===")
            query_products_with_embeddings = """
            MATCH (p:Product)
            WHERE p.embedding IS NOT NULL
            RETURN p.code, p.name, size(p.embedding) AS embedding_size
            LIMIT 5;
            """
            print("Vérification d'exemples de produits avec des embeddings...")
            result = session.run(query_products_with_embeddings)
            for record in result:
                print(f"Produit: {record['p.name']} (code: {record['p.code']})")
                print(f"Taille de l'embedding: {record['embedding_size']} dimensions")
                
            # 10. Vérification de traductions/synonymes stockés dans les nœuds
            print("\n=== VÉRIFICATION DES TRADUCTIONS/SYNONYMES ===")
            query_translations = """
            MATCH (n)
            WHERE n.translations_en IS NOT NULL OR n.translations_fr IS NOT NULL
            RETURN labels(n)[0] AS NodeType, 
                   count(n) AS Count,
                   count(n.translations_en) AS with_en_translations,
                   count(n.translations_fr) AS with_fr_translations
            """
            print("Vérification des nœuds avec des traductions...")
            result = session.run(query_translations)
            for record in result:
                print(f"{record['NodeType']}: {record['Count']} nœuds au total")
                print(f"  - avec traductions anglaises: {record['with_en_translations']}")
                print(f"  - avec traductions françaises: {record['with_fr_translations']}")
                
    finally:
        # Fermeture de la connexion à Neo4j
        driver.close()

if __name__ == "__main__":
    verify_neo4j_schema()
