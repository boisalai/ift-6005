"""
Module qui gère les intentions détectées et dirige la requête vers la bonne méthode
pour interroger la base Neo4j.
"""

import logging
from typing import Dict, List, Any
from intent_analyser import IntentType

logger = logging.getLogger("IntentHandler")

class IntentHandler:
    """
    Traite les différentes intentions et exécute la requête correspondante sur la base de données.
    """
    def __init__(self, db_connector):
        self.db = db_connector

    def handle_intent(self, intent: IntentType, entities: List[str], context: Dict) -> Dict:
        logger.info(f"Traitement de l'intention: {intent}, Entités: {entities}")
        if intent == IntentType.PRODUCT_INFO:
            return self._handle_product_info(entities, context)
        elif intent == IntentType.BRAND_QUERY:
            return self._handle_brand_query(entities, context)
        elif intent == IntentType.INGREDIENT_QUERY:
            return self._handle_ingredient_query(entities, context)
        elif intent == IntentType.ALLERGEN_CHECK:
            return self._handle_allergen_check(entities, context)
        elif intent == IntentType.NUTRITIONAL_INFO:
            return self._handle_nutritional_info(entities, context)
        elif intent == IntentType.RECOMMENDATION:
            return self._handle_recommendation(entities, context)
        elif intent == IntentType.DIET_QUERY:
            return self._handle_diet_query(entities, context)
        elif intent == IntentType.COMPARISON:
            return self._handle_comparison(entities, context)
        else:
            return self._handle_general_query(entities, context)

    def _handle_product_info(self, entities: List[str], context: Dict) -> Dict:
        if not entities:
            return {"success": False, "message": "Produit non spécifié"}
        product_name = entities[0]
        results = self.db.run_query("PRODUCT_INFO", {"product_name": product_name})
        return {"success": True, "results": results, "query_type": "product_info", "query_params": {"product_name": product_name}}

    def _handle_brand_query(self, entities: List[str], context: Dict) -> Dict:
        if not entities:
            return {"success": False, "message": "Marque non spécifiée"}
        brand_name = entities[0]
        results = self.db.run_query("BRAND_PRODUCTS", {"brand_name": brand_name})
        return {"success": True, "results": results, "query_type": "brand_query", "query_params": {"brand_name": brand_name}}

    def _handle_ingredient_query(self, entities: List[str], context: Dict) -> Dict:
        if not entities:
            return {"success": False, "message": "Ingrédient non spécifié"}
        ingredient_name = entities[0]
        results = self.db.run_query("PRODUCTS_WITH_INGREDIENT", {"ingredient_name": ingredient_name})
        return {"success": True, "results": results, "query_type": "ingredient_query", "query_params": {"ingredient_name": ingredient_name}}

    def _handle_allergen_check(self, entities: List[str], context: Dict) -> Dict:
        if not entities:
            return {"success": False, "message": "Allergène non spécifié"}
        allergen_name = entities[0]
        results = self.db.run_query("PRODUCTS_WITHOUT_ALLERGEN", {"allergen_name": allergen_name})
        return {"success": True, "results": results, "query_type": "allergen_check", "query_params": {"allergen_name": allergen_name}}

    def _handle_nutritional_info(self, entities: List[str], context: Dict) -> Dict:
        if not entities:
            return {"success": False, "message": "Produit non spécifié"}
        product_name = entities[0]
        results = self.db.run_query("NUTRITIONAL_INFO", {"product_name": product_name})
        return {"success": True, "results": results, "query_type": "nutritional_info", "query_params": {"product_name": product_name}}

    def _handle_recommendation(self, entities: List[str], context: Dict) -> Dict:
        if not entities:
            return {"success": False, "message": "Produit de référence non spécifié"}
        product_name = entities[0]
        results = self.db.run_query("SIMILAR_PRODUCTS", {"product_name": product_name})
        return {"success": True, "results": results, "query_type": "recommendation", "query_params": {"product_name": product_name}}

    def _handle_diet_query(self, entities: List[str], context: Dict) -> Dict:
        if not entities:
            return {"success": False, "message": "Type de régime non spécifié"}
        diet_type = entities[0].lower()
        if "vegan" in diet_type or "végétalien" in diet_type:
            results = self.db.run_query("VEGAN_PRODUCTS")
        elif "vegetarian" in diet_type or "végétarien" in diet_type:
            results = self.db.run_query("VEGETARIAN_PRODUCTS")
        elif "gluten" in diet_type:
            results = self.db.run_query("GLUTEN_FREE_PRODUCTS")
        elif "bio" in diet_type or "organic" in diet_type:
            results = self.db.run_query("ORGANIC_PRODUCTS")
        else:
            return {"success": False, "message": f"Régime alimentaire non reconnu: {diet_type}"}
        return {"success": True, "results": results, "query_type": "diet_query", "query_params": {"diet_type": diet_type}}

    def _handle_comparison(self, entities: List[str], context: Dict) -> Dict:
        if len(entities) < 2:
            return {"success": False, "message": "Deux produits sont nécessaires pour une comparaison"}
        product1_name = entities[0]
        product2_name = entities[1]
        results = self.db.run_query("COMPARE_PRODUCTS", {"product1_name": product1_name, "product2_name": product2_name})
        return {"success": True, "results": results, "query_type": "comparison", "query_params": {"product1_name": product1_name, "product2_name": product2_name}}

    def _handle_general_query(self, entities: List[str], context: Dict) -> Dict:
        query_text = " ".join(entities) if entities else ""
        if not query_text:
            return {"success": False, "message": "Requête vide"}
        # Pour une requête générale, on pourrait effectuer une recherche vectorielle ou autre.
        results = self.db.vector_search(query_text)
        return {"success": True, "results": results, "query_type": "general_query", "query_params": {"query_text": query_text}}
