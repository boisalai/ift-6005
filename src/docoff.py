"""
docoff.py: Open Food Facts Database Column Documentation Generator

This script automatically generates comprehensive JSON documentation for columns in the 
Open Food Facts Canadian products database. For each column, it:
- Analyzes data structure and content
- Extracts representative examples
- Identifies common query patterns
- Validates SQL queries
- Generates standardized documentation

Features:
- Uses Claude 3.5 LLM for intelligent analysis
- Performs DuckDB SQL queries on the database
- Searches Open Food Facts documentation
- Saves documentation in structured JSON format

Documentation format for each column:
{
    "type": "Data type from DuckDB schema",
    "description": "Clear description of the column",
    "examples": [
        "Example 1",
        "Example 2",
        "Example 3"
    ],
    "is_nullable": true/false,
    "common_queries": [
        {
            "description": "Description of query purpose",
            "sql": "SQL query example"
        },
        // Exactly 3 queries per column
    ]
}

Usage:
    python docoff.py

Requirements:
    - DuckDB database file at ../data/food_canada.duckdb
    - Python packages: duckdb, smolagents, litellm, duckduckgo-search
    - Claude 3.5 API access

Author: Alain Boisvert
Date: February 2025
"""
import os
import json
import warnings
from pathlib import Path
from textwrap import dedent
from typing import Dict, Any

