"""
Changes:
- Version 17:
    - Added sqlglot and validate_query() function
"""
import os
import re
import json
import warnings
from pathlib import Path
from textwrap import dedent
from typing import Dict, Any, Union

import duckdb
import sqlglot
from dotenv import load_dotenv
from smolagents import tool
from smolagents import (
    Tool,
    CodeAgent,
    ManagedAgent,
    ToolCallingAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    HfApiModel,
    LiteLLMModel,
)

# Disable specific warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Load environment variables
load_dotenv()

# Logs configuration
os.environ["LITELLM_LOG"] = "INFO"  # Change to 'DEBUG' for more details

# Define file paths
DATA_DIR = Path("../data")
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

"""
Structure du code:
- Fonction pour créer une instance du LLM
- Classe pour l'outil de recherche DuckDB
- Classe pour l'outil de recherche sur le Web
"""

def create_model(
    type_engine: str, api_key: str = None
) -> Union[HfApiModel, LiteLLMModel]:
    """Creates a language model instance based on selected engine.

    Args:
        type_engine (str): Type of LLM engine to use (e.g. "openai/gpt-4o").
        api_key (str, optional): API key required for some models.

    Returns:
        Union[HfApiModel, LiteLLMModel]: Instance of selected model.

    Raises:
        ValueError: If engine type is invalid.
    """
    if type_engine in [
        "ollama/qwen2.5-coder:3b",
        "ollama/phi4:latest",
        "ollama/qwen:14b"
        "ollama/deepseek-r1:latest",
    ]:
        # Free for local use, but requires a license for commercial use
        return LiteLLMModel(
            model_id=type_engine,
            api_base="http://localhost:11434",
            num_ctx=8192,
            # ollama default is 2048 which will often fail horribly.
            # 8192 works for easy tasks, more is better.
            # Check https://huggingface.co/spaces/NyxKrage/LLM-Model-VRAM-Calculator
            # to calculate how much VRAM this will need for the selected model.
        )

    if type_engine == "hf_api":
        # Requires an API key from Hugging Face
        return HfApiModel(model_id="mistralai/Mistral-7B-Instruct-v0.1")

    if type_engine == "claude-haiku":
        # Requires an API key from Anthropic
        # $4/MTok (see https://www.anthropic.com/pricing#anthropic-api)
        return LiteLLMModel(
            model_id="anthropic/claude-3-haiku-20240307",
        )

    if type_engine == "claude-sonnet":
        # Requires an API key from Anthropic
        # $15/MTok (see https://www.anthropic.com/pricing#anthropic-api)
        return LiteLLMModel(
            model_id="anthropic/claude-3-5-sonnet-20240620",
        )

    if type_engine == "gpt-4o-2024-08-06":
        # Requires an API key from OpenAI
        # $10/MTok (see https://platform.openai.com/docs/pricing#latest-models)
        return LiteLLMModel(
            model_id="openai/gpt-4o",
            max_tokens=1024,
        )
    else:
        raise ValueError("Invalid engine type.")

