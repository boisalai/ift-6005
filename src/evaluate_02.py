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
from pathlib import Path
from textwrap import dedent

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging
import numpy as np
import sqlglot

from dotenv import load_dotenv
from statistics import mean, median
import duckdb
from datetime import datetime
from sentence_transformers import SentenceTransformer
import faiss

# Import agent components from chatbot script
from chatbot_19 import (
    SearchCanadaFoodGuideTool
)

from smolagents import (
    Tool,
    CodeAgent,
    VisitWebpageTool,
    LiteLLMModel,
    ToolCallingAgent,
    LogLevel
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
class QueryResults:
    """Résultats de requête pour comparaison"""
    expected: List[Any]
    actual: List[Any]
    comparison: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationMetrics:
    """Métriques d'évaluation regroupées"""
    sql_metrics: Dict[str, float] = field(default_factory=lambda: {
        "query_present": 0.0,
        "execution_success": 0.0,
        "results_match": 0.0,
        "combined": 0.0
    })
    semantic_metrics: Dict[str, float] = field(default_factory=lambda: {
        "accuracy": 0.0
    })
    sequence_metrics: Dict[str, float] = field(default_factory=lambda: {
        "sequence_respect": 0.0,
        "steps_count": 0
    })
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationResult:
    """Résultat d'évaluation d'une question"""
    question_id: int
    language: str  # Langue de l'évaluation ('fr' ou 'en')
    question: Dict[str, str]  # Questions bilingues
    expected_answer: Dict[str, str]  # Réponses attendues bilingues
    agent_answer: Dict[str, Any]  # Réponse dans la langue évaluée
    query_results: Optional[QueryResults] = None
    metrics: Optional[EvaluationMetrics] = None
    response_time: float = 0.0
    error: Optional[str] = None

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
        "query": {"type": "string", "description": "Valid DuckDB SQL query to execute"}
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

    def _get_agent_response(self, agent, question: str, relevant_columns: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], float]:
        """
        Get response from agent for a given question and measure response time.
        
        Args:
            agent: The agent to query
            question: The question to ask
            relevant_columns: List of relevant columns identified for the question
            
        Returns:
            Tuple[str, float]: Agent's response and response time in seconds
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

            IMPORTANT RESPONSE FORMAT:
            You must return a valid JSON string with the following structure:

            {{
                "answer": {{
                    "text": "Your natural language response here",
                    "source": "Source used (Open Food Facts and/or Canada Food Guide)"
                }},
                "sql_query": "Your SQL query if one was executed, or null if none was used",
                "steps": [
                    {{
                        "step": 1,
                        "action": "database_query",  # One of: database_query, alternative_query, food_guide_search
                        "description": "Description of what was attempted",
                        "query": "SQL query used (if applicable)",
                        "success": true/false,
                        "result": "Description of the result or why it failed"
                    }},
                    {{
                        "step": 2,
                        "action": "alternative_query",
                        "description": "Tried alternative approach with different columns",
                        "query": "Alternative SQL query",
                        "success": true/false,
                        "result": "Description of the result"
                    }},
                    {{
                        "step": 3,
                        "action": "food_guide_search",
                        "description": "Searched Canada Food Guide for additional information",
                        "query": null,
                        "success": true/false,
                        "result": "Information found in Food Guide"
                    }}
                ]
            }}

            SEARCH SEQUENCE RULES:
            1. ALWAYS start with database queries using the most relevant columns
            2. If initial query fails, try alternative database queries with different columns or approaches
            3. Only if database queries are unsuccessful, search the Canada Food Guide
            4. Document EVERY attempt in the steps array, including failures
            5. Never skip straight to Food Guide without trying database first

            REQUIREMENTS:
            - Return a valid JSON string that can be parsed with json.loads()
            - Document every search attempt in the steps array
            - Respond in the same language as the question (French or English)
            - Be explicit about any data limitations or uncertainties
            - Follow the search sequence rules strictly

            IMPORTANT:
            - Your response MUST include a "steps" array documenting your search process
            - Each step MUST have all the fields shown in the example
            - The sequence of steps matters and will be evaluated
            - Always try database queries before falling back to Food Guide search
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

        # Parse and validate the response
        try:
            # Parse the JSON response
            if isinstance(agent_response, str):
                response_data = json.loads(agent_response)
            else:
                response_data = agent_response

            # Ensure the response has the required structure
            default_structure = {
                "answer": {
                    "text": "",
                    "source": "Unknown"
                },
                "sql_query": None,
                "steps": []
            }

            # If response_data is not a dictionary, wrap it
            if not isinstance(response_data, dict):
                response_data = {
                    "answer": {
                        "text": str(response_data),
                        "source": "Unknown"
                    },
                    "sql_query": None,
                    "steps": []
                }

            # Ensure all required keys exist with valid types
            if "answer" not in response_data or not isinstance(response_data["answer"], dict):
                response_data["answer"] = default_structure["answer"]
            
            if "sql_query" not in response_data:
                response_data["sql_query"] = default_structure["sql_query"]
                
            if "steps" not in response_data or not isinstance(response_data["steps"], list):
                response_data["steps"] = default_structure["steps"]

            # Ensure answer has both text and source
            if not isinstance(response_data["answer"], dict):
                response_data["answer"] = {
                    "text": str(response_data["answer"]),
                    "source": "Unknown"
                }
            if "text" not in response_data["answer"]:
                response_data["answer"]["text"] = ""
            if "source" not in response_data["answer"]:
                response_data["answer"]["source"] = "Unknown"

            # Validate each step in the steps array
            validated_steps = []
            for step in response_data["steps"]:
                if isinstance(step, dict):
                    validated_step = {
                        "step": step.get("step", len(validated_steps) + 1),
                        "action": step.get("action", "unknown"),
                        "description": step.get("description", ""),
                        "query": step.get("query", None),
                        "success": bool(step.get("success", False)),
                        "result": step.get("result", "")
                    }
                    validated_steps.append(validated_step)
            response_data["steps"] = validated_steps

        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse agent response as JSON: {e}")
            self.logger.warning(f"Agent response: {agent_response}")
            response_data = {
                "answer": {
                    "text": str(agent_response),
                    "source": "Unknown"
                },
                "sql_query": None,
                "steps": []
            }
        except Exception as e:
            self.logger.error(f"Error processing agent response: {e}")
            response_data = default_structure

        self.logger.debug(f"Processed response data: {response_data}")
        
        return response_data, response_time

    def evaluate_single_case(self, agent, qa_pair: Dict[str, Any], lang: str) -> EvaluationResult:
        """
        Évalue un cas de test unique avec la nouvelle structure.
        """
        question = qa_pair['questions'][lang]
        relevant_columns = self._search_relevant_columns(question)

        try:
            # Obtenir la réponse de l'agent
            response_data, response_time = self._get_agent_response(agent, question, relevant_columns)
            
            # Calculer toutes les métriques
            sql_metrics, query_results = self._calculate_sql_accuracy(response_data, qa_pair, lang)
            semantic_accuracy = self._calculate_semantic_accuracy(response_data, qa_pair)
            sequence_metrics = self._evaluate_search_sequence(response_data)
            
            # Créer l'objet metrics avec la nouvelle structure
            metrics = EvaluationMetrics(
                sql_metrics=sql_metrics,
                semantic_metrics={"accuracy": semantic_accuracy},
                sequence_metrics=sequence_metrics,
                details={
                    'relevant_columns': [col['name'] for col in relevant_columns],
                    'sql_analysis': {
                        'has_query': bool(response_data.get('sql_query')),
                        'execution_details': query_results.comparison if query_results else None
                    },
                    'sequence_analysis': sequence_metrics
                }
            )

            # Retourner le résultat complet
            return EvaluationResult(
                question_id=qa_pair.get('id', 0),
                language=lang,
                question=qa_pair['questions'],
                expected_answer=qa_pair['answers'],
                agent_answer=response_data,
                query_results=query_results,
                metrics=metrics,
                response_time=response_time
            )

        except Exception as e:
            self.logger.error(f"Error evaluating question: {str(e)}")
            # Créer un résultat d'erreur avec la nouvelle structure de métriques
            return EvaluationResult(
                question_id=qa_pair.get('id', 0),
                language=lang,
                question=qa_pair['questions'],
                expected_answer=qa_pair['answers'],
                agent_answer={
                    "answer": {"text": "", "source": "Unknown"},
                    "sql_query": None,
                    "steps": []
                },
                metrics=EvaluationMetrics(
                    details={'error': str(e)}
                ),
                response_time=0.0,
                error=str(e)
            )
        
    def _calculate_sql_accuracy(self, response_data: dict, qa_pair: Dict[str, Any], lang: str) -> Tuple[Dict[str, float], QueryResults]:
        """
        Calculate SQL accuracy and prepare detailed query results.
        """
        agent_sql = response_data.get('sql_query')
        
        # Si pas de requête SQL
        if not agent_sql:
            return (
                {
                    "query_present": 0.0,
                    "execution_success": 0.0,
                    "results_match": 0.0,
                    "combined": 0.0
                },
                None
            )

        # Exécuter les requêtes
        reference_results = self.execute_query(qa_pair['sql'])
        agent_results = self.execute_query(agent_sql)

        # Préparer les résultats pour comparaison
        query_results = QueryResults(
            expected=reference_results.results if reference_results.success else [],
            actual=agent_results.results if agent_results.success else [],
            comparison={
                'ref_success': reference_results.success,
                'agent_success': agent_results.success,
                'error': agent_results.error if not agent_results.success else None
            }
        )

        # Calculer les métriques
        metrics = {
            "query_present": 1.0,
            "execution_success": float(agent_results.success),
            "results_match": 0.0,
            "combined": 0.0
        }

        # Comparer les résultats si les deux requêtes ont réussi
        if reference_results.success and agent_results.success:
            ref_set = {tuple(str(item) for item in row) for row in reference_results.results}
            agent_set = {tuple(str(item) for item in row) for row in agent_results.results}
            
            if ref_set or agent_set:
                intersection = len(ref_set.intersection(agent_set))
                union = len(ref_set.union(agent_set))
                metrics["results_match"] = intersection / union
                
                query_results.comparison.update({
                    'matching_rows': intersection,
                    'total_rows': union,
                    'ref_rows': len(ref_set),
                    'agent_rows': len(agent_set)
                })
            else:
                metrics["results_match"] = 1.0  # Les deux ensembles vides = correspondance
                
        # Calculer le score combiné
        weights = {"query_present": 0.2, "execution_success": 0.3, "results_match": 0.5}
        metrics["combined"] = sum(metrics[k] * v for k, v in weights.items())

        return metrics, query_results
    
    def _calculate_semantic_accuracy(self, response_data: dict, qa_pair: Dict) -> float:
        """
        Calculate semantic similarity between responses.
        
        Args:
            response_data (dict): The parsed response from the agent
            qa_pair (Dict): The question-answer pair for comparison
            
        Returns:
            float: Semantic similarity score between 0 and 1
        """
        agent = CodeAgent(
            tools=[],
            model=self.model,
            max_steps=3
        )

        # Extract the text response from the parsed data
        agent_response = response_data.get('answer', {}).get('text', '')

        prompt = f"""Compare these two responses and rate their semantic similarity from 0 to 1:
        Expected: {qa_pair['answers']['en']}
        Actual: {agent_response}
        
        Consider:
        1. Key information present in both responses
        2. Factual consistency
        3. Completeness of information
        
        Return only a number between 0 and 1."""
        
        try:
            similarity = float(agent.run(prompt))
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
        Calcule les métriques globales à partir des résultats d'évaluation.
        
        Args:
            results: Liste des résultats d'évaluation
            
        Returns:
            Dict[str, float]: Métriques globales calculées
        """
        if not results:
            return {
                "execution_accuracy": 0.0,
                "semantic_accuracy": 0.0,
                "sequence_respect": 0.0,
                "avg_response_time": 0.0
            }

        # Calculer les moyennes des différentes métriques
        execution_accuracy = mean(
            r.metrics.sql_metrics["combined"] for r in results if r.metrics
        )
        semantic_accuracy = mean(
            r.metrics.semantic_metrics["accuracy"] for r in results if r.metrics
        )
        sequence_respect = mean(
            r.metrics.sequence_metrics["sequence_respect"] for r in results if r.metrics
        )
        avg_response_time = mean(r.response_time for r in results)

        # Convertir en pourcentages où approprié
        metrics = {
            "execution_accuracy": execution_accuracy * 100,
            "semantic_accuracy": semantic_accuracy * 100,
            "sequence_respect": sequence_respect * 100,
            "avg_response_time": avg_response_time
        }

        # Ajouter des statistiques détaillées
        metrics.update(self._calculate_detailed_stats(results))

        return metrics

    def _calculate_detailed_stats(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Calcule des statistiques détaillées sur les résultats.
        """
        stats = {
            "success_rate": {
                "total": len(results),
                "successful": sum(1 for r in results if not r.error),
                "failed": sum(1 for r in results if r.error)
            },
            "query_stats": {
                "with_query": sum(1 for r in results 
                    if r.agent_answer.get('sql_query')),
                "successful_execution": sum(1 for r in results 
                    if r.metrics and r.metrics.sql_metrics["execution_success"] > 0)
            },
            "response_time_stats": {
                "min": min(r.response_time for r in results),
                "max": max(r.response_time for r in results),
                "median": median(r.response_time for r in results)
            }
        }
        
        # Calculer le taux de succès en pourcentage
        stats["success_rate"]["percentage"] = (
            stats["success_rate"]["successful"] / stats["success_rate"]["total"] * 100
        )
        
        return stats

    def _get_stats(self, values: List[float]) -> Dict[str, float]:
        """
        Calcule les statistiques descriptives pour une liste de valeurs.
        
        Args:
            values (List[float]): Liste des valeurs à analyser
            
        Returns:
            Dict[str, float]: Dictionnaire contenant les statistiques suivantes:
                - min: valeur minimale
                - max: valeur maximale
                - avg: moyenne
                - median: médiane
                - std: écart-type
        """
        try:
            if not values:
                return {
                    'min': 0.0,
                    'max': 0.0,
                    'avg': 0.0,
                    'median': 0.0,
                    'std': 0.0
                }
                
            # Convertir en tableau numpy pour les calculs statistiques
            import numpy as np
            values_array = np.array(values)
            
            # Calculer les statistiques de base
            stats = {
                'min': float(np.min(values_array)),
                'max': float(np.max(values_array)),
                'avg': float(np.mean(values_array)),
                'median': float(np.median(values_array)),
                'std': float(np.std(values_array))
            }
            
            # Conversion en pourcentages si les valeurs sont entre 0 et 1
            if all(0 <= v <= 1 for v in values):
                stats = {k: v * 100 for k, v in stats.items()}
                
            # Arrondir les valeurs à 2 décimales
            stats = {k: round(v, 2) for k, v in stats.items()}
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating statistics: {str(e)}")
            # Retourner des valeurs par défaut en cas d'erreur
            return {
                'min': 0.0,
                'max': 0.0,
                'avg': 0.0,
                'median': 0.0,
                'std': 0.0
            }
    
    def _log_detailed_results(self, results: List[EvaluationResult], metrics: Dict[str, float]):
        """
        Génère un rapport des résultats d'évaluation au format Markdown.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path(f"evaluation_results_{timestamp}.md")

        total_time = sum(r.response_time for r in results)
        avg_time = total_time / len(results)

        with open(log_path, 'w', encoding='utf-8') as f:
            # En-tête du rapport
            f.write("# Rapport d'évaluation de l'agent Open Food Facts\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Informations sur l'exécution
            f.write("## Informations d'exécution\n\n")
            f.write("| Paramètre | Valeur |\n")
            f.write("|-----------|--------|\n")
            f.write(f"| Langue | {results[0].language} |\n")
            f.write(f"| Questions traitées | {len(results)} |\n")
            f.write(f"| Modèle LLM | {self.model.model_id} |\n")
            f.write(f"| Temps total | {total_time:.2f}s |\n")
            f.write(f"| Temps moyen par question | {avg_time:.2f}s |\n\n")

            # Description des métriques
            f.write("## Description des métriques\n\n")
            f.write("- **Exécution SQL** : Évalue si l'agent génère des requêtes SQL valides qui retournent les bons résultats\n")
            f.write("- **Sémantique** : Mesure si la réponse en langage naturel de l'agent correspond au sens de la réponse attendue\n")
            f.write("- **Séquence de recherche** : Évalue si l'agent suit une progression logique dans sa recherche d'information\n")
            f.write("  - Respect de la séquence : Vérifie si l'agent commence par la base de données avant d'utiliser d'autres sources\n")
            f.write("  - Nombre d'étapes : Compte le nombre total d'étapes de recherche effectuées\n\n")

            # Tableau des métriques principales
            f.write("## Métriques de Performance\n\n")
            f.write("| Métrique | Score (%) | Min | Max | Moyenne | Médiane |\n")
            f.write("|-----------|-----------|-----|-----|---------|----------|\n")

            # SQL scores
            sql_scores = [r.metrics.sql_metrics['combined'] for r in results]
            sql_stats = self._get_stats(sql_scores)
            f.write(f"| Exécution SQL | {metrics['execution_accuracy']:.2f} | {sql_stats['min']:.2f} | {sql_stats['max']:.2f} | {sql_stats['avg']:.2f} | {sql_stats['median']:.2f} |\n")

            # Semantic scores
            semantic_scores = [r.metrics.semantic_metrics['accuracy'] for r in results]
            semantic_stats = self._get_stats(semantic_scores)
            f.write(f"| Sémantique | {metrics['semantic_accuracy']:.2f} | {semantic_stats['min']:.2f} | {semantic_stats['max']:.2f} | {semantic_stats['avg']:.2f} | {semantic_stats['median']:.2f} |\n")

            # Sequence respect scores
            sequence_scores = [r.metrics.sequence_metrics['sequence_respect'] for r in results]
            sequence_stats = self._get_stats(sequence_scores)
            f.write(f"| Respect séquence | {metrics['sequence_respect']:.2f} | {sequence_stats['min']:.2f} | {sequence_stats['max']:.2f} | {sequence_stats['avg']:.2f} | {sequence_stats['median']:.2f} |\n\n")

            # Statistiques détaillées des étapes
            f.write("## Statistiques des étapes de recherche\n\n")
            steps_counts = [r.metrics.sequence_metrics['steps_count'] for r in results]
            steps_stats = self._get_stats(steps_counts)
            f.write("| Statistique | Valeur |\n")
            f.write("|-------------|--------|\n")
            f.write(f"| Nombre minimum d'étapes | {steps_stats['min']:.0f} |\n")
            f.write(f"| Nombre maximum d'étapes | {steps_stats['max']:.0f} |\n")
            f.write(f"| Nombre moyen d'étapes | {steps_stats['avg']:.1f} |\n")
            f.write(f"| Nombre médian d'étapes | {steps_stats['median']:.0f} |\n\n")

            # Détails des temps de réponse
            f.write("## Temps de réponse\n\n")
            time_stats = metrics["response_time_stats"]
            f.write("| Statistique | Valeur (secondes) |\n")
            f.write("|-------------|-------------------|\n")
            f.write(f"| Minimum | {time_stats['min']:.2f} |\n")
            f.write(f"| Maximum | {time_stats['max']:.2f} |\n")
            f.write(f"| Moyenne | {avg_time:.2f} |\n")
            f.write(f"| Médiane | {time_stats['median']:.2f} |\n\n")

            # Statistiques des requêtes
            f.write("## Statistiques des requêtes\n\n")
            query_stats = metrics["query_stats"]
            total = metrics["success_rate"]["total"]
            f.write("| Métrique | Nombre | Pourcentage |\n")
            f.write("|-----------|---------|-------------|\n")
            f.write(f"| Requêtes avec SQL | {query_stats['with_query']} | {(query_stats['with_query']/total)*100:.1f}% |\n")
            f.write(f"| Exécutions réussies | {query_stats['successful_execution']} | {(query_stats['successful_execution']/total)*100:.1f}% |\n")

        self.logger.info(f"Rapport généré : {log_path}")

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
        model = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-20240620")
    
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
    print(f"Execution Accuracy (EX): {metrics['execution_accuracy']:.2f}%")
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

if __name__ == "__main__":
    main()
