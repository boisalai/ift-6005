"""
Changes:
- Version 17:
    - Added sqlglot and validate_query() function
- Version 18:
    - Added docs_path = DATA_DIR / "columns_documentation.json"
    - Ajout de la recherche sémantique avec FAISS pour la documentation de la base de données
"""
import os
import json
import warnings
import logging
from pathlib import Path
from dataclasses import dataclass
from textwrap import dedent
from typing import List, Dict, Any, Union

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import duckdb
import sqlglot
from dotenv import load_dotenv
import requests
from smolagents import (
    Tool,
    CodeAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    HfApiModel,
    LiteLLMModel,
    MLXModel
)

# Disable specific warnings
warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Logs configuration
os.environ["LITELLM_LOG"] = "INFO"  # Change to 'DEBUG' for more details

# Define file paths
DATA_DIR = Path("../data")
DOCS_DIR = Path("../docs")


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
    if type_engine.startswith("ollama/") and type_engine in [
        "ollama/qwen2.5-coder:3b",
        "ollama/phi4:latest",
        "ollama/qwen:14b"
        "ollama/deepseek-r1:latest",
        "ollama/llama3.1:8b-instruct-q8_0"
    ]:
        # Free for local use, but requires a license for commercial use
        return LiteLLMModel(
            model_id=type_engine,
            api_base="http://localhost:11434",
            num_ctx=8192
        )

    if type_engine == "mlx":
        return MLXModel("mlx-community/Qwen2.5-Coder-32B-Instruct-4bit")

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

@dataclass
class ColumnMetadata:
    """Metadata for each column"""
    name: str
    type: str
    description: str
    examples: List[Any]
    common_queries: List[Dict[str, str]]