class DuckDBSearchTool(Tool):
    name = "sql_engine"
    description = dedent(
        """\
    Execute SQL queries using DuckDB syntax. The database contains a single table named `products` with
    detailed information about food items.

    KEY COLUMNS AND THEIR USAGE:
    - product_name: Multilingual product names (use list_filter for language selection)
    - categories_tags: Food category tags (e.g., 'en:snacks', 'fr:biscuits')
    - ingredients_tags: Ingredient classification tags
    - allergens_tags: Present allergens (e.g., 'en:milk', 'en:nuts')
    - labels_tags: Product certifications and claims (e.g., 'en:organic')
    - brands_tags: Brand identifiers
    - stores_tags: Retail store identifiers
    - nova_group: Processing level (1-4, where 1=unprocessed, 4=ultra-processed)
    - nutriscore_grade: Nutritional quality (A-E, where A=best)
    - ecoscore_grade: Environmental impact (A-E, where A=best)

    IMPORTANT QUERY GUIDELINES:
    1. Toujours planifier les requêtes avant de les exécuter pour éviter les résultats volumineux 
    2. Use list_contains() for array columns (e.g., categories_tags, labels_tags)
    3. Handle multilingual text fields using list_filter() to select language
    4. Always include error handling for NULL values
    5. Limit results when appropriate to avoid large result sets

    COMMON QUERY PATTERNS:
    1. Product name extraction:
       ```sql
       unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name
       ```

    2. Array field search:
       ```sql
       list_contains(categories_tags, 'en:category-name')
       ```

    3. Multilingual search (categories example):
       ```sql
       WHERE list_contains(categories_tags, 'en:category-name')
          OR list_contains(categories_tags, 'fr:category-name')
       ```

    4. Aggregation with minimum product threshold:
       ```sql
       GROUP BY field
       HAVING count(*) > threshold
       ```

    BEST PRACTICES
    - For multilingual fields (`STRUCT[lang VARCHAR, "text" VARCHAR][]`):
        - Use `LIST_FILTER()` to select language
        - Access text with ['text']
    - For arrays (`VARCHAR[]`):
        - Use `LIST_CONTAINS()` for exact matches
        - Use `UNNEST() WITH column_alias` for detailed search with `LIKE`
        - Be aware that `UNNEST` can duplicate rows - use `DISTINCT` if needed
    - For text searches:
        - Use `LOWER()` for case-insensitive search
        - Use `LIKE` with wildcards (`%`) for partial matches
        - Prefer `UNNEST` with `LIKE` over `ARRAY_TO_STRING()`
    - Other tips:
        - Handle NULLs with `COALESCE()`
        - Cast timestamps using `TO_TIMESTAMP()`
        - Add `LIMIT` for large results
        - Use column aliases in `UNNEST` with format: `UNNEST(array) AS alias(column)`

    RESPONSE FORMAT:
    The tool returns a JSON object with the following structure:
    ```json
    {
        "columns": ["col1", "col2", ...],     // Array of column names
        "rows": [                             // Array of row values
            ["val1", "val2", ...],            // Each value converted to string
            ...
        ],
        "row_count": 42,                      // Total number of results
        "error": "error message"              // Present only if query fails
    }
    ```

    ERROR HANDLING:
    - Check "error" field in response for query execution problems
    - Common errors: syntax errors, invalid column names, type mismatches
    - Use TRY_CAST() for safer type conversions
    - Always validate array access with list_contains() before using
    """
    )

    inputs = {
        "query": {"type": "string", "description": "Valid DuckDB SQL query to execute"}
    }
    output_type = "string"

    def __init__(self, db_path: Path):
        super().__init__()
        self.db_path = db_path
        self.connection = None

    def setup(self) -> None:
        """Initialize database connection"""
        if not self.db_path.exists():
            print(f"Database file does not exist: {self.db_path}")
        try:
            self.connection = duckdb.connect(str(self.db_path))
            self.is_initialized = True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            raise

    def validate_query(query: str) -> tuple[bool, str]:
        """
        Valide une requête SQL et retourne (succès, message d'erreur)
        """
        try:
            # Parse la requête pour vérifier la syntaxe
            sqlglot.parse_one(query, dialect='duckdb')
            return True, ""
        except sqlglot.errors.ParseError as e:
            return False, f"Erreur de syntaxe SQL: {str(e)}"
    
    def format_output(self, columns: list, rows: list) -> Dict[str, Any]:
        """Format output as JSON dictionary"""
        return {
            "columns": columns,
            "rows": [tuple(str(item) for item in row) for row in rows],
            "row_count": len(rows),
        }

    def forward(self, query: str) -> str:
        """Execute SQL query and return results"""
        # Validation de la requête avant exécution
        is_valid, error_msg = self.validate_query(query)
        if not is_valid:
            return json.dumps({"error": error_msg})
    
        try:
            result = self.connection.sql(query)
            output = self.format_output(result.columns, result.fetchall())

            return json.dumps(output)

        except duckdb.Error as e:
            return json.dumps({"error": f"DuckDB error: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})

    def __del__(self):
        """Properly close database connection"""
        if self.connection:
            self.connection.close()


class FoodGuideSearchTool(DuckDuckGoSearchTool):
    def forward(self, query: str) -> str:
        print(f"DEBUG: Searching for query: {query}")

        en_results = self.ddgs.text(
            "site:https://food-guide.canada.ca/en/ " + query,
            max_results=self.max_results,
        )
        fr_results = self.ddgs.text(
            "site:https://guide-alimentaire.canada.ca/fr/ " + query,
            max_results=self.max_results,
        )
        results = en_results + fr_results

        if len(results) == 0:
            raise Exception("No results found! Try a less restrictive/shorter query.")
        postprocessed_results = [
            f"[{result['title']}]({result['href']})\n{result['body']}"
            for result in results
        ]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)


model = create_model("claude-sonnet")

sql_tool = DuckDBSearchTool(db_path=FILTERED_DB_PATH)
sql_agent = ToolCallingAgent(tools=[sql_tool], model=model, max_steps=3)
managed_sql_agent = ManagedAgent(
    agent=sql_agent,
    name="search",
    description=dedent(
        """\
    Queries the Open Food Facts Canadian products database using DuckDB SQL syntax.
    Input a valid DuckDB SQL query to search product information."""
    ),
)

web_search_tool = FoodGuideSearchTool()
visit_webpage = VisitWebpageTool()
web_agent = ToolCallingAgent(
    tools=[web_search_tool, visit_webpage], model=model, max_steps=3
)
managed_web_agent = ManagedAgent(
    agent=web_agent,
    name="search",
    description=dedent(
        """\
    Searches Canada's Food Guide website for nutrition and dietary guidance.
    Accepts natural language queries in English and French."""
    ),
)

agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[managed_web_agent, managed_sql_agent],
    additional_authorized_imports=["json"],
)

# Additional instructions for the agent
ADDITIONAL_NOTES = dedent(
    """\
Process user prompt as follows:

1. Identify type of the prompt: greeting, question, or conversation

2. Process by type:
   - Greeting: Offer food-related assistance
   - Question: Search in order:
     1. Base de données sur les produits alimentaires d'Open Food Facts
     2. Canadian's food guide web site if needed
   - Conversation: Keep to food/nutrition topics

3. Respond in user's language (FR/EN):
   - Cite source (Open Food Facts/Canadian's food guide)
   - Be concise and accurate
   - State clearly if answer unknown

Maintain language consistency throughout.
"""
)

def run_interactive() -> None:
    while True:
        user_input = input("User (or 'exit'): ")
        if user_input.lower().strip() == "exit":
            break
        response = agent.run(
            user_input,
            additional_args={
                "additional_notes": ADDITIONAL_NOTES,
            },
        )
        print("Agent answer: ", response)

def run(prompt: str) -> None:
    response = agent.run(
        prompt,
        additional_args={
            "additional_notes": ADDITIONAL_NOTES,
        },
    )
    print(f"Results:\n{response}")

if __name__ == "__main__":
    #PROMPT = "Combien de produits dans la base de données?"
    #run(PROMPT)
    run_interactive()
