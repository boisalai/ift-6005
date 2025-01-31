# Bibliothèque standard
from pathlib import Path
import time
import logging
from typing import List, Dict, Tuple, Protocol
from abc import ABC, abstractmethod

# Bibliothèques tierces
import requests
import pandas as pd
import duckdb
import openai
from anthropic import Anthropic
from langchain.chat_models import ChatOpenAI, ChatAnthropic, ChatOllama
from langchain.schema import HumanMessage, SystemMessage

# Configuration de l'environnement
DATA_DIR = Path("../data")
PARQUET_PATH = DATA_DIR / "food.parquet"
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"


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


# Schéma de la base de données
DATABASE_SCHEMA = """
La base de données contient une table appelée `food_facts` avec les colonnes suivantes :
- `product_name` (texte) : Le nom du produit
- `brands` (texte) : La marque du produit
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


class TAGSystem:
    """
    Implémentation du modèle TAG (Table-Augmented Generation).
    """

    # Dictionnaire de mapping des colonnes
    COLUMN_MAPPING = {
        "marque": "brands",
        "marques": "brands",
        "brand": "brands",
        "brands": "brands",
        "nom": "product_name",
        "produit": "product_name",
        "product": "product_name",
        "quantité": "product_quantity",
        "quantity": "product_quantity",
        "nutriscore": "nutriscore_grade",
        "nutri-score": "nutriscore_grade",
        "nutri_score": "nutriscore_grade",
        "pays": "countries",
        "country": "countries",
        "magasins": "stores",
        "stores": "stores",
    }

    def __init__(self, db_path: Path, llm: Protocol, table_name: str, schema: str):
        self.db_path = db_path
        self.llm = llm
        self.conn = duckdb.connect(str(db_path))
        self.table_name = table_name
        self.schema = schema

        # Récupère les colonnes réelles de la table
        self.available_columns = self._get_available_columns()
        logger.info(f"Colonnes disponibles: {', '.join(self.available_columns)}")

    def _get_available_columns(self) -> List[str]:
        """Récupère la liste des colonnes disponibles dans la table."""
        columns = self.conn.execute(f"DESCRIBE {self.table_name}").fetchdf()
        return columns["column_name"].tolist()

    def _map_column_name(self, column: str) -> str:
        """Mappe un nom de colonne utilisateur vers le nom réel dans la base."""
        column = column.lower()
        if column in self.COLUMN_MAPPING:
            mapped = self.COLUMN_MAPPING[column]
            if mapped in self.available_columns:
                return mapped
        return column

    def _format_dataframe(self, df: pd.DataFrame, max_rows: int = 10) -> str:
        """
        Formate un DataFrame pour l'affichage.
        Args:
            df: DataFrame à formater
            max_rows: Nombre maximal de lignes à afficher
        """
        if df.empty:
            return "Aucun résultat"

        # Pour les requêtes COUNT
        if len(df.columns) == 1 and df.columns[0].lower() in ["count", "total", "n"]:
            return str(df.iloc[0, 0])

        # Pour les autres résultats, limite l'affichage
        preview = df.head(max_rows)
        total_rows = len(df)
        preview_str = preview.to_string(index=False)

        if total_rows > max_rows:
            preview_str += f"\n... ({total_rows-max_rows} lignes supplémentaires)"

        return preview_str

    def syn(
        self, request: str, conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Query Synthesis: convertit la requête en langage naturel en SQL."""
        context = (
            "\n".join(
                f"{msg['role']}: {msg['content']}" for msg in conversation_history[-3:]
            )
            if conversation_history
            else ""
        )

        prompt = f"""
        Tu dois convertir cette question en une requête SQL simple et directe.

        Schéma de la base:
        {self.schema}
        
        IMPORTANT: 
        - Le nom de la table est exactement '{self.table_name}'
        - Voici les colonnes disponibles: {', '.join(self.available_columns)}
        
        Contexte conversation:
        {context}
        
        Question: {request}
        
        Instructions CRITIQUES:
        1. Si la question demande le nombre total de produits, utilise 'SELECT COUNT(*) as total FROM {self.table_name}'
        2. Si la question demande le nombre d'éléments spécifiques, utilise COUNT avec les conditions appropriées
        3. Pour lister des valeurs uniques, utilise DISTINCT
        4. Utilise EXACTEMENT le nom de table '{self.table_name}'
        5. Vérifie que les noms de colonnes existent dans la liste fournie
        6. Limite les résultats avec LIMIT si nécessaire

        Génère uniquement la requête SQL, sans explication ni commentaire.
        """

        query = self.llm.generate(prompt).strip().rstrip(";")

        # Tente de corriger les noms de colonnes
        for word in query.split():
            if word in self.COLUMN_MAPPING:
                mapped = self.COLUMN_MAPPING[word]
                if mapped in self.available_columns:
                    query = query.replace(word, mapped)

        return query

    def exec(self, query: str) -> pd.DataFrame:
        """Query Execution: exécute la requête sur la base de données."""
        try:
            logger.info(f"Requête SQL:\n{query}")
            df = self.conn.execute(query).fetchdf()
            logger.info(f"\nRésultats bruts:\n{self._format_dataframe(df)}")
            return df
        except Exception as e:
            # Tente de corriger les erreurs communes
            if "column not found" in str(e).lower():
                col = str(e).split('"')[1] if '"' in str(e) else None
                if col and col in self.COLUMN_MAPPING:
                    corrected_query = query.replace(col, self.COLUMN_MAPPING[col])
                    logger.info(
                        f"Tentative avec la colonne corrigée: {corrected_query}"
                    )
                    return self.conn.execute(corrected_query).fetchdf()
            raise RuntimeError(f"Erreur d'exécution SQL: {str(e)}")

    def gen(self, request: str, data: pd.DataFrame) -> str:
        """Answer Generation: génère une réponse en langage naturel."""
        prompt = f"""
        Génère une réponse claire et naturelle à cette question.
        
        Question: {request}
        
        Données ({len(data)} lignes):
        {self._format_dataframe(data)}
        
        Instructions:
        1. Réponds directement à la question
        2. Pour les requêtes COUNT, donne UNIQUEMENT le nombre exact
        3. Pour les autres requêtes:
        - Présente les résultats de manière structurée
        - Si plus de 10 résultats, fais un résumé
        - Mentionne le nombre total de résultats
        4. Ne fais PAS de comparaisons ou d'observations supplémentaires
        5. Reste factuel et précis
        """

        return self.llm.generate(prompt)


