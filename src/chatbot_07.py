# Bibliothèque standard
from pathlib import Path
import time
import logging
import json
from typing import List, Dict, Tuple, Protocol, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Bibliothèques tierces
import requests
import pandas as pd
import duckdb
from crewai import Agent, Task, Crew, Process
# import openai
# from anthropic import Anthropic
# from langchain.chat_models import ChatOpenAI, ChatAnthropic, ChatOllama
# from langchain.schema import HumanMessage, SystemMessage

# Configuration de l'environnement
DATA_DIR = Path("../data")
PARQUET_PATH = DATA_DIR / "food.parquet"
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"
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


class BaseLLM(ABC):
    """Classe de base abstraite pour les LLMs."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Méthode abstraite pour la génération de texte."""
        pass


class OllamaLLM(BaseLLM):
    """Implémentation pour Ollama API."""

    def __init__(
        self, model: str = "mistral:7b", base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
        )
        return response.json()["response"]


class OpenAILLM(BaseLLM):
    """Implémentation pour OpenAI API."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI()
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content


class AnthropicLLM(BaseLLM):
    """Implémentation pour Anthropic API."""

    def __init__(self, model: str = "claude-3-opus-20240229"):
        self.client = Anthropic()
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model, messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


class LangChainLLM(BaseLLM):
    """Implémentation pour LangChain."""

    def __init__(self, model_name: str, provider: str = "ollama"):
        if provider == "ollama":
            self.model = ChatOllama(model=model_name)
        elif provider == "openai":
            self.model = ChatOpenAI(model=model_name)
        elif provider == "anthropic":
            self.model = ChatAnthropic(model=model_name)
        else:
            raise ValueError(f"Provider {provider} non supporté")

    def generate(self, prompt: str) -> str:
        messages = [
            SystemMessage(content="Tu es un assistant expert en SQL."),
            HumanMessage(content=prompt),
        ]
        response = self.model.invoke(messages)
        return response.content


def create_llm(provider: str, **kwargs) -> BaseLLM:
    """Factory pour créer l'instance LLM appropriée."""
    providers = {
        "ollama": OllamaLLM,
        "openai": OpenAILLM,
        "anthropic": AnthropicLLM,
        "langchain": LangChainLLM,
    }

    if provider not in providers:
        raise ValueError(f"Provider {provider} non supporté")

    # Filtrer les kwargs selon le provider
    if provider == "langchain":
        # LangChain a besoin de model_name et provider
        required_kwargs = {
            "model_name": kwargs.get("model"),
            "provider": kwargs.get("model_provider"),
        }
    else:
        # Les autres providers n'ont besoin que du model
        required_kwargs = {"model": kwargs.get("model")}

    return providers[provider](**required_kwargs)





@dataclass
class QueryContext:
    """Contexte partagé entre les agents"""
    query: str
    sql: Optional[str] = None
    results: Optional[pd.DataFrame] = None
    conversation_history: Optional[List[Dict[str, str]]] = None
    schema: Optional[str] = None
    table_name: Optional[str] = None

class StrategyPlannerAgent(Agent):
    """Agent qui planifie la stratégie de recherche"""
    
    def __init__(self, llm: BaseLLM):
        # Définir l'outil avec les attributs requis
        planning_tool = {
            "name": "plan_strategy",
            "description": "Planifie la stratégie de recherche",
            "func": self.plan_strategy
        }
        
        super().__init__(
            name="Strategy Planner",
            role="Expert en planification de recherche",
            goal="Planifier la meilleure stratégie de recherche",
            backstory="Expert en analyse de requêtes et planification de recherche",
            verbose=True,
            allow_delegation=False,
            tools=[planning_tool]
        )
        self.llm = llm

    async def plan_strategy(self, context: QueryContext) -> Dict:
        """Détermine la meilleure stratégie pour répondre à la requête"""
        prompt = f"""
        Analayse cette requête et détermine la meilleure stratégie.
        
        Requête: {context.query}
        Schéma: {context.schema}
        
        Retourne un plan au format JSON avec:
        1. Le type de recherche requis (sql, semantic, hybrid)
        2. Les colonnes pertinentes
        3. Les conditions de filtrage nécessaires
        4. L'ordre de tri souhaité
        """
        
        response = await self.llm.generate(prompt)
        return json.loads(response)

class SQLGeneratorAgent(Agent):
    """Agent qui convertit une requête en SQL"""
    
    def __init__(self, llm: BaseLLM):
        sql_tool = {
            "name": "generate_sql",
            "description": "Génère une requête SQL optimale",
            "func": self.generate_sql
        }

        super().__init__(
            name="SQL Generator",
            role="Expert SQL",
            goal="Générer des requêtes SQL optimales",
            backstory="Expert en SQL et bases de données",
            verbose=True,
            allow_delegation=False,
            tools=[self.generate_sql]
        )
        self.llm = llm
        
    async def generate_sql(self, context: QueryContext, strategy: Dict) -> str:
        """Génère une requête SQL basée sur la stratégie"""
        prompt = f"""
        Génère une requête SQL optimale.
        
        Question: {context.query}
        Table: {context.table_name}
        Stratégie: {json.dumps(strategy, indent=2)}
        
        Règles:
        1. Utilise uniquement les colonnes disponibles
        2. Optimise pour la performance
        3. Ajoute LIMIT si nécessaire
        """
        
        return await self.llm.generate(prompt).strip().rstrip(';')

