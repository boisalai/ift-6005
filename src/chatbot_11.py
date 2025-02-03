"""
pip install litellm
pip install smolagents python-dotenv sqlalchemy --upgrade -q

https://huggingface.co/learn/cookbook/en/agent_data_analyst
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from pathlib import Path
import os
import json
from dotenv import load_dotenv

import duckdb
import litellm
from smolagents import CodeAgent, LiteLLMModel, Tool


load_dotenv()
os.environ['LITELLM_LOG'] = 'DEBUG'

DATA_DIR = Path("../data")
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"
DATA_DICT_PATH = DATA_DIR / "data_dictionary.json"


class DuckDBTool(Tool):
    name = "sql_engine"
    description = """
    Allows you to perform SQL queries on the DuckDB database containing product data.
    The table 'products' contains product information.
    Returns query results as formatted strings with the following structure:
    - First line: Column names as a tuple with quoted strings ('col1', 'col2', ...)
    - Following lines: Data rows as tuples (with parentheses and commas)
    
    For example:
    ('id', 'name', 'value')
    (1, 'product1', 10)
    (2, 'product2', 20)

    Returns:
        A formatted string containing column names followed by rows of data.
        Returns "Empty query" if query is empty or "No results found" if query returns no results.
    """
    inputs = {
        "query": {
            "type": "string",
            "description": "The SQL query to execute. Must be valid DuckDB SQL syntax."
        }
    }
    output_type = "string"

    def setup(self):
        """Initialisation - appelée avant la première utilisation"""
        self.is_initialized = True

    def forward(self, query: str) -> str:
        if not query or not query.strip():
            return "Empty query"

        try:
            with duckdb.connect(str(FILTERED_DB_PATH)) as con:
                results = con.sql(query)
                if not results:
                    return "No results found"

                # Get column names
                columns = results.columns
                # Get the data
                rows = results.fetchall()
                
                # Create header
                output = "(" + ", ".join(f"'{col}'" for col in columns) + ")"
                for row in rows:
                    output += "\n" + str(row)
                return output
        except duckdb.Error as e:
            return f"DuckDB error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

# tool
def visit_webpage(url: str) -> str:
    # See https://huggingface.co/docs/smolagents/examples/multiagents
    return f"Visiting {url}..."

model = LiteLLMModel(
    model_id="ollama/phi4:latest",
    api_base="http://localhost:11434", 
    temperature=0.1
)

sql_tool = DuckDBTool()
agent = CodeAgent(tools=[sql_tool], model=model, add_base_tools=True)

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

if __name__ == "__main__":
    prompt = "Combien de produits dans la table?"
    instruction = "Tu es un expert sur les produits alimentaires. Réponds à la question de l'utilisateur en utilisant des requêtes SQL sur la base de données des produits alimentaires."
    output = agent.run(prompt)
    agent.run("Combien de produits dans la table?")
    # print(load_dict())
    # query("SELECT COUNT(*) FROM products")
    # query("SELECT additives_n, additives_tags, product_name FROM products LIMIT 5")
