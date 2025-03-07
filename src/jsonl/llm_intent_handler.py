import json
import pandas as pd
from enum import Enum
from typing import Tuple, List, Dict, Any, Optional, Union

class IntentType(Enum):
    PRODUCT_INFO = "product_info"
    BRAND_QUERY = "brand_query"
    INGREDIENT_QUERY = "ingredient_query"
    ALLERGEN_CHECK = "allergen_check"
    NUTRITIONAL_INFO = "nutritional_info"
    RECOMMENDATION = "recommendation"
    DIET_QUERY = "diet_query"
    COMPARISON = "comparison"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"

class LLMIntentHandler:
    def __init__(self, agent):
        """
        Initialise le gestionnaire d'intentions basé sur LLM.
        
        Args:
            agent: L'instance de l'agent OpenFoodFacts qui utilise ce gestionnaire
        """
        self.agent = agent
        self.llm = agent.llm  # Réutiliser le même LLM que l'agent
    
    def detect_intent(self, query: str) -> Tuple[str, List[str]]:
        """
        Utilise le LLM pour détecter l'intention et les entités dans la question de l'utilisateur.
        
        Args:
            query: La question de l'utilisateur
            
        Returns:
            Tuple contenant le type d'intention (str) et une liste d'entités détectées (List[str])
        """
        prompt = f"""
        Analyse la question suivante et identifie l'intention et les entités concernées.
        Retourne uniquement un objet JSON au format suivant, sans commentaires ni texte supplémentaire :
        {{
            "intent": "<type_intention>",
            "entities": ["<entité1>", "<entité2>", ...]
        }}
        
        Types d'intentions possibles :
        - "product_info": demande d'information sur un produit spécifique
        - "brand_query": recherche de produits d'une marque spécifique
        - "ingredient_query": recherche de produits contenant un ingrédient spécifique
        - "allergen_check": vérification d'allergènes ou produits sans certains ingrédients
        - "nutritional_info": demande d'information nutritionnelle
        - "recommendation": demande de recommandation de produits
        - "diet_query": requête sur des régimes alimentaires (végétalien, sans gluten, etc.)
        - "comparison": comparaison entre produits
        - "general_query": autre type de question
        
        Question : {query}
        """
        
        try:
            response = self.llm.invoke(prompt)
            # Extraire le contenu JSON de la réponse
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
                
            # Nettoyer la réponse pour éviter les problèmes de parsing JSON
            content = content.strip()
            # Si la réponse est entourée par des backticks de code JSON, les enlever
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3].strip()
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3].strip()
                
            result = json.loads(content)
            intent = result.get("intent", "general_query")
            entities = result.get("entities", [])
            
            # Conversion en IntentType si applicable
            try:
                intent = IntentType(intent)
            except ValueError:
                # Si l'intent string ne correspond pas à une valeur d'énumération, utiliser general_query
                intent = IntentType.GENERAL_QUERY
                
            return intent, entities
            
        except Exception as e:
            print(f"Erreur lors de l'analyse de l'intention: {e}")
            return IntentType.GENERAL_QUERY, []
    
    def handle_intent(self, query: str) -> Tuple[str, Optional[pd.DataFrame]]:
        """
        Traite la requête en fonction de l'intention détectée par le LLM.
        
        Args:
            query: La question de l'utilisateur
            
        Returns:
            Tuple contenant la réponse textuelle (str) et les données tabulaires éventuelles (DataFrame ou None)
        """
        intent, entities = self.detect_intent(query)
        
        print(f"Intent détecté par LLM: {intent}, Entités: {entities}")
        
        # Cas où aucune entité n'est détectée pour des intents nécessitant des entités
        if not entities and intent not in [IntentType.GENERAL_QUERY, IntentType.DIET_QUERY]:
            response = self.agent.qa_chain.invoke({"query": query})
            return response, None
        
        # Traitement selon le type d'intention
        if intent == IntentType.BRAND_QUERY and entities:
            return self._handle_brand_query(entities[0])
            
        elif intent == IntentType.PRODUCT_INFO and entities:
            return self._handle_product_info(entities[0])
            
        elif intent == IntentType.INGREDIENT_QUERY and entities:
            return self._handle_ingredient_query(entities[0])
            
        elif intent == IntentType.ALLERGEN_CHECK and entities:
            return self._handle_allergen_check(entities[0])
            
        elif intent == IntentType.NUTRITIONAL_INFO and entities:
            return self._handle_nutritional_info(entities[0])
            
        elif intent == IntentType.RECOMMENDATION and entities:
            return self._handle_recommendation(entities[0])
            
        elif intent == IntentType.DIET_QUERY:
            diet_type = entities[0] if entities else "végétalien"
            return self._handle_diet_query(diet_type)
            
        elif intent == IntentType.COMPARISON and len(entities) >= 2:
            return self._handle_comparison(entities[0], entities[1])
        
        # Par défaut ou pour les questions générales
        response = self.agent.qa_chain.invoke({"query": query})
        return response, None
    
    def _handle_brand_query(self, brand_name: str) -> Tuple[str, Optional[pd.DataFrame]]:
        """Recherche des produits d'une marque spécifique"""
        cypher = f"""
        MATCH (p:Product)-[:BELONGS_TO]->(b:Brand)
        WHERE toLower(b.name) CONTAINS toLower('{brand_name}')
        RETURN p.name AS Produit, p.nutriscore AS Nutriscore, p.quantity AS Quantité
        LIMIT 10
        """
        results = self.agent.execute_custom_cypher(cypher)
        
        if isinstance(results, list) and len(results) > 0:
            response = f"Voici les produits de la marque '{brand_name}':"
            return response, pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé de produits de la marque '{brand_name}'.", None
    
    def _handle_product_info(self, product_name: str) -> Tuple[str, Optional[pd.DataFrame]]:
        """Recherche d'informations sur un produit spécifique"""
        cypher = f"""
        MATCH (p:Product)
        WHERE toLower(p.name) CONTAINS toLower('{product_name}')
        OPTIONAL MATCH (p)-[:BELONGS_TO]->(b:Brand)
        OPTIONAL MATCH (p)-[:CATEGORIZED_AS]->(c:Category)
        RETURN p.name AS Produit, p.nutriscore AS Nutriscore, 
               p.quantity AS Quantité, collect(DISTINCT b.name) AS Marques,
               collect(DISTINCT c.name) AS Catégories
        LIMIT 5
        """
        results = self.agent.execute_custom_cypher(cypher)
        
        if isinstance(results, list) and len(results) > 0:
            response = f"Voici les informations sur les produits correspondant à '{product_name}':"
            return response, pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé d'informations sur des produits nommés '{product_name}'.", None
    
    def _handle_ingredient_query(self, ingredient_name: str) -> Tuple[str, Optional[pd.DataFrame]]:
        """Recherche de produits contenant un ingrédient spécifique"""
        cypher = f"""
        MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
        WHERE toLower(i.name) CONTAINS toLower('{ingredient_name}')
        RETURN p.name AS Produit, p.nutriscore AS Nutriscore, i.name AS Ingrédient
        LIMIT 10
        """
        results = self.agent.execute_custom_cypher(cypher)
        
        if isinstance(results, list) and len(results) > 0:
            response = f"Voici les produits qui contiennent '{ingredient_name}':"
            return response, pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé de produits contenant '{ingredient_name}'.", None
    
    def _handle_allergen_check(self, allergen_name: str) -> Tuple[str, Optional[pd.DataFrame]]:
        """Recherche de produits sans un allergène spécifique"""
        cypher = f"""
        MATCH (p:Product)
        WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {{name: '{allergen_name}'}})
        RETURN p.name AS Produit, p.nutriscore AS Nutriscore
        LIMIT 10
        """
        results = self.agent.execute_custom_cypher(cypher)
        
        if isinstance(results, list) and len(results) > 0:
            response = f"Voici des produits qui ne contiennent pas l'allergène '{allergen_name}':"
            return response, pd.DataFrame(results)
        else:
            return f"Je n'ai pas pu trouver de produits sans l'allergène '{allergen_name}', ou cet allergène n'est pas répertorié dans la base de données.", None
    
    def _handle_nutritional_info(self, product_name: str) -> Tuple[str, Optional[pd.DataFrame]]:
        """Recherche d'informations nutritionnelles sur un produit"""
        cypher = f"""
        MATCH (p:Product)-[r:HAS_NUTRIENT]->(n:Nutrient)
        WHERE toLower(p.name) CONTAINS toLower('{product_name}')
        RETURN p.name AS Produit, n.name AS Nutriment, r.value AS Valeur, r.unit AS Unité
        """
        results = self.agent.execute_custom_cypher(cypher)
        
        if isinstance(results, list) and len(results) > 0:
            response = f"Voici les informations nutritionnelles pour '{product_name}':"
            return response, pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé d'informations nutritionnelles pour '{product_name}'.", None
    
    def _handle_recommendation(self, product_name: str) -> Tuple[str, Optional[pd.DataFrame]]:
        """Recherche de recommandations de produits similaires"""
        cypher = f"""
        MATCH (p1:Product)-[:CATEGORIZED_AS]->(c:Category)<-[:CATEGORIZED_AS]-(p2:Product)
        WHERE toLower(p1.name) CONTAINS toLower('{product_name}') AND p1.name <> p2.name
        WITH p1, p2, count(c) AS common_categories
        WHERE common_categories > 0
        RETURN p1.name AS Produit_Source, p2.name AS Recommandation, 
               p2.nutriscore AS Nutriscore, common_categories AS Catégories_Communes
        ORDER BY common_categories DESC, p2.nutriscore
        LIMIT 5
        """
        results = self.agent.execute_custom_cypher(cypher)
        
        if isinstance(results, list) and len(results) > 0:
            response = f"Voici des produits similaires à '{product_name}':"
            return response, pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé de produits similaires à '{product_name}'.", None
    
    def _handle_diet_query(self, diet_type: str) -> Tuple[str, Optional[pd.DataFrame]]:
        """Recherche de produits adaptés à un régime alimentaire spécifique"""
        diet_type = diet_type.lower()
        
        if "vegan" in diet_type or "végétalien" in diet_type:
            cypher = """
            MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
            WITH p, collect(i.vegan) AS vegan_status
            WHERE ALL(status IN vegan_status WHERE status = 'yes')
            RETURN p.name AS Produit, p.nutriscore AS Nutriscore
            LIMIT 10
            """
        elif "végétarien" in diet_type or "végé" in diet_type or "vege" in diet_type or "vegetarian" in diet_type:
            cypher = """
            MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
            WITH p, collect(i.vegetarian) AS vegetarian_status
            WHERE ALL(status IN vegetarian_status WHERE status = 'yes')
            RETURN p.name AS Produit, p.nutriscore AS Nutriscore
            LIMIT 10
            """
        elif "gluten" in diet_type:
            cypher = """
            MATCH (p:Product)
            WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {name: 'gluten'})
            RETURN p.name AS Produit, p.nutriscore AS Nutriscore
            LIMIT 10
            """
        elif "bio" in diet_type or "biologique" in diet_type or "organic" in diet_type:
            cypher = """
            MATCH (p:Product)-[:HAS_LABEL]->(l:Label)
            WHERE l.name CONTAINS 'organic' OR l.name CONTAINS 'bio'
            RETURN p.name AS Produit, p.nutriscore AS Nutriscore, l.name AS Label
            LIMIT 10
            """
        else:
            return f"Je ne connais pas encore le régime '{diet_type}' ou je n'ai pas suffisamment d'informations pour l'identifier.", None
        
        results = self.agent.execute_custom_cypher(cypher)
        
        if isinstance(results, list) and len(results) > 0:
            response = f"Voici des produits adaptés au régime {diet_type}:"
            return response, pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé de produits adaptés au régime {diet_type}.", None
    
    def _handle_comparison(self, product1: str, product2: str) -> Tuple[str, Optional[pd.DataFrame]]:
        """Comparaison entre deux produits"""
        cypher = f"""
        MATCH (p1:Product)
        WHERE toLower(p1.name) CONTAINS toLower('{product1}')
        WITH p1 LIMIT 1
        MATCH (p2:Product)
        WHERE toLower(p2.name) CONTAINS toLower('{product2}')
        WITH p1, p2 LIMIT 1
        OPTIONAL MATCH (p1)-[r1:HAS_NUTRIENT]->(n1:Nutrient)
        OPTIONAL MATCH (p2)-[r2:HAS_NUTRIENT]->(n2:Nutrient)
        WHERE n1.name = n2.name
        RETURN p1.name AS Produit1, p2.name AS Produit2, 
               p1.nutriscore AS Nutriscore1, p2.nutriscore AS Nutriscore2,
               n1.name AS Nutriment, r1.value AS Valeur1, r2.value AS Valeur2,
               r1.unit AS Unité
        """
        results = self.agent.execute_custom_cypher(cypher)
        
        if isinstance(results, list) and len(results) > 0:
            response = f"Voici une comparaison entre '{product1}' et '{product2}':"
            return response, pd.DataFrame(results)
        else:
            return f"Je n'ai pas pu comparer '{product1}' et '{product2}', peut-être qu'un des produits n'existe pas dans ma base de données.", None
    
    def _format_results(self, results):
        """Formate les résultats pour l'affichage"""
        if isinstance(results, list) and results:
            return pd.DataFrame(results)
        return results