import os
from pathlib import Path
import time
import json
import requests
import pandas as pd
import duckdb
import sqlglot
from typing import List, Dict, Tuple, Optional, Protocol
from abc import ABC, abstractmethod
import openai
# from anthropic import Anthropic
# from langchain.chat_models import ChatOpenAI, ChatAnthropic, ChatOllama
# from langchain.schema import HumanMessage, SystemMessage

# Configuration
DATA_DIR = Path("../data")
PARQUET_PATH = DATA_DIR / "food.parquet"
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

"""
from langchain_openai import ChatOpenAI 
from langchain_community.llms import Ollama
models = {
    "chatgpt3.5": ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=st.secrets["OPENAI_API_KEY"]),
    "chatgpt-4o": ChatOpenAI(model="gpt-4o", temperature=0, api_key=st.secrets["OPENAI_API_KEY"]),
    "duckdb-nsql": Ollama(model="duckdb-nsql", temperature=0),
    "sqlcoder": Ollama(model="mannix/defog-llama3-sqlcoder-8b", temperature=0),
    "codegemma":  Ollama(model="codegemma", temperature=0),
    "llama3": Ollama(model="llama3", temperature=0),
}
"""

# Schéma de la base de données
DATABASE_SCHEMA = """
La base de données contient une table appelée `food_facts` avec les colonnes suivantes :
- `product_name` (texte) : Le nom du produit
- `brand` (texte) : La marque du produit
- `quantity` (texte) : La quantité du produit
- `nutrients` (texte) : Les nutriments présents
- `allergens` (texte) : Les allergènes présents
- `additives` (texte) : Les additifs présents
- `nutri_score` (texte) : Le Nutri-Score du produit
- `eco_score` (texte) : L'Eco-Score du produit
- `origin_country` (texte) : Le pays d'origine
- `stores` (texte) : Les magasins disponibles
"""

class LLMInterface(Protocol):
    """Protocol définissant l'interface commune pour tous les LLMs."""
    def generate(self, prompt: str) -> str:
        """Génère une réponse basée sur le prompt."""
        pass

class BaseLLM(ABC):
    """Classe de base abstraite pour les LLMs."""
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Méthode abstraite pour la génération de texte."""
        pass

class OllamaLLM(BaseLLM):
    """Implémentation pour Ollama API."""
    def __init__(self, model: str = "mistral:7b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        
    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"]

class OpenAILLM(BaseLLM):
    """Implémentation pour OpenAI API."""
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI()
        self.model = model
        
    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

class AnthropicLLM(BaseLLM):
    """Implémentation pour Anthropic API."""
    def __init__(self, model: str = "claude-3-opus-20240229"):
        self.client = Anthropic()
        self.model = model
        
    def generate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": prompt
            }]
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
            HumanMessage(content=prompt)
        ]
        response = self.model.invoke(messages)
        return response.content

def create_llm(provider: str, **kwargs) -> BaseLLM:
    """Factory pour créer l'instance LLM appropriée."""
    providers = {
        "ollama": OllamaLLM,
        "openai": OpenAILLM,
        "anthropic": AnthropicLLM,
        "langchain": LangChainLLM
    }
    
    if provider not in providers:
        raise ValueError(f"Provider {provider} non supporté")
        
    # Filtrer les kwargs selon le provider
    if provider == "langchain":
        # LangChain a besoin de model_name et provider
        required_kwargs = {
            "model_name": kwargs.get("model"),
            "provider": kwargs.get("model_provider")
        }
    else:
        # Les autres providers n'ont besoin que du model
        required_kwargs = {
            "model": kwargs.get("model")
        }
        
    return providers[provider](**required_kwargs)

