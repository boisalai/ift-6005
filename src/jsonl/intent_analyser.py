"""
Module d'analyse d'intention basé sur le LLM.
Il identifie l'intention et extrait les entités dans une question (en français ou en anglais).
"""

import json
import logging
from enum import Enum
from typing import Tuple, List, Optional

class IntentType(Enum):
    PRODUCT_INFO = "product_info"          # Information sur un produit
    BRAND_QUERY = "brand_query"            # Recherche par marque
    INGREDIENT_QUERY = "ingredient_query"  # Recherche par ingrédient
    ALLERGEN_CHECK = "allergen_check"      # Vérification d'allergènes
    NUTRITIONAL_INFO = "nutritional_info"    # Information nutritionnelle
    RECOMMENDATION = "recommendation"      # Recommandation de produits
    DIET_QUERY = "diet_query"              # Question sur un régime (vegan, sans gluten, etc.)
    COMPARISON = "comparison"              # Comparaison entre produits
    GENERAL_QUERY = "general_query"        # Autre type de question

class IntentAnalyzer:
    """
    Analyse l'intention et les entités d'une question grâce au LLM.
    """
    def __init__(self, llm):
        self.llm = llm
        self.logger = logging.getLogger("IntentAnalyzer")
        self.default_intent = IntentType.GENERAL_QUERY

    def analyze(self, query: str) -> Tuple[IntentType, Optional[List[str]]]:
        """
        Analyse la question et retourne l'intention et les entités sous forme d'objet JSON.
        """
        if not self.llm:
            self.logger.error("Aucun LLM configuré pour l'analyse d'intention")
            return self.default_intent, None

        prompt = (
            "Analyze the following question and identify the intent and entities.\n"
            "The question can be in French or English.\n"
            "Return only a JSON object in the following format, without any extra text:\n"
            '{ "intent": "<intent_type>", "entities": ["<entity1>", "<entity2>", ...] }\n'
            "Possible intent types:\n"
            "- product_info\n- brand_query\n- ingredient_query\n- allergen_check\n"
            "- nutritional_info\n- recommendation\n- diet_query\n- comparison\n- general_query\n\n"
            f"Question: {query}"
        )

        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            content = content.strip()
            if content.startswith("```") and content.endswith("```"):
                content = content.strip("```").strip()
            self.logger.debug(f"LLM response: {content}")
            result = json.loads(content)
            intent_str = result.get("intent", "general_query")
            entities = result.get("entities", [])
            try:
                intent = IntentType(intent_str)
            except ValueError:
                self.logger.warning(f"Intent inconnue reçue: {intent_str}")
                intent = self.default_intent
            return intent, entities if entities else None
        except Exception as e:
            self.logger.error(f"Erreur pendant l'analyse d'intention: {e}")
            return self.default_intent, None
