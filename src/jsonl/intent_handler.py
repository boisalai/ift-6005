import re
from enum import Enum
import pandas as pd

class IntentType(Enum):
    PRODUCT_INFO = "information_produit"
    BRAND_QUERY = "recherche_marque"
    INGREDIENT_QUERY = "recherche_ingredient"
    ALLERGEN_CHECK = "verification_allergene"
    NUTRITIONAL_INFO = "information_nutritionnelle"
    RECOMMENDATION = "recommandation"
    DIET_QUERY = "regime_alimentaire"
    COMPARISON = "comparaison"
    GENERAL_QUERY = "question_generale"
    UNKNOWN = "inconnu"

class IntentHandler:
    def __init__(self, agent):
        self.agent = agent
        self.intent_patterns = {
            IntentType.PRODUCT_INFO: [
                r"(?:qu[''](?:est-ce|est ce)|c['']est quoi|info(?:rmation)?s? (?:sur|pour)|parle[sz]-moi de|dis-moi (?:plus )?sur)(?: le| la| les)? (.+?)(?:\?|$)",
                r"(?:que (?:sais|connais)(?:-tu| tu) (?:sur|de))(?: le| la| les)? (.+?)(?:\?|$)",
                r"(?:puis-je avoir|donne(?:s|z)?(?:-moi)?|obtenir)(?: des)? (?:info(?:rmation)?s?|détails)(?: sur| pour| à propos de)(?: le| la| les)? (.+?)(?:\?|$)"
            ],
            IntentType.BRAND_QUERY: [
                r"(?:quels (?:sont|produits)(?: les)?|montre(?:s|z)?(?:-moi)?|liste(?:s|z)?|donne(?:s|z)?(?:-moi)?)(?: les| des)? (?:produits|articles)(?:(?:(?:(?:de|par) la)|(?:(?:fabriqués|vendus|produits|fait) par))?(?: la)? marque| de) (.+?)(?:\?|$)",
                r"(?:je (?:cherche|recherche|veux))(?: des| les)? (?:produits|articles)(?: de| par)?(?: la)? marque (.+?)(?:\?|$)"
            ],
            IntentType.INGREDIENT_QUERY: [
                r"(?:quels (?:sont|produits)(?: les)?|montre(?:s|z)?(?:-moi)?|liste(?:s|z)?|donne(?:s|z)?(?:-moi)?)(?: les| des)? (?:produits|articles)(?: qui|) (?:contien(?:nen)?t|avec)(?: du| de la| des| les?)? (.+?)(?:\?|$)",
                r"(?:y a(?:-t-il| t il)|existe(?:-t-il| t il))(?: des| les)? (?:produits|articles)(?: qui|) (?:contien(?:nen)?t|avec)(?: du| de la| des| les?)? (.+?)(?:\?|$)"
            ],
            IntentType.ALLERGEN_CHECK: [
                r"(?:quels (?:sont|produits)(?: les)?|montre(?:s|z)?(?:-moi)?|liste(?:s|z)?|donne(?:s|z)?(?:-moi)?)(?: les| des)? (?:produits|articles)(?: qui|) (?:sont|) (?:sans|ne contien(?:nen)?t pas)(?: de| d[''])? (.+?)(?:\?|$)",
                r"(?:comment savoir si|puis-je|est-ce que|est ce que)(?: les| des)? (?:produits|articles)(?: contien(?:nen)?t| ont)(?: de| des| du| de la)? (.+?)(?:\?|$)",
                r"(?:je suis allergique|allergie)(?: à| au| aux)? (.+?)(?: quel|\?|$)"
            ],
            IntentType.NUTRITIONAL_INFO: [
                r"(?:quelle|combien)(?: est| d[''])? (?:est la |la )?(?:valeur|teneur) (?:nutritionnelle|nutritive|calorique|en calories|en sucres?|en graisses?|en lipides|en glucides|en protéines|en sel|en sodium)(?: de| pour| dans)?(?: les| la| le)? (.+?)(?:\?|$)",
                r"(?:quelles sont|donne(?:s|z)?(?:-moi)?)(?: les)? (?:infos?|informations)? (?:nutritionnelles?|nutritives)(?: de| pour| sur| dans)?(?: les| la| le)? (.+?)(?:\?|$)"
            ],
            IntentType.RECOMMENDATION: [
                r"(?:peux-tu|pouvez-vous|peux tu|pouvez vous|pourriez[- ]vous)(?: me)? (?:recommander|suggérer|conseiller|proposer)(?: des| les)? (?:produits?|alternatives?)(?:(?:similaires?|comme|ressemblants?)(?: à| au| aux)?)? (.+?)(?:\?|$)",
                r"(?:quels? (?:sont|seraient?|est|serait))(?: les?)? (?:produits?|alternatives?)(?:(?:similaires?|comme|ressemblants?)(?: à| au| aux)?)? (.+?)(?:\?|$)",
                r"(?:je cherche|recherche)(?: des| les)? (?:produits?|alternatives?)(?: similaires?(?: à| au| aux)?)? (.+?)(?:\?|$)"
            ],
            IntentType.DIET_QUERY: [
                r"(?:quels (?:sont|produits)(?: les)?|montre(?:s|z)?(?:-moi)?|liste(?:s|z)?|donne(?:s|z)?(?:-moi)?)(?: les| des)? (?:produits|articles)(?: qui sont| adaptés? aux?)? (vegan|végétalien|végétarien|sans gluten|bio|biologique|halal|kasher|casher|végé|vege)(?:s|ne|nes)?(?:\?|$)",
                r"(?:je suis|mon régime est|mon alimentation est) (vegan|végétalien|végétarien|sans gluten|bio|biologique|halal|kasher|casher|végé|vege)(?:ne)?(?:, |. | )(?:quels?|conseille[sz]-moi|recommande[sz]-moi|montre[sz]-moi)(?: des| les)? (?:produits|aliments)(?:\?|$)"
            ],
            IntentType.COMPARISON: [
                r"(?:compare(?:s|z)?|quelle est la différence entre|qu[''](?:est-ce|est ce) qui différencie|quelles sont les différences entre)(?: les| la| le)? (.+?) et (?:les?|la)? (.+?)(?:\?|$)",
                r"(?:lequel|laquelle)(?: est| sont)? (?:meilleur|mieux|plus sain|plus nutritif|plus nutritionnel|plus healthy|healthier)(?: entre| parmi)?(?: les| la| le)? (.+?) et (?:les?|la)? (.+?)(?:\?|$)"
            ],
        }
    
    def detect_intent(self, query):
        """Détecte l'intention de l'utilisateur à partir de sa requête"""
        query = query.lower().strip()
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query)
                if match:
                    if intent_type == IntentType.COMPARISON and len(match.groups()) >= 2:
                        return intent_type, [match.group(1), match.group(2)]
                    return intent_type, match.group(1)
        
        # Si aucun pattern ne correspond, essayer de détecter des mots-clés génériques
        if any(keyword in query for keyword in ["nutriment", "calorie", "nutrition", "protéine", "sucre", "graisse"]):
            return IntentType.NUTRITIONAL_INFO, None
        
        if any(keyword in query for keyword in ["allergie", "allergique", "sans", "contient pas"]):
            return IntentType.ALLERGEN_CHECK, None
        
        if any(keyword in query for keyword in ["produit", "aliment", "nourriture", "manger"]):
            return IntentType.PRODUCT_INFO, None
        
        return IntentType.GENERAL_QUERY, None
    
    def handle_intent(self, query):
        """Traite la requête en fonction de l'intention détectée"""
        intent_type, entity = self.detect_intent(query)
        
        # Logging pour le débogage
        print(f"Intent détecté: {intent_type.value}, Entité: {entity}")
        
        if intent_type == IntentType.GENERAL_QUERY:
            # Utiliser la chaîne QA standard pour les requêtes générales
            return self.agent.qa_chain.invoke({"query": query}), None
        
        elif intent_type == IntentType.PRODUCT_INFO and entity:
            # Requête d'information sur un produit spécifique
            cypher = f"""
            MATCH (p:Product)
            WHERE p.name CONTAINS '{entity}'
            OPTIONAL MATCH (p)-[:BELONGS_TO]->(b:Brand)
            OPTIONAL MATCH (p)-[:CATEGORIZED_AS]->(c:Category)
            RETURN p.name AS Produit, p.nutriscore AS Nutriscore, 
                   p.quantity AS Quantité, collect(DISTINCT b.name) AS Marques,
                   collect(DISTINCT c.name) AS Catégories
            LIMIT 5
            """
            results = self.agent.execute_custom_cypher(cypher)
            
            if results and len(results) > 0:
                response = f"Voici les informations sur les produits correspondant à '{entity}':"
                return response, self._format_results(results)
            else:
                return f"Je n'ai pas trouvé d'informations sur des produits nommés '{entity}'.", None
        
        elif intent_type == IntentType.BRAND_QUERY and entity:
            # Requête sur une marque spécifique
            cypher = f"""
            MATCH (p:Product)-[:BELONGS_TO]->(b:Brand)
            WHERE toLower(b.name) CONTAINS toLower('{entity}')
            RETURN p.name AS Produit, p.nutriscore AS Nutriscore, p.quantity AS Quantité
            LIMIT 10
            """
            results = self.agent.execute_custom_cypher(cypher)
            
            if results and len(results) > 0:
                response = f"Voici les produits de la marque '{entity}':"
                return response, self._format_results(results)
            else:
                return f"Je n'ai pas trouvé de produits de la marque '{entity}'.", None
        
        elif intent_type == IntentType.INGREDIENT_QUERY and entity:
            # Requête sur un ingrédient
            cypher = f"""
            MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
            WHERE toLower(i.name) CONTAINS toLower('{entity}')
            RETURN p.name AS Produit, p.nutriscore AS Nutriscore, i.name AS Ingrédient
            LIMIT 10
            """
            results = self.agent.execute_custom_cypher(cypher)
            
            if results and len(results) > 0:
                response = f"Voici les produits qui contiennent '{entity}':"
                return response, self._format_results(results)
            else:
                return f"Je n'ai pas trouvé de produits contenant '{entity}'.", None
        
        elif intent_type == IntentType.ALLERGEN_CHECK and entity:
            # Vérification d'allergène
            cypher = f"""
            MATCH (p:Product)
            WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {{name: '{entity}'}})
            RETURN p.name AS Produit, p.nutriscore AS Nutriscore
            LIMIT 10
            """
            results = self.agent.execute_custom_cypher(cypher)
            
            if results and len(results) > 0:
                response = f"Voici des produits qui ne contiennent pas l'allergène '{entity}':"
                return response, self._format_results(results)
            else:
                return f"Je n'ai pas pu trouver de produits sans l'allergène '{entity}', ou cet allergène n'est pas répertorié dans la base de données.", None
        
        elif intent_type == IntentType.NUTRITIONAL_INFO and entity:
            # Information nutritionnelle
            cypher = f"""
            MATCH (p:Product)-[r:HAS_NUTRIENT]->(n:Nutrient)
            WHERE p.name CONTAINS '{entity}'
            RETURN p.name AS Produit, n.name AS Nutriment, r.value AS Valeur, r.unit AS Unité
            """
            results = self.agent.execute_custom_cypher(cypher)
            
            if results and len(results) > 0:
                response = f"Voici les informations nutritionnelles pour '{entity}':"
                return response, self._format_results(results)
            else:
                return f"Je n'ai pas trouvé d'informations nutritionnelles pour '{entity}'.", None
        
        elif intent_type == IntentType.RECOMMENDATION and entity:
            # Recommandation de produits similaires
            cypher = f"""
            MATCH (p1:Product)-[:CATEGORIZED_AS]->(c:Category)<-[:CATEGORIZED_AS]-(p2:Product)
            WHERE p1.name CONTAINS '{entity}' AND p1.name <> p2.name
            WITH p1, p2, count(c) AS common_categories
            WHERE common_categories > 0
            RETURN p1.name AS Produit_Source, p2.name AS Recommandation, 
                   p2.nutriscore AS Nutriscore, common_categories AS Catégories_Communes
            ORDER BY common_categories DESC, p2.nutriscore
            LIMIT 5
            """
            results = self.agent.execute_custom_cypher(cypher)
            
            if results and len(results) > 0:
                response = f"Voici des produits similaires à '{entity}':"
                return response, self._format_results(results)
            else:
                return f"Je n'ai pas trouvé de produits similaires à '{entity}'.", None
        
        elif intent_type == IntentType.DIET_QUERY and entity:
            # Requête sur un régime alimentaire
            diet_type = entity.lower()
            
            if "vegan" in diet_type or "végétalien" in diet_type:
                cypher = """
                MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
                WITH p, collect(i.vegan) AS vegan_status
                WHERE ALL(status IN vegan_status WHERE status = 'yes')
                RETURN p.name AS Produit, p.nutriscore AS Nutriscore
                LIMIT 10
                """
            elif "végétarien" in diet_type or "végé" in diet_type or "vege" in diet_type:
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
            elif "bio" in diet_type or "biologique" in diet_type:
                cypher = """
                MATCH (p:Product)-[:HAS_LABEL]->(l:Label)
                WHERE l.name CONTAINS 'organic' OR l.name CONTAINS 'bio'
                RETURN p.name AS Produit, p.nutriscore AS Nutriscore, l.name AS Label
                LIMIT 10
                """
            else:
                return f"Je ne connais pas encore le régime '{entity}' ou je n'ai pas suffisamment d'informations pour l'identifier.", None
            
            results = self.agent.execute_custom_cypher(cypher)
            
            if results and len(results) > 0:
                response = f"Voici des produits adaptés au régime {entity}:"
                return response, self._format_results(results)
            else:
                return f"Je n'ai pas trouvé de produits adaptés au régime {entity}.", None
        
        elif intent_type == IntentType.COMPARISON and isinstance(entity, list) and len(entity) >= 2:
            # Comparaison entre deux produits
            product1, product2 = entity[0], entity[1]
            
            cypher = f"""
            MATCH (p1:Product)
            WHERE p1.name CONTAINS '{product1}'
            WITH p1 LIMIT 1
            MATCH (p2:Product)
            WHERE p2.name CONTAINS '{product2}'
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
            
            if results and len(results) > 0:
                response = f"Voici une comparaison entre '{product1}' et '{product2}':"
                return response, self._format_results(results)
            else:
                return f"Je n'ai pas pu comparer '{product1}' et '{product2}', peut-être qu'un des produits n'existe pas dans ma base de données.", None
        
        # Fallback pour les autres cas
        response = self.agent.qa_chain.invoke({"query": query})
        return response, None
    
    def _format_results(self, results):
        """Formate les résultats pour l'affichage"""
        if isinstance(results, list) and results:
            return pd.DataFrame(results)
        return results