class FoodDatabaseBot:
    def __init__(self, db_path: Path, llm: BaseLLM):
        """
        Initialise le bot avec une connexion à la base de données et un LLM.
        Vérifie la structure de la base de données au démarrage.
        """
        if not db_path.exists():
            raise FileNotFoundError(f"La base de données {db_path} n'existe pas.")
    
        print(f"Utilisation de la base de données: {db_path}.")
        self.conn = duckdb.connect(str(db_path))
        self.llm = llm
        self.conversation_history: List[Dict[str, str]] = []
        
        # Vérifie la structure de la base de données
        self.table_name = self._get_table_name()
        self.schema = self._get_schema()

    def _get_table_name(self) -> str:
        """Récupère le nom de la première table de la base de données."""
        tables = self.conn.execute("SHOW TABLES").fetchdf()
        if tables.empty:
            raise ValueError("La base de données ne contient aucune table.")

        print(f"Tables disponibles: {tables['name'].tolist()}")
        print(f"Utilisation de la première table: {tables.iloc[0]['name']}")
        return tables.iloc[0]['name']

    def _get_schema(self) -> str:
        """Récupère le schéma réel de la table."""
        columns = self.conn.execute(f"DESCRIBE {self.table_name}").fetchdf()
        
        schema = f"""
        La base de données contient une table appelée `{self.table_name}` avec les colonnes suivantes :
        """
        for _, row in columns.iterrows():
            schema += f"\n- `{row['column_name']}` ({row['column_type']}) : Colonne de la table"
            
        return schema

    def determine_query_type(self, user_input: str) -> Tuple[str, str]:
        """
        Détermine si l'entrée nécessite une requête SQL ou une simple réponse conversationnelle.
        Retourne un tuple (type, explication)
        """
        prompt = f"""
        Tu es un assistant qui analyse les questions pour déterminer si elles nécessitent d'accéder à une base de données.

        Contexte: Tu as accès à une base de données de produits alimentaires avec {self.schema}

        Question de l'utilisateur: {user_input}

        Détermine si cette question :
        1. Nécessite une requête SQL pour accéder aux données ("sql")
        2. Est une simple question conversationnelle ("conversation")
        3. Est une salutation ou premier contact ("greeting")

        Réponds exactement avec un seul mot parmi : "sql", "conversation", ou "greeting"
        """

        response = self.llm.generate(prompt).strip().lower()
        
        # Normalisation de la réponse
        if "sql" in response or "database" in response or "query" in response:
            return "sql", "Nécessite une requête SQL"
        elif "greet" in response or "hello" in response or "hi" in response:
            return "greeting", "Salutation"
        else:
            return "conversation", "Question conversationnelle"

    def handle_conversation(self, user_input: str) -> str:
        """Gère une question conversationnelle sans accès à la base de données."""
        prompt = f"""
        Tu es un assistant expert des produits alimentaires.
        
        Historique récent de la conversation:
        {self._format_history()}
        
        Question: {user_input}
        
        Réponds de manière naturelle et utile, sans accéder à la base de données.
        """
        
        response = self.llm.generate(prompt)
        return response

    def handle_greeting(self) -> str:
        """Gère une salutation avec un comptage rapide des produits."""
        try:
            result = self.conn.execute(f"SELECT COUNT(*) as total FROM {self.table_name}").fetchdf()
            total = result.iloc[0]['total']
            return f"Bonjour ! Je suis votre assistant pour explorer la base de données des produits alimentaires. Elle contient {total} produits. Comment puis-je vous aider ?"
        except Exception as e:
            return "Bonjour ! Je suis votre assistant pour explorer la base de données des produits alimentaires. Comment puis-je vous aider ?"

    def _format_history(self) -> str:
        """Formate l'historique récent de la conversation."""
        return "\n".join(
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history[-3:]
        )

    def text_to_sql(self, question: str) -> str:
        """Convertit une question en langage naturel en requête SQL."""
        conversation_context = "\n".join(
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history[-3:]
        )
        
        prompt = f"""
        Tu es un assistant expert en SQL qui convertit des questions en requêtes SQL.
        
        Contexte de la base de données:
        {self.schema}
        
        Historique récent:
        {conversation_context}
        
        Question: {question}
        
        Génère uniquement une requête SQL valide qui répond à cette question.
        Important:
        - La table s'appelle `{self.table_name}`
        - Assure-toi que la requête est compatible avec DuckDB
        - Utilise uniquement les colonnes listées ci-dessus
        - Pour une première interaction ou un "bonjour", retourne une requête simple qui compte le nombre total de produits
        - Ne met pas de commentaires ou d'explications
        
        Requête SQL:
        """
        
        sql_query = self.llm.generate(prompt).strip()
        return sql_query
    
    def validate_sql(self, query: str) -> Tuple[bool, str]:
        """Valide la requête SQL avec sqlglot."""
        try:
            # Tente de parser et reformater la requête
            validated_query = sqlglot.transpile(query, read='sqlite', write='duckdb')[0]
            return True, validated_query
        except Exception as e:
            return False, str(e)
    
    def execute_query(self, sql: str) -> Tuple[bool, pd.DataFrame | str]:
        """Exécute la requête SQL sur DuckDB."""
        try:
            result = self.conn.execute(sql).fetchdf()
            return True, result
        except Exception as e:
            return False, str(e)
    
    def generate_response(self, question: str, sql: str, query_result: pd.DataFrame) -> str:
        """Génère une réponse en langage naturel basée sur les résultats."""
        prompt = f"""
        Question originale: {question}
        
        Requête SQL exécutée: {sql}
        
        Résultats de la requête:
        {query_result.to_string()}
        
        Génère une réponse claire et naturelle qui:
        1. Résume les résultats de manière compréhensible
        2. Met en évidence les informations importantes
        3. Utilise un langage simple et direct
        """
        
        return self.llm.generate(prompt)
    
    def process_user_input(self, user_input: str) -> str:
        """Traite l'entrée utilisateur avec le bon type de réponse."""
        try:
            # Détermine le type de question
            query_type, _ = self.determine_query_type(user_input)
            
            # Traite selon le type
            if query_type == "greeting":
                response = self.handle_greeting()
            elif query_type == "conversation":
                response = self.handle_conversation(user_input)
            else:  # sql
                response = self.handle_sql_query(user_input)
            
            # Met à jour l'historique
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            return f"Désolé, une erreur s'est produite : {str(e)}"

    def handle_sql_query(self, user_input: str) -> str:
        """Gère une question nécessitant une requête SQL."""
        # Convertit la question en SQL
        sql_query = self.text_to_sql(user_input)
        
        # Valide la requête SQL
        is_valid, validated_sql = self.validate_sql(sql_query)
        if not is_valid:
            return f"Désolé, je n'ai pas pu générer une requête SQL valide. Erreur: {validated_sql}"
        
        # Exécute la requête
        success, result = self.execute_query(validated_sql)
        if not success:
            return f"Désolé, je n'ai pas pu exécuter la requête. Erreur: {result}"
        
        # Génère la réponse
        return self.generate_response(user_input, validated_sql, result)


