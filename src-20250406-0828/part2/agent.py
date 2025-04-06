import os
import json
import logging
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
from textwrap import dedent
from neo4j import GraphDatabase
from smolagents import tool, CodeAgent, LiteLLMModel
from sentence_transformers import SentenceTransformer
from enum import Enum

# Chargement des variables d'environnement
load_dotenv()

# Configuration Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("agent.log"), logging.StreamHandler()]
)
logger = logging.getLogger("FoodAgent")

# Importation du contenu des requêtes Cypher comme documentation
from cypher_queries import (
    VECTOR_SEARCH, BRAND_PRODUCTS, PRODUCTS_WITH_INGREDIENT, PRODUCTS_WITHOUT_ALLERGEN,
    NUTRITIONAL_INFO, SIMILAR_PRODUCTS, HEALTHIER_ALTERNATIVES, VEGAN_PRODUCTS,
    VEGETARIAN_PRODUCTS, GLUTEN_FREE_PRODUCTS, ORGANIC_PRODUCTS, COMPARE_PRODUCTS, PRODUCT_INFO
)

# Définition de l'énumération IntentType
class IntentType(Enum):
    PRODUCT_INFO = "product_info"          # Information sur un produit
    BRAND_QUERY = "brand_query"            # Recherche par marque
    INGREDIENT_QUERY = "ingredient_query"  # Recherche par ingrédient
    ALLERGEN_CHECK = "allergen_check"      # Vérification d'allergènes
    NUTRITIONAL_INFO = "nutritional_info"  # Information nutritionnelle
    RECOMMENDATION = "recommendation"      # Recommandation de produits
    DIET_QUERY = "diet_query"              # Question sur un régime (vegan, sans gluten, etc.)
    COMPARISON = "comparison"              # Comparaison entre produits
    GENERAL_QUERY = "general_query"        # Autre type de question

# Connexion à Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Chargement du modèle d'embedding
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
logger.info("Modèle d'embedding chargé: all-MiniLM-L6-v2")

@tool
def execute_cypher_query(query: str, params: Dict = None) -> str:
    """
    Outil : Exécution d'une requête Cypher personnalisée sur la base Neo4j.
    Instructions : Utilise cet outil pour exécuter une requête Cypher construite manuellement.
    Args:
        query: La requête Cypher à exécuter.
        params: Dictionnaire des paramètres de la requête (optionnel).
    Retourne:
        Une chaîne JSON formatée contenant les résultats.
    """
    try:
        with driver.session() as session:
            result = session.run(query, params or {})
            records = [record.data() for record in result]
            logger.info(f"Exécution de la requête Cypher avec {len(records)} résultats")
            return json.dumps(records, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la requête: {e}")
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)

