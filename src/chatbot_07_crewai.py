# Bibliothèque standard
from pathlib import Path
import logging
import json
from typing import List, Dict

# Bibliothèques tierces
import pandas as pd
import duckdb
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool

# Configuration de l'environnement
DATA_DIR = Path("../data")
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"
DATA_DICT_PATH = DATA_DIR / "data_dictionary.json"


# Configuration du logging avec couleurs
class ColorFormatter(logging.Formatter):
    COLORS = {
        "INFO": "\033[92m",  # Vert
        "DEBUG": "\033[94m",  # Bleu
        "WARNING": "\033[93m",  # Jaune
        "ERROR": "\033[91m",  # Rouge
        "ENDC": "\033[0m",  # Reset
    }

    def format(self, record):
        levelname = record.levelname  # Sauvegarde le niveau original
        if levelname in self.COLORS:
            color = self.COLORS[levelname]
            record.msg = f"{color}{record.msg}{self.COLORS['ENDC']}"
        return super().format(record)


# Configuration du logger
logger = logging.getLogger(__name__)
if not logger.handlers:  # Évite les handlers dupliqués
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class SQLExecutionTool(BaseTool):
    name: str = "SQL Execution Tool"
    description: str = "Execute SQL queries on the database"
    db_path: Path

    def _run(self, sql: str) -> pd.DataFrame:
        try:
            logger.info(f"Executing SQL: {sql}")
            with duckdb.connect(str(self.db_path)) as conn:
                results = conn.execute(sql).fetchdf()
            return results
        except duckdb.Error as e:
            logger.error(f"SQL Execution Error: {str(e)}")
            return pd.DataFrame()