def create_test_set() -> List[Dict]:
    """Crée un ensemble de test avec des questions et réponses attendues."""
    return [
        {
            "question": "Quels sont les produits avec un Nutri-score A ?",
            "sql": "SELECT product_name, brand, nutri_score FROM food_facts WHERE nutri_score = 'A' LIMIT 5",
            "expected_response_contains": ["produits", "Nutri-score A"]
        },
        {
            "question": "Combien y a-t-il de produits sans allergènes ?",
            "sql": "SELECT COUNT(*) as count FROM food_facts WHERE allergens = 'None' OR allergens IS NULL",
            "expected_response_contains": ["produits", "sans allergènes"]
        }
        # Ajoutez d'autres cas de test ici
    ]

def evaluate_system(bot: FoodDatabaseBot, test_set: List[Dict]) -> Dict:
    """Évalue les performances du système sur l'ensemble de test."""
    results = {
        "total_tests": len(test_set),
        "successful_queries": 0,
        "response_quality": 0,
        "average_response_time": 0,
        "errors": []
    }
    
    total_time = 0
    
    for test_case in test_set:
        start_time = time.time()
        
        try:
            # Traite la question
            response = bot.process_user_input(test_case["question"])
            
            # Vérifie la présence des éléments attendus dans la réponse
            quality_score = sum(
                1 for phrase in test_case["expected_response_contains"]
                if phrase.lower() in response.lower()
            ) / len(test_case["expected_response_contains"])
            
            results["successful_queries"] += 1
            results["response_quality"] += quality_score
            
        except Exception as e:
            results["errors"].append({
                "question": test_case["question"],
                "error": str(e)
            })
        
        total_time += time.time() - start_time
    
    # Calcule les moyennes
    results["response_quality"] /= results["total_tests"]
    results["average_response_time"] = total_time / results["total_tests"]
    
    return results

# --------------------------------------------------------------------------------
# 7. Main interactive loop
# --------------------------------------------------------------------------------
def chatbot():
    """Fonction principale du chatbot."""
    # Exemple de configuration avec différents LLMs
    config = {
        "provider": "ollama",  # ou "langchain", "ollama", "openai", "anthropic"
        "model": "mistral:7b",  # ou "mistral:7b", "deepseek-r1:7b", "qwen:14b"
        "model_provider": "ollama"  # Utilisé uniquement avec LangChain
    }
    
    # Pour utiliser différents LLMs :
    # Pour Ollama
    # config = {"provider": "ollama", "model": "mistral:7b"}
    # config = {"provider": "ollama", "model": "llama3.1:8b-instruct-q4_0"} # See https://ollama.com/library/llama3.1:8b-instruct-q4_0
    # Pour OpenAI
    # config = {"provider": "openai", "model": "gpt-3.5-turbo"}
    # Pour LangChain
    # config = {"provider": "langchain", "model": "deepseek-coder", "model_provider": "ollama"}

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
                
            try:
                response = bot.process_user_input(user_input)
                print(f"\nAssistant: {response}")
            except Exception as e:
                print(f"\nDésolé, une erreur s'est produite: {str(e)}")
                
    except Exception as e:
        print(f"Erreur d'initialisation: {str(e)}")

if __name__ == "__main__":
    chatbot()