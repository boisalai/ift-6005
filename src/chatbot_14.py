
"""
pip install litellm
pip install smolagents python-dotenv sqlalchemy --upgrade -q
pip install markdownify duckduckgo-search smolagents --upgrade -q

https://huggingface.co/learn/cookbook/en/agent_data_analyst
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import json
from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv
import duckdb
import litellm
from smolagents import (
    CodeAgent, ManagedAgent,
    Tool, tool, ToolCallingAgent, 
    DuckDuckGoSearchTool,
    LiteLLMModel, 
)

import re
import requests
from markdownify import markdownify
from requests.exceptions import RequestException


# Configuration
load_dotenv()
os.environ['LITELLM_LOG'] = 'DEBUG'

DATA_DIR = Path("../data")
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"
DATA_DICT_PATH = DATA_DIR / "data_dictionary.json"

    
class DuckDBTool(Tool):
    name = "sql_engine"
    description = """
    Outil pour exécuter des requêtes SQL sur la base DuckDB.
    Retourne les résultats au format JSON avec la structure :
    {
        "columns": [noms des colonnes],
        "rows": [valeurs des lignes],
        "row_count": nombre de résultats,
        "error": "(optionnel) message d'erreur"
    }
    """
    inputs = {
        "query": {
            "type": "string",
            "description": "Requête SQL DuckDB valide à exécuter"
        }
    }
    output_type = "string"

    def __init__(self, db_path: Path):
        super().__init__()
        self.db_path = db_path
        self.connection = None
        
    def setup(self) -> None:
        """Initialise la connexion à la base de données"""
        if not self.db_path.exists():
            print(f"Le fichier de base de données n'existe pas: {self.db_path}")
        try:
            self.connection = duckdb.connect(str(self.db_path))
            self.is_initialized = True
        except Exception as e:
            print(f"Erreur de connexion : {str(e)}")
            raise

    def validate_query(self, query: str) -> None:
        """Valide basiquement la requête SQL"""
        if not query.strip():
            raise ValueError("Requête vide")
        if not query.lower().startswith(('select', 'with')):
            raise ValueError("Seules les requêtes SELECT sont autorisées")

    def format_output(self, columns: list, rows: list) -> Dict[str, Any]:
        """Formate la sortie en dictionnaire JSON"""
        return {
            "columns": columns,
            "rows": [tuple(str(item) for item in row) for row in rows],
            "row_count": len(rows)
        } 

    def forward(self, query: str) -> str:
        """Exécute la requête SQL et retourne les résultats"""
        try:
            self.validate_query(query)
            
            if not self.connection:
                self.setup()
                
            result = self.connection.sql(query)
            output = self.format_output(result.columns, result.fetchall())
            
            return json.dumps(output)
            
        except (ValueError, DatabaseError) as e:
            return json.dumps({"error": str(e)})
        except duckdb.Error as e:
            return json.dumps({"error": f"Erreur DuckDB: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Erreur inattendue: {str(e)}"})

    def __del__(self):
        """Ferme proprement la connexion à la base de données"""
        if self.connection:
            self.connection.close()

@tool
def visit_webpage(url: str) -> str:
    """Visits a webpage at the given URL and returns its content as a markdown string.

    Args:
        url: The URL of the webpage to visit.

    Returns:
        The content of the webpage converted to Markdown, or an error message if the request fails.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Convert the HTML content to Markdown
        markdown_content = markdownify(response.text).strip()

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

        return markdown_content

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"



