"""
Ce module centralise toutes les requêtes Cypher utilisées par l'agent.
Il contient les requêtes pour obtenir des informations sur les produits,
les marques, les ingrédients, les allergènes, l'information nutritionnelle,
les recommandations, les régimes et la comparaison de produits.
"""

# Requête pour l'information produit
PRODUCT_INFO = """
MATCH (p:Product)
WHERE toLower(p.name) CONTAINS toLower($product_name)
OPTIONAL MATCH (p)-[:HAS_BRAND]->(b:Brand)
OPTIONAL MATCH (p)-[:HAS_CATEGORY]->(c:Category)
RETURN p.code AS Code,
       p.name AS Produit, 
       p.generic_name AS Description,
       p.nutriscore_grade AS Nutriscore, 
       p.quantity AS Quantité, 
       collect(DISTINCT b.name) AS Marques,
       collect(DISTINCT c.name) AS Catégories
LIMIT 5
"""

# Requête pour obtenir les produits d'une marque
BRAND_PRODUCTS = """
MATCH (p:Product)-[:HAS_BRAND]->(b:Brand)
WHERE toLower(b.name) CONTAINS toLower($brand_name)
RETURN p.code AS Code,
       p.name AS Produit, 
       p.generic_name AS Description,
       p.nutriscore_grade AS Nutriscore, 
       p.quantity AS Quantité
LIMIT 10
"""

# Requête pour les produits contenant un ingrédient spécifique
PRODUCTS_WITH_INGREDIENT = """
MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
WHERE toLower(i.name) CONTAINS toLower($ingredient_name)
RETURN p.code AS Code,
       p.name AS Produit, 
       p.generic_name AS Description,
       p.nutriscore_grade AS Nutriscore, 
       i.name AS Ingrédient
LIMIT 10
"""

# Requête pour les produits sans un allergène spécifique
PRODUCTS_WITHOUT_ALLERGEN = """
MATCH (p:Product)
WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {name: $allergen_name})
RETURN p.code AS Code,
       p.name AS Produit, 
       p.generic_name AS Description,
       p.nutriscore_grade AS Nutriscore
LIMIT 10
"""

# Requête pour l'information nutritionnelle
NUTRITIONAL_INFO = """
MATCH (p:Product)-[r:HAS_NUTRIMENT]->(n:Nutriment)
WHERE toLower(p.name) CONTAINS toLower($product_name)
RETURN p.name AS Produit, 
       n.name AS Nutriment, 
       r.value AS Valeur, 
       r.unit AS Unité
"""

# Requête pour obtenir des produits similaires
SIMILAR_PRODUCTS = """
MATCH (p1:Product)-[:HAS_CATEGORY]->(c:Category)<-[:HAS_CATEGORY]-(p2:Product)
WHERE toLower(p1.name) CONTAINS toLower($product_name) AND p1.code <> p2.code
WITH p1, p2, count(c) AS common_categories
WHERE common_categories > 0
RETURN p1.name AS Produit_Source, 
       p2.name AS Recommandation, 
       p2.nutriscore_grade AS Nutriscore, 
       common_categories AS Catégories_Communes
ORDER BY common_categories DESC, p2.nutriscore_grade
LIMIT 5
"""

# Requête pour obtenir des alternatives plus saines
HEALTHIER_ALTERNATIVES = """
MATCH (p1:Product)-[:HAS_CATEGORY]->(c:Category)<-[:HAS_CATEGORY]-(p2:Product)
WHERE toLower(p1.name) CONTAINS toLower($product_name) 
  AND p2.code <> p1.code 
  AND p2.nutriscore_grade IS NOT NULL 
  AND p1.nutriscore_grade IS NOT NULL
  AND p2.nutriscore_grade < p1.nutriscore_grade
RETURN p1.name AS Produit_Original, 
       p2.name AS Alternative, 
       p1.nutriscore_grade AS Nutriscore_Original, 
       p2.nutriscore_grade AS Nutriscore_Alternative
ORDER BY p2.nutriscore_grade
LIMIT 5
"""

# Requête pour obtenir des produits végétaliens
VEGAN_PRODUCTS = """
MATCH (p:Product)-[:HAS_LABEL]->(l:Label)
WHERE toLower(l.name) CONTAINS 'vegan' OR toLower(l.name) CONTAINS 'végétalien'
RETURN p.code AS Code,
       p.name AS Produit, 
       p.generic_name AS Description,
       p.nutriscore_grade AS Nutriscore
LIMIT 10
"""

# Requête pour obtenir des produits végétariens
VEGETARIAN_PRODUCTS = """
MATCH (p:Product)-[:HAS_LABEL]->(l:Label)
WHERE toLower(l.name) CONTAINS 'vegetarian' OR toLower(l.name) CONTAINS 'végétarien'
RETURN p.code AS Code,
       p.name AS Produit, 
       p.generic_name AS Description,
       p.nutriscore_grade AS Nutriscore
LIMIT 10
"""

# Requête pour obtenir des produits sans gluten
GLUTEN_FREE_PRODUCTS = """
MATCH (p:Product)
WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {name: 'gluten'})
RETURN p.code AS Code,
       p.name AS Produit, 
       p.generic_name AS Description,
       p.nutriscore_grade AS Nutriscore
LIMIT 10
"""

# Requête pour obtenir des produits biologiques
ORGANIC_PRODUCTS = """
MATCH (p:Product)-[:HAS_LABEL]->(l:Label)
WHERE toLower(l.name) CONTAINS 'organic' OR toLower(l.name) CONTAINS 'bio'
RETURN p.code AS Code,
       p.name AS Produit, 
       p.generic_name AS Description,
       p.nutriscore_grade AS Nutriscore,
       l.name AS Label
LIMIT 10
"""

# Requête pour comparer deux produits
COMPARE_PRODUCTS = """
MATCH (p1:Product)
WHERE toLower(p1.name) CONTAINS toLower($product1_name)
WITH p1 LIMIT 1
MATCH (p2:Product)
WHERE toLower(p2.name) CONTAINS toLower($product2_name)
WITH p1, p2 LIMIT 1
OPTIONAL MATCH (p1)-[r1:HAS_NUTRIMENT]->(n1:Nutriment)
OPTIONAL MATCH (p2)-[r2:HAS_NUTRIMENT]->(n2:Nutriment)
WHERE n1.name = n2.name
RETURN p1.name AS Produit1, 
       p2.name AS Produit2, 
       p1.nutriscore_grade AS Nutriscore1, 
       p2.nutriscore_grade AS Nutriscore2,
       n1.name AS Nutriment, 
       r1.value AS Valeur1, 
       r2.value AS Valeur2,
       r1.unit AS Unité
"""

# Requête pour la recherche vectorielle
VECTOR_SEARCH = """
CALL db.index.vector.queryNodes($index_name, $limit, $embedding)
YIELD node as product, score
WITH product, score
OPTIONAL MATCH (product)-[:HAS_BRAND]->(brand:Brand)
OPTIONAL MATCH (product)-[:HAS_CATEGORY]->(category:Category)
RETURN product.code as code, 
       product.name as name, 
       product.generic_name as generic_name, 
       product.nutriscore_grade as nutriscore,
       collect(distinct brand.name) as brands,
       collect(distinct category.name) as categories,
       score
ORDER BY score DESC
"""