class SQLExecutorAgent(Agent):
    """Agent qui exécute les requêtes SQL"""
    
    def __init__(self, db_path: Path):
        # Initialiser la connexion avant super().__init__
        self._db_path = db_path
        self._conn = duckdb.connect(str(db_path))
        
        executor_tool = {
            "name": "execute_sql",
            "description": "Exécute une requête SQL",
            "func": self.execute_sql
        }

        super().__init__(
            name="SQL Executor",
            role="Expert en exécution SQL",
            goal="Exécuter les requêtes SQL de manière optimale",
            backstory="Expert en optimisation de requêtes SQL",
            verbose=True,
            allow_delegation=False,
            tools=[self.execute_sql]
        )
        
    async def execute_sql(self, sql: str) -> pd.DataFrame:
        """Exécute la requête SQL et retourne les résultats"""
        try:
            logger.info(f"Exécution SQL: {sql}")
            return self._conn.execute(sql).fetchdf()
        except Exception as e:
            logger.error(f"Erreur SQL: {str(e)}")
            raise

class ResponseGeneratorAgent(Agent):
    """Agent qui génère les réponses en langage naturel"""
    
    def __init__(self, llm: BaseLLM):
        response_tool = {
            "name": "generate_response",
            "description": "Génère une réponse en langage naturel",
            "func": self.generate_response
        }

        super().__init__(
            name="Response Generator",
            role="Expert en communication",
            goal="Générer des réponses claires et naturelles",
            backstory="Expert en communication et analyse de données",
            verbose=True,
            allow_delegation=False,
            tools=[self.generate_response]
        )
        self.llm = llm
        
    async def generate_response(self, context: QueryContext) -> str:
        """Génère une réponse basée sur les résultats"""
        prompt = f"""
        Génère une réponse claire et naturelle.
        
        Question: {context.query}
        Résultats: {context.results.to_string()}
        
        Instructions:
        1. Réponds directement à la question
        2. Utilise les données pertinentes
        3. Reste concis et précis
        """
        
        return await self.llm.generate(prompt)


class FoodDatabaseBot:
    """Interface utilisateur pour la base de données alimentaire"""
    
    def __init__(self, db_path: Path, llm: BaseLLM):
        if not db_path.exists():
            raise FileNotFoundError(f"Base de données non trouvée: {db_path}")
            
        # Initialisation des agents
        self.planner = StrategyPlannerAgent(llm)
        self.sql_generator = SQLGeneratorAgent(llm)
        self.executor = SQLExecutorAgent(db_path)
        self.response_generator = ResponseGeneratorAgent(llm)
        
        # Configuration du crew
        self.crew = Crew(
            agents=[self.planner, self.sql_generator, 
                   self.executor, self.response_generator],
            process=Process.sequential
        )
        
        # Autres initialisations
        self.table_name = self._get_table_name(db_path)
        self.schema = self._get_schema(db_path)
        self.conversation_history: List[Dict[str, str]] = []
        
    def _get_table_name(self, db_path: Path) -> str:
        """Récupère le nom de la première table"""
        conn = duckdb.connect(str(db_path))
        tables = conn.execute("SHOW TABLES").fetchdf()
        conn.close()
        return tables.iloc[0]["name"]
        
    def _get_schema(self, db_path: Path) -> str:
        """Récupère le schéma de la table"""
        conn = duckdb.connect(str(db_path))
        columns = conn.execute(f"DESCRIBE {self.table_name}").fetchdf()
        conn.close()
        
        schema = []
        for _, row in columns.iterrows():
            schema.append(f"{row['column_name']} ({row['column_type']})")
        return "\n".join(schema)
    
    async def process_query(self, query: str) -> str:
        """Traite une requête utilisateur"""
        try:
            # Création du contexte
            context = QueryContext(
                query=query,
                conversation_history=self.conversation_history,
                schema=self.schema,
                table_name=self.table_name
            )
            
            # Création des tâches
            tasks = [
                Task(
                    description="Planifier la stratégie de recherche",
                    agent=self.planner,
                    expected_output="Stratégie de recherche sous forme de dictionnaire",
                    context={"context": context}
                ),
                Task(
                    description="Générer la requête SQL",
                    agent=self.sql_generator,
                    expected_output="Requête SQL optimisée",
                    context={"context": context}
                ),
                Task(
                    description="Exécuter la requête SQL",
                    agent=self.executor,
                    expected_output="Résultats de la requête",
                    context={"context": context}
                ),
                Task(
                    description="Générer la réponse",
                    agent=self.response_generator,
                    expected_output="Réponse en langage naturel",
                    context={"context": context}
                )
            ]
            
            # Exécution des tâches
            result = self.crew.kickoff(tasks)
            
            # Mise à jour de l'historique
            self.conversation_history.append({
                "role": "user",
                "content": query
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur de traitement: {str(e)}")
            return f"Désolé, une erreur s'est produite: {str(e)}"

async def chatbot():
    """Interface en ligne de commande du chatbot"""
    config = {
        "provider": "ollama",
        "model": "mistral:7b",
        "model_provider": "ollama"
    }

    try:
        llm = create_llm(**config)
        bot = FoodDatabaseBot(FILTERED_DB_PATH, llm)

        print("Bienvenue dans le chatbot Open Food Facts!")
        print(f"Utilisation du LLM: {config['provider']} - {config['model']}")
        print("Tapez 'exit' pour quitter.")

        while True:
            user_input = input("\nVous: ").strip()

            if user_input.lower() == "exit":
                break

            response = await bot.process_query(user_input)
            print(f"\nAssistant: {response}")

    except Exception as e:
        print(f"Erreur d'initialisation: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    # Création de la boucle d'événements asyncio
    loop = asyncio.get_event_loop()
    try:
        # Exécution du chatbot dans la boucle
        loop.run_until_complete(chatbot())
    finally:
        # Fermeture propre de la boucle
        loop.close()