class FaissDocumentationTool(Tool):
    name = "faiss_docs"
    description = dedent(
        """\
        Searches the Open Food Facts database documentation using FAISS vector similarity.
        
        PURPOSE:
        This tool helps identify relevant database columns and query patterns for user requests by:
        - Finding columns semantically related to the user's question
        - Providing SQL query examples and best practices
        - Explaining data structures and types
        - Suggesting appropriate query patterns
        
        WORKFLOW:
        1. Process user's natural language query
        2. Review returned columns by similarity score (>0.7 indicates high relevance)
        3. Check column types and adapt query patterns accordingly
        4. Use provided SQL examples as templates
        5. Consider data structure notes for complex fields
        
        RESPONSE FORMAT:
        The tool returns a JSON-formatted string that must be parsed using json.loads() before use. The parsed structure will be:
        ```json
        {
            "columns": [
                {
                    "name": "column_name",
                    "type": "data_type",
                    "description": "column_description",
                    "similarity": 0.85,
                    "examples": ["example1", "example2"],
                    "common_queries": [
                        {"description": "query_description", "sql": "SELECT ..."}
                    ]
                }
            ],
            "sql_examples": {
                "column_name": ["SELECT ...", "SELECT ..."]
            },
            "metadata": {
                "total_columns": 42,
                "query_embedding_dim": 768
            }
        }
        ```
        
        IMPORTANT: Since this tool returns a JSON-formatted string, you must first parse it with:
        ```python
        import json
        columns_info_str = faiss_docs(query) 
        columns_info = json.loads(columns_info_str)
        relevant_columns = [column['name'] for column in columns_info.get('columns', []) if column.get('similarity') > 0.7]
        ```

        After parsing, you can access the relevant columns and their metadata to construct SQL queries.
        
        QUERY CONSTRUCTION GUIDELINES:
        1. Multilingual Fields:
           - Use list_filter() to select language
           - Access text with ['text'] operator
           - Example: unnest(list_filter(product_name, x -> x.lang == 'fr'))['text']
        
        2. Array Fields:
           - Use list_contains() for exact matches
           - Use unnest() for pattern matching
           - Handle potential duplicates with DISTINCT
           - Example: list_contains(categories_tags, 'en:organic')
        
        3. Data Quality:
           - Always handle NULL values with COALESCE()
           - Check array length before accessing elements
           - Consider data completeness (use metadata)
           - Add appropriate LIMIT clauses
        
        4. Performance:
           - Filter data early in the query
           - Use appropriate indexes
           - Avoid unnecessary UNNEST operations
           - Limit result sets appropriately
        
        IMPORTANT:
        - Review similarity scores to ensure relevance
        - Consider multiple columns for complex queries
        - Always validate data types before operations
        - Follow provided SQL patterns for consistent results
        - Handle missing data appropriately
        """
    )

    inputs = {
        "query": {
            "type": "string",
            "description": "Natural language query about database content, structure, or how to query specific information"
        }
    }
    output_type = "string"

    def __init__(
        self, docs_path: Path, cache_dir: Path, model_name: str = "all-MiniLM-L6-v2"
    ):
        super().__init__()
        self.docs_path = docs_path
        self.cache_dir = cache_dir
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product index

        # Store column metadata
        self.columns: List[ColumnMetadata] = []
        self.setup()

        # Initialize or load FAISS index from cache
        cache_file = self.cache_dir / "docs_faiss.index"
        if cache_file.exists():
            # Load cached index
            self.index = faiss.read_index(str(cache_file))
        else:
            # Create new index and cache it
            self.setup()
            cache_dir.mkdir(exist_ok=True)
            faiss.write_index(self.index, str(cache_file))

    def setup(self) -> None:
        """Initialize FAISS index with documentation embeddings"""
        try:
            # Charger la documentation
            with open(self.docs_path) as f:
                docs = json.load(f)

            # Vérifier la structure du document
            if "tables" not in docs or "products" not in docs["tables"]:
                raise ValueError("Invalid documentation structure: missing tables/products")

            # S'assurer que nous avons la section columns
            columns = docs["tables"]["products"].get("columns", {})
            if not columns:
                raise ValueError("No columns found in documentation")

            # Vider les listes existantes pour éviter les doublons
            self.columns.clear()
            
            # Traiter chaque colonne
            embeddings = []
            for col_name, col_info in columns.items():
                # Créer un texte descriptif pour l'embedding en vérifiant les champs requis
                if not all(key in col_info for key in ["type", "description"]):
                    print(f"Warning: Column {col_name} missing required fields")
                    continue

                # Construire le texte à encoder
                text_to_embed = (
                    f"Column {col_name} ({col_info['type']}): {col_info['description']}"
                )

                # Ajouter les exemples s'ils existent
                if "examples" in col_info:
                    examples_str = str(col_info["examples"])
                    if len(examples_str) > 500:  # Limiter la longueur des exemples
                        examples_str = examples_str[:500] + "..."
                    text_to_embed += f" Examples: {examples_str}"

                try:
                    # Générer l'embedding
                    embedding = self.model.encode(text_to_embed)
                    embeddings.append(embedding)

                    # Stocker les métadonnées
                    self.columns.append(ColumnMetadata(
                        name=col_name,
                        type=col_info["type"],
                        description=col_info["description"],
                        examples=col_info.get("examples", []),
                        common_queries=col_info.get("common_queries", [])
                    ))
                except Exception as embed_error:
                    print(f"Error processing column {col_name}: {str(embed_error)}")
                    continue

            # Vérifier que nous avons des embeddings
            if not embeddings:
                raise ValueError("No embeddings were created")

            # Ajouter les embeddings à l'index FAISS
            embeddings_array = np.array(embeddings).astype('float32')
            self.index.add(embeddings_array)

            print(f"Successfully initialized FAISS index with {len(embeddings)} columns")
            self.is_initialized = True

        except Exception as e:
            print(f"Error initializing FAISS index: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant columns using FAISS"""
        try:
            # Vérifier que nous avons des données indexées
            if len(self.columns) == 0:
                raise ValueError("No columns available in the index")

            # Generate query embedding
            query_embedding = self.model.encode(query)
            query_embedding = np.array([query_embedding]).astype('float32')

            # Vérifier la dimensionnalité
            if query_embedding.shape[1] != self.dimension:
                raise ValueError(f"Query embedding dimension {query_embedding.shape[1]} does not match index dimension {self.dimension}")

            # Search FAISS index with dimension checks
            top_k = min(top_k, len(self.columns))  # S'assurer que top_k ne dépasse pas le nombre de colonnes
            similarities, indices = self.index.search(query_embedding, top_k)

            # Format results
            results = []
            for similarity, idx in zip(similarities[0], indices[0]):
                if idx < 0 or idx >= len(self.columns):
                    continue  # Ignorer les index invalides
                col_data = self.columns[idx]
                results.append({
                    "name": col_data.name,
                    "type": col_data.type,
                    "description": col_data.description,
                    "similarity": float(similarity),
                    "examples": col_data.examples,
                    "common_queries": col_data.common_queries
                })

            return results

        except Exception as e:
            print(f"Search failed: {str(e)}")
            return []  # Retourner une liste vide en cas d'erreur
            
    def get_sql_examples(self, columns: List[str]) -> Dict[str, List[str]]:
        """Get SQL examples for the specified columns"""
        examples = {}
        for col_name in columns:
            col_examples = []
            for col in self.columns:
                if col.name == col_name:
                    col_examples.extend([q["sql"] for q in col.common_queries])
            if col_examples:
                examples[col_name] = col_examples
        return examples

    def forward(self, query: str) -> str:
        """Process query and return relevant documentation"""
        print(f"DEBUG-309: Searching for query: {query}")
        try:
            # Search for relevant columns
            search_results = self.search(query)

            # Get SQL examples
            col_names = [result["name"] for result in search_results]
            sql_examples = self.get_sql_examples(col_names)

            # Prepare response
            response = {
                "columns": search_results,
                "sql_examples": sql_examples,
                "metadata": {
                    "total_columns": len(self.columns),
                    "query_embedding_dim": self.dimension
                }
            }

            return json.dumps(response, indent=2)

        except Exception as e:
            return json.dumps({"error": f"Search failed: {str(e)}"})


class DuckDBSearchTool(Tool):
    name = "sql_db"
    description = dedent(
        """\
    Execute SQL queries using DuckDB syntax. The database contains a single table named `products` with
    detailed information about food items.

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

    def validate_query(self, query: str) -> tuple[bool, str]:
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
    name = "web_search"
    description = dedent(
        """\
    Searches Canada's Food Guide official websites (English and French) for nutrition and dietary information.
    
    PURPOSE:
    This tool helps find official Canadian dietary guidelines and recommendations by:
    - Searching both English and French versions of Canada's Food Guide
    - Verifying URL availability
    - Returning relevant content with links
    
    USAGE:
    - Input simple keywords or phrases related to your nutrition question
    - The tool will search:
      * English site: https://food-guide.canada.ca/en/
      * French site: https://guide-alimentaire.canada.ca/fr/
    
    SEARCH TIPS:
    - Use clear, specific terms (e.g., "protein recommendations" rather than just "protein")
    - Try both English and French keywords for better results
    - Keep queries concise (2-4 words typically work best)
    
    RESPONSE FORMAT:
    Returns results in Markdown format with:
    - Article titles with clickable links
    - Brief content descriptions
    - Each result separated by newlines
    
    Example usage:
    query="daily vegetable servings"
    query="recommandations fruits légumes"
    query="healthy protein sources"
    """
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "Keywords to search in Canada's Food Guide websites (English and French versions)"
        }
    }
    output_type = "string"

    def url_exists(self, url: str) -> bool:
        """Vérifie si une URL existe"""
        try:
            response = requests.head(url)
            return response.status_code == 200
        except:
            return False
        
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

        results = []
        for result in en_results + fr_results:
            # Verify that URL exists before including it
            if self.url_exists(result['href']):
                results.append(result)

        if len(results) == 0:
            raise Exception("No results found! Try a less restrictive/shorter query.")
        
        postprocessed_results = [
            f"[{result['title']}]({result['href']})\n{result['body']}"
            for result in results
        ]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)


# model = create_model("claude-sonnet")
# model = create_model("claude-haiku")
model = create_model("ollama/llama3.1:8b-instruct-q8_0")

docs_path = DOCS_DIR / "data" / "columns_documentation.json"
cache_dir = DOCS_DIR / "data" / "cache"
faiss_docs = FaissDocumentationTool(docs_path, cache_dir)

filtered_db_path = DATA_DIR / "food_canada.duckdb"
sql_db = DuckDBSearchTool(db_path=filtered_db_path)

search_webpage = FoodGuideSearchTool()
visit_webpage = VisitWebpageTool()

agent = CodeAgent(
    tools=[faiss_docs, sql_db, search_webpage, visit_webpage],
    model=model,
    additional_authorized_imports=["json"]
)

# Additional instructions for the agent
AGENT_INSTRUCTIONS = dedent(
    """\
Process user prompt by following these precise steps:

1. IDENTIFY QUERY TYPE
   - Greeting: Welcome user and offer food-related assistance
   - Question: Process as information request
   - Conversation: Maintain food/nutrition focus

2. PROCESS INFORMATION REQUEST
   A. First try Open Food Facts database search:
      1. Documentation search phase:
         - Search database documentation using natural language to identify relevant columns
         - Parse returned JSON containing:
           * relevant columns and their metadata
           * example SQL queries
           * similarity scores for relevance
         - Review returned column information (names, types, structures)
         - Note relevant example queries from documentation
         - Only proceed with columns having high similarity (>0.7)
      
      2. Query construction phase:
         - Use only verified column names from documentation search results
         - Follow documented query patterns
         - Implement proper NULL handling
         - Include language filtering for multilingual fields
         - Apply suggested best practices for each data type
      
      3. Execution and presentation phase:
         - Execute the constructed SQL query
         - Format results clearly
         - Note any data limitations
         - Explain potential caveats

   B. If database search insufficient:
      - Search Canada's Food Guide website
      - Focus on official dietary guidance
      - Extract relevant information from search results

3. RESPONSE FORMATTING
   - Match user's language (French/English)
   - Cite information source:
     * "Source: Open Food Facts database" or
     * "Source: Canada's Food Guide"
   - Present information concisely
   - If information unavailable or incomplete:
     * State this clearly
     * Explain any limitations
     * Suggest alternative approaches if relevant

IMPORTANT RULES:
- NEVER assume column names - always verify through documentation search
- Use natural language when searching documentation
- Maintain consistent language throughout response
- Follow strict data handling practices from documentation
- Consider data quality and completeness in responses
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
                "additional_notes": AGENT_INSTRUCTIONS,
            },
        )
        print("Agent answer: ", response)

def run(prompt: str) -> None:
    response = agent.run(
        prompt,
        additional_args={
            "additional_notes": AGENT_INSTRUCTIONS,
        },
    )
    print(f"Results:\n{response}")

if __name__ == "__main__":
    prompt = "Combien de produits dans la base de données?"
    prompt = "Quels sont les produits sans gluten qui ont un bon score nutritionnel?"
    run(prompt)

    # run_interactive()