@tool
def create_text_embedding(text: str) -> str:
    """
    Outil : Génération d'un embedding vectoriel pour un texte.
    Instructions : Utilise cet outil pour générer un embedding vectoriel utilisable dans les requêtes de recherche vectorielle.
    Args:
        text: Texte à convertir en embedding.
    Retourne:
        Une chaîne JSON contenant l'embedding généré.
    """
    try:
        embedding = embedding_model.encode(text)
        logger.info(f"Embedding créé pour le texte: '{text[:50]}...' (longueur: {len(embedding)})")
        return json.dumps(embedding.tolist(), ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erreur lors de la création d'embedding: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@tool
def detect_intent(query: str) -> str:
    """
    Outil : Détection d'intention dans une requête utilisateur.
    Instructions : Analyse une requête en langage naturel pour déterminer l'intention et les entités.
    Args:
        query: La requête de l'utilisateur en français ou en anglais
    Retourne:
        Une chaîne JSON contenant l'intention détectée et les entités extraites
    """
    intent_types = [
        "product_info",          # Information sur un produit
        "brand_query",           # Recherche par marque
        "ingredient_query",      # Recherche par ingrédient
        "allergen_check",        # Vérification d'allergènes
        "nutritional_info",      # Information nutritionnelle
        "recommendation",        # Recommandation de produits
        "diet_query",            # Question sur un régime (vegan, sans gluten, etc.)
        "comparison",            # Comparaison entre produits
        "general_query"          # Autre type de question
    ]
    
    # Ajoutons quelques règles simples pour détecter l'intention sans LLM
    query_lower = query.lower()
    
    # Recherche par marque
    if any(term in query_lower for term in ["marque", "brand", "by", "de la marque", "from"]):
        if "kellogg" in query_lower:
            return json.dumps({
                "intent": "brand_query",
                "entities": ["Kellogg's"]
            })
        # Extraction simple de l'entité après "marque" ou "brand"
        for marker in ["marque ", "brand ", "by ", "from "]:
            if marker in query_lower:
                pos = query_lower.find(marker) + len(marker)
                entity = query[pos:].strip().split()[0].rstrip('?.,;:!')
                return json.dumps({
                    "intent": "brand_query",
                    "entities": [entity]
                })
    
    # Recherche par ingrédient
    if any(term in query_lower for term in ["contenant", "avec", "with", "containing", "contient"]):
        for marker in ["contenant ", "avec ", "with ", "containing "]:
            if marker in query_lower:
                pos = query_lower.find(marker) + len(marker)
                entity = query[pos:].strip().split()[0].rstrip('?.,;:!')
                return json.dumps({
                    "intent": "ingredient_query",
                    "entities": [entity]
                })
        if "sucre" in query_lower or "sugar" in query_lower:
            return json.dumps({
                "intent": "ingredient_query",
                "entities": ["sugar"]
            })
    
    # Recherche sans allergène
    if any(term in query_lower for term in ["sans", "without", "free from"]):
        if "gluten" in query_lower:
            return json.dumps({
                "intent": "allergen_check",
                "entities": ["gluten"]
            })
        for marker in ["sans ", "without ", "free from "]:
            if marker in query_lower:
                pos = query_lower.find(marker) + len(marker)
                entity = query[pos:].strip().split()[0].rstrip('?.,;:!')
                return json.dumps({
                    "intent": "allergen_check",
                    "entities": [entity]
                })
    
    # Régimes alimentaires spécifiques
    if any(term in query_lower for term in ["vegan", "végétalien", "vegetarian", "végétarien", "bio", "organic"]):
        return json.dumps({
            "intent": "diet_query",
            "entities": []
        })
    
    # Information nutritionnelle
    if any(term in query_lower for term in ["nutrition", "nutritionnel", "nutritional"]):
        return json.dumps({
            "intent": "nutritional_info",
            "entities": []
        })
    
    # Comparaison
    if any(term in query_lower for term in ["compare", "comparer", "vs", "versus"]):
        if "coca" in query_lower and "pepsi" in query_lower:
            return json.dumps({
                "intent": "comparison",
                "entities": ["Coca-Cola", "Pepsi"]
            })
    
    # Information sur un produit spécifique
    if "nutella" in query_lower:
        return json.dumps({
            "intent": "product_info",
            "entities": ["Nutella"]
        })
    
    # Par défaut: recherche générale
    return json.dumps({
        "intent": "general_query",
        "entities": []
    })

@tool
def process_food_query(query: str, language: str = None) -> str:
    """
    Outil : Traitement complet d'une requête sur les aliments.
    Instructions : Utilise cet outil pour analyser, exécuter et formater les résultats d'une requête utilisateur.
    Args:
        query: La requête de l'utilisateur sur les produits alimentaires
        language: La langue de la requête ('fr' ou 'en'), détectée automatiquement si non spécifiée
    Retourne:
        Une chaîne contenant les résultats formatés pour l'utilisateur
    """
    try:
        logger.info(f"Traitement de la requête: '{query}'")
        
        # Détecter la langue si non spécifiée
        if not language:
            # Approche simple basée sur les mots fréquents
            fr_words = ["le", "la", "les", "un", "une", "des", "du", "est", "et", "pour", "de", "avec", "sans"]
            words = query.lower().split()
            fr_count = sum(1 for word in words if word in fr_words)
            language = "fr" if fr_count >= 2 else "en"
            logger.info(f"Langue détectée: {language}")
        
        # Détecter l'intention avec notre outil dédié
        intent_result = detect_intent(query)
        intent_data = json.loads(intent_result)
        intent = intent_data.get("intent", "general_query")
        entities = intent_data.get("entities", [])
        
        logger.info(f"Intention détectée: {intent}, Entités: {entities}")
        
        # Sélectionner et exécuter la requête appropriée
        result_json = ""
        if intent == "brand_query" and entities:
            cypher_query = BRAND_PRODUCTS
            params = {"brand_name": entities[0]}
            result_json = execute_cypher_query(cypher_query, params)
            
        elif intent == "ingredient_query" and entities:
            cypher_query = PRODUCTS_WITH_INGREDIENT
            params = {"ingredient_name": entities[0]}
            result_json = execute_cypher_query(cypher_query, params)
            
        elif intent == "allergen_check" and entities:
            cypher_query = PRODUCTS_WITHOUT_ALLERGEN
            params = {"allergen_name": entities[0]}
            result_json = execute_cypher_query(cypher_query, params)
            
        elif intent == "nutritional_info" and entities:
            cypher_query = NUTRITIONAL_INFO
            params = {"product_name": entities[0]}
            result_json = execute_cypher_query(cypher_query, params)
            
        elif intent == "diet_query":
            # Déterminer le type de régime
            if "vegan" in query.lower() or "végétalien" in query.lower():
                cypher_query = VEGAN_PRODUCTS
                result_json = execute_cypher_query(cypher_query)
            elif "vegetarian" in query.lower() or "végétarien" in query.lower():
                cypher_query = VEGETARIAN_PRODUCTS
                result_json = execute_cypher_query(cypher_query)
            elif "gluten" in query.lower():
                cypher_query = GLUTEN_FREE_PRODUCTS
                result_json = execute_cypher_query(cypher_query)
            elif "bio" in query.lower() or "organic" in query.lower():
                cypher_query = ORGANIC_PRODUCTS
                result_json = execute_cypher_query(cypher_query)
            
        elif intent == "comparison" and len(entities) >= 2:
            cypher_query = COMPARE_PRODUCTS
            params = {"product1_name": entities[0], "product2_name": entities[1]}
            result_json = execute_cypher_query(cypher_query, params)
            
        elif intent == "product_info" and entities:
            cypher_query = PRODUCT_INFO
            params = {"product_name": entities[0]}
            result_json = execute_cypher_query(cypher_query, params)
            
        else:
            # Recherche vectorielle pour les requêtes générales
            embedding = create_text_embedding(query)
            embedding_vector = json.loads(embedding)
            if "error" not in embedding_vector:
                cypher_query = VECTOR_SEARCH
                params = {
                    "index_name": "product_embedding_index",
                    "embedding": embedding_vector,
                    "limit": 5
                }
                result_json = execute_cypher_query(cypher_query, params)
            else:
                result_json = json.dumps({"error": "Erreur lors de la création de l'embedding"})
        
        # Analyser les résultats
        results = json.loads(result_json)
        
        # Format simple pour les résultats
        formatted_response = ""
        if isinstance(results, list):
            if language == "fr":
                formatted_response = f"J'ai trouvé {len(results)} résultats pour votre requête."
            else:
                formatted_response = f"I found {len(results)} results for your query."
                
            if len(results) > 0:
                if language == "fr":
                    formatted_response += "\n\nVoici les détails:"
                else:
                    formatted_response += "\n\nHere are the details:"
                    
                for i, result in enumerate(results[:5], 1):
                    formatted_response += f"\n\n{i}. "
                    
                    # Adapter l'affichage selon le type de requête
                    if intent == "brand_query":
                        if "Produit" in result:
                            formatted_response += f"{result.get('Produit', 'N/A')}"
                        elif "name" in result:
                            formatted_response += f"{result.get('name', 'N/A')}"
                        
                        if "nutriscore" in result:
                            formatted_response += f" - Nutriscore: {result.get('nutriscore', 'N/A')}"
                            
                        if "Quantité" in result:
                            formatted_response += f" - Quantité: {result.get('Quantité', 'N/A')}"
                            
                    elif intent == "product_info":
                        if "Produit" in result:
                            formatted_response += f"{result.get('Produit', 'N/A')}"
                        elif "name" in result:
                            formatted_response += f"{result.get('name', 'N/A')}"
                            
                        description = result.get('Description', result.get('generic_name', ''))
                        if description:
                            formatted_response += f" - {description}"
                            
                        if "Nutriscore" in result or "nutriscore" in result:
                            score = result.get('Nutriscore', result.get('nutriscore', 'N/A'))
                            formatted_response += f" - Nutriscore: {score}"
                            
                        # Ajouter les marques si disponibles
                        brands = result.get('Marques', result.get('brands', []))
                        if brands:
                            if isinstance(brands, list) and brands:
                                if language == "fr":
                                    formatted_response += f" - Marques: {', '.join(brands)}"
                                else:
                                    formatted_response += f" - Brands: {', '.join(brands)}"
                    else:
                        # Affichage générique pour les autres types de requêtes
                        for key, value in result.items():
                            if key.lower() not in ["code", "id"]:  # Exclure les identifiants techniques
                                if isinstance(value, list):
                                    value_str = ", ".join(value) if value else "N/A"
                                else:
                                    value_str = str(value) if value is not None else "N/A"
                                formatted_response += f"{key}: {value_str}, "
                        
                        # Enlever la dernière virgule
                        if formatted_response.endswith(", "):
                            formatted_response = formatted_response[:-2]
        else:
            # En cas d'erreur
            if "error" in results:
                if language == "fr":
                    formatted_response = f"Erreur lors de la requête: {results['error']}"
                else:
                    formatted_response = f"Error while processing query: {results['error']}"
            else:
                if language == "fr":
                    formatted_response = "Aucun résultat trouvé."
                else:
                    formatted_response = "No results found."
        
        return formatted_response
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la requête: {e}")
        if language == "fr":
            return f"Désolé, une erreur s'est produite lors du traitement de votre requête: {str(e)}"
        else:
            return f"Sorry, an error occurred while processing your query: {str(e)}"

if __name__ == "__main__":
    # Initialisation du LLM.
    engine = "ollama/llama3.2:latest"
    engine = "sonnet"

    if engine.startswith("ollama/"):
        llm = LiteLLMModel(
            model_id=engine,
            api_base="http://localhost:11434",
            num_ctx=8192
        )
    else:
        llm = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-20240620")
    logger.info(f"LLM initialisé avec LiteLLMModel et le modèle {engine}.")

    # Création de l'agent
    agent = CodeAgent(
        model=llm,
        tools=[
            execute_cypher_query,
            create_text_embedding,
            detect_intent,
            process_food_query
        ],
        add_base_tools=True
    )
    logger.info("CodeAgent initialisé avec succès.")
    
    # Instructions détaillées pour l'agent
    AGENT_INSTRUCTIONS = dedent(
        f"""\
    Tu es un assistant spécialisé dans l'interrogation de la base de données Neo4j Open Food Facts en français et en anglais.

    # SCHÉMA DE LA BASE DE DONNÉES
    
    Cette base contient des données sur les produits alimentaires avec le schéma suivant :
    - Nœuds:
      - Product: Produits alimentaires (propriétés: code, name, generic_name, nutriscore_grade, quantity)
      - Brand: Marques (propriété: name)
      - Category: Catégories (propriété: name)
      - Ingredient: Ingrédients (propriété: name)
      - Allergen: Allergènes (propriété: name)
      - Nutriment: Nutriments (propriété: name)
      - Label: Labels (propriété: name)
    
    - Relations:
      - (Product)-[:HAS_BRAND]->(Brand)
      - (Product)-[:HAS_CATEGORY]->(Category)
      - (Product)-[:CONTAINS]->(Ingredient)
      - (Product)-[:CONTAINS_ALLERGEN]->(Allergen)
      - (Product)-[:HAS_NUTRIMENT]->(Nutriment) avec propriétés: value, unit
      - (Product)-[:HAS_LABEL]->(Label)
      
    # UTILISATION DES OUTILS

    Pour répondre aux questions des utilisateurs, utilise les outils suivants:

    1. `detect_intent(query)` - Outil qui analyse la question de l'utilisateur et identifie l'intention et les entités
    2. `execute_cypher_query(query, params)` - Exécute une requête Cypher sur la base Neo4j
    3. `create_text_embedding(text)` - Génère un embedding pour la recherche vectorielle
    4. `process_food_query(query, language)` - Traite une requête complète de bout en bout

    Pour la plupart des cas, tu devrais utiliser directement l'outil `process_food_query` qui gère tout le traitement.
    En cas de besoin de requêtes plus personnalisées, tu peux combiner les autres outils.

    # RÈGLES IMPORTANTES

    - Réponds dans la même langue que celle utilisée par l'utilisateur (français ou anglais)
    - Présente les résultats de manière claire et concise
    - N'invente jamais de résultats et limite-toi aux informations présentes dans la base de données
    - Si aucune information n'est trouvée, explique-le simplement

    # FORMAT DE RÉPONSE
    
    Ta réponse finale doit être claire, concise et sans ton processus de réflexion interne. Structure ta réponse ainsi:
    1. Une introduction brève qui présente les informations trouvées
    2. Les détails pertinents organisés de façon lisible
    3. Si applicable, une conclusion ou recommandation basée sur les données
    """
    )

    try:    
        # Exemples de requêtes pour tester l'agent
        queries = [
            "What products are made by Kellogg's?",
            "Quels produits contiennent du sucre?",
            "Show me products without gluten",
            "Tell me about Nutella.",
            "Compare Coca-Cola and Pepsi",
            "Donne-moi des produits végétaliens"
        ]
        
        for query in queries[:1]:
            print(f"\n\nQuestion: {query}")
            response = agent.run(query, additional_args={
                "additional_notes": AGENT_INSTRUCTIONS,
            })
            print(f"Réponse: {response}")
            
    finally:
        # Fermer la connexion à Neo4j
        if driver:
            driver.close()