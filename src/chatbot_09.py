"""
pip install litellm
pip install smolagents python-dotenv sqlalchemy --upgrade -q

Ce code fonctionne bien.
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

DATA_DIR = Path("../data")
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"
DATA_DICT_PATH = DATA_DIR / "data_dictionary.json"


class DuckDBTool(Tool):
    name = "sql_engine"
    description = """
    Execute SQL queries on the DuckDB database containing product data.
    Returns query results as a formatted string where each row is a tuple (with parentheses and commas).
    For example, a count query will return "(number,)".
    The table 'products' contains product information. 
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
                results = con.sql(query).fetchall()
                if not results:
                    return "No results found"    
                output = "\n".join(str(row) for row in results)
                return output
        except duckdb.Error as e:
            return f"DuckDB error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

os.environ['LITELLM_LOG'] = 'DEBUG'

model = LiteLLMModel(
    model_id="ollama/phi4:latest", # This model is a bit weak for agentic behaviours though
    api_base="http://localhost:11434", # replace with 127.0.0.1:11434 or remote open-ai compatible server if necessary
    temperature=0.1,  # Réduit les hallucinations
)

agent = CodeAgent(tools=[DuckDBTool()], model=model)

def load_dict() -> str:
    # Chargement du dictionnaire de données
    with open(DATA_DICT_PATH, 'r', encoding='utf-8') as f:
        data_dict = json.load(f)

    output = ""
    for k, v in data_dict.items():
        output += f"- {k} ({v['type']}): {v['description']}\n"
    return output

def query(query: str) -> str:
    sql_tool = DuckDBTool()
    output = sql_tool(query)
    print(f"Output: {output}")

if __name__ == "__main__":
    agent.run("Combien de produits dans la table?")
    # print(load_dict())
    # query("SELECT COUNT(*) FROM products")
