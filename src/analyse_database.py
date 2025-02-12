import os
import re
import json
import warnings
from pathlib import Path
from textwrap import dedent
from typing import Dict, Any, Union
from pydantic import BaseModel, Field

import requests
import markdownify
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

# Check if data folder and files exist
if not DATA_DIR.exists():
    raise FileNotFoundError(f"Data directory '{DATA_DIR}' not found.")
elif not FILTERED_DB_PATH.exists():
    raise FileNotFoundError(f"Database '{FILTERED_DB_PATH}' not found.")


class DuckDBSearchTool(Tool):
    name = "sql_engine"
    description = dedent(
        """\
    Execute SQL queries on the Open Food Facts Canadian products database using
    DuckDB syntax. The database contains a single table named `products` with
    detailed information about food items.

    EXAMPLE DUCKDB QUERIES TO USE:
    ```sql
    -- Basic column information
    SELECT data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'products' 
    AND column_name = '[column_name]';

    -- Show detailed information about columns in the products table
    SELECT * FROM pragma_table_info('products') WHERE name = 'column_name';

    -- Sample values
    SELECT DISTINCT [column_name]
    FROM products
    LIMIT 10;

    -- Value distribution
    SELECT 
        COUNT(*) as total_rows,
        COUNT(CASE WHEN [column_name] IS NULL THEN 1 END) as null_count,
        COUNT(DISTINCT [column_name]) as unique_values
    FROM products;
    ```

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

    def format_output(self, columns: list, rows: list) -> Dict[str, Any]:
        """Format output as JSON dictionary"""
        return {
            "columns": columns,
            "rows": [tuple(str(item) for item in row) for row in rows],
            "row_count": len(rows),
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
    Performs a web search in the Open Food Facts website based on your query.
    """
    )

    def forward(self, query: str) -> str:
        en_results = self.ddgs.text(
            "site:https://world.openfoodfacts.org/ " + query,
            max_results=self.max_results,
        )
        fr_results = self.ddgs.text(
            "site:https://github.com/openfoodfacts/ " + query,
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

class WriteTool(Tool):
    name = "write_tool"
    description = "This is a tool that writes column documentation to a documentation file"
    inputs = {
        "column_name": {
            "description": "Name of the column.",
            "type": "string"
        },
        "description": {
            "description": "Brief description (max 200 chars).",
            "type": "string"
        },
        "data_type": {
            "description": "Technical type info (max 100 chars).",
            "type": "string"
        },
        "structure": {
            "description": "Field structure details (max 100 chars).",
            "type": "string"
        },
        "purpose": {
            "description": "Main use of the column (max 100 chars).",
            "type": "string"
        },
        "analysis": {
            "description": "Analysis findings (max 100 chars).",
            "type": "string"
        },
        "web_research": {
            "description": "Info from Open Food Facts (max 100 chars).",
            "type": "string"
            
        }
    }
    output_type = "string"

    def __init__(self, docs_dir: Path):
        super().__init__()
        self.docs_dir = docs_dir
        self.docs_dir.mkdir(exist_ok=True)
        self.file_path = self.docs_dir / "columns_documentation.md"

    def forward(self, column_name: str, description: str, data_type: str, 
                structure: str, purpose: str, analysis: str, 
                web_research: str) -> str:
        try:
            # Format the content
            formatted_content = dedent(f"""\
                ## {column_name}
                - Description: {description}
                - Data Type: {data_type}
                - Structure: {structure}
                - Purpose: {purpose}
                - Analysis: {analysis}
                - Web Research: {web_research}
            """)
            
            # Append content to file
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(formatted_content)
                f.write("\n")
                            
            return f"Documentation for column '{column_name}' written successfully."
        except Exception as e:
            return f"Error writing documentation: {str(e)}"

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
            max_tokens=1024,
        )

    if type_engine == "claude-sonnet":
        # Requires an API key from Anthropic
        # $15/MTok (see https://www.anthropic.com/pricing#anthropic-api)
        return LiteLLMModel(
            model_id="anthropic/claude-3-5-sonnet-latest",
            max_tokens=1024,
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


web_search_tool = FoodGuideSearchTool()
sql_tool = DuckDBSearchTool(db_path=FILTERED_DB_PATH)

# model = create_model("claude-sonnet") # "claude-sonnet" or "claude-haiku" or "ollama/phi4:latest" ou "ollama/qwen:14b"
model = create_model("claude-haiku") # "claude-sonnet" or "claude-haiku" or "ollama/phi4:latest" ou "ollama/qwen:14b"

web_agent = ToolCallingAgent(
    tools=[web_search_tool, visit_webpage], model=model, max_steps=3
)
managed_web_agent = ManagedAgent(
    agent=web_agent,
    name="search",
    description=dedent(
        """\
    Search the Open Food Facts site for information about the data and columns in the database
    """
    ),
)

sql_agent = ToolCallingAgent(tools=[sql_tool], model=model, max_steps=3)
managed_sql_agent = ManagedAgent(
    agent=sql_agent,
    name="search",
    description=dedent(
        """\
    Queries the Open Food Facts products database using DuckDB SQL syntax.
    Input a valid DuckDB SQL query to search product information."""
    ),
)

write_tool = WriteTool(docs_dir=DATA_DIR/"docs")
write_agent = ToolCallingAgent(tools=[write_tool], model=model, max_steps=1)
managed_write_agent = ManagedAgent(
    agent=write_agent,
    name="write",
    description=dedent(
        """\
    Writes column documentation to a documentation file."""
    ),
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[managed_web_agent, managed_sql_agent, managed_write_agent],
    additional_authorized_imports=["json"],
)

# Additional instructions for primary agent
# Additional instructions for primary agent
ADDITIONAL_NOTES = dedent(
    """\
You will receive the name of the column ([column_name]) to analyze. Your task 
is to analyze and document this SINGLE column from the 'products' table in a 
DuckDB database. Focus ONLY on this specific column. When given a column name, follow these steps:

1. Data Structure Analysis:
   - Execute this query:
   ```sql
   SELECT data_type
   FROM information_schema.columns 
   WHERE table_name = 'products' 
   AND column_name = '[column_name]';
   ```
   Document:
     * The column's exact data type and structure
     * For structured types, examine and describe all components
     * For array/list types, analyze the possible values for each field

2. Sample Data Analysis:
   - Execute this query:
   ```sql
   SELECT DISTINCT [column_name]
   FROM products
   LIMIT 10;
   ```
   Identify:
     * Common patterns in the data
     * Variations in structure
     * Special cases or exceptions

3. Web Research:
   - Search the Open Food Facts website for 
     information about THIS specific column's [column_name] 
     standard definitions and uses

4. Documentation:
   - Call the write_tool with all required arguments:
     ```python
     write_tool(
         column_name="the_name",         # Name of the column
         description="description",      # Brief description (max 200 chars)
         data_type="type_info",         # Technical type info (max 100 chars)
         structure="structure_info",     # Field structure details (max 100 chars)
         purpose="main_purpose",         # Main use of the column (max 100 chars)
         analysis="findings",            # Analysis findings (max 100 chars)
         web_research="off_info"         # Info from Open Food Facts (max 100 chars)
     )
     ```
   - Example of correct usage:
     ```python
     write_tool(
         column_name="product_name",
         description="Name of the product in different languages",
         data_type="STRUCT(lang VARCHAR, text VARCHAR)[]",
         structure="[{'lang': [main|en|fr], 'text': [name of product]}]",
         purpose="Stores multilingual product names",
         analysis="Contains names in main language plus translations",
         web_research="Standard field in Open Food Facts database"
     )
     ```
"""
)


def run(prompt: str) -> None:
    response = manager_agent.run(
        prompt,
        additional_args={
            "additional_notes": ADDITIONAL_NOTES,
        },
    )
    print(f"Results:\n{response}")


if __name__ == "__main__":
    # prompt = "Quelles sont les qualités nutritives des pommes?"
    # prompt = "Bonjour"
    PROMPT = "product_name"
    run(PROMPT)
