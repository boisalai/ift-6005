#!/usr/bin/env python
# coding: utf-8

import os
from dotenv import load_dotenv
import textwrap
import pandas as pd
from tqdm import tqdm
from pathlib import Path

# Neo4j et graphes
from neo4j import GraphDatabase
from langchain_community.graphs import Neo4jGraph

# LLM et embeddings
from langchain_anthropic import ChatAnthropic
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import GraphCypherQAChain
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.vectorstores import Neo4jVector
from sentence_transformers import SentenceTransformer

# Gestion des avertissements
import warnings
warnings.filterwarnings("ignore")

class OpenFoodFactsAgent:
    def __init__(self):
        """Initialise l'agent conversationnel pour OpenFoodFacts avec des capacités RAG."""
        # Chargement des variables d'environnement
        load_dotenv()
        
        # Configuration Neo4j
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Constantes pour les index vectoriels
        self.vector_index_name = "product_embedding_index"
        self.vector_node_label = "Product"
        self.vector_embedding_property = "embedding"
        
        # Connexion à Neo4j via LangChain
        self.graph = Neo4jGraph(
            url=self.neo4j_uri,
            username=self.neo4j_user,
            password=self.neo4j_password
        )
        
        # Connexion directe à Neo4j pour certaines opérations
        self.driver = GraphDatabase.driver(
            self.neo4j_uri, 
            auth=(self.neo4j_user, self.neo4j_password)
        )
        
        # Initialisation du modèle SentenceTransformer pour les embeddings
        print("Chargement du modèle SentenceTransformer...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Modèle SentenceTransformer chargé: all-MiniLM-L6-v2")
        
        # Initialisation du LLM (Claude)
        self.llm = ChatAnthropic(
            temperature=0,
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=self.anthropic_api_key
        )
        
        # Modèle de prompt pour la génération Cypher
        self.setup_cypher_generation()
        
        # Initialisation des chaînes RAG
        self.setup_retrieval_chains()

    def setup_cypher_generation(self):
        """Configure le template pour la génération de requêtes Cypher."""
        self.cypher_template = """Task: Générer une requête Cypher pour interroger une base de données de graphe de produits alimentaires.

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
MATCH (p:Product)-[:HAS_BRAND]->(b:Brand {name: 'Kroger'})
RETURN p.name, p.nutriscore_grade, p.quantity

# Quels sont les produits qui contiennent du sucre?
MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
WHERE toLower(i.name) CONTAINS 'sugar' OR toLower(i.name) CONTAINS 'sucre'
RETURN p.name, p.nutriscore_grade

# Trouve-moi des produits végétaliens
MATCH (p:Product)-[:HAS_LABEL]->(l:Label)
WHERE toLower(l.name) CONTAINS 'vegan' OR toLower(l.name) CONTAINS 'végétalien'
RETURN p.name, p.nutriscore_grade

# Quels sont les produits sans gluten?
MATCH (p:Product)
WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {name: 'gluten'})
RETURN p.name, p.nutriscore_grade

# Quels sont les produits avec un bon Nutri-Score?
MATCH (p:Product)
WHERE p.nutriscore_grade IN ['a', 'b']
RETURN p.name, p.nutriscore_grade
ORDER BY p.nutriscore_grade

# Quels sont les produits biologiques?
MATCH (p:Product)-[:HAS_LABEL]->(l:Label)
WHERE toLower(l.name) CONTAINS 'bio' OR toLower(l.name) CONTAINS 'organic'
RETURN p.name, p.nutriscore_grade, l.name

La question est:
{question}"""
        
        self.cypher_prompt = PromptTemplate(
            input_variables=["schema", "question"],
            template=self.cypher_template
        )
        
        # Chaîne de génération et exécution de requêtes Cypher
        self.cypher_chain = GraphCypherQAChain.from_llm(
            self.llm,
            graph=self.graph,
            verbose=True,
            cypher_prompt=self.cypher_prompt,
            top_k=10,  # Augmenter le nombre de résultats
            return_direct=False,  # Pour permettre à LLM de traiter les résultats
            allow_dangerous_requests=True
        )

    def setup_retrieval_chains(self):
        """Configure les chaînes de récupération RAG."""
        # Configuration de la chaîne RAG standard sans requête personnalisée
        self.vector_store = Neo4jVector.from_existing_graph(
            embedding=self,  # Utiliser la méthode embed_query de cette classe
            url=self.neo4j_uri,
            username=self.neo4j_user,
            password=self.neo4j_password,
            index_name=self.vector_index_name,
            node_label=self.vector_node_label,
            text_node_properties=["name", "generic_name"],
            embedding_node_property=self.vector_embedding_property,
        )
        
        # Créer les retrievers à partir des vector stores
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        
        # Créer la chaîne RAG
        self.rag_chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm,
            chain_type="stuff",
            retriever=self.retriever
        )

    def embed_query(self, text):
        """
        Génère un embedding pour le texte fourni en utilisant SentenceTransformer.
        Cette méthode est utilisée par Neo4jVector.
        """
        if not text or text.strip() == "":
            return [0] * 384  # Dimension de all-MiniLM-L6-v2
        
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
    def embed_documents(self, documents):
        """
        Génère des embeddings pour une liste de documents.
        Cette méthode est utilisée par Neo4jVector.
        """
        embeddings = []
        for doc in documents:
            embedding = self.embed_query(doc)
            embeddings.append(embedding)
        return embeddings

    def execute_query(self, cypher, params=None):
        """Exécute une requête Cypher directement avec Neo4j."""
        with self.driver.session() as session:
            result = session.run(cypher, params or {})
            return [record.data() for record in result]

    def refresh_schema(self):
        """Rafraîchit le schéma du graphe depuis Neo4j."""
        self.graph.refresh_schema()
        print("Schéma du graphe rafraîchi.")
    
    def get_schema(self):
        """Obtient le schéma actuel du graphe."""
        return self.graph.schema

    def search_products(self, query_text, limit=5):
        """
        Recherche des produits similaires à une requête textuelle en utilisant 
        la recherche vectorielle.
        """
        # Générer l'embedding pour la requête
        query_embedding = self.embed_query(query_text)
        
        # Rechercher les produits similaires
        search_query = """
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
        
        results = self.execute_query(search_query, {
            "index_name": self.vector_index_name,
            "limit": limit,
            "embedding": query_embedding
        })
        
        return results

    def query(self, question):
        """Répond à une question en utilisant l'approche RAG ou Cypher."""
        # Question sur les marques bio
        if "marques" in question.lower() and ("biologique" in question.lower() or "bio" in question.lower()):
            try:
                query = """
                MATCH (p:Product)-[:HAS_BRAND]->(brand:Brand)
                MATCH (p)-[:HAS_LABEL]->(l:Label)
                WHERE toLower(l.name) CONTAINS 'bio' OR toLower(l.name) CONTAINS 'organic'
                WITH brand.name as Marque, count(p) as NombreProduits
                RETURN Marque, NombreProduits
                ORDER BY NombreProduits DESC
                LIMIT 10
                """
                results = self.execute_query(query)
                
                if results and len(results) > 0:
                    df = pd.DataFrame(results)
                    
                    # Formater la réponse
                    response = "Voici les marques qui proposent le plus de produits biologiques :\n\n"
                    for _, row in df.iterrows():
                        response += f"- {row['Marque']}: {row['NombreProduits']} produits bio\n"
                    
                    return response, df
                else:
                    pass  # Continue to other methods if no results
            except Exception as e:
                pass  # Continue to other methods if this fails
        
        # Vérifie s'il s'agit d'une question spécifique sur le nutriscore
        if "meilleur nutriscore" in question.lower() or "nutriscore a" in question.lower() or "bon nutriscore" in question.lower():
            try:
                query = """
                MATCH (p:Product)
                WHERE p.nutriscore_grade IN ['a', 'b']
                RETURN p.name as Produit, 
                       p.nutriscore_grade as Nutriscore, 
                       p.generic_name as Description
                ORDER BY p.nutriscore_grade
                LIMIT 10
                """
                results = self.execute_query(query)
                
                if results and len(results) > 0:
                    df = pd.DataFrame(results)
                    
                    # Formater la réponse
                    response = "Voici les produits avec le meilleur Nutri-Score (A et B) :\n\n"
                    for _, row in df.iterrows():
                        response += f"- {row['Produit']} (Nutriscore: {row['Nutriscore'].upper()})"
                        if row['Description'] and isinstance(row['Description'], str):
                            response += f"\n  Description: {row['Description']}"
                        response += "\n\n"
                    
                    return response, df
                else:
                    return "Je n'ai pas trouvé de produits avec un bon Nutri-Score dans la base de données.", None
            except Exception as e:
                pass  # Continue to other methods if this fails
        
        # Vérifie s'il s'agit d'une question sur les produits sans sucre
        if "sans sucre" in question.lower() or "no sugar" in question.lower():
            try:
                query = """
                MATCH (p:Product)
                WHERE NOT EXISTS {
                    MATCH (p)-[:CONTAINS]->(i:Ingredient)
                    WHERE toLower(i.name) CONTAINS 'sugar' 
                       OR toLower(i.name) CONTAINS 'sucre'
                }
                RETURN p.name as Produit, 
                       p.nutriscore_grade as Nutriscore, 
                       p.generic_name as Description
                LIMIT 10
                """
                results = self.execute_query(query)
                
                if results and len(results) > 0:
                    df = pd.DataFrame(results)
                    
                    # Formater la réponse
                    response = "Voici des produits qui ne contiennent pas de sucre selon leurs ingrédients :\n\n"
                    for _, row in df.iterrows():
                        response += f"- {row['Produit']}"
                        if row['Nutriscore'] and row['Nutriscore'] != 'unknown':
                            response += f" (Nutriscore: {row['Nutriscore'].upper()})"
                        if row['Description'] and isinstance(row['Description'], str):
                            response += f"\n  Description: {row['Description']}"
                        response += "\n\n"
                    
                    return response, df
                else:
                    pass  # Continue to other methods if no results
            except Exception as e:
                pass  # Continue to other methods if this fails
                
        # Essayer la génération de requête Cypher pour les questions directes
        if any(keyword in question.lower() for keyword in ["quels sont", "trouve", "cherche", "liste", "montre"]):
            try:
                cypher_response = self.cypher_chain.run(question)
                return cypher_response, None
            except Exception as e_cypher:
                # En cas d'échec, fallback sur RAG
                pass
        
        # Utiliser la chaîne RAG pour répondre à la question
        try:
            response = self.rag_chain(
                {"question": question},
                return_only_outputs=True
            )
            
            answer = response.get("answer", "")
            sources = response.get("sources", "")
            
            # Présenter la réponse de manière formatée
            if sources:
                footer = f"\n\nSources : {sources}"
            else:
                footer = ""
                
            return answer + footer, None
        except Exception as e:
            # Récupérer des produits avec la recherche vectorielle directe
            try:
                products = self.search_products(question, limit=5)
                if products:
                    results = "Voici les produits les plus pertinents pour votre question :\n\n"
                    for p in products:
                        results += f"- {p.get('name', 'Produit sans nom')}\n"
                        if p.get('generic_name'):
                            results += f"  Description: {p.get('generic_name')}\n"
                        if p.get('nutriscore'):
                            results += f"  Nutriscore: {p.get('nutriscore')}\n"
                        if p.get('brands') and len(p.get('brands')) > 0:
                            results += f"  Marques: {', '.join(p.get('brands'))}\n"
                        if p.get('categories') and len(p.get('categories')) > 0:
                            results += f"  Catégories: {', '.join(p.get('categories')[:3])}\n"
                        results += "\n"
                    return results, None
                else:
                    return f"Je n'ai pas trouvé de produits correspondant à votre question.", None
            except Exception as e2:
                return f"Je n'ai pas pu répondre à cette question. Veuillez essayer de reformuler votre demande.", None

    def get_product_recommendations(self, product_name, criteria="healthier"):
        """Recommande des produits similaires ou plus sains."""
        if criteria == "healthier":
            query = """
            MATCH (p1:Product)-[:HAS_CATEGORY]->(c:Category)<-[:HAS_CATEGORY]-(p2:Product)
            WHERE p1.name CONTAINS $product_name 
              AND p2.name <> p1.name 
              AND p1.nutriscore_grade > p2.nutriscore_grade
            WITH DISTINCT p1, p2
            RETURN p1.name as Produit_Original, 
                   p2.name as Recommandation, 
                   p1.nutriscore_grade as Nutriscore_Original, 
                   p2.nutriscore_grade as Nutriscore_Recommandé
            ORDER BY p2.nutriscore_grade
            LIMIT 5
            """
        else:  # similar
            query = """
            MATCH (p1:Product)-[:CONTAINS]->(i:Ingredient)<-[:CONTAINS]-(p2:Product)
            WHERE p1.name CONTAINS $product_name AND p2.name <> p1.name
            WITH p1, p2, count(i) AS common_ingredients
            WHERE common_ingredients > 2
            RETURN p1.name as Produit_Original, 
                   p2.name as Recommandation, 
                   common_ingredients as Ingrédients_Communs
            ORDER BY common_ingredients DESC
            LIMIT 5
            """
        
        results = self.execute_query(query, {"product_name": product_name})
        
        if isinstance(results, list) and len(results) > 0:
            return f"Recommandations pour '{product_name}':", pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé de recommandations pour '{product_name}'. Essayez un autre produit.", None

    def get_nutritional_analysis(self, product_name):
        """Obtient une analyse nutritionnelle pour un produit spécifique."""
        query = """
        MATCH (p:Product)-[r:HAS_NUTRIMENT]->(n:Nutriment)
        WHERE p.name CONTAINS $product_name
        RETURN p.name as Produit, 
               n.name as Nutriment, 
               r.value as Valeur, 
               r.unit as Unité
        """
        results = self.execute_query(query, {"product_name": product_name})
        
        if isinstance(results, list) and len(results) > 0:
            return f"Informations nutritionnelles pour '{product_name}':", pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé d'informations nutritionnelles pour '{product_name}'.", None

    def get_dietary_info(self, diet_type="vegan"):
        """Obtient des produits adaptés à un régime alimentaire spécifique."""
        if diet_type.lower() in ["végétalien", "vegan"]:
            query = """
            MATCH (p:Product)-[:HAS_LABEL]->(l:Label)
            WHERE toLower(l.name) CONTAINS 'vegan' OR toLower(l.name) CONTAINS 'végétalien'
            RETURN p.name as Produit, 
                   p.nutriscore_grade as Nutriscore, 
                   p.quantity as Quantité
            LIMIT 10
            """
        elif diet_type.lower() in ["végétarien", "vegetarian"]:
            query = """
            MATCH (p:Product)-[:HAS_LABEL]->(l:Label)
            WHERE toLower(l.name) CONTAINS 'vegetarian' OR toLower(l.name) CONTAINS 'végétarien'
            RETURN p.name as Produit, 
                   p.nutriscore_grade as Nutriscore, 
                   p.quantity as Quantité
            LIMIT 10
            """
        elif diet_type.lower() == "sans gluten":
            query = """
            MATCH (p:Product)
            WHERE NOT (p)-[:CONTAINS_ALLERGEN]->(:Allergen {name: 'gluten'})
            RETURN p.name as Produit, 
                   p.nutriscore_grade as Nutriscore, 
                   p.quantity as Quantité
            LIMIT 10
            """
        elif diet_type.lower() in ["biologique", "bio", "organic"]:
            query = """
            MATCH (p:Product)-[:HAS_LABEL]->(l:Label)
            WHERE toLower(l.name) CONTAINS 'organic' OR toLower(l.name) CONTAINS 'bio'
            RETURN p.name as Produit, 
                   p.nutriscore_grade as Nutriscore, 
                   l.name as Label
            LIMIT 10
            """
        else:
            return f"Type de régime non pris en charge: {diet_type}", None
        
        results = self.execute_query(query)
        
        if isinstance(results, list) and len(results) > 0:
            return f"Produits adaptés au régime {diet_type}:", pd.DataFrame(results)
        else:
            return f"Je n'ai pas trouvé de produits adaptés au régime {diet_type}.", None

    def close(self):
        """Ferme les connexions à la base de données."""
        if hasattr(self, 'driver'):
            self.driver.close()
        print("Connexions fermées.")

