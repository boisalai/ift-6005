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

# Chargement des variables d'environnement
root_dir = Path(__file__).parent.parent.parent.absolute()
dotenv_path = os.path.join(root_dir, '.env')
print(f"Chargement des variables d'environnement depuis : {dotenv_path}")
load_dotenv(dotenv_path)

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
    VEGETARIAN_PRODUCTS, GLUTEN_FREE_PRODUCTS, ORGANIC_PRODUCTS, COMPARE_PRODUCTS
)

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
            return json.dumps([record.data() for record in result], indent=2, ensure_ascii=False)
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
        return json.dumps(embedding.tolist(), ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erreur lors de la création d'embedding: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialisation du LLM via LiteLLMModel
    # engine = "ollama/deepseek-r1:7b"
    engine = "claude-3-5-sonnet-20240620"
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
            create_text_embedding
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
      
    # EXEMPLES DE REQUÊTES CYPHER
    
    Voici des exemples de requêtes Cypher pour différentes tâches :
    
    ## Recherche vectorielle (utilise l'index de similarité)
    ```
    {VECTOR_SEARCH}
    ```
    
    ## Recherche par marque
    ```
    {BRAND_PRODUCTS}
    ```
    
    ## Recherche par ingrédient
    ```
    {PRODUCTS_WITH_INGREDIENT}
    ```
    
    ## Recherche sans allergène
    ```
    {PRODUCTS_WITHOUT_ALLERGEN}
    ```
    
    ## Information nutritionnelle
    ```
    {NUTRITIONAL_INFO}
    ```
    
    ## Produits similaires
    ```
    {SIMILAR_PRODUCTS}
    ```
    
    ## Alternatives plus saines
    ```
    {HEALTHIER_ALTERNATIVES}
    ```
    
    ## Produits végétaliens
    ```
    {VEGAN_PRODUCTS}
    ```
    
    ## Produits végétariens
    ```
    {VEGETARIAN_PRODUCTS}
    ```
    
    ## Produits sans gluten
    ```
    {GLUTEN_FREE_PRODUCTS}
    ```
    
    ## Produits biologiques
    ```
    {ORGANIC_PRODUCTS}
    ```
    
    ## Comparaison de produits
    ```
    {COMPARE_PRODUCTS}
    ```
    
    # UTILISATION DES OUTILS

    Pour répondre aux questions des utilisateurs, suis ce processus :

    1. COMPRENDRE LA REQUÊTE
    - Analyse la question de l'utilisateur pour déterminer le type d'information recherchée
    - Identifie les entités pertinentes (produits, marques, ingrédients, etc.)
    - Détermine le type de requête à effectuer

    2. CONSTRUIRE LA REQUÊTE CYPHER
    - Utilise les exemples fournis comme modèles
    - Adapte la requête selon les besoins spécifiques de l'utilisateur
    - Assure-toi que la syntaxe Cypher est correcte
    - Pour les recherches textuelles, utilise toLower() pour rendre la recherche insensible à la casse

    3. EXÉCUTER LA REQUÊTE ET FORMATER LA RÉPONSE
    - Pour les requêtes normales, utilise l'outil execute_cypher_query(query, params)
    - Pour les recherches vectorielles :
        a. Génère d'abord l'embedding avec create_text_embedding(text)
        b. Utilise cet embedding dans execute_cypher_query pour la recherche vectorielle
    - Formate la réponse de manière claire et lisible
    - Adapte le style selon que l'utilisateur demande en français ou en anglais

    # RÈGLES IMPORTANTES

    - Respecte TOUJOURS la syntaxe Cypher correcte
    - Utilise des paramètres ($param) plutôt que d'insérer directement les valeurs dans les requêtes
    - Limite le nombre de résultats (LIMIT) pour éviter les réponses trop longues
    - Vérifie que les noms de propriétés et de relations sont corrects
    - Pour la recherche vectorielle, utilise l'index "product_embedding_index"
    - Réponds dans la même langue que celle utilisée par l'utilisateur (français ou anglais)

    # GESTION DES INFORMATIONS NON TROUVÉES

    Si la requête Cypher ne retourne aucun résultat ou si l'information demandée n'est pas disponible dans la base de données Neo4j :
    - En français : Réponds "Désolé, la base de données ne permet pas de répondre à cette question." puis propose éventuellement une requête alternative si pertinent.
    - En anglais : Réponds "Sorry, the database does not contain information to answer this question." puis propose éventuellement une requête alternative si pertinent.

    N'invente jamais de résultats et n'essaie pas de répondre avec des connaissances générales. Limite-toi uniquement aux informations présentes dans la base de données Neo4j.
    
    # FORMAT DE RÉPONSE
    
    Ta réponse finale doit être claire, concise et sans ton processus de réflexion interne. Structure ta réponse ainsi :
    1. Une introduction brève qui présente les informations trouvées
    2. Les détails pertinents organisés de façon lisible
    3. Si applicable, une conclusion ou recommandation basée sur les données
    """
    )

    try:
        question = "Tell me about Nutella."
        response = agent.run(question, additional_args={
                "additional_notes": AGENT_INSTRUCTIONS,
            })
        print("Réponse de l'agent :", response)
    finally:
        """Ferme la connexion à Neo4j."""
        if driver:
            driver.close()