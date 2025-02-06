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
DATA_DICT_PATH = DATA_DIR / "data_dictionary.json"

# Check if data folder and files exist
if not DATA_DIR.exists():
    raise FileNotFoundError(
        f"Data directory '{DATA_DIR}' not found."
    )
elif not FILTERED_DB_PATH.exists():
    raise FileNotFoundError(
        f"Database '{FILTERED_DB_PATH}' not found."
)
elif not DATA_DICT_PATH.exists():
    raise FileNotFoundError(
        f"Data dictionary '{DATA_DICT_PATH}' not found."
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

model = create_model("claude-haiku")

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

def load_dict() -> None:
    # Load data dictionary
    with open(DATA_DICT_PATH, 'r', encoding='utf-8') as f:
        data_dict = json.load(f)

    output = ""
    for k, v in data_dict.items():
        output += f"- {k} ({v['type']}): {v['description']}\n"
    print(output)

def duckdb_query(query: str, indent: int = None) -> str:
    """Executes a DuckDB query and returns results as a list."""
    def format_output(columns: list, rows: list) -> Dict[str, Any]:
        """Formats output, ensuring proper Unicode character display"""
        return {
            "columns": columns,
            "rows": [tuple(str(item) for item in row) for row in rows],
            "row_count": len(rows)
        } 
    try:
        with duckdb.connect(str(FILTERED_DB_PATH)) as con:
            result = con.sql(query)
            output = format_output(result.columns, result.fetchall())
            return json.dumps(output, indent=indent)
    except Exception as e:
        return f"Error executing query: {e}"

def duckdb_query_demo(query: str) -> str:
    print(f"{query}")
    print(duckdb_query(query))
   
def sql(index: int) -> None:
    print(f"\nindex: {index}")
    
    if index == 1:
        query = dedent("""\
        -- List all tables in the database
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main';
        """)
        duckdb_query_demo(query)
    
    elif index == 2:
        query = dedent("""\
        -- Show columns in the products table
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'products';
        """)
        duckdb_query_demo(query)
    
    elif index == 3:
        query = dedent("""\
        -- Count all rows in the products table 
        SELECT COUNT(*) AS count FROM products;
        """)
        duckdb_query_demo(query)
    
    elif index == 4:
        query = dedent("""\
        -- Product names sample and type
        SELECT 
            product_name,
            typeof(product_name) AS type_colonne
        FROM products 
        LIMIT 5;
        """)
        duckdb_query_demo(query)

    elif index == 55:
        query = dedent("""\
        -- Gets distinct data types from the products table
        SELECT DISTINCT data_type
        FROM information_schema.columns 
        WHERE table_name = 'products'
        ORDER BY data_type;
        """)
        duckdb_query_demo(query)
    
    # Categories
    elif index == 5:
        query = dedent("""\
        -- Products with milk category (French/English)
        SELECT
            code,
            unnest(
                list_filter (product_name, x -> x.lang == 'main')
            )['text'] AS product_name
        FROM products
        WHERE list_contains(categories_tags, 'en:%milks%')
           OR list_contains(categories_tags, 'fr:%laits%')
        LIMIT 10;
        """)
        duckdb_query_demo(query)
    
    elif index == 25:
        query = dedent("""
        -- Search categories with 'chocolat' or 'chocolate'
        SELECT DISTINCT
            unnest AS category
        FROM products,
            unnest(categories_tags) AS unnest 
        WHERE category LIKE 'fr:%chocolat%' 
        OR category LIKE 'en:%chocolate%'
        ORDER BY category
        LIMIT 30;
        """)
        duckdb_query_demo(query)
    elif index == 26:
        query = dedent("""\
        -- Products containing 'chocolat' or 'chocolate' in their French/English categories
        SELECT DISTINCT
            code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            categories_tags
        FROM products
        WHERE array_to_string(categories_tags, ',') LIKE 'fr:%chocolat%' 
        OR array_to_string(categories_tags, ',') LIKE 'en:%chocolate%'
        LIMIT 10;
        """)
        duckdb_query_demo(query)

    # Allergen tags
    elif index == 9:
        query = dedent("""\
        -- Search in the list `allergen_tags` values containing `fr`
        SELECT count(code) AS nb, ANY_VALUE(code) AS code, allergens_tags
        FROM products
        WHERE regexp_matches(array_to_string(allergens_tags, ','), 'fr:')
        GROUP BY allergens_tags
        ORDER BY nb desc
        """)
        duckdb_query_demo(query, "")
    elif index == 20:
        query = dedent("""\
        -- Products avec allergies aux arachides
        SELECT
            code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
        allergens_tags
        FROM products
        WHERE list_contains(allergens_tags, 'en:peanuts') 
        OR list_contains(allergens_tags, 'fr:arachides')
        LIMIT 10;
        """)
        duckdb_query_demo(query)

    # NOVA groups
    elif index == 10:
        query = dedent("""\
        -- Number of products per NOVA group
        SELECT nova_group, count(*) AS count
        FROM products
        WHERE nova_group IS NOT NULL
        GROUP BY nova_group
        ORDER BY nova_group;
        """)
        duckdb_query_demo(query)

    # Scores
    elif index == 11:
        query = dedent("""\
        -- Average Nutri-Score by brand with more than 100 products
        SELECT 
            unnest AS brand,
            avg(nutriscore_score) AS avg_score,
            count(*) AS products
        FROM products,
             unnest(brands_tags) AS unnest
        GROUP BY brand
        HAVING count(*) > 100
        ORDER BY avg_score;
        """)
        duckdb_query_demo(query)
    elif index == 21:
        query = dedent("""\
        -- Products without palm oil and good Nutri-Score
        SELECT code, 
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            nutriscore_grade
        FROM products 
        WHERE ingredients_from_palm_oil_n = 0
        AND nutriscore_grade IN ('a','b')
        LIMIT 10;
        """)
        duckdb_query_demo(query)
    elif index == 19:
        query = dedent("""\
        -- Products by ecoscore grade
        SELECT 
            ecoscore_grade,
            count(*) as count,
            avg(ecoscore_score) as avg_score
        FROM products
        WHERE ecoscore_grade IS NOT NULL
        GROUP BY ecoscore_grade
        ORDER BY avg_score DESC;
        """)
        duckdb_query_demo(query)

    # Ingredients 
    elif index == 12:
        query = dedent("""\
        -- Products with palm oil
        SELECT 
            code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            ingredients_from_palm_oil_n
        FROM products 
        WHERE ingredients_from_palm_oil_n > 0;
        """)
        duckdb_query_demo(query)
    elif index == 13:
        query = dedent("""\
        -- Products with most ingredients
        SELECT 
            code, 
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            ingredients_n
        FROM products
        WHERE ingredients_n IS NOT NULL
        ORDER BY ingredients_n DESC
        LIMIT 10;
        """)
        duckdb_query_demo(query)

    # Vitamins
    elif index == 14:            
        query = dedent("""\
        -- Most common vitamins
        SELECT 
            unnest AS vitamin,
            count(*) AS count
        FROM products,
            unnest(vitamins_tags) AS unnest
        GROUP BY vitamin
        ORDER BY count DESC;
        """)
        duckdb_query_demo(query)

    # Serving size
    elif index == 15:
        query = dedent("""\
        -- Products by serving size
        SELECT serving_size, count(*) AS count
        FROM products
        WHERE serving_size IS NOT NULL
        GROUP BY serving_size
        ORDER BY count DESC
        LIMIT 10;
        """)
        duckdb_query_demo(query)

    # Labels
    elif index == 16:
        query = dedent("""\
        -- Most used labels
        SELECT 
            unnest AS label,
            count(*) AS count
        FROM products,
            unnest(labels_tags) as unnest
        GROUP BY label
        ORDER BY count DESC
        LIMIT 10;
        """)
        duckdb_query_demo(query)
    elif index == 22:
        query = dedent("""\
        -- Organic products
        SELECT code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name
        FROM products
        WHERE list_contains(labels_tags, 'en:organic')
        LIMIT 10;
        """)
        duckdb_query_demo(query)
    
    # Stores
    elif index == 17:
        query = dedent("""\
        -- Products by store
        SELECT 
            unnest as store_name,
            count(*) as count
        FROM products,
            unnest(stores_tags) as unnest
        GROUP BY store_name
        ORDER BY count DESC
        LIMIT 5;
        """)
        duckdb_query_demo(query)

    # Completeness
    elif index == 18:
        query = dedent("""\
        -- Complete vs incomplete products
        SELECT 
            complete,
            count(*) as count,
            avg(completeness) as avg_completeness
        FROM products
        GROUP BY complete;
        """)
        duckdb_query_demo(query)
    
    # Food group
    elif index == 23:
        query = dedent("""\
        -- Products by food group
        SELECT 
            unnest AS food_group,
            count(*) AS count
        FROM products,
            unnest(food_groups_tags) AS unnest
        GROUP BY food_group
        ORDER BY count DESC;
        """)
        duckdb_query_demo(query)

    # Creation dates
    elif index == 24:
        query = dedent("""\
        -- Recently added products
        SELECT code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            to_timestamp(created_t) AS added_date
        FROM products
        WHERE created_t IS NOT NULL
        ORDER BY created_t DESC
        LIMIT 10;
        """)
        duckdb_query_demo(query)
    elif index == 7:
        query = dedent("""\
        -- Top 10 best contributors in Open Food Facts
        SELECT creator, count(*) AS count
        FROM products
        GROUP BY creator
        ORDER BY count DESC
        LIMIT 10;
        """)
        duckdb_query_demo(query)
    elif index == 8:
        query = dedent("""\
        -- Number of added products per year
        SELECT
            entry_dates_tags[3] AS year, count(*) AS count
        FROM products
        GROUP BY year
        ORDER BY year DESC;
        """)
        duckdb_query_demo(query)

    elif index == 30:
        query = dedent("""\
        -- Products containing 'café', 'cafe', or 'coffee' in their generic name
        SELECT product_name, generic_name
        FROM products
        WHERE lower(generic_name::VARCHAR) LIKE '%café%'
           OR lower(generic_name::VARCHAR) LIKE '%cafe%'
           OR lower(generic_name::VARCHAR) LIKE '%coffee%';
        """)
        duckdb_query_demo(query)
    elif index == 31:
        query = dedent("""\
        -- Find products with all ingredients marked as vegan (no non-vegan or maybe-vegan ingredients)
        -- The ingredients column contains a JSON array where each ingredient has a "vegan" property
        -- that can be "yes", "no", or "maybe". We extract and clean the "text" field of each ingredient.
        --
        -- Example of ingredients JSON structure:
        -- [{"text": "water", "vegan": "yes"}, {"text": "sugar", "vegan": "yes"}]
        --
        -- The query:
        -- 1. Filters for products with only vegan ingredients using LIKE on the raw JSON
        -- 2. Extracts the text field for each ingredient using json_extract
        -- 3. Cleans up the extracted text by removing brackets and quotes
        -- 4. Returns the brand and a comma-separated list of ingredients
        WITH ingredient_array AS (
            SELECT 
                brands,
                TRY_CAST(ingredients AS JSON) AS ingredients_json
            FROM products
            WHERE ingredients IS NOT NULL
            AND ingredients != '[]'
            AND ingredients LIKE '%"vegan":"yes"%'    -- Has at least one vegan ingredient
            AND NOT ingredients LIKE '%"vegan":"no"%'  -- No non-vegan ingredients
            AND NOT ingredients LIKE '%"vegan":"maybe"%' -- No maybe-vegan ingredients
        ),
        clean_ingredients AS (
            SELECT 
                brands,
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        json_extract(ingredients_json, '$[*].text')::VARCHAR,
                        '[\[\]]',
                        ''
                    ),
                    '"',
                    ''
                ) as ingredients_list
            FROM ingredient_array
        )
        SELECT 
            brands,
            ingredients_list
        FROM clean_ingredients
        WHERE LENGTH(ingredients_list) > 0
        LIMIT 10;
        """)
        duckdb_query_demo(query)

    elif index == 101:
        query = dedent("""\
        SELECT 
  last_editor,
  COUNT(*) as frequency
FROM products 
WHERE last_editor IS NOT NULL
GROUP BY last_editor
ORDER BY frequency DESC
LIMIT 10;
       
        """)
        duckdb_query_demo(query)

        query = dedent("""\
        SELECT 
  COUNT(*) as total_products,
  COUNT(DISTINCT last_editor) as unique_editors,
  COUNT(CASE WHEN last_editor IS NOT NULL THEN 1 END) as products_with_editor
FROM products;
        """)
        duckdb_query_demo(query)

def agent_01():
    prompt = "SELECT * FROM products"
    prompt = "Comment faire une tarte aux pommes?"
    prompt = "Bonjour"
    prompt = "Combien de produits dans la base de données?"
    prompt = "Quelles sont les qualités nutritives des pommes?"
    run(prompt)

if __name__ == "__main__":
    #for i in range(1, 20):
    #    sql(i)

    # sql(1)
    sql(101)

    # agent_01()
    # run(prompt)
    # load_dict()
