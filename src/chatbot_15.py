import os
import re
import json
import warnings
import unicodedata
from pathlib import Path
from textwrap import dedent
from typing import Dict, Any, Union

import markdownify
import requests
import duckdb
from dotenv import load_dotenv
from requests.exceptions import RequestException
from smolagents import tool
from smolagents import (
    CodeAgent, 
    ManagedAgent,
    Tool, 
    ToolCallingAgent, 
    DuckDuckGoSearchTool,
    HfApiModel, 
    LiteLLMModel
)

# Disable specific warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Load environment variables
load_dotenv()

# Logs configuration
os.environ['LITELLM_LOG'] = 'INFO'  # Change to 'DEBUG' for more details

# Define file paths
DATA_DIR = Path("../data")
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

# Check if data folder and files exist
if not DATA_DIR.exists():
    raise FileNotFoundError(
        f"Data directory '{DATA_DIR}' not found."
    )
elif not FILTERED_DB_PATH.exists():
    raise FileNotFoundError(
        f"Database '{FILTERED_DB_PATH}' not found."
)

class DuckDBSearchTool(Tool):
    name = "sql_engine"
    description = dedent("""\
    Execute SQL queries on the Open Food Facts Canadian products database using DuckDB syntax.
    The database contains a single table named `products` with detailed information about food items.
    
    IMPORTANT QUERY GUIDELINES:
    1. Use list_contains() for array columns (e.g., categories_tags, labels_tags)
    2. Handle multilingual text fields using list_filter() to select language
    3. Always include error handling for NULL values
    4. Limit results when appropriate to avoid large result sets
    
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
    """)

    inputs = {
        "query": {
            "type": "string",
            "description": "Valid DuckDB SQL query to execute"
        }
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

    def format_output(self, columns: list, rows: list) -> Dict[str, Any]:
        """Format output as JSON dictionary"""
        return {
            "columns": columns,
            "rows": [tuple(str(item) for item in row) for row in rows],
            "row_count": len(rows)
        } 

    def forward(self, query: str) -> str:
        """Execute SQL query and return results"""
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
    description = dedent("""\
    Performs a web search in the Canadian Food Guide website based on your query.
    The Guide is Health Canada's official dietary guidance for Canadians aged 2+, 
    providing recommendations, resources, and tools to promote health and prevent 
    diet-related diseases. Content includes:
    
    - Public resources: eating recommendations, visual guides in multiple languages 
      (including Indigenous), tips, and recipes
    - Professional resources: detailed guidelines, implementation guidance, 
      educational toolkits, research tools
    - Specialized content: Indigenous guidance and dietitian referral systems
    
    Available in English and French.
    """)
    
    def forward(self, query: str) -> str:
        en_results = self.ddgs.text("site:https://food-guide.canada.ca/en/ " + query, max_results=self.max_results)
        fr_results = self.ddgs.text("site:https://guide-alimentaire.canada.ca/fr/ " + query, max_results=self.max_results)
        results = en_results + fr_results

        if len(results) == 0:
            raise Exception("No results found! Try a less restrictive/shorter query.")
        postprocessed_results = [f"[{result['title']}]({result['href']})\n{result['body']}" for result in results]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)

@tool
def visit_webpage(url: str) -> str:
    """Visits a webpage at the given URL and returns its content as a markdown string.

    Args:
        url: The URL of the webpage to visit.

    Returns:
        The content of the webpage converted to Markdown, or an error message if
        the request fails.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Convert the HTML content to Markdown
        markdown_content = markdownify.markdownify(response.text).strip()

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

        return markdown_content

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


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
    if type_engine in ["ollama/qwen2.5-coder:3b", "ollama/phi4:latest", "ollama/deepseek-r1:latest"]:
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
    elif type_engine == "hf_api":
        # Requires an API key from Hugging Face
        return HfApiModel(model_id="mistralai/Mistral-7B-Instruct-v0.1")
    elif type_engine == "claude-haiku":
        # Requires an API key from Anthropic
        # $4/MTok (see https://www.anthropic.com/pricing#anthropic-api)
        return LiteLLMModel(
            model_id="anthropic/claude-3.5-haiku",
            max_tokens=1024,
        )
    elif type_engine == "claude-sonnet":
        # Requires an API key from Anthropic
        # $15/MTok (see https://www.anthropic.com/pricing#anthropic-api)
        return LiteLLMModel(
            model_id="anthropic/claude-3-5-sonnet-latest", 
            max_tokens=1024,
        )
    elif type_engine == "gpt-4o-2024-08-06":
        # Requires an API key from OpenAI
        # $10/MTok (see https://platform.openai.com/docs/pricing#latest-models)
        return LiteLLMModel(
            model_id="openai/gpt-4o",
            max_tokens=1024,
        )
    else:
        raise ValueError("Invalid engine type.")


web_search_tool = FoodGuideSearchTool()
sql_tool = DuckDBSearchTool(db_path=FILTERED_DB_PATH)

model = create_model("claude-sonnet")

web_agent = ToolCallingAgent(tools=[web_search_tool, visit_webpage], model=model, max_steps=3)
managed_web_agent = ManagedAgent(
    agent=web_agent,
    name="search",
    description=dedent("""\
    Searches Canada's Food Guide website for nutrition and dietary guidance. 
    Accepts natural language queries in English and French."""),
)

sql_agent = ToolCallingAgent(tools=[sql_tool], model=model, max_steps=3)
managed_sql_agent = ManagedAgent(
    agent=sql_agent,
    name="search",
    description=dedent("""\
    Queries the Open Food Facts Canadian products database using DuckDB SQL syntax. 
    Input a valid DuckDB SQL query to search product information."""),
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[managed_web_agent, managed_sql_agent], 
    additional_authorized_imports=['json'],
)

# Additional instructions for primary agent
ADDITIONAL_NOTES = dedent("""\
Expert in food products and nutrition. Process queries as follows:

1. Identify type: greeting, question, or conversation

2. Process by type:
   - Greeting: Offer food-related assistance
   - Question: Search in order:
     1. Open Food Facts DuckDB
     2. Canadian Food Guide if needed
   - Conversation: Keep to food/nutrition topics

3. Respond in user's language (FR/EN):
   - Cite source (Open Food Facts/Food Guide)
   - Be concise and accurate
   - State clearly if answer unknown

Maintain language consistency throughout.
""")

def run(prompt: str) -> None:
    response = manager_agent.run(
        prompt,
        additional_args={
            "additional_notes": ADDITIONAL_NOTES,
        }
    )
    print(f"Results:\n{response}")

if __name__ == "__main__":
    prompt = "Quelles sont les qualités nutritives des pommes?"
    prompt = "Bonjour"
    prompt = "Combien de produits dans la base de données?"
    run(prompt)