class FoodDatabaseBot:
    """Interface utilisateur pour la base de données alimentaire"""
    
    def __init__(self, db_path: Path, data_dict_path: Path, llm: LLM):
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        if not data_dict_path.exists():
            raise FileNotFoundError(f"Data dictionary not found: {data_dict_path}")

        # Chargement du dictionnaire de données
        with open(data_dict_path, 'r', encoding='utf-8') as f:
            self.data_dict = json.load(f)
        
        # Création des outils
        self.sql_tool = SQLExecutionTool(db_path=db_path)
        
        # Récupération du schéma simplifié
        conn = duckdb.connect(str(db_path))
        tables = conn.execute("SHOW TABLES").fetchdf()
        self.table_name = tables.iloc[0]["name"]
        
        # Création d'un schéma plus simple et plus clair pour le LLM
        self.schema = self._create_simplified_schema(conn)
        conn.close()
        
        # Exemples de requêtes SQL qui fonctionnent
        self.sql_examples = """
        Exemples de requêtes SQL valides :
        1. Compter tous les produits :
           SELECT COUNT(*) as total FROM products
        
        2. Obtenir les produits par marque :
           SELECT brands, COUNT(*) as count 
           FROM products 
           WHERE brands IS NOT NULL 
           GROUP BY brands 
           ORDER BY count DESC 
           LIMIT 5
        
        3. Rechercher par mot-clé dans le nom du produit :
           SELECT p.* 
           FROM products p, unnest(p.product_name) as n(lang, text)
           WHERE LOWER(n.text) LIKE '%chocolat%'
        """
        
        # Description de la structure pour le LLM
        self.structure_info = """
        Notes importantes sur la structure de la base de données :
        1. Les champs comme 'product_name' sont des tableaux de structures contenant 'lang' et 'text'
        2. Pour accéder au texte d'un champ structuré, utilisez : unnest(field_name) as alias(lang, text)
        3. Les champs se terminant par '_tags' sont des tableaux de chaînes
        4. Pour les champs numériques, vérifiez toujours IS NOT NULL
        """
        
        self.classifier = Agent(
            role="Query Classifier",
            goal="Classify user input correctly",
            backstory="""Expert in classifying user queries into three categories:
            - greeting: for greetings and first contact
            - sql: for questions requiring database queries
            - conversation: for general questions
            You MUST output ONLY ONE of these three words.""",
            tools=[],
            verbose=True,
            llm=llm
        )
        
        self.planner = Agent(
            role="Query Planner",
            goal="Plan optimal database queries",
            backstory="""Expert in analyzing natural language queries and planning SQL search strategies.
            You have deep understanding of DuckDB and structured data.""",
            tools=[self.sql_tool],
            verbose=True,
            llm=llm
        )
        
        self.sql_generator = Agent(
            role="SQL Generator",
            goal="Generate optimal SQL queries",
            backstory="""Expert in SQL and DuckDB optimization.
            You understand how to query complex structured data and arrays.""",
            tools=[self.sql_tool],
            verbose=True,
            llm=llm
        )
        
        self.response_generator = Agent(
            role="Response Generator",
            goal="Generate clear and natural responses",
            backstory="""Expert in data interpretation and communication.
            You provide helpful and accurate responses based on query results.""",
            tools=[self.sql_tool],
            verbose=True,
            llm=llm
        )
        
        self.conversation_history: List[Dict[str, str]] = []

    def get_total_products(self) -> int:
        """Récupère le nombre total de produits"""
        try:
            result = self.sql_tool._run("SELECT COUNT(*) as total FROM products")
            return result['total'].iloc[0]
        except Exception as e:
            logger.error(f"Error getting total products: {str(e)}")
            return 0

    def _create_simplified_schema(self, conn) -> str:
        """Crée une représentation simplifiée du schéma pour le LLM"""
        columns = conn.execute(f"DESCRIBE {self.table_name}").fetchdf()
        schema_parts = []
        
        for _, row in columns.iterrows():
            col_name = row['column_name']
            col_type = row['column_type']
            
            # Ajouter la description du dictionnaire de données si disponible
            if col_name in self.data_dict:
                desc = self.data_dict[col_name]['description']
                schema_parts.append(f"{col_name} ({col_type}): {desc}")
            else:
                schema_parts.append(f"{col_name} ({col_type})")
        
        return "\n".join(schema_parts)

    def process_query(self, query: str) -> str:
        """Traite une requête utilisateur"""
        try:
            # Classification de la requête avec description améliorée
            classification_task = Task(
                description=f"""
                Classify this query into ONE of these categories:
                - greeting: ONLY for greetings, salutations, and first contact
                Examples: "bonjour", "salut", "hello", "bonsoir"
                
                - sql: for ANY questions about the data or requests to display/show/list/find/search/count products or information
                Examples: 
                - "affiche la liste des produits"
                - "montre les produits"
                - "cherche les produits avec du chocolat"
                - "trouve les marques"
                - "combien y a-t-il de produits"
                - "liste les ingrédients"
                - "quels sont les produits"
                
                - conversation: ONLY for general questions about the bot's capabilities or non-data questions
                Examples:
                - "que peux-tu faire"
                - "comment ça marche"
                - "qui es-tu"
                - "aide-moi"
                
                Query: {query}
                
                IMPORTANT: 
                1. Output ONLY ONE word from the categories above
                2. If the query asks to display/show/find/list ANY information, it is an SQL query
                3. Only use 'conversation' if the query is really about the bot itself
                4. When in doubt between sql and conversation, choose sql
                """,
                expected_output="One word classification (greeting/sql/conversation)",
                agent=self.classifier
            )
            
            classification_crew = Crew(
                agents=[self.classifier],
                tasks=[classification_task],
                process=Process.sequential,
                verbose=True
            )
            
            query_type = str(classification_crew.kickoff()).strip().lower()

            # Traitement selon la classification
            if query_type == "greeting":
                total = self.get_total_products()
                return f"Bonjour ! Je suis votre assistant pour explorer la base de données des produits alimentaires. Elle contient {total} produits. Comment puis-je vous aider ?"
                
            elif query_type == "sql":
                # Création des tâches SQL dans ce scope
                sql_tasks = []
                sql_tasks.append(Task(
                    description=f"""
                    Analyze this query and plan the search strategy:
                    Query: {query}
                    Schema: {self.schema}
                    Structure Information: {self.structure_info}
                    SQL Examples: {self.sql_examples}
                    Table: {self.table_name}
                    """,
                    expected_output="Search strategy JSON with required columns and conditions",
                    agent=self.planner
                ))
                
                sql_tasks.append(Task(
                    description="Generate an optimized SQL query based on the strategy",
                    expected_output="SQL query string",
                    agent=self.sql_generator,
                    context=[sql_tasks[0]]  # Reference to planning_task
                ))
                
                sql_tasks.append(Task(
                    description="Generate a natural language response based on the query results",
                    expected_output="Natural language response",
                    agent=self.response_generator,
                    context=[sql_tasks[0], sql_tasks[1]]  # References to both previous tasks
                ))
                
                sql_crew = Crew(
                    agents=[self.planner, self.sql_generator, self.response_generator],
                    tasks=sql_tasks,
                    process=Process.sequential,
                    verbose=True
                )
                
                return str(sql_crew.kickoff())
                
            else:  # conversation
                return "Je suis là pour répondre à vos questions sur les produits alimentaires. Posez-moi des questions sur les ingrédients, les marques, la nutrition, etc."
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"Sorry, an error occurred: {str(e)}"

def chatbot():
    """Interface en ligne de commande du chatbot"""
    try:
        print("Initializing chatbot...")

        # Création centralisée du LLM
        # Don't forget to start the LLM server with the chosen model
        # Example: ollama pull deepseek-r1:1.5b
        llm = LLM(model="ollama/mistral:7b", base_url="http://localhost:11434")
        # llm = LLM(model="ollama/qwen:1.8b", base_url="http://localhost:11434")
        # llm = LLM(model="ollama/deepseek-r1:1.5b", base_url="http://localhost:11434")
        # llm = LLM(model="ollama/8b-instruct-q4_0", base_url="http://localhost:11434")

        bot = FoodDatabaseBot(FILTERED_DB_PATH, DATA_DICT_PATH, llm)

        print("\nWelcome to the Food Database Chatbot!")
        print("Using Ollama with mistral:7b model")
        print("Type 'exit' to quit.\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() == "exit":
                    print("Goodbye!")
                    break

                response = bot.process_query(user_input)
                print(f"\nAssistant: {response}\n")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError processing query: {str(e)}")
                print("Please try again.")

    except Exception as e:
        print(f"Initialization error: {str(e)}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    chatbot()