"""
# Evaluation Framework for Open Food Facts Conversational Agent

This script implements a comprehensive evaluation framework for testing and measuring 
the performance of a conversational agent designed to query the Open Food Facts database. 
The agent converts natural language questions into SQL queries and provides informative responses 
about food products.

## Key Components:
1. Evaluator Class:
   - Manages the evaluation process for question-answer pairs
   - Connects to DuckDB database containing Open Food Facts data
   - Calculates performance metrics and generates detailed reports
2. QueryResult & EvaluationResult Classes:
   - Data structures for storing query execution results and evaluation outcomes
   - Track success/failure states, execution times, and error messages
3. Performance Metrics:
   a) Execution Accuracy (EX):
      - Measures the ability to generate correct SQL queries
      - Considers query presence, execution success, and result accuracy
      - Weighted scoring: query presence (20%), execution success (30%), results match (50%)
   b) Missing Data Coverage Rate (TCM):
      - Evaluates how well the agent handles incomplete data scenarios
      - Tracks use of alternative data sources and appropriate acknowledgment of data gaps
      - Considers both database coverage and alternative source usage
   c) Average Response Time (TRM):
      - Measures end-to-end processing time for each query
      - Includes query generation, execution, and response formatting

## Key Functions:
- `evaluate_single_case()`: Processes individual test cases and computes metrics
- `calculate_metrics()`: Aggregates results across all test cases
- `_calculate_sql_accuracy()`: Compares generated SQL with reference queries
- `_calculate_semantic_accuracy()`: Evaluates response quality using LLM
- `_calculate_data_coverage()`: Assesses handling of missing data scenarios

## Usage:
The script supports both English and French evaluation cases, with the following features:
- Loads test cases from a JSON file of question-answer pairs
- Connects to a DuckDB database containing Open Food Facts data
- Uses LLM for semantic similarity scoring of responses
- Generates detailed evaluation reports in Markdown format

Example usage:
```python
evaluator = Evaluator(db_path, qa_path, model)
metrics = evaluator.evaluate_all(agent, lang='en')
```

## Output:
Generates both summary metrics and detailed per-question analysis including:
- Overall accuracy scores
- Response time statistics
- Data coverage metrics
- Detailed error logs and execution traces
"""
import json
import time
import re
import sys
from pathlib import Path
from textwrap import dedent

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging
import numpy as np
import sqlglot

from dotenv import load_dotenv
from statistics import mean, median
import requests
import duckdb
from datetime import datetime
from sentence_transformers import SentenceTransformer
import faiss

from smolagents import (
    Tool,
    CodeAgent,
    VisitWebpageTool,
    DuckDuckGoSearchTool,
    LiteLLMModel,
    ToolCallingAgent,
    LogLevel,
    HfApiModel  # Add this line to import HfApiModel
)

# Load environment variables
load_dotenv()

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Create log file with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = log_dir / f"evaluation_{timestamp}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s - %(levelname)s - %(message)s',
    format='%(asctime)s - %(name)s - %(module)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file), mode='w', encoding='utf-8'),
        logging.StreamHandler()  # Also display in console
    ],
    force=True
)

# Create logger at module level
logger = logging.getLogger('food_agent')
logger.setLevel(logging.INFO)  # Ensure logger level matches basicConfig

# Verify logging is working
logger.debug("Technical details useful for debugging")
logger.info("General information about execution progress")
logger.info(f"Logging initialized. Writing to {log_file}")
logger.warning("Non-critical warnings")
logger.error("Important but non-fatal errors")  
logger.critical("Critical errors that prevent evaluation")

def cleanup_old_logs(log_dir: Path, keep_last_n: int = 3) -> None:
    """
    Clean up old log files, keeping only the N most recent ones.
    
    Args:
        log_dir (Path): Directory containing log files
        keep_last_n (int): Number of most recent log files to keep
    """
    # Get all log files
    log_files = list(log_dir.glob("evaluation_*.log"))
    
    # Sort files by modification time (newest first)
    log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Remove old files beyond keep_last_n
    for old_file in log_files[keep_last_n:]:
        try:
            old_file.unlink()
        except Exception as e:
            print(f"Error deleting {old_file}: {e}")

# Clean up old logs
cleanup_old_logs(log_dir)

@dataclass
class QueryResult:
    """Résultat d'exécution d'une requête SQL"""
    success: bool
    results: List[Any]
    error: Optional[str] = None

@dataclass
class EvaluationResult:
    """Résultat d'évaluation d'une question"""
    question_id: int
    language: str  # Langue de l'évaluation ('fr' ou 'en')
    question: str  # Question dans la langue évaluée
    expected_answer: str  # Réponse attendue dans la langue évaluée
    agent_answer: Dict[str, str]  # Réponse de l'agent avec texte et source
    metrics: Dict[str, Any]  # Métriques d'évaluation simplifiées

