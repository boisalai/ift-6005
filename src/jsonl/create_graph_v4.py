import json
import os
from neo4j import GraphDatabase
import logging
from dotenv import load_dotenv
from collections import defaultdict, Counter
import time
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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

    def create_canonical_entities(self, entities_list, entity_type, similarity_threshold=0.85):
        """
        Regroupe automatiquement les entités similaires en utilisant des embeddings
        et retourne un dictionnaire de mapping vers les formes canoniques
        
        Args:
            entities_list: Liste des entités à normaliser (format dépend du type d'entité)
            entity_type: Type d'entité ('ingredient', 'category', 'brand', etc.)
            similarity_threshold: Seuil de similarité pour le regroupement
            
        Returns:
            Dictionnaire de mapping {nom_original: nom_canonique}
        """
        try:
            print(f"Normalisation des entités de type {entity_type}...")
            
            # Vérifier si la liste est vide
            if not entities_list:
                print(f"Aucune entité de type {entity_type} à normaliser.")
                return {}
            
            # Extraire les noms selon le type d'entité
            entity_names = []
            try:
                if entity_type == 'ingredient':
                    # Les ingrédients sont des tuples (nom, vegan, vegetarian)
                    entity_names = [str(item[0]) if item and len(item) > 0 else "" for item in entities_list]
                    # Filtrer les noms vides
                    entity_names = [name for name in entity_names if name]
                else:
                    # Les autres entités sont des chaînes simples
                    entity_names = [str(item) if item else "" for item in entities_list]
                    # Filtrer les noms vides
                    entity_names = [name for name in entity_names if name]
            except Exception as e:
                print(f"Erreur lors de l'extraction des noms pour {entity_type}: {e}")
                print(f"Échantillon des entités: {str(entities_list[:5]) if len(entities_list) > 5 else str(entities_list)}")
                # Retourner un dictionnaire identité en cas d'erreur
                if entity_type == 'ingredient':
                    return {str(item[0]): str(item[0]) for item in entities_list if item and len(item) > 0}
                else:
                    return {str(item): str(item) for item in entities_list if item}
            
            # Vérifier qu'il reste des noms valides
            if not entity_names:
                print(f"Aucun nom valide extrait pour les entités de type {entity_type}.")
                return {}
                
            print(f"Initialisation du modèle d'embeddings multilingue pour {len(entity_names)} entités...")
            
            try:
                # Charger le modèle multilingue
                model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
                
                # Calculer les embeddings
                embeddings = model.encode(entity_names)
                
                # Calculer la matrice de similarité
                similarity_matrix = cosine_similarity(embeddings)
                
                # Regrouper les entités similaires
                canonical_mapping = {}
                processed = set()
                
                for i, name in enumerate(entity_names):
                    if name in processed:
                        continue
                        
                    group = [name]
                    processed.add(name)
                    
                    for j, other_name in enumerate(entity_names):
                        if other_name in processed or i == j:
                            continue
                            
                        if similarity_matrix[i, j] > similarity_threshold:
                            group.append(other_name)
                            processed.add(other_name)
                    
                    # Stratégies spécifiques pour choisir le nom canonique selon le type d'entité
                    try:
                        if entity_type == 'brand' or entity_type == 'nutrient':
                            # Pour les marques et nutriments: privilégier la version avec majuscules (officielle)
                            canonical_name = max(group, key=lambda x: (not x.islower(), -len(x)))
                        elif entity_type == 'category' or entity_type == 'label':
                            # Pour les catégories et labels: privilégier la version anglaise (souvent plus courte)
                            canonical_name = min(group, key=lambda x: (x.lower() == x, len(x)))
                        elif entity_type == 'allergen':
                            # Pour les allergènes: privilégier le format standard (première lettre majuscule)
                            canonical_name = max(group, key=lambda x: x[0:1].isupper() if x else False)
                        else:
                            # Pour les autres entités: utiliser la forme la plus courte
                            canonical_name = min(group, key=len)
                    except Exception as e:
                        print(f"Erreur lors du choix du nom canonique pour le groupe {group}: {e}")
                        # Utiliser le premier élément en cas d'erreur
                        canonical_name = group[0]
                    
                    # Mettre à jour le mapping pour tous les membres du groupe
                    for item in group:
                        canonical_mapping[item] = canonical_name
                
                print(f"Terminé. {len(canonical_mapping)} entités {entity_type} mappées vers {len(set(canonical_mapping.values()))} formes canoniques.")
                return canonical_mapping
                
            except ImportError as e:
                print(f"AVERTISSEMENT: Dépendances manquantes pour la normalisation de {entity_type}: {e}")
                print("Installation requise: pip install sentence-transformers scikit-learn")
                # Retourner un dictionnaire identité comme fallback
                if entity_type == 'ingredient':
                    return {str(item[0]): str(item[0]) for item in entities_list if item and len(item) > 0}
                else:
                    return {str(item): str(item) for item in entities_list if item}
            
            except Exception as e:
                print(f"Erreur lors du regroupement des entités {entity_type}: {e}")
                # Retourner un dictionnaire identité en cas d'erreur générale
                if entity_type == 'ingredient':
                    return {str(item[0]): str(item[0]) for item in entities_list if item and len(item) > 0}
                else:
                    return {str(item): str(item) for item in entities_list if item}
                    
        except Exception as e:
            print(f"Erreur non gérée dans la normalisation des {entity_type}: {e}")
            # Retourner un dictionnaire identité comme dernier recours
            try:
                if entity_type == 'ingredient':
                    return {str(item[0]): str(item[0]) for item in entities_list if item and len(item) > 0}
                else:
                    return {str(item): str(item) for item in entities_list if item}
            except:
                # Si tout échoue, retourner un dictionnaire vide
                print(f"Échec complet du traitement des entités {entity_type}")
                return {}

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
        
        # Diagnostic: examiner les 3 premiers produits
        logger.info(f"DIAGNOSTIC - Examen des 3 premiers produits sur {len(products)} total:")
        for i, prod in enumerate(products[:3]):
            logger.info(f"  Produit #{i+1}:")
            logger.info(f"    ID: {prod.get('_id', 'MANQUANT')}")
            logger.info(f"    Nom: {prod.get('product_name', 'MANQUANT')}")
            logger.info(f"    Marques: {prod.get('brands', 'MANQUANT')}")
            logger.info(f"    Catégories: {prod.get('categories', 'MANQUANT')}")
            logger.info(f"    A des ingrédients: {'Oui' if 'ingredients' in prod else 'Non'}")
            logger.info(f"    A des nutriments: {'Oui' if 'nutriments' in prod else 'Non'}")
        
        # Compteurs pour le diagnostic
        skipped_products = 0
        skipped_reasons = Counter()
        
        # Première passe: collecter toutes les entités
        for product_data in products:
            try:
                # Vérification et extraction de l'ID du produit
                product_id = self.extract_field(product_data, '_id', '')
                if not product_id:
                    skipped_reasons["missing_id"] += 1
                    skipped_products += 1
                    continue
                
                # Extraction du nom du produit - ASSOUPLISSEMENT: utiliser un nom par défaut si manquant
                product_name = self.extract_field(product_data, 'product_name', '')
                if not product_name:
                    product_name = self.extract_field(product_data, 'product_name_en', '')
                
                if not product_name:
                    product_name = f"Product {product_id}"  # Nom par défaut au lieu de sauter
                    skipped_reasons["default_name_used"] += 1
                    
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
                try:
                    if "ingredients" in product_data and isinstance(product_data["ingredients"], list):
                        for ingr in product_data["ingredients"]:
                            if isinstance(ingr, dict) and "text" in ingr:
                                ingredient = {
                                    "name": ingr["text"],
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
                except Exception as e:
                    logger.warning(f"Erreur lors de l'extraction des ingrédients pour {product_id}: {e}")
                    # Continuer malgré l'erreur d'ingrédients
                
                # Extraire les allergènes
                product_allergens = []
                try:
                    if "allergens_tags" in product_data:
                        allergens = [allergen.replace("en:", "") for allergen in product_data["allergens_tags"]]
                        product_allergens = allergens
                        allergens_set.update(allergens)
                except Exception as e:
                    logger.warning(f"Erreur lors de l'extraction des allergènes pour {product_id}: {e}")
                    # Continuer malgré l'erreur d'allergènes
                
                # Extraire les données nutritionnelles
                product_nutrients = []
                try:
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
                except Exception as e:
                    logger.warning(f"Erreur lors de l'extraction des nutriments pour {product_id}: {e}")
                    # Continuer malgré l'erreur de nutriments
                
                # Extraire les labels
                product_labels = []
                try:
                    if "labels_tags" in product_data:
                        labels = [label.replace("en:", "") for label in product_data["labels_tags"]]
                        product_labels = labels
                        labels_set.update(labels)
                except Exception as e:
                    logger.warning(f"Erreur lors de l'extraction des labels pour {product_id}: {e}")
                    # Continuer malgré l'erreur de labels
                
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
                
            except Exception as e:
                skipped_reasons[str(e)[:100]] += 1  # Tronquer les messages d'erreur longs
                skipped_products += 1
                logger.error(f"Erreur lors du prétraitement du produit {product_data.get('_id', 'ID inconnu')}: {e}")
                continue  # Passer au produit suivant en cas d'erreur
        
        # Afficher des statistiques de diagnostic
        logger.info(f"Prétraitement - Total: {len(products)}, Valides: {len(valid_products)}, Ignorés: {skipped_products}")
        for reason, count in skipped_reasons.most_common(10):
            logger.info(f"  Raison d'exclusion: {reason} - {count} produits")
        
        # Vérifier s'il n'y a pas de produits valides et ajouter des produits minimaux si besoin
        if len(valid_products) == 0:
            logger.error("ERREUR CRITIQUE: Aucun produit valide après prétraitement!")
            # Accepter au moins quelques produits même avec données minimales
            for i, product_data in enumerate(products[:100]):  # Essayer avec les 100 premiers
                try:
                    product_id = self.extract_field(product_data, '_id', f"default-{i}")
                    product_name = self.extract_field(product_data, 'product_name', f"Product {product_id}")
                    
                    valid_products.append({
                        'node': {
                            'id': product_id,
                            'name': product_name,
                            'quantity': '',
                            'nutriscore': '',
                            'nova_group': None,
                            'ecoscore': '',
                            'has_nutrition': False
                        },
                        'brands': [],
                        'categories': [],
                        'countries': [],
                        'ingredients': [],
                        'allergens': [],
                        'nutrients': [],
                        'labels': []
                    })
                except Exception as e:
                    logger.error(f"Erreur lors de la création du produit minimal: {e}")
            
            logger.info(f"Récupération d'urgence: {len(valid_products)} produits basiques ajoutés")
        
        # Deuxième passe: normaliser toutes les entités
        logger.info("Création des mappings de normalisation pour toutes les entités...")
        
        # Créer les mappings pour chaque type d'entité avec gestion des erreurs
        try:
            ingredient_mapping = {}
            if ingredients_set:
                ingredient_mapping = self.create_canonical_entities(ingredients_set, 'ingredient')
            
            brand_mapping = {}
            if brands_set:
                brand_mapping = self.create_canonical_entities(brands_set, 'brand')
            
            category_mapping = {}
            if categories_set:
                category_mapping = self.create_canonical_entities(categories_set, 'category')
            
            allergen_mapping = {}
            if allergens_set:
                allergen_mapping = self.create_canonical_entities(allergens_set, 'allergen')
            
            label_mapping = {}
            if labels_set:
                label_mapping = self.create_canonical_entities(labels_set, 'label')
            
            # Pour les nutriments, on utilise une liste fixe
            nutrient_names = ['Énergie', 'Energy', 'Matières grasses', 'Fat', 'Protéines', 
                            'Proteins', 'Glucides', 'Carbohydrates', 'Sucres', 'Sugars', 
                            'Sodium', 'Sel', 'Salt', 'Fibres', 'Fiber']
            nutrient_mapping = self.create_canonical_entities(nutrient_names, 'nutrient')
            
            # Normaliser les entités dans les produits
            try:
                for product in valid_products:
                    # Normaliser les marques
                    try:
                        product['brands'] = [brand_mapping.get(brand, brand) for brand in product['brands']]
                    except Exception as e:
                        logger.warning(f"Erreur lors de la normalisation des marques: {e}")
                    
                    # Normaliser les catégories
                    try:
                        product['categories'] = [category_mapping.get(cat, cat) for cat in product['categories']]
                    except Exception as e:
                        logger.warning(f"Erreur lors de la normalisation des catégories: {e}")
                    
                    # Normaliser les ingrédients
                    try:
                        for ingredient in product['ingredients']:
                            ingredient['original_name'] = ingredient['name']
                            ingredient['name'] = ingredient_mapping.get(ingredient['name'], ingredient['name'])
                    except Exception as e:
                        logger.warning(f"Erreur lors de la normalisation des ingrédients: {e}")
                    
                    # Normaliser les allergènes
                    try:
                        product['allergens'] = [allergen_mapping.get(allergen, allergen) for allergen in product['allergens']]
                    except Exception as e:
                        logger.warning(f"Erreur lors de la normalisation des allergènes: {e}")
                    
                    # Normaliser les labels
                    try:
                        product['labels'] = [label_mapping.get(label, label) for label in product['labels']]
                    except Exception as e:
                        logger.warning(f"Erreur lors de la normalisation des labels: {e}")
                    
                    # Normaliser les nutriments
                    try:
                        for nutrient in product['nutrients']:
                            nutrient['original_name'] = nutrient['name']
                            nutrient['name'] = nutrient_mapping.get(nutrient['name'], nutrient['name'])
                    except Exception as e:
                        logger.warning(f"Erreur lors de la normalisation des nutriments: {e}")
            except Exception as e:
                logger.error(f"Erreur lors de la normalisation des produits: {e}")
        except Exception as e:
            logger.error(f"Erreur générale lors de la création des mappings: {e}")
            # Continuer avec les produits non normalisés en cas d'erreur majeure
        
        # Mettre à jour les ensembles d'entités uniques avec les formes canoniques
        try:
            canonical_brands_set = set(brand_mapping.values()) if brand_mapping else brands_set
            canonical_categories_set = set(category_mapping.values()) if category_mapping else categories_set
            canonical_allergens_set = set(allergen_mapping.values()) if allergen_mapping else allergens_set
            canonical_labels_set = set(label_mapping.values()) if label_mapping else labels_set
            
            # Pour les ingrédients (qui sont des tuples), c'est un peu plus complexe
            canonical_ingredients_set = set()
            if ingredient_mapping:
                for orig_name, vegan, vegetarian in ingredients_set:
                    canonical_name = ingredient_mapping.get(orig_name, orig_name)
                    canonical_ingredients_set.add((canonical_name, vegan, vegetarian))
            else:
                canonical_ingredients_set = ingredients_set
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des ensembles canoniques: {e}")
            # Fallback aux ensembles originaux en cas d'erreur
            canonical_brands_set = brands_set
            canonical_categories_set = categories_set
            canonical_allergens_set = allergens_set
            canonical_labels_set = labels_set
            canonical_ingredients_set = ingredients_set
        
        logger.info(f"Prétraitement terminé: {len(valid_products)} produits valides")
        
        return {
            'products': valid_products,
            'unique_brands': list(canonical_brands_set),
            'unique_categories': list(canonical_categories_set),
            'unique_countries': list(countries_set),  # Pas de normalisation pour les pays
            'unique_ingredients': list(canonical_ingredients_set),
            'unique_allergens': list(canonical_allergens_set),
            'unique_labels': list(canonical_labels_set),
            # Conserver les mappings pour référence
            'mappings': {
                'ingredient': ingredient_mapping,
                'brand': brand_mapping,
                'category': category_mapping,
                'allergen': allergen_mapping,
                'label': label_mapping,
                'nutrient': nutrient_mapping
            }
        }

    def create_entity_nodes_batch(self, session, entity_type, entities, batch_size=1000, mapping=None):
        """Créer des nœuds d'entité en lots, avec normalisation sémantique"""
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
                    SET b.original_variants = $variants[item]
                """, batch=batch, variants={name: [k for k, v in mapping.items() if v == name] if mapping else [name] for name in batch})
                
            elif entity_type == "Category":
                session.run("""
                    UNWIND $batch AS item
                    MERGE (c:Category {name: item})
                    SET c.original_variants = $variants[item]
                """, batch=batch, variants={name: [k for k, v in mapping.items() if v == name] if mapping else [name] for name in batch})
                
            elif entity_type == "Label":
                session.run("""
                    UNWIND $batch AS item
                    MERGE (l:Label {name: item})
                    SET l.original_variants = $variants[item]
                """, batch=batch, variants={name: [k for k, v in mapping.items() if v == name] if mapping else [name] for name in batch})
                
            elif entity_type == "Allergen":
                session.run("""
                    UNWIND $batch AS item
                    MERGE (a:Allergen {name: item})
                    SET a.original_variants = $variants[item]
                """, batch=batch, variants={name: [k for k, v in mapping.items() if v == name] if mapping else [name] for name in batch})
                
            elif entity_type == "Ingredient":
                # Pour les ingrédients (tuples avec 3 éléments)
                session.run("""
                    UNWIND $batch AS item
                    MERGE (i:Ingredient {name: item[0]})
                    SET i.vegan = item[1],
                        i.vegetarian = item[2],
                        i.original_variants = $variants[item[0]]
                """, batch=batch, 
                    variants={name: [k for k, v in mapping.items() if v == name] if mapping else [name] 
                            for name in [item[0] for item in batch]})
                
            elif entity_type == "Nutrient":
                session.run("""
                    UNWIND $batch AS item
                    MERGE (n:Nutrient {name: item})
                    SET n.original_variants = $variants[item]
                """, batch=batch, variants={name: [k for k, v in mapping.items() if v == name] if mapping else [name] for name in batch})
                
            elif entity_type == "Country":
                # Pas de normalisation pour les pays
                session.run("""
                    UNWIND $batch AS item
                    MERGE (c:Country {name: item})
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
        
        # Récupérer les mappings
        mappings = preprocessed.get('mappings', {})
        
        # Créer tous les nœuds d'entité
        with self.driver.session() as session:
            # Nutriments (entités fixes)
            key_nutrients = preprocessed['unique_nutrients'] if 'unique_nutrients' in preprocessed else ['Énergie', 'Matières grasses', 'Protéines', 'Glucides', 'Sucres', 'Sodium', 'Sel', 'Fibres']
            self.create_entity_nodes_batch(session, "Nutrient", key_nutrients, mapping=mappings.get('nutrient', {}))
            
            # Entités uniques
            self.create_entity_nodes_batch(session, "Brand", preprocessed['unique_brands'], mapping=mappings.get('brand', {}))
            self.create_entity_nodes_batch(session, "Category", preprocessed['unique_categories'], mapping=mappings.get('category', {}))
            self.create_entity_nodes_batch(session, "Country", preprocessed['unique_countries'])  # Pas de mapping
            self.create_entity_nodes_batch(session, "Ingredient", preprocessed['unique_ingredients'], mapping=mappings.get('ingredient', {}))
            self.create_entity_nodes_batch(session, "Allergen", preprocessed['unique_allergens'], mapping=mappings.get('allergen', {}))
            self.create_entity_nodes_batch(session, "Label", preprocessed['unique_labels'], mapping=mappings.get('label', {}))
            
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
    limit = 100
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