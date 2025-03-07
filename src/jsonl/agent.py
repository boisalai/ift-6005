import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate
from intent_handler import IntentHandler

# Charger les variables d'environnement
load_dotenv()

# Configuration Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class OpenFoodFactsAgent:
    def __init__(self):
        # Connexion à Neo4j via LangChain
        self.graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USER,
            password=NEO4J_PASSWORD
        )
        
        # Modèle de génération Cypher pour l'agent
        self.cypher_generation_template = """Task: Générer une requête Cypher pour interroger une base de données de graphe de produits alimentaires.

Instructions:
Utilise uniquement les types de relations et propriétés fournis dans le schéma.
N'utilise pas d'autres types de relations ou propriétés qui ne sont pas fournis.

Schéma:
{schema}

Note: N'inclus pas d'explications ou d'excuses dans tes réponses.
Ne réponds pas aux questions qui pourraient demander autre chose que la construction d'une requête Cypher.
N'inclus aucun texte à part la requête Cypher générée.

Exemples: Voici quelques exemples de requêtes Cypher générées pour des questions particulières:

# Quels sont les produits de la marque Kroger?
MATCH (p:Product)-[:BELONGS_TO]->(b:Brand {name: 'Kroger'})
RETURN p.name, p.nutriscore, p.quantity

# Quels sont les produits qui contiennent du sucre?
MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
WHERE i.name CONTAINS 'sugar' OR i.name CONTAINS 'sucre'
RETURN p.name, p.nutriscore

# Trouve-moi des produits végétaliens
MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
WITH p, collect(i.vegan) AS vegan_status
WHERE ALL(status IN vegan_status WHERE status = 'yes')
RETURN p.name, p.id

# Quels sont les produits sans gluten?
MATCH (p:Product)
WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {name: 'gluten'})
RETURN p.name, p.id

# Quels sont les produits avec un bon Nutri-Score?
MATCH (p:Product)
WHERE p.nutriscore IN ['a', 'b']
RETURN p.name, p.nutriscore
ORDER BY p.nutriscore

La question est:
{question}"""

        self.cypher_prompt = PromptTemplate(
            input_variables=["schema", "question"],
            template=self.cypher_generation_template
        )
        
        # Initialiser le LLM
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo"  # ou un autre modèle adapté
        )
        
        # Chaîne de questions-réponses
        self.qa_chain = GraphCypherQAChain.from_llm(
            self.llm,
            graph=self.graph,
            verbose=True,
            cypher_prompt=self.cypher_prompt,
        )
        
        # Initialiser le gestionnaire d'intentions
        self.intent_handler = IntentHandler(self)
        
    def refresh_schema(self):
        """Rafraîchir le schéma du graphe depuis Neo4j"""
        self.graph.refresh_schema()
        print("Schéma du graphe rafraîchi.")
        
    def get_schema(self):
        """Obtenir le schéma actuel du graphe"""
        return self.graph.schema
        
    def query(self, question):
        """Répondre à une question en langage naturel"""
        try:
            # Utiliser le gestionnaire d'intentions pour traiter la requête
            response, data = self.intent_handler.handle_intent(question)
            return response, data
        except Exception as e:
            return f"Erreur lors de la requête: {str(e)}", None
    
    def execute_custom_cypher(self, cypher_query, params=None):
        """Exécuter une requête Cypher personnalisée"""
        try:
            result = self.graph.query(cypher_query, params=params or {})
            return result
        except Exception as e:
            return f"Erreur d'exécution Cypher: {str(e)}"
    
    def get_product_recommendations(self, product_name, criteria="healthier"):
        """Recommander des produits similaires ou plus sains"""
        if criteria == "healthier":
            query = """
            MATCH (p1:Product)-[:CATEGORIZED_AS]->(c:Category)<-[:CATEGORIZED_AS]-(p2:Product)
            WHERE p1.name CONTAINS $product_name 
              AND p2.name <> p1.name 
              AND p1.nutriscore > p2.nutriscore
            RETURN DISTINCT p1.name as Produit_Original, p2.name as Recommandation, 
                   p1.nutriscore as Nutriscore_Original, p2.nutriscore as Nutriscore_Recommandé
            ORDER BY p2.nutriscore
            LIMIT 5
            """
        else:  # similar
            query = """
            MATCH (p1:Product)-[:CONTAINS]->(i:Ingredient)<-[:CONTAINS]-(p2:Product)
            WHERE p1.name CONTAINS $product_name AND p2.name <> p1.name
            WITH p1, p2, count(i) AS common_ingredients
            WHERE common_ingredients > 2
            RETURN p1.name as Produit_Original, p2.name as Recommandation, 
                   common_ingredients as Ingrédients_Communs
            ORDER BY common_ingredients DESC
            LIMIT 5
            """
        
        results = self.execute_custom_cypher(query, {"product_name": product_name})
        
        if isinstance(results, list) and len(results) > 0:
            return f"Recommandations pour '{product_name}':", pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé de recommandations pour '{product_name}'. Essayez un autre produit.", None
    
    def get_nutritional_analysis(self, product_name):
        """Obtenir une analyse nutritionnelle pour un produit spécifique"""
        query = """
        MATCH (p:Product)-[r:HAS_NUTRIENT]->(n:Nutrient)
        WHERE p.name CONTAINS $product_name
        RETURN p.name as Produit, n.name as Nutriment, r.value as Valeur, r.unit as Unité
        """
        results = self.execute_custom_cypher(query, {"product_name": product_name})
        
        if isinstance(results, list) and len(results) > 0:
            return f"Informations nutritionnelles pour '{product_name}':", pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé d'informations nutritionnelles pour '{product_name}'.", None
    
    def get_dietary_info(self, diet_type="vegan"):
        """Obtenir des produits adaptés à un régime alimentaire spécifique"""
        if diet_type.lower() == "végétalien" or diet_type.lower() == "vegan":
            query = """
            MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
            WITH p, collect(i.vegan) AS vegan_status
            WHERE ALL(status IN vegan_status WHERE status = 'yes')
            RETURN p.name as Produit, p.nutriscore as Nutriscore, p.quantity as Quantité
            LIMIT 10
            """
        elif diet_type.lower() == "végétarien" or diet_type.lower() == "vegetarian":
            query = """
            MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
            WITH p, collect(i.vegetarian) AS vegetarian_status
            WHERE ALL(status IN vegetarian_status WHERE status = 'yes')
            RETURN p.name as Produit, p.nutriscore as Nutriscore, p.quantity as Quantité
            LIMIT 10
            """
        elif diet_type.lower() == "sans gluten":
            query = """
            MATCH (p:Product)
            WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {name: 'gluten'})
            RETURN p.name as Produit, p.nutriscore as Nutriscore, p.quantity as Quantité
            LIMIT 10
            """
        elif diet_type.lower() == "biologique" or diet_type.lower() == "bio":
            query = """
            MATCH (p:Product)-[:HAS_LABEL]->(l:Label)
            WHERE l.name CONTAINS 'organic' OR l.name CONTAINS 'bio'
            RETURN p.name as Produit, p.nutriscore as Nutriscore, l.name as Label
            LIMIT 10
            """
        else:
            return f"Type de régime non pris en charge: {diet_type}", None
        
        results = self.execute_custom_cypher(query)
        
        if isinstance(results, list) and len(results) > 0:
            return f"Produits adaptés au régime {diet_type}:", pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé de produits adaptés au régime {diet_type}.", None

# Interface de conversation simple
def main():
    agent = OpenFoodFactsAgent()
    
    print("Agent Conversationnel OpenFoodFacts initialié.")
    print("Schéma du graphe chargé.")
    print("\nVous pouvez maintenant poser des questions sur les produits alimentaires.")
    print("Tapez 'exit' pour quitter.")
    
    while True:
        user_input = input("\nVotre question: ")
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Au revoir!")
            break
            
        response = agent.query(user_input)
        print("\nRéponse:", response)

if __name__ == "__main__":
    main()