# Instructions pour l'agent
ADDITIONAL_NOTES = """
Tu es un expert en produit alimentaire qui aide les utilisateurs à trouver des informations sur les produits alimentaires, l'alimentation et la nutrition.

ÉTAPE 1 - CLASSIFICATION DE LA REQUÊTE:
Classe la demande de l'utilisateur dans une de ces trois catégories :
1. greeting : salutations comme "bonjour", "salut", "hello"
2. sql : questions sur les données alimentaires ou recherche d'informations nutritionnelles
3. conversation : autres questions générales

ÉTAPE 2 - TRAITEMENT SELON LA CATÉGORIE:

Si GREETING:
- Réponds poliment dans la langue de l'utilisateur (français ou anglais)
- Propose ton aide pour des questions alimentaires
Exemple: "Bonjour! Je suis votre assistant culinaire. Comment puis-je vous aider avec vos questions sur l'alimentation?"

Si CONVERSATION:
- Réponds de manière appropriée dans la langue de l'utilisateur (français ou anglais)
- Reste focalisé sur le domaine alimentaire
Exemple: "Je suis spécialisé dans les questions sur les produits alimentaires, l'alimentation et la nutrition. Je peux vous aider à..."

Si SQL:
1. TOUJOURS essayer d'abord une requête SQL:
```python
# Exemple de requête SQL
result = sql_engine("SELECT * FROM products WHERE...")
data = json.loads(result)

if 'error' in data:
    final_answer(f"Erreur SQL : {data['error']}")
elif data['row_count'] == 0:
    # Si pas de résultats SQL, OBLIGATOIREMENT consulter le Guide alimentaire canadien
    response = managed_web_agent("chercher sur https://guide-alimentaire.canada.ca/fr/ pour " + question_utilisateur)
    final_answer(response)
else:
    # Formater la réponse des résultats SQL
    final_answer(formater_resultats(data))
```

2. Si la requête SQL ne donne pas de résultats satisfaisants:
- OBLIGATOIREMENT utiliser managed_web_agent pour chercher sur le Guide alimentaire canadien
- Utiliser UNIQUEMENT ces URLs:
  * Français: https://guide-alimentaire.canada.ca/fr/
  * Anglais: https://food-guide.canada.ca/en/

RÈGLES IMPORTANTES:
1. TOUJOURS répondre dans la langue de l'utilisateur (français ou anglais)
2. Pour les requêtes alimentaires sans résultats SQL, TOUJOURS consulter le Guide alimentaire canadien
3. Bien formater les réponses avec des sections claires
4. Citer les sources (SQL ou Guide alimentaire) dans la réponse

Exemple d'utilisation pour une recette:
```python
# D'abord essayer SQL
result = sql_engine("SELECT * FROM products WHERE product_name LIKE '%pomme%'")
data = json.loads(result)

if data['row_count'] == 0:
    # Si pas de résultats, consulter le Guide alimentaire
    response = managed_web_agent("rechercher recette pommes bleuets sur https://guide-alimentaire.canada.ca/fr/")
    final_answer("Selon le Guide alimentaire canadien:\\n" + response)
```
"""

# Initialisation du modèle
# Éventuellement, utiliser qwen2.5-coder:3b pour un modèle plus rapide
# Voir https://ollama.com/library/qwen2.5-coder:7b ou qwen2.5-coder:14b
model = LiteLLMModel(
    model_id="ollama/phi4:latest",
    api_base="http://localhost:11434",
    temperature=0.1,
    max_tokens=8096,
)

# Agent pour les recherches web
web_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), visit_webpage],
    model=model,
    max_steps=10,

)

# Agent web géré pour les recherches
managed_web_agent = ManagedAgent(
    agent=web_agent,
    name="search",
    description="Effectue des recherches sur le Guide alimentaire canadien. Donnez-lui votre requête comme argument.",
)

# Agent SQL
sql_engine = DuckDBTool(db_path=FILTERED_DB_PATH)

# Agent principal
manager_agent = CodeAgent(
    tools=[sql_engine], 
    model=model,
    managed_agents=[managed_web_agent], 
    additional_authorized_imports=['json'],
)


class TaskClassifierTool(Tool):
    name = "task_classifier"
    description = """
    Cet outil sert à classer le prompt de l'utilisateur dans une seule de ces trois catégories : "salutation", "conversation" ou "SQL".
    """
    inputs = {"category": {"type": "string", "description": "La catégorie du prompt de l'utilisateur ('salutation', 'conversation', 'SQL')"}}
    output_type = "string"

    def forward(self, category: str) -> str:
        return category
    
task_classifier = TaskClassifierTool()
classifier_agent = ToolCallingAgent(
    tools=[task_classifier],
    model=model,
    max_steps=1,
)


def load_dict() -> str:
    # Chargement du dictionnaire de données
    with open(DATA_DICT_PATH, 'r', encoding='utf-8') as f:
        data_dict = json.load(f)

    output = ""
    for k, v in data_dict.items():
        output += f"- {k} ({v['type']}): {v['description']}\n"
    return output

def query(query: str) -> str:
    output = sql_engine(query)
    print(f"Output:\n{output}")

def test():
    prompt = "Combien de produits dans la table?"
    prompt = "Bonjour"
    prompt = "Proposes un recette de croquant aux pommes et aux bleuets"

    response = manager_agent.run(
        prompt,
        additional_args={
            "additional_notes": ADDITIONAL_NOTES,
            "language": "french"
        }
    )
    
    print("Réponse finale :", response)

def classify_task() -> None:
    for prompt in ["Bonjour", "SELECT * FROM products", "Comment faire une tarte aux pommes?"]:
        response = classifier_agent.run(
            prompt,
            additional_args={
                "additional_notes": "Identifie la catégorie du prompt de l'utilisateur",
            }
        )
        print(f"Classification de la tâche: {response}")

if __name__ == "__main__":
    classify_task()


    # test()

    # print(load_dict())
    # result = sql_engine("SELECT COUNT(*) FROM products")                                                                         
    # data = json.loads(result)
    # print(data) 
    # query("SELECT additives_n, additives_tags, product_name FROM products LIMIT 5")