# Interface de conversation simple
def main():
    agent = OpenFoodFactsAgent()
    
    print("Agent Conversationnel OpenFoodFacts avec RAG initialisé.")
    print("Schéma du graphe chargé.")
    print("\nCommandes spéciales:")
    print("- 'search: [terme]' pour rechercher des produits")
    print("- 'nutri: [produit]' pour obtenir des informations nutritionnelles")
    print("- 'rec: [produit]' pour obtenir des recommandations plus saines")
    print("- 'diet: [régime]' pour obtenir des produits adaptés à un régime")
    print("- 'exit' pour quitter")
    
    try:
        while True:
            user_input = input("\nVotre question: ")
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Au revoir!")
                break
            
            # Traitement des commandes spéciales
            if user_input.lower().startswith("search:"):
                search_term = user_input[7:].strip()
                products = agent.search_products(search_term)
                print(f"\nRésultats de recherche pour '{search_term}':")
                
                if products:
                    for p in products:
                        print(f"\n- {p['name']}")
                        if p['generic_name']:
                            print(f"  Description: {p['generic_name']}")
                        print(f"  Nutriscore: {p['nutriscore']}")
                        if p['brands']:
                            print(f"  Marques: {', '.join(p['brands'])}")
                        if p['categories']:
                            print(f"  Catégories: {', '.join(p['categories'][:3])}")
                        print(f"  Score de similarité: {p['score']:.2f}")
                else:
                    print("Aucun produit trouvé.")
                continue
                
            elif user_input.lower().startswith("nutri:"):
                product_name = user_input[6:].strip()
                response, data = agent.get_nutritional_analysis(product_name)
                print("\n" + response)
                if data is not None:
                    print("\n" + data.to_string(index=False))
                continue
                
            elif user_input.lower().startswith("rec:"):
                product_name = user_input[4:].strip()
                response, data = agent.get_product_recommendations(product_name)
                print("\n" + response)
                if data is not None:
                    print("\n" + data.to_string(index=False))
                continue
                
            elif user_input.lower().startswith("diet:"):
                diet_type = user_input[5:].strip()
                response, data = agent.get_dietary_info(diet_type)
                print("\n" + response)
                if data is not None:
                    print("\n" + data.to_string(index=False))
                continue
            
            # Traitement des questions normales
            response, data = agent.query(user_input)
            
            # Afficher la réponse avec formatage
            print("\nRéponse:", textwrap.fill(response, 100))
            
            # Afficher les données si disponibles
            if data is not None and isinstance(data, pd.DataFrame):
                print("\nDonnées:")
                print(data.to_string(index=False))
    
    finally:
        # Fermer la connexion à la base de données
        agent.close()

if __name__ == "__main__":
    main()