class QueryDatabaseTool(Tool):
    name = "query_db"
    description = dedent(
        """\
    Execute SQL queries using DuckDB syntax. The database contains a single table
    named `products` with detailed information about food items.

    IMPORTANT QUERY GUIDELINES:
    1. ALWAYS include a LIMIT clause (maximum 100 rows) to avoid large result sets
    2. NEVER use modification clauses (INSERT, UPDATE, DELETE, DROP, ALTER, CREATE)
    3. ALWAYS specify columns explicitly (no SELECT *)
    4. Use list_contains() for array columns (e.g. categories_tags, labels_tags)
    5. Handle multilingual text fields using list_filter() to select language like this:
       ```sql
       SELECT 
            unnest(list_filter(product_name, x -> x.lang == 'en'))['text'] AS name,
            nutriscore_grade,
            COUNT(*) AS count
       FROM products 
       WHERE nutriscore_grade IS NOT NULL
       AND list_contains(categories_tags, 'en:beverages')
       GROUP BY name, nutriscore_grade
       HAVING count > 5
       ORDER BY count DESC
       LIMIT 50
       ```
    3. Multilingual search (categories example):
       ```sql
       WHERE list_contains(categories_tags, 'en:category-name')
          OR list_contains(categories_tags, 'fr:category-name')
       ```
    6. Always include error handling for NULL values
    7. Limit results when appropriate to avoid large result sets
    8. Use LOWER() for case-insensitive searches
    
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
    """
    )

    inputs = {
        "query": {
            "type": "string", 
            "description": "Valid DuckDB SQL query to execute"
        }
    }

    output_type = "string"

    def __init__(self, db_path: Path, max_rows: int = 100):
        """Initializes the database connection and query limits"""
        super().__init__()
        self.db_path = db_path
        self.connection = duckdb.connect(str(self.db_path))
        self.max_rows = max_rows

    def validate_query(self, query: str) -> tuple[bool, str]:
        """Validates a SQL query for security"""
        try:
            # Parse query
            parsed = sqlglot.parse_one(query, dialect='duckdb')
            
            # List of forbidden keywords
            forbidden_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE']
            
            # Convert query to text and check forbidden keywords
            query_text = str(parsed).upper()
            for keyword in forbidden_keywords:
                if keyword in query_text:
                    return False, f"Query not allowed: {keyword} forbidden"

            # Check for SELECT *
            if 'SELECT *' in query_text:
                return False, "SELECT * not allowed - specify columns explicitly"

            # Check for LIMIT clause
            if 'LIMIT' not in query_text:
                return False, "LIMIT clause required"

            # Extract LIMIT value
            limit_matches = re.findall(r'LIMIT\s+(\d+)', query_text)
            if limit_matches:
                limit_value = int(limit_matches[0])
                if limit_value > self.max_rows:
                    return False, f"LIMIT too high (max {self.max_rows})"

            # Check for WHERE in non-aggregated queries
            if ('GROUP BY' not in query_text and 
                'COUNT(' not in query_text and 
                'WHERE' not in query_text):
                return False, "WHERE clause required for non-aggregated queries"

            return True, ""

        except sqlglot.errors.ParseError as e:
            return False, f"SQL syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
        
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

class SearchCanadaFoodGuideTool(DuckDuckGoSearchTool):
    name = "search_food_guide"
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