import duckdb
from dotenv import load_dotenv
from smolagents import (
    CodeAgent,
    Tool,
    ToolCallingAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
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
DOCS_DIR = DATA_DIR / "docs"

class DuckDBSearchTool(Tool):
    name = "sql_engine"
    description = dedent(
        """\
    Execute SQL queries on the Open Food Facts Canadian products database using
    DuckDB syntax. The database contains a single table named `products` with
    detailed information about food items.

    IMPORTANT: Always use LIMIT 50 in your queries.

    EXAMPLE DUCKDB QUERIES TO USE:
    ```sql
    -- Basic column information
    SELECT data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'products' 
    AND column_name = '[column_name]'
    LIMIT 50;

    -- Show detailed information about columns in the products table
    SELECT * FROM pragma_table_info('products') 
    WHERE name = 'column_name' 
    LIMIT 50;

    -- Sample values
    SELECT DISTINCT [column_name]
    FROM products
    LIMIT 50;

    -- Value distribution
    SELECT 
        COUNT(*) as total_rows,
        COUNT(CASE WHEN [column_name] IS NULL THEN 1 END) as null_count,
        COUNT(DISTINCT [column_name]) as unique_values
    FROM products
    LIMIT 50;
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

    def truncate_str(self, s: str, max_length: int = 50) -> str:
        """Truncate string if longer than max_length and add ellipsis"""
        s = str(s)  # Convert any non-string input to string
        if len(s) <= max_length:
            return s
        return s[:max_length-3] + "..."

    def format_output(self, columns: list, rows: list) -> Dict[str, Any]:
        """Format output as JSON dictionary"""
        limited_rows = rows[:50]  # Limit to 50 rows for display

        # Truncate all string values in rows
        formatted_rows = []
        for row in limited_rows:
            formatted_row = tuple(self.truncate_str(item, 100) for item in row)
            formatted_rows.append(formatted_row)

        return {
            "columns": columns,
            "rows": formatted_rows,
            "row_count": len(limited_rows),
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


class WriteTool(Tool):
    name = "write_tool"
    description = "Creates and updates JSON documentation for database columns"
    inputs = {
        "column_name": {
            "description": "Name of the column.",
            "type": "string"
        },
        "type": {
            "description": "Technical data type from DuckDB schema.",
            "type": "string"
        },
        "description": {
            "description": "Clear description of the column's content.",
            "type": "string"
        },
        "examples": {
            "description": "Array of exactly 3 real examples from the database.",
            "type": "array"
        },
        "is_nullable": {
            "description": "Whether the column can contain NULL values.",
            "type": "boolean"
        },
        "common_queries": {
            "description": "List of useful queries for this column.",
            "type": "array"
        }
    }
    output_type = "string"

    def __init__(self, docs_dir: Path):
        super().__init__()
        self.docs_dir = docs_dir
        self.docs_dir.mkdir(exist_ok=True)
        self.file_path = self.docs_dir / "columns_documentation.json"
        
        # Initialize or load documentation
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:  # Ajout de la vérification de taille
            self.doc_data = {
                "tables": {
                    "products": {
                        "description": "Main table containing information about food products",
                        "columns": {}
                    }
                }
            }
            self._save_doc()
        else:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.doc_data = json.load(f)
            except json.JSONDecodeError:
                # Si le fichier est corrompu, on réinitialise
                self.doc_data = {
                    "tables": {
                        "products": {
                            "description": "Main table containing information about food products",
                            "columns": {}
                        }
                    }
                }
                self._save_doc()

    def _save_doc(self):
        """Save documentation to JSON file with proper formatting"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.doc_data, f, indent=2, ensure_ascii=False)

    def forward(self, column_name: str, type: str, description: str, 
                examples: list, is_nullable: bool, common_queries: list) -> str:
        """Add or update column documentation"""
        try:
            # Validate number of examples
            if len(examples) != 3:
                return f"Error: Must provide exactly 3 examples. Got {len(examples)}."
            if len(common_queries) != 3:
                return f"Error: Must provide exactly 3 common queries. Got {len(common_queries)}."
        
            # Create column documentation
            column_doc = {
                "type": type,
                "description": description,
                "examples": examples,
                "is_nullable": is_nullable,
                "common_queries": common_queries
            }
            
            # Add or update column in documentation
            self.doc_data["tables"]["products"]["columns"][column_name] = column_doc
            
            # Save updated documentation
            self._save_doc()
            
            return f"Documentation for column '{column_name}' successfully written."
        except Exception as e:
            return f"Error writing documentation: {str(e)}"

    def get_documented_columns(self) -> set:
        """Return set of column names that have been documented"""
        return set(self.doc_data["tables"]["products"]["columns"].keys())

model = LiteLLMModel("anthropic/claude-3-5-sonnet-latest")

sql_tool = DuckDBSearchTool(db_path=FILTERED_DB_PATH)
web_search_tool = FoodGuideSearchTool()
visit_webpage = VisitWebpageTool()
write_tool = WriteTool(docs_dir=DOCS_DIR)

manager_agent = CodeAgent(
    tools=[sql_tool, web_search_tool, visit_webpage, write_tool],
    model=model,
    additional_authorized_imports=["json"],
)

# Additional instructions for primary agent
ADDITIONAL_NOTES = dedent(
    """\
You will analyze and document a database column. Your task is to create JSON 
documentation for a SINGLE column from the 'products' table. Follow these steps:

1. Data Structure Analysis:
   - Execute this query to get the column's data type and nullability:
   ```sql
   SELECT data_type, is_nullable
   FROM information_schema.columns 
   WHERE table_name = 'products' 
   AND column_name = '[column_name]';

2. Sample Data Analysis:
   - Execute this query to get 10 distinct values from the column:
   ```sql
   SELECT DISTINCT [column_name]
   FROM products
   WHERE [column_name] IS NOT NULL
   LIMIT 10;
   ```
   - Document the column's exact data type and structure:
     - For structured types, examine and describe all components
     - For array/list types, analyze the possible values for each field
     - Identify common patterns in the data, special cases or exceptions

3. Search Open Food Facts documentation for this column.

4. Create Column Documentation: 
   - Design useful queries for this column
   - TEST EACH QUERY before including it in the documentation:
     ```sql
     -- Test your query with a LIMIT clause first
     [Your query] LIMIT 5;
     ```
   - Only include queries that successfully execute
   - Each query must return meaningful results
   - Verify joins, filters, and aggregations work as expected

5. Documentation Creation:
   - Use ENGLISH for all documentation fields
   - Generate a JSON object following this exact structure:
     ```json
     {
       "type": "data_type_from_schema",
       "description": "Clear description of the column IN ENGLISH",
       "example": ["array of 3 examples from the data"],
       "is_nullable": true_or_false,
       "common_queries": [
          {
            "description": "Description of query purpose IN ENGLISH",
            "sql": "SQL query example (tested and verified to work)"
          },
          {
            "description": "Description of second query purpose IN ENGLISH",
            "sql": "Second SQL query example (tested and verified to work)"
          },
          {
            "description": "Description of third query purpose IN ENGLISH",
            "sql": "Third SQL query example (tested and verified to work)"
          }
        ]
     }
     ```
   - Always include exactly 3 common queries in the `common_queries` array. No more, no less.
   - Example of correct documentation (IN ENGLISH):
     ```json
     {
       "type": "STRUCT(lang VARCHAR, text VARCHAR)[]",
       "description": "Product name in different languages, typically includes main language and translations",
       "examples": [
         "[{'lang': 'fr', 'text': 'Pain complet'}, {'lang': 'en', 'text': 'Whole bread'}, {'lang': 'main', 'text': 'Whole bread'}]",
         "[{'lang': 'en', 'text': 'Milk'}, {'lang': 'main', 'text': 'Milk'}]",
         "[{'lang': 'fr', 'text': 'Yaourt nature'}, {'lang': 'main', 'text': 'Plain yogurt'}]"
       ],
       "is_nullable": true,
       "common_queries": [
         {
           "description": "Get product name in French, fallback to main language or English",
           "sql": "SELECT code, COALESCE(UNNEST(LIST_FILTER(product_name, x -> x.lang = 'fr'))['text'], UNNEST(LIST_FILTER(product_name, x -> x.lang = 'main'))['text'], UNNEST(LIST_FILTER(product_name, x -> x.lang = 'en'))['text']) AS product_name FROM products LIMIT 1000"
         },
         {
           "description": "Get products with missing translations",
           "sql": "SELECT code, product_name FROM products WHERE ARRAY_LENGTH(product_name) < 2 LIMIT 1000"
         },
         {
           "description": "Get products with all three languages (fr, en, main)",
           "sql": "SELECT code, product_name FROM products WHERE list_contains(list_transform(product_name, x -> x.lang), 'fr') AND list_contains(list_transform(product_name, x -> x.lang), 'en') AND list_contains(list_transform(product_name, x -> x.lang), 'main') LIMIT 1000"
         }
       ]
     }
     ```
     """
)

def run_column_documentation(column_name: str) -> None:
    """Documents a specific column from the database."""
    prompt = f"Analyze and document the column '{column_name}' from the products table."
    response = manager_agent.run(
        prompt,
        additional_args={
            "additional_notes": ADDITIONAL_NOTES,
        },
    )
    print(f"Documentation completed for column: {column_name}")
    print(f"Results:\n{response}\n")
    print("-" * 80)

def execute_query(duckdb_path: Path, query: str) -> str:
    try:
        with duckdb.connect(str(duckdb_path)) as con:
            result = con.sql(query)
            # Convertir le résultat en format dictionnaire
            return {
                "columns": result.columns,
                "rows": result.fetchall()
            }
    except Exception as e:
        return f"Error executing query: {e}"

def get_all_columns(duckdb_path: Path) -> list:
    """Retrieve all columns from the 'products' table."""
    query = """
    SELECT column_name
    FROM information_schema.columns 
    WHERE table_name = 'products'
    ORDER BY column_name;
    """
    result = execute_query(duckdb_path, query)
    return [row[0] for row in result["rows"]]

def get_documented_columns(docs_dir: Path) -> set:
    """Retrieve already documented columns from JSON file."""
    doc_file = docs_dir / "columns_documentation.json"
    if not doc_file.exists():
        return set()
    
    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
        return set(doc_data.get("tables", {}).get("products", {}).get("columns", {}).keys())
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in columns_documentation.json")
        return set()

def clean_sql_queries(json_file: Path):
    """Remove newline characters and extra spaces from SQL queries in JSON file."""
    try:
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
        
        # Process each column's documentation
        for column in doc_data.get("tables", {}).get("products", {}).get("columns", {}).values():
            if "common_queries" in column:
                for query_obj in column["common_queries"]:
                    if isinstance(query_obj, dict) and "sql" in query_obj:
                        # Clean the SQL query string
                        query_obj["sql"] = " ".join(query_obj["sql"].split())
        
        # Write back the cleaned data
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)
        print("SQL queries cleaned successfully.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in columns_documentation.json")
    except Exception as e:
        print(f"Error cleaning SQL queries: {str(e)}")

if __name__ == "__main__":
    duckdb_path = FILTERED_DB_PATH

    # Get all columns
    columns = get_all_columns(duckdb_path)

    # print(f"Found {len(columns)} columns to document.")
    # for col in columns:
    #    print(f"- {col}")

    # Get already documented columns
    documented_columns = get_documented_columns(DOCS_DIR)
    print(f"Documented columns: {documented_columns}")

    # Filter undocumented columns
    columns_to_process = [col for col in columns if col not in documented_columns]
    print(f"Found {len(columns_to_process)} columns remaining to document.")

    # Document remaining columns
    for i, column in enumerate(columns_to_process, 1):
        if i >= 5:
            break
        print(f"\nProcessing column {i}/{len(columns_to_process)}: {column}")
        try:
            run_column_documentation(column)
        except Exception as e:
            print(f"Error processing column {column}: {str(e)}")
            continue

    JSON_FILE = DOCS_DIR / "columns_documentation.json"
    clean_sql_queries(JSON_FILE)