class FoodDatabaseBot:
    """
    Interface utilisateur avancée pour le système TAG appliqué à la base Open Food Facts.
    Conserve les fonctionnalités spécifiques tout en utilisant l'architecture TAG.
    """

    def __init__(self, db_path: Path, llm: BaseLLM):
        if not db_path.exists():
            raise FileNotFoundError(f"La base de données {db_path} n'existe pas.")

        print(f"Utilisation de la base de données: {db_path}.")
        self.table_name = self._get_table_name(db_path)
        self.schema = self._get_schema(db_path)
        self.llm = llm
        self.conversation_history: List[Dict[str, str]] = []

        # Initialisation du système TAG
        self.tag_system = TAGSystem(db_path, llm, self.table_name, self.schema)

    def _get_table_name(self, db_path: Path) -> str:
        """Récupère le nom de la première table de la base de données."""
        conn = duckdb.connect(str(db_path))
        tables = conn.execute("SHOW TABLES").fetchdf()
        if tables.empty:
            raise ValueError("La base de données ne contient aucune table.")
        conn.close()

        print(f"Tables disponibles: {tables['name'].tolist()}")
        print(f"Utilisation de la première table: {tables.iloc[0]['name']}")
        return tables.iloc[0]["name"]

    def _get_schema(self, db_path: Path) -> str:
        """Récupère le schéma réel de la table."""
        conn = duckdb.connect(str(db_path))
        columns = conn.execute(f"DESCRIBE {self.table_name}").fetchdf()
        conn.close()

        schema = f"""
        La base de données contient une table appelée `{self.table_name}` avec les colonnes suivantes :
        """
        for _, row in columns.iterrows():
            schema += f"\n- `{row['column_name']}` ({row['column_type']}) : Colonne de la table"

        return schema

    def determine_query_type(self, user_input: str) -> Tuple[str, str]:
        """Détermine le type de requête nécessaire."""
        prompt = f"""
        Analyse cette entrée utilisateur et réponds UNIQUEMENT avec un des mots suivants:
        - greeting (pour une salutation ou premier contact)
        - sql (pour une question nécessitant des données)
        - conversation (pour une question générale)

        Entrée: {user_input}

        Réponse (un seul mot):"""

        response = self.llm.generate(prompt).strip().lower()

        # Simplifie la logique de détection
        if "greeting" in response:
            return "greeting", "Salutation"
        elif "sql" in response:
            return "sql", "Nécessite une requête SQL"
        else:
            return "conversation", "Question conversationnelle"

    def handle_conversation(self, user_input: str) -> str:
        """Gère une question conversationnelle."""
        prompt = f"""
        Tu es un assistant expert des produits alimentaires.
        
        Historique récent de la conversation:
        {self._format_history()}
        
        Question: {user_input}
        
        Réponds de manière naturelle et utile, sans accéder à la base de données.
        """

        return self.llm.generate(prompt)

    def handle_greeting(self) -> str:
        """Gère une salutation."""
        try:
            sql_query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            results = self.tag_system.exec(sql_query)
            total = results.iloc[0]["total"]
            return f"Bonjour ! Je suis votre assistant pour explorer la base de données des produits alimentaires. Elle contient {total} produits. Comment puis-je vous aider ?"
        except Exception:
            return "Bonjour ! Je suis votre assistant pour explorer la base de données des produits alimentaires. Comment puis-je vous aider ?"

    def handle_sql_query(self, user_input: str) -> str:
        """Gère une question nécessitant une requête SQL en utilisant le système TAG."""
        try:
            # 1. Query Synthesis avec contexte de conversation
            sql_query = self.tag_system.syn(user_input, self.conversation_history)

            # 2. Query Execution
            results = self.tag_system.exec(sql_query)

            # 3. Answer Generation
            return self.tag_system.gen(user_input, results)

        except ValueError as e:
            return f"Erreur de synthèse SQL: {str(e)}"
        except RuntimeError as e:
            return f"Erreur d'exécution: {str(e)}"
        except Exception as e:
            return f"Erreur inattendue: {str(e)}"

    def _format_history(self) -> str:
        """Formate l'historique récent de la conversation."""
        return "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-3:]
        )

    def process_user_input(self, user_input: str) -> str:
        """Point d'entrée principal qui détermine et traite le type de requête."""
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