class Evaluator:
    def __init__(self, db_path: Path, qa_path: Path, model: LiteLLMModel):
        self.db_path = db_path
        self.qa_pairs = self._load_qa_pairs(qa_path)
        self.connection = duckdb.connect(str(db_path))
        self.logger = logging.getLogger('food_agent')
        self.model = model

        # Initialize FAISS components
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = self.sentence_model.get_sentence_embedding_dimension()

        # Define cache paths
        self.cache_dir = Path("../data/cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.faiss_cache = self.cache_dir / "docs_faiss.index"
        self.metadata_cache = self.cache_dir / "columns_metadata.json"

        # Initialize index and metadata
        self.index = None
        self.columns: List[Dict[str, Any]] = []
        
        # Load or create FAISS index and metadata
        self._initialize_faiss()

    def _load_qa_pairs(self, qa_path: Path) -> List[Dict]:
        """Load Q&A pairs from JSON file"""
        with open(qa_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _initialize_faiss(self) -> None:
        """Initialize FAISS index from cache or create new one"""
        try:
            if self._load_from_cache():
                self.logger.info("Successfully loaded FAISS index and metadata from cache")
                return
            
            self.logger.info("Cache not found or invalid, creating new FAISS index")
            self._setup_faiss_index()
            self._save_to_cache()
            
        except Exception as e:
            self.logger.error(f"Error initializing FAISS: {str(e)}")
            raise

    def _load_from_cache(self) -> bool:
        """Load FAISS index and metadata from cache if available"""
        try:
            # Check if both cache files exist
            if not (self.faiss_cache.exists() and self.metadata_cache.exists()):
                return False

            # Load FAISS index
            self.index = faiss.read_index(str(self.faiss_cache))

            # Load columns metadata
            with open(self.metadata_cache, 'r') as f:
                self.columns = json.load(f)

            # Validate index and metadata
            if (self.index.ntotal == len(self.columns) and 
                self.index.d == self.dimension):
                return True
            
            self.logger.warning("Cache validation failed, will recreate index")
            return False

        except Exception as e:
            self.logger.error(f"Error loading cache: {str(e)}")
            return False

    def _save_to_cache(self) -> None:
        """Save FAISS index and metadata to cache"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.faiss_cache))

            # Save columns metadata
            with open(self.metadata_cache, 'w') as f:
                json.dump(self.columns, f, indent=2)

            self.logger.info("Successfully saved FAISS index and metadata to cache")

        except Exception as e:
            self.logger.error(f"Error saving cache: {str(e)}")
            raise

    def _setup_faiss_index(self) -> None:
        """Initialize FAISS index with documentation embeddings"""
        try:
            docs_path = Path("../data/columns_documentation.json")
            with open(docs_path) as f:
                docs = json.load(f)

            if "tables" not in docs or "products" not in docs["tables"]:
                raise ValueError("Invalid documentation structure")

            columns = docs["tables"]["products"].get("columns", {})
            if not columns:
                raise ValueError("No columns found in documentation")

            self.columns.clear()
            embeddings = []
            
            # Create new FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)

            for col_name, col_info in columns.items():
                if not all(key in col_info for key in ["type", "description"]):
                    self.logger.warning(f"Column {col_name} missing required fields")
                    continue

                # Create text to embed
                text_to_embed = f"Column {col_name} ({col_info['type']}): {col_info['description']}"
                if "examples" in col_info:
                    examples_str = str(col_info["examples"])[:500]  # Limit length
                    text_to_embed += f" Examples: {examples_str}"

                try:
                    # Generate embedding
                    embedding = self.sentence_model.encode(text_to_embed)
                    embeddings.append(embedding)

                    # Store column metadata
                    self.columns.append({
                        "name": col_name,
                        "type": col_info["type"],
                        "description": col_info["description"],
                        "examples": col_info.get("examples", []),
                        "common_queries": col_info.get("common_queries", [])
                    })
                except Exception as e:
                    self.logger.error(f"Error processing column {col_name}: {str(e)}")
                    continue

            if not embeddings:
                raise ValueError("No embeddings were created")

            # Add embeddings to FAISS index
            embeddings_array = np.array(embeddings).astype('float32')
            self.index.add(embeddings_array)

            self.logger.info(f"FAISS index initialized with {len(embeddings)} columns")

        except Exception as e:
            self.logger.error(f"Error initializing FAISS index: {str(e)}")
            raise

    def _search_relevant_columns(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for columns relevant to the query using FAISS"""
        try:
            if not self.index or len(self.columns) == 0:
                raise ValueError("FAISS index not initialized")

            # Generate query embedding
            query_embedding = self.sentence_model.encode(query)
            query_embedding = np.array([query_embedding]).astype('float32')

            # Search index
            similarities, indices = self.index.search(query_embedding, min(top_k, len(self.columns)))

            # Format results
            results = []
            for similarity, idx in zip(similarities[0], indices[0]):
                if idx < 0 or idx >= len(self.columns):
                    continue
                col_data = self.columns[idx]
                results.append({
                    "name": col_data["name"],
                    "type": col_data["type"],
                    "description": col_data["description"],
                    "similarity": float(similarity),
                    "examples": col_data["examples"],
                    "common_queries": col_data["common_queries"]
                })

            self.logger.info(f"Found {len(results)} relevant columns for query: {query}")
            for r in results:
                self.logger.info(f"Column '{r['name']}' with similarity {r['similarity']:.3f}")

            return results

        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            return []
                
    def execute_query(self, query: str) -> QueryResult:
        """Execute SQL query and return results"""
        try:
            result = self.connection.execute(query)
            return QueryResult(
                success=True,
                results=result.fetchall()
            )
        except Exception as e:
            return QueryResult(
                success=False,
                results=[],
                error=str(e)
            )

    def _get_agent_response(self, agent, question: str, relevant_columns: List[Dict[str, Any]]) -> Tuple[dict, float]:
        """
        Get response from agent for a given question and measure response time.
        
        Args:
            agent: The agent to query
            question: The question to ask
            relevant_columns: List of relevant columns identified for the question
            
        Returns:
            Tuple[dict, float]: A dictionary containing the agent's response, steps sequence, and other metadata,
                            and response time in seconds
        """
        self.logger.info("Getting agent response")

        # Format column information for the agent
        columns_info = []

        for col in relevant_columns:
            if col['similarity'] > 0.5:  # Only include highly relevant columns
                # Basic column information
                column_section = [
                    f"Column: {col['name']}\n"
                    f"Type: {col['type']}\n"
                    f"Description: {col['description']}\n"
                    f"Examples of values: {', '.join(map(str, col['examples'][:3]))}"
                ]
                
                # Add query examples directly after the column
                if 'common_queries' in col and col['common_queries']:
                    column_section.append(f"Query examples:")
                    for query in col['common_queries']:
                        column_section.append(
                            f"# {query.get('description', '')}:\n"
                            f"{query.get('sql', '')}"
                        )
                
                # Join all information for this column
                columns_info.append("\n".join(column_section))

        # Combine all column sections
        columns_text = "\n\n".join(columns_info)

        additional_notes = dedent(
            """\
            You are a helpful assistant that answers questions about food products 
            using the Open Food Facts database.

            POTENTIALLY RELEVANT COLUMNS:
            The following columns have been identified through semantic search as potentially relevant, 
            with their similarity scores (higher means more likely relevant):
            
            {columns_text}

            SEARCH SEQUENCE RULES:
            1. ALWAYS start with database queries using the most relevant columns
            2. If initial query fails, try alternative database queries with different columns or approaches
            3. Only if database queries are unsuccessful, search the Canada Food Guide
            4. Document EVERY attempt in the steps array, including failures
            5. Never skip straight to Food Guide without trying database first
            6. Always include the source of the information in the answer ("Open Food Facts" or "Canada Food Guide")
            7. Always respond in the same language as the question (French or English)
            
            RESPONSE FORMAT REQUIREMENTS:
            1. Provide ONLY the natural language answer to the user's question
            2. Maximum response length: 200 characters
            3. DO NOT include SQL queries, code snippets, or technical details
            4. DO NOT explain your reasoning or methodology
            5. Respond in the same language as the question (French or English)
            6. DO mention the source of information ("Open Food Facts" or "Canada Food Guide")
            
            Please follow these rules to ensure a consistent and effective search strategy.
            """
        ).format(columns_text=columns_text)

        self.logger.info(f"Additional notes for agent: {additional_notes}")

        # Measure response time
        start_time = time.time()
        agent_response = agent.run(
            question,
            additional_args={
                "additional_notes": additional_notes,
            },
        )
        response_time = time.time() - start_time
        
        # Create a structured response with all the information we need
        response_data = {
            "answer": {
                "text": agent_response if isinstance(agent_response, str) else str(agent_response),
                "source": "Unknown"  # Will be updated by the agent if it follows instructions
            },
            "sql_query": None,  # Will be populated if the agent used SQL
            "steps": []  # Will contain the sequence of steps
        }
        
        # Extract steps sequence and SQL query from agent memory
        last_successful_sql = None
        
        if hasattr(agent, 'memory') and hasattr(agent.memory, 'steps'):
            steps_sequence = []
            
            for step in agent.memory.steps:
                # Skip system prompt and task steps
                if not hasattr(step, 'tool_calls') or not step.tool_calls:
                    continue
                    
                tool_call = step.tool_calls[0]
                
                # Process python_interpreter calls
                if tool_call.name == "python_interpreter" and isinstance(tool_call.arguments, str):
                    code = tool_call.arguments
                    step_data = {}
                    
                    # Parse the observation to determine success
                    success = True if step.observations and "error" not in step.observations.lower() else False
                    
                    # Look for SQL queries in the code
                    if "query_db" in code:
                        # Extract SQL using more robust pattern matching
                        sql_query = self._extract_sql_from_code(code)
                        
                        if sql_query:
                            step_data = {
                                "action": "database_query",
                                "query": sql_query,
                                "success": success,
                                "result": step.observations
                            }
                            
                            # Track the last successful SQL query
                            if success and not sql_query.strip().startswith("WITH") and "SELECT" in sql_query.upper():
                                last_successful_sql = sql_query
                        else:
                            step_data = {
                                "action": "alternative_query",
                                "code": code[:200] + ("..." if len(code) > 200 else ""),
                                "success": success,
                                "result": step.observations
                            }
                    
                    # Detect food guide searches
                    elif "search_food_guide" in code:
                        # Try to extract the query
                        query_matches = re.findall(r'query\s*=\s*[\'"](.+?)[\'"]', code)
                        query = query_matches[0] if query_matches else "unknown query"
                        
                        step_data = {
                            "action": "food_guide_search",
                            "query": query,
                            "success": success,
                            "result": step.observations
                        }
                    
                    # Fallback for other Python code
                    else:
                        step_data = {
                            "action": "processing",
                            "code": code[:200] + ("..." if len(code) > 200 else ""),
                            "success": success,
                            "result": step.observations
                        }
                    
                    if step_data:
                        steps_sequence.append(step_data)
            
            # Add the steps to our response
            response_data["steps"] = steps_sequence
            
            # Set the SQL query to the last successful one
            response_data["sql_query"] = last_successful_sql
            
            # Try to extract source information from the answer
            for source in ["Open Food Facts", "Canada Food Guide"]:
                if source.lower() in agent_response.lower():
                    response_data["answer"]["source"] = source
                    break
        
        return response_data, response_time

    def _extract_sql_from_code(self, code: str) -> Optional[str]:
        """
        Extract SQL query from Python code using more robust pattern matching.
        
        Args:
            code (str): The Python code to analyze
            
        Returns:
            Optional[str]: The extracted SQL query or None if not found
        """
        # Try different pattern matching approaches
        
        # Pattern 1: Look for query assignments with triple quotes
        pattern1 = r'(?:query|sql)\s*=\s*(?:f|r)?"""(.*?)"""'
        matches = re.findall(pattern1, code, re.DOTALL)
        if matches:
            return matches[0]
        
        # Pattern 2: Look for query assignments with single triple quotes
        pattern2 = r"(?:query|sql)\s*=\s*(?:f|r)?'''(.*?)'''"
        matches = re.findall(pattern2, code, re.DOTALL)
        if matches:
            return matches[0]
        
        # Pattern 3: Look for query assignments with single quotes
        pattern3 = r"(?:query|sql)\s*=\s*(?:f|r)?'(.*?SELECT.*?)'"
        matches = re.findall(pattern3, code, re.DOTALL)
        if matches:
            return matches[0]
        
        # Pattern 4: Look for query assignments with double quotes
        pattern4 = r'(?:query|sql)\s*=\s*(?:f|r)?"(.*?SELECT.*?)"'
        matches = re.findall(pattern4, code, re.DOTALL)
        if matches:
            return matches[0]
        
        # Pattern 5: Look for query_db calls 
        pattern5 = r'query_db\s*\(\s*(?:query\s*=\s*)?[\'"]([^"\']+)[\'"]'
        matches = re.findall(pattern5, code, re.DOTALL)
        if matches:
            return matches[0]
        
        # Pattern 6: Look for any SQL query pattern
        pattern6 = r'SELECT\s+.+?\s+FROM\s+.+?(?:WHERE|GROUP BY|ORDER BY|LIMIT|$)'
        matches = re.findall(pattern6, code, re.DOTALL | re.IGNORECASE)
        if matches:
            return matches[0]
        
        return None
    
    def evaluate_single_case(self, agent, qa_pair: Dict[str, Any], lang: str) -> EvaluationResult:
        """
        Évalue un cas de test unique avec une structure très simplifiée.
        """
        question = qa_pair['questions'][lang]
        relevant_columns = self._search_relevant_columns(question)

        try:
            # Obtenir la réponse de l'agent
            response_data, response_time = self._get_agent_response(agent, question, relevant_columns)
            
            # Extraire uniquement la réponse textuelle et la source
            agent_answer = {
                "text": response_data.get('answer', {}).get('text', ''),
                "source": response_data.get('answer', {}).get('source', 'Unknown')
            }
            
            # Calculer les métriques simplifiées
            sql_accuracy = self._calculate_sql_accuracy(response_data, qa_pair)
            semantic_accuracy = self._calculate_semantic_accuracy(response_data, qa_pair, lang)
            sequence_respect = self._evaluate_search_sequence(response_data)["sequence_respect"]
            
            # Créer un objet metrics simplifié incluant le temps de réponse
            metrics = {
                "sql_accuracy": sql_accuracy,
                "semantic_accuracy": semantic_accuracy,
                "sequence_respect": sequence_respect,
                "response_time": response_time
            }

            # Retourner le résultat très simplifié
            return EvaluationResult(
                question_id=qa_pair.get('id', 0),
                language=lang,
                question=question,
                expected_answer=qa_pair['answers'][lang],
                agent_answer=agent_answer,
                metrics=metrics
            )

        except Exception as e:
            self.logger.error(f"Error evaluating question: {str(e)}")
            # Créer un résultat d'erreur encore plus simplifié
            return EvaluationResult(
                question_id=qa_pair.get('id', 0),
                language=lang,
                question=question,
                expected_answer=qa_pair['answers'][lang],
                agent_answer={"text": "", "source": "Unknown"},
                metrics={
                    "sql_accuracy": 0.0,
                    "semantic_accuracy": 0.0,
                    "sequence_respect": 0.0,
                    "response_time": 0.0,
                    "error": str(e)
                }
            )
        
    def _calculate_sql_accuracy(self, response_data: dict, qa_pair: Dict[str, Any]) -> float:
        """
        Calculate combined SQL accuracy metric.
        
        Returns:
            float: Combined accuracy score between 0 and 1
        """
        agent_sql = response_data.get('sql_query')
        
        # Si pas de requête SQL
        if not agent_sql:
            return 0.0

        # Exécuter les requêtes
        reference_results = self.execute_query(qa_pair['sql'])
        agent_results = self.execute_query(agent_sql)

        # Calculer les métriques individuelles
        query_present = 1.0
        execution_success = float(agent_results.success)
        results_match = 0.0

        # Comparer les résultats si les deux requêtes ont réussi
        if reference_results.success and agent_results.success:
            ref_set = {tuple(str(item) for item in row) for row in reference_results.results}
            agent_set = {tuple(str(item) for item in row) for row in agent_results.results}
            
            if ref_set or agent_set:
                intersection = len(ref_set.intersection(agent_set))
                union = len(ref_set.union(agent_set))
                results_match = intersection / union
            else:
                results_match = 1.0  # Les deux ensembles vides = correspondance
                    
        # Calculer le score combiné
        weights = {"query_present": 0.2, "execution_success": 0.3, "results_match": 0.5}
        combined_score = (query_present * weights["query_present"] + 
                        execution_success * weights["execution_success"] + 
                        results_match * weights["results_match"])

        return combined_score
    
    def _calculate_semantic_accuracy(self, response_data: dict, qa_pair: Dict, lang: str) -> float:
        """
        Calculate semantic similarity between responses.
        
        Args:
            response_data (dict): The parsed response from the agent
            qa_pair (Dict): The question-answer pair for comparison
            lang (str): Language code ('en' or 'fr')
            
        Returns:
            float: Semantic similarity score between 0 and 1
        """
        agent = CodeAgent(
            tools=[],
            model=self.model        
        )

        # Extract the text response from the parsed data
        agent_response = response_data.get('answer', {}).get('text', '')

        prompt = dedent(f"""\
        Compare these two responses and rate their semantic similarity from 0 to 1:
        Response #1: {qa_pair['answers'][lang]}
        Response #2: {agent_response}

        Consider:
        1. Key information present in both responses
        2. Factual consistency
        3. Completeness of information

        Output format: 
        Return exactly one line containing only a number between 0 and 1, with no 
        explanation or additional text. For example: 0.75
        """)

        self.logger.info(f"prompt: {prompt}")

        try:
            response = agent.run(prompt)
            self.logger.debug(f"Semantic similarity response: {response}")
            
            # Check response type
            if isinstance(response, float):
                similarity = response
            else:
                # If string, clean it and convert
                response_str = str(response).strip()
                similarity = float(response_str)
                
            return max(0.0, min(1.0, similarity))  # Ensure value is between 0 and 1
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error calculating semantic similarity: {e}")
            return 0.0
        
    def _evaluate_search_sequence(self, response_data: dict) -> dict:
        """
        Évalue la séquence de recherche avec deux indicateurs :
        1. Respect de la séquence (binaire : 1.0 ou 0.0)
        2. Nombre d'étapes effectuées
        
        Returns:
            dict: {
                "sequence_respect": 1.0 ou 0.0,
                "steps_count": nombre entier d'étapes
            }
        """
        try:
            steps = response_data.get('steps', [])
            
            if not steps:
                self.logger.warning("No steps found in agent response")
                return {
                    "sequence_respect": 0.0,
                    "steps_count": 0
                }

            # Initialiser les compteurs
            db_attempts = []
            web_attempt = None
            sequence_respected = True  # Par défaut, on suppose que la séquence est respectée

            # Analyser la séquence des étapes
            for step in steps:
                if step['action'] in ['database_query', 'alternative_query']:
                    db_attempts.append(step)
                    # Vérifier si une requête DB arrive après une recherche web (violation)
                    if web_attempt is not None:
                        sequence_respected = False
                        break
                elif step['action'] == 'food_guide_search':
                    web_attempt = step

            # Score binaire de respect de la séquence
            sequence_score = 1.0 if sequence_respected else 0.0

            # Simple décompte du nombre d'étapes
            steps_count = len(steps)

            return {
                "sequence_respect": sequence_score,
                "steps_count": steps_count
            }

        except Exception as e:
            self.logger.error(f"Error evaluating search sequence: {e}")
            return {
                "sequence_respect": 0.0,
                "steps_count": 0
            }
        
    def evaluate_all(self, agent, lang: str, max_cases: int = None) -> Dict[str, float]:
        """
        Evaluate agent on Q&A pairs.
        
        Args:
            agent: The agent to evaluate
            lang (str): Language code ('en' or 'fr')
            max_cases (int, optional): Maximum number of cases to evaluate. 
                                    If None, evaluates all cases.
        
        Returns:
            Dict[str, float]: Evaluation metrics
        """
        self.logger.debug("Entering evaluation loop")

        if lang not in ['en', 'fr']:
            raise ValueError("Language must be 'en' or 'fr'")
        
        results = []
        qa_pairs = self.qa_pairs[:max_cases] if max_cases else self.qa_pairs

        for idx, qa_pair in enumerate(qa_pairs, start=1):
            try:
                qa_pair_with_id = {**qa_pair, 'id': idx}
                self.logger.info(f"Évaluation de la question {idx}/{len(qa_pairs)}")
                result = self.evaluate_single_case(agent, qa_pair_with_id, lang)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Erreur lors de l'évaluation de la question {idx}: {e}")

        # Calculate metrics
        metrics = self.calculate_metrics(results)

        # Log detailed results
        self._log_detailed_results(results, metrics)

        return metrics

    def calculate_metrics(self, results: List[EvaluationResult]) -> Dict[str, float]:
        """
        Calcule les métriques globales à partir des résultats d'évaluation simplifiés.
        
        Args:
            results: Liste des résultats d'évaluation
                
        Returns:
            Dict[str, float]: Métriques globales calculées
        """
        if not results:
            return {
                "sql_accuracy": 0.0,
                "semantic_accuracy": 0.0,
                "sequence_respect": 0.0,
                "avg_response_time": 0.0
            }

        # Calculer les moyennes des différentes métriques
        sql_accuracy = mean([r.metrics.get("sql_accuracy", 0.0) for r in results])
        semantic_accuracy = mean([r.metrics.get("semantic_accuracy", 0.0) for r in results])
        sequence_respect = mean([r.metrics.get("sequence_respect", 0.0) for r in results])
        avg_response_time = mean([r.metrics.get("response_time", 0.0) for r in results])

        # Convertir en pourcentages où approprié
        metrics = {
            "sql_accuracy": sql_accuracy * 100,
            "semantic_accuracy": semantic_accuracy * 100,
            "sequence_respect": sequence_respect * 100,
            "avg_response_time": avg_response_time
        }

        # Ajouter quelques statistiques supplémentaires
        metrics.update({
            "success_rate": (sum(1 for r in results if "error" not in r.metrics) / len(results)) * 100,
            "min_response_time": min([r.metrics.get("response_time", 0.0) for r in results]),
            "max_response_time": max([r.metrics.get("response_time", 0.0) for r in results]),
            "median_response_time": median([r.metrics.get("response_time", 0.0) for r in results])
        })

        return metrics
    
    def _log_detailed_results(self, results: List[EvaluationResult], metrics: Dict[str, float]):
        """
        Écrit les résultats détaillés d'évaluation dans le fichier log.
        Accumule d'abord le rapport dans une chaîne puis l'écrit en une seule fois.
        """
        # Initialiser la chaîne de rapport
        report_lines = []
        report_lines.append("====== RAPPORT D'ÉVALUATION - AGENT OPEN FOOD FACTS ======")
        report_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Informations sur l'exécution
        report_lines.append("\n----- INFORMATIONS D'EXÉCUTION -----")
        report_lines.append(f"Langue: {results[0].language}")
        report_lines.append(f"Questions traitées: {len(results)}")
        report_lines.append(f"Modèle LLM: {self.model.model_id}")
        report_lines.append(f"Temps total: {sum(r.metrics['response_time'] for r in results):.2f}s")
        report_lines.append(f"Temps moyen par question: {metrics['avg_response_time']:.2f}s")

        # Métriques de performance
        report_lines.append("\n----- MÉTRIQUES DE PERFORMANCE -----")
        report_lines.append(f"Précision SQL: {metrics['sql_accuracy']:.2f}%")
        report_lines.append(f"Précision sémantique: {metrics['semantic_accuracy']:.2f}%")
        report_lines.append(f"Respect de séquence: {metrics['sequence_respect']:.2f}%")
        report_lines.append(f"Taux de succès: {metrics['success_rate']:.2f}%")

        # Statistiques des temps de réponse
        report_lines.append("\n----- TEMPS DE RÉPONSE -----")
        report_lines.append(f"Minimum: {metrics['min_response_time']:.2f}s")
        report_lines.append(f"Maximum: {metrics['max_response_time']:.2f}s")
        report_lines.append(f"Moyenne: {metrics['avg_response_time']:.2f}s")
        report_lines.append(f"Médiane: {metrics['median_response_time']:.2f}s")

        # Détails par question
        report_lines.append("\n----- DÉTAILS PAR QUESTION -----")
        for idx, result in enumerate(results, start=1):
            report_lines.append(f"\nQuestion {idx}: {result.question[:50]}...")
            
            # Métriques spécifiques à la question
            report_lines.append("Métriques:")
            report_lines.append(f"- Précision SQL: {result.metrics.get('sql_accuracy', 0.0)*100:.2f}%")
            report_lines.append(f"- Précision sémantique: {result.metrics.get('semantic_accuracy', 0.0)*100:.2f}%")
            report_lines.append(f"- Respect de séquence: {result.metrics.get('sequence_respect', 0.0)*100:.2f}%")
            report_lines.append(f"- Temps de réponse: {result.metrics.get('response_time', 0.0):.2f}s")
            
            # Affichage des erreurs si présentes
            if "error" in result.metrics:
                report_lines.append(f"Erreur: {result.metrics['error']}")
            
            # Extraits des réponses
            report_lines.append(f"Réponse attendue (extrait): {result.expected_answer[:100]}...")
            report_lines.append(f"Réponse de l'agent (extrait): {result.agent_answer.get('text', '')[:100]}...")
            report_lines.append(f"Source: {result.agent_answer.get('source', 'Non spécifiée')}")
            
            report_lines.append("-" * 40)  # Séparateur entre les questions

        report_lines.append("====== FIN DU RAPPORT D'ÉVALUATION ======")
        
        # Joindre toutes les lignes en une seule chaîne avec des sauts de ligne
        full_report = '\n'.join(report_lines)
        
        # Écrire le rapport complet en un seul appel
        self.logger.info(full_report)

def create_agent(model: LiteLLMModel) -> CodeAgent:
    """Create and initialize the conversational agent"""
    
    filtered_db_path = Path("../data/food_canada.duckdb")
    query_db = QueryDatabaseTool(db_path=filtered_db_path, max_rows=10)
    
    search_web_agent = ToolCallingAgent(
        tools=[SearchCanadaFoodGuideTool(), VisitWebpageTool()],
        model=model,
        name="search_web_agent",
        description=dedent(
            """\
        Specialized agent for searching nutrition information from Canada's Food Guide.

        CAPABILITIES:
        - Searches both English and French official Food Guide websites
        - Retrieves official dietary recommendations and guidelines
        - Complements Open Food Facts database information
        - Validates products against Canadian nutrition standards

        SOURCES:
        - English: food-guide.canada.ca/en/
        - French: guide-alimentaire.canada.ca/fr/
        """
        )
    )

    # Create agent
    agent = CodeAgent(
        tools=[query_db],
        model=model,
        managed_agents=[search_web_agent],
        additional_authorized_imports=["json"],
        verbosity_level=LogLevel.INFO,
    )

    agent.planning_interval = 4
    
    return agent

def main():
    logger.info("Starting evaluation script")

    # Initialize paths
    # The Open Food Facts database of Canadian products
    db_path = Path("../data/food_canada.duckdb")
    # Question-answer pairs for evaluation
    qa_path = Path("../data/qa_pairs.json")
    
    # Initialize model
    engine = "anthropic" # or ["ollama"|"anthropic"]
    if engine == "ollama":
        model = LiteLLMModel(
            model_id="ollama/llama3.1:8b-instruct-q8_0",
            api_base="http://localhost:11434",
            num_ctx=8192
        )
    elif engine == "anthropic":
        model = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-20241022")
        # model = LiteLLMModel(model_id="anthropic/claude-3-7-sonnet-20250219")
    elif engine == "qwen":
        model = HfApiModel("Qwen/Qwen2.5-Coder-32B-Instruct")
    
    # Initialize agent
    try:
        agent = create_agent(model)
        logging.info("Agent initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize agent: {e}")
        return
    
    # Create evaluator
    evaluator = Evaluator(db_path, qa_path, model)
    
    # Run evaluation
    lang = 'en'  # or 'fr'
    max_cases = 1  # Set to None to evaluate
    metrics = evaluator.evaluate_all(agent, lang, max_cases)
    
    # Print results
    print("\nEvaluation Results:")
    print(f"Language: {lang}")
    print(f"SQL Accuracy: {metrics['sql_accuracy']:.2f}%")  # Changed from 'execution_accuracy'
    print(f"Semantic Accuracy: {metrics['semantic_accuracy']:.2f}%")
    print(f"Sequence Respect: {metrics['sequence_respect']:.2f}%")
    print(f"Average Response Time: {metrics['avg_response_time']:.2f}s")

    # Print detailed stats if available
    if "query_stats" in metrics:
        print("\nQuery Statistics:")
        stats = metrics["query_stats"]
        print(f"Queries with SQL: {stats['with_query']}")
        print(f"Successful executions: {stats['successful_execution']}")

    if "response_time_stats" in metrics:
        print("\nResponse Time Statistics:")
        time_stats = metrics["response_time_stats"]
        print(f"Min: {time_stats['min']:.2f}s")
        print(f"Max: {time_stats['max']:.2f}s")
        print(f"Median: {time_stats['median']:.2f}s")

def foo():
    question = "Quels sont les aliments riches en protéines ?"
    
if __name__ == "__main__":
    main()
