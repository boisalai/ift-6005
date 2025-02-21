"""
# Evaluation Framework for Open Food Facts Conversational Agent

This script implements a comprehensive evaluation framework for testing and measuring 
the performance of a conversational agent designed to query the Open Food Facts database. 
The agent converts natural language questions into SQL queries and provides informative responses 
about food products.

## Key Components:
1. AgentEvaluator Class:
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
evaluator = AgentEvaluator(db_path, qa_path, model)
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
from pathlib import Path
from textwrap import dedent

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging
import numpy as np
from dotenv import load_dotenv
from statistics import mean
import duckdb
from datetime import datetime
from sentence_transformers import SentenceTransformer
import faiss

# Import agent components from chatbot script
from chatbot_19 import (
    QueryDatabaseTool,
    SearchCanadaFoodGuideTool
)

from smolagents import (
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

@dataclass
class QueryResult:
    """Results from executing a query"""
    success: bool
    results: List[Tuple]
    error: str = None

@dataclass
class EvaluationResult:
    """Results from one evaluation case"""
    question_id: int
    question: Dict[str, str]  # {'fr': '...', 'en': '...'}
    expected_answer: Dict[str, str]  # {'fr': '...', 'en': '...'}
    agent_answer: Dict[str, Dict[str, Any]]  # {lang: {parsed response structure}}
    response_time: float
    sql_accuracy: Dict[str, float]  # Detailed SQL accuracy metrics
    semantic_accuracy: float        # Semantic similarity score
    tcm_score: float                # New field to store TCM score from _evaluate_search_sequence
    error: str = None

class AgentEvaluator:
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
                self.logger.info(f"- Column '{r['name']}' with similarity {r['similarity']:.3f}")

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
                columns_info.append(
                    f"Column: {col['name']}\n"
                    f"Type: {col['type']}\n"
                    f"Description: {col['description']}\n"
                    f"Examples: {', '.join(map(str, col['examples'][:3]))}"
                )

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

    def evaluate_single_case(self, agent, qa_pair: Dict, lang: str) -> EvaluationResult:
        """
        Evaluates a single Q&A test case.
        
        Args:
            agent: The agent to evaluate
            qa_pair (Dict): The question-answer pair to evaluate
            lang (str): Language code ('en' or 'fr')
            
        Returns:
            EvaluationResult: Results of the evaluation
        """
        self.logger.info(f"Evaluating single case for question_id: {qa_pair.get('id', 0)}")
        
        question = qa_pair['questions'][lang]

        # Search for relevant columns
        relevant_columns = self._search_relevant_columns(question, top_k=5)

        try:
            # Get agent's response - returns parsed dictionary
            response_data, response_time = self._get_agent_response(agent, question, relevant_columns)

            # Calculate metrics using the parsed response directly
            sql_accuracy = self._calculate_sql_accuracy(response_data, qa_pair)
            semantic_accuracy = self._calculate_semantic_accuracy(response_data, qa_pair)
            tcm_result = self._evaluate_search_sequence(response_data, qa_pair)
            
            return EvaluationResult(
                question_id=qa_pair.get('id', 0),
                question=qa_pair['questions'],
                expected_answer=qa_pair['answers'],
                agent_answer={lang: response_data},
                response_time=response_time,
                sql_accuracy=sql_accuracy,
                semantic_accuracy=semantic_accuracy,
                tcm_score=tcm_result,
                error=None
            )

        except Exception as e:
            self.logger.error(f"Error evaluating question: {str(e)}")
            return EvaluationResult(
                question_id=qa_pair.get('id', 0),
                question=qa_pair['questions'],
                expected_answer=qa_pair['answers'],
                agent_answer={lang: {
                    "answer": {"text": "", "source": "Unknown"},
                    "sql_query": None,
                    "steps": []
                }},
                response_time=0.0,
                sql_accuracy={
                    "query_present": 0.0,
                    "execution_success": 0.0,
                    "results_match": 0.0,
                    "combined": 0.0
                },
                semantic_accuracy=0.0,
                tcm_score=0.0,
                error=str(e)
            )
    
    def _calculate_sql_accuracy(self, response_data: dict, qa_pair: Dict) -> Dict[str, float]:
        """
        Calculate SQL accuracy by comparing query results.
        Returns a dictionary with different accuracy metrics.
        
        Args:
            response_data (dict): The parsed response from the agent
            qa_pair (Dict): The question-answer pair being evaluated
            
        Returns:
            Dict[str, float]: Dictionary containing accuracy metrics
        """
        self.logger.info(f"Evaluating SQL accuracy for question_id: {qa_pair.get('id', 'unknown')}")
        
        # Extract SQL query directly from the parsed response
        agent_sql = response_data.get('sql_query')
        
        if not agent_sql:
            self.logger.warning("No SQL query found in agent response")
            return {
                "query_present": 0.0,
                "execution_success": 0.0,
                "results_match": 0.0,
                "combined": 0.0
            }

        # Log the queries for comparison
        self.logger.debug(f"Reference SQL: {qa_pair['sql']}")
        self.logger.debug(f"Agent SQL: {agent_sql}")

        # Execute both queries
        reference_results = self.execute_query(qa_pair['sql'])
        agent_results = self.execute_query(agent_sql)

        # Calculate component scores
        query_present = 1.0  # Agent generated a SQL query
        execution_success = float(agent_results.success)

        # Compare results if both queries executed successfully
        results_match = 0.0
        if reference_results.success and agent_results.success:
            # Convert result rows to sets of tuples for comparison
            ref_set = {tuple(str(item) for item in row) for row in reference_results.results}
            agent_set = {tuple(str(item) for item in row) for row in agent_results.results}

            if ref_set or agent_set:  # Avoid division by zero
                # Calculate Jaccard similarity: intersection over union
                intersection = len(ref_set.intersection(agent_set))
                union = len(ref_set.union(agent_set))
                results_match = intersection / union
            else:
                # Both queries returned empty sets - consider this a match
                results_match = 1.0

        # Calculate combined score with weights
        weights = {
            "query_present": 0.2,
            "execution_success": 0.3,
            "results_match": 0.5
        }
        
        combined_score = (
            weights["query_present"] * query_present +
            weights["execution_success"] * execution_success +
            weights["results_match"] * results_match
        )

        return {
            "query_present": query_present,
            "execution_success": execution_success,
            "results_match": results_match,
            "combined": combined_score
        }

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
            model=self.model
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
        

    def _evaluate_search_sequence(self, response_data: dict, qa_pair: Dict) -> float:
        """
        Évalue la capacité de l'agent à gérer les données manquantes selon une progression stricte.
        
        Args:
            response_data (dict): The parsed response from the agent
            qa_pair (Dict): The question-answer pair being evaluated
            
        Returns:
            float: Score between 0 and 1 indicating search sequence quality
        """
        try:
            steps = response_data.get('steps', [])
            
            if not steps:
                self.logger.warning("No steps found in agent response")
                return 0.0

            score = 0.0
            db_attempts = []
            web_attempt = None

            # Vérifier la séquence des tentatives
            for step in steps:
                if step['action'] in ['database_query', 'alternative_query']:
                    db_attempts.append(step)
                    # Pénaliser une requête DB après une recherche web
                    if web_attempt is not None:
                        return 0.0  # Violation de la séquence
                elif step['action'] == 'food_guide_search':
                    web_attempt = step
            
            # Évaluer la progression
            if db_attempts:
                # Points pour avoir commencé par la DB
                score += 0.4
                
                # Points pour chaque tentative alternative pertinente
                if len(db_attempts) > 1:
                    score += min(0.3, 0.1 * (len(db_attempts) - 1))
                    
                # Points pour avoir consulté le guide seulement après échec des requêtes DB
                if web_attempt and not any(attempt['success'] for attempt in db_attempts):
                    score += 0.3

            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"Error evaluating search sequence: {e}")
            return 0.0

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
                result = self.evaluate_single_case(agent, qa_pair_with_id, lang)
                results.append(result)
                self.logger.info(f"Evaluated question {idx}")
            except Exception as e:
                self.logger.error(f"Error evaluating question {idx}: {e}")

        # Calculate metrics
        metrics = self.calculate_metrics(results)

        # Log detailed results
        self._log_detailed_results(results, metrics)

        return metrics

    def calculate_metrics(self, results: List[EvaluationResult]) -> Dict[str, float]:
        """Calculate the metrics from evaluation results"""
        total = len(results)
        if total == 0:
            return {
                "execution_accuracy": 0.0,
                "tcm_score": 0.0,
                "avg_response_time": 0.0,
                "semantic_accuracy": 0.0
            }
        
        # Execution Accuracy (EX)
        execution_accuracy = mean(r.sql_accuracy["combined"] for r in results)

        # TCM Score from _evaluate_search_sequence
        tcm_score = mean(r.tcm_score for r in results)

        # Semantic Accuracy
        semantic_accuracy = mean(r.semantic_accuracy for r in results)

        # Average Response Time (TRM)
        avg_response_time = mean(r.response_time for r in results)

        return {
            "execution_accuracy": execution_accuracy * 100,
            "tcm_score": tcm_score * 100,
            "semantic_accuracy": semantic_accuracy * 100,
            "avg_response_time": avg_response_time
        }


    def _log_detailed_results(self, results: List[EvaluationResult], metrics: Dict[str, float]):
        """Log detailed evaluation results"""
        log_path = Path("evaluation_results.md")

        with open(log_path, 'w', encoding='utf-8') as f:
            # Write summary
            f.write("# Evaluation Results\n\n")
            f.write("## Summary Metrics\n")
            f.write(f"- Execution Accuracy (EX): {metrics['execution_accuracy']:.2f}%\n")
            f.write(f"- TCM Score: {metrics['tcm_score']:.2f}%\n")
            f.write(f"- Average Response Time (TRM): {metrics['avg_response_time']:.2f}s\n\n")

            # Write detailed results
            f.write("## Detailed Results\n\n")
            for r in results:
                f.write(f"### Question {r.question_id}\n")
                f.write(f"**English Question:** {r.question['en']}\n")
                f.write(f"**Response Time:** {r.response_time:.2f}s\n")
                
                # SQL Accuracy section
                f.write(f"**SQL Accuracy Metrics:**\n")
                f.write(f"- Query Present: {r.sql_accuracy['query_present']:.2f}\n")
                f.write(f"- Execution Success: {r.sql_accuracy['execution_success']:.2f}\n")
                f.write(f"- Results Match: {r.sql_accuracy['results_match']:.2f}\n")
                f.write(f"- Combined Score: {r.sql_accuracy['combined']:.2f}\n")
                
                # TCM Score section
                f.write(f"**TCM Score:** {r.tcm_score:.2f}\n")
                
                # Error section if applicable
                if r.error:
                    f.write(f"**Error:** {r.error}\n")
                f.write("\n")

def create_agent(model: LiteLLMModel) -> CodeAgent:
    """Create and initialize the conversational agent"""
    
    filtered_db_path = Path("../data/food_canada.duckdb")
    query_db = QueryDatabaseTool(db_path=filtered_db_path)
    
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

    # Clean up old logs
    cleanup_old_logs(log_dir)

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
    evaluator = AgentEvaluator(db_path, qa_path, model)
    
    # Run evaluation
    lang = 'en'  # or 'fr'
    max_cases = 1  # Set to None to evaluate
    metrics = evaluator.evaluate_all(agent, lang, max_cases)
    
    # Print results
    print("\nEvaluation Results:")
    print(f"Language: {lang}")
    print(f"Execution Accuracy (EX): {metrics['execution_accuracy']:.2f}%")
    print(f"Missing Data Coverage (TCM): {metrics['tcm_score']:.2f}%")
    print(f"Average Response Time (TRM): {metrics['avg_response_time']:.2f}s")

if __name__ == "__main__":
    main()