def create_test_set() -> List[Dict]:
    """Crée un ensemble de test avec des questions et réponses attendues."""
    return [
        {
            "question": "Quels sont les produits avec un Nutri-score A ?",
            "sql": "SELECT product_name, brands, nutri_score FROM food_facts WHERE nutri_score = 'A' LIMIT 5",
            "expected_response_contains": ["produits", "Nutri-score A"],
        },
        {
            "question": "Combien y a-t-il de produits sans allergènes ?",
            "sql": "SELECT COUNT(*) as count FROM food_facts WHERE allergens = 'None' OR allergens IS NULL",
            "expected_response_contains": ["produits", "sans allergènes"],
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
        "errors": [],
    }

    total_time = 0

    for test_case in test_set:
        start_time = time.time()

        try:
            # Traite la question
            response = bot.process_user_input(test_case["question"])

            # Vérifie la présence des éléments attendus dans la réponse
            quality_score = sum(
                1
                for phrase in test_case["expected_response_contains"]
                if phrase.lower() in response.lower()
            ) / len(test_case["expected_response_contains"])

            results["successful_queries"] += 1
            results["response_quality"] += quality_score

        except Exception as e:
            results["errors"].append(
                {"question": test_case["question"], "error": str(e)}
            )

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
        "model_provider": "ollama",  # Utilisé uniquement avec LangChain
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
