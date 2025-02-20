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
from dotenv import load_dotenv
from statistics import mean
import duckdb
from datetime import datetime

# Import agent components from chatbot script
from chatbot_19 import (
    SearchDatabaseDocumentationTool,
    QueryDatabaseTool,
    SearchCanadaFoodGuideTool
)

from smolagents import (
    CodeAgent,
    VisitWebpageTool,
    LiteLLMModel,
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
    agent_answer: Dict[str, str]
    sql_query: str
    response_time: float
    execution_success: bool
    missing_data_handled: bool
    error: str = None

class AgentEvaluator:
    def __init__(self, db_path: Path, qa_path: Path, model: LiteLLMModel):
        self.db_path = db_path
        self.qa_pairs = self._load_qa_pairs(qa_path)
        self.connection = duckdb.connect(str(db_path))
        self.logger = logging.getLogger('food_agent')
        self.model = model

    def _load_qa_pairs(self, qa_path: Path) -> List[Dict]:
        """Load Q&A pairs from JSON file"""
        with open(qa_path, 'r', encoding='utf-8') as f:
            return json.load(f)

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

    def _get_agent_response(self, agent, question: str) -> Tuple[str, float]:
        """
        Get response from agent for a given question and measure response time.
        
        Args:
            agent: The agent to query
            question: The question to ask
            
        Returns:
            Tuple[str, float]: Agent's response and response time in seconds
        """
        self.logger.info("Getting agent response")

        additional_notes = dedent(
            """\
            You are a helpful assistant that answers questions about food products 
            using the Open Food Facts database.

            Follow these steps to answer questions:

            1. Use the documentation search tool (search_db_docs) to understand 
               which columns contain the needed information
            2. Write and execute an SQL query to get the data using the query 
               tool (query_db)
            3. If data is missing, use the Food Guide search tool for complementary 
               information (search_food_guide and visit_webpage)
            4. Format your response as a JSON string with the following structure:

            {
                "answer": {
                    "text": "Your natural language response here",
                    "source": "Source used (either 'Open Food Facts' or 'Canada Food Guide' or 'Both')"
                },
                "sql_query": "Your SQL query if one was executed, or None if none was used"
            }

            IMPORTANT FORMATTING RULES:
            - Your complete response must be a valid JSON string that can be parsed using json.loads()
            - The "text" field should contain your complete answer in natural language
            - The "source" field must be exactly one of: "Open Food Facts", "Canada Food Guide", or "Both"
            - The "sql_query" field should contain the full SQL query if database was queried, or null if no query was executed
            - If data is missing or incomplete, explicitly mention it in the "text" field
            - Respond in the same language as the question (French or English)

            Example response:
            {
                "answer": {
                    "text": "Based on the Open Food Facts database, the average sugar content in breakfast cereals is 25g per 100g. Products with the highest sugar content are...",
                    "source": "Open Food Facts"
                },
                "sql_query": "SELECT AVG(sugars_100g) FROM products WHERE category LIKE '%breakfast cereals%';"
            }
            """
        )

        # Measure response time
        start_time = time.time()
        agent_response = agent.run(
            question,
            additional_args={
                "additional_notes": additional_notes,
            },
        )
        response_time = time.time() - start_time

        self.logger.info(f"Question: {question}")
        self.logger.info(f"Agent response: {agent_response}")
        self.logger.info(f"Response time: {response_time:.2f}s")
        
        return agent_response, response_time
    
    def evaluate_single_case(self, agent, qa_pair: Dict, lang: str) -> EvaluationResult:
        """
        Evaluates a single Q&A test case.

        Args:
            qa_pair: Test case containing the question and answer
            lang (str): Language code ('en' or 'fr'). Defaults to 'en'
        """
        self.logger.info("Evaluating single case")

        if lang not in ['en', 'fr']:
            raise ValueError("Language must be 'en' or 'fr'")
        
        question = qa_pair['questions'][lang]

        # Get agent's response
        agent_response, response_time = self._get_agent_response(agent, question)

        # Calculate metrics
        sql_accuracy = self._calculate_sql_accuracy(agent_response, qa_pair)
        semantic_accuracy = self._calculate_semantic_accuracy(agent_response, qa_pair)
        data_coverage = self._calculate_data_coverage(agent_response, qa_pair)
        
        return EvaluationResult(
            question_id=qa_pair.get('id', 0),
            question=qa_pair['questions'],
            expected_answer=qa_pair['answers'],
            agent_answer={'en': agent_response},
            response_time=response_time,
            sql_accuracy=sql_accuracy,
            semantic_accuracy=semantic_accuracy,
            data_coverage=data_coverage
        )

    def _extract_sql_query(self, agent_response: str) -> str:
        """
        Extract SQL query from agent's JSON response.
        
        Args:
            agent_response (str): The full response from the agent (should be JSON)
            
        Returns:
            str: Extracted SQL query or None if no query is found
        """
        self.logger.info("Extracting SQL query from agent response")
        self.logger.info(f"Agent response: {agent_response}")

        try:
            # Parse the JSON response
            response_data = json.loads(agent_response)
            
            # Extract the SQL query
            sql_query = response_data.get('sql_query')
            
            # Return None if no query or query is null
            if not sql_query:
                self.logger.info("No SQL query in response (null or missing)")
                return None
                
            return sql_query.strip()
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse agent response as JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting SQL query: {e}")
            return None
    
    def _calculate_sql_accuracy(self, agent_response: str, qa_pair: Dict) -> Dict[str, float]:
        """
        Calculate SQL accuracy by comparing query results.
        Returns a dictionary with different accuracy metrics.
        """
        # Extract SQL query from agent response (implement based on your agent's output format)
        agent_sql = self._extract_sql_query(agent_response)

        self.logger.info(f"Evaluating SQL accuracy for question_id: {qa_pair.get('id', 'unknown')}")
    
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

        """
        Cette méthode calcule l'exactitude SQL en trois composantes :

        1. query_present (20% du score) :
          - Vérifie si l'agent a généré une requête SQL
          - Score de 1.0 si une requête est présente, 0.0 sinon

        2. execution_success (30% du score) :
          - Vérifie si la requête s'exécute sans erreur
          - Score de 1.0 si la requête s'exécute, 0.0 sinon

        3. results_match (50% du score) :
          - Compare les résultats des requêtes de l'agent et de référence
          - Utilise la similarité de Jaccard (intersection/union)
          - Gère les cas spéciaux comme les ensembles vides

        La méthode retourne un dictionnaire avec tous les scores composants et le score combiné pondéré.
        """
        # Calculate combined score
        # Weights could be adjusted based on importance
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

    def _calculate_semantic_accuracy(self, agent_response: str, qa_pair: Dict) -> float:
        """Calculate semantic similarity between responses"""

        agent = CodeAgent(
            tools=[],
            model=self.model        
        )

        prompt = f"""Compare these two responses and rate their semantic similarity from 0 to 1:
        Expected: {qa_pair['answers']['en']}
        Actual: {agent_response}
        
        Consider:
        1. Key information present in both responses
        2. Factual consistency
        3. Completeness of information
        
        Return only a number between 0 and 1."""
        
        # Use model (Claude) to evaluate semantic similarity
        similarity = float(agent.run(prompt))
        return similarity

    def _calculate_data_coverage(self, agent_response: str, qa_pair: Dict) -> Dict[str, float]:
        """Evaluate data coverage and alternative sources"""
        # Check if the question requires database access
        db_required = "SELECT" in qa_pair['sql']
        
        # Check if the agent used food guide information
        food_guide_used = any(indicator in agent_response.lower() for indicator in [
            "according to the food guide",
            "food guide recommends",
            "guide alimentaire"
        ])
        
        # Check for missing data acknowledgment
        missing_data_handled = self._check_missing_data_handling(agent_response, qa_pair['answers']['en'])
        
        # Calculate components
        db_coverage = 1.0 if not db_required or not missing_data_handled else 0.0
        alternative_sources = 1.0 if food_guide_used and missing_data_handled else 0.0
        
        return {
            "db_coverage": db_coverage,
            "alternative_sources": alternative_sources,
            "combined": (db_coverage + alternative_sources) / 2
        }

    def _check_missing_data_handling(self, agent_response: str, expected_answer: str) -> bool:
        """Check if agent properly handles missing data"""
        missing_data_indicators = [
            # English indicators
            "data is not available",
            "information is missing",
            "no data",
            "incomplete data",
            "alternatively",
            "estimate",
            
            # French indicators
            "données non disponibles",
            "données manquantes",
            "information manquante",
            "pas de données",
            "données incomplètes",
            "alternativement",
            "estimation"
        ]

        # Check if both responses acknowledge missing data
        agent_handles = any(indicator in agent_response.lower() 
                          for indicator in missing_data_indicators)
        expected_handles = any(indicator in expected_answer.lower() 
                             for indicator in missing_data_indicators)

        return agent_handles == expected_handles

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

        results = []
        qa_pairs = self.qa_pairs[:max_cases] if max_cases else self.qa_pairs

        for qa_pair in qa_pairs: 
            try:
                result = self.evaluate_single_case(agent, qa_pair, lang)
                results.append(result)
                self.logger.info(f"Evaluated question {result.question_id}")
            except Exception as e:
                self.logger.error(f"Error evaluating question {qa_pair.get('id', 0)}: {e}")

        # Calculate metrics
        metrics = self.calculate_metrics(results)

        # Log detailed results
        self._log_detailed_results(results, metrics)

        return metrics

    def calculate_metrics(self, results: List[EvaluationResult]) -> Dict[str, float]:
        """Calculate the three main metrics"""
        total = len(results)
        if total == 0:
            return {
                "execution_accuracy": 0.0,
                "missing_data_coverage": 0.0,
                "avg_response_time": 0.0
            }

        # Execution Accuracy (EX)
        execution_accuracy = sum(1 for r in results if r.execution_success) / total

        # Missing Data Coverage Rate (TCM)
        missing_data_coverage = sum(1 for r in results if r.missing_data_handled) / total

        # Average Response Time (TRM)
        avg_response_time = mean(r.response_time for r in results)

        return {
            "execution_accuracy": execution_accuracy * 100,
            "missing_data_coverage": missing_data_coverage * 100,
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
            f.write(f"- Missing Data Coverage (TCM): {metrics['missing_data_coverage']:.2f}%\n")
            f.write(f"- Average Response Time (TRM): {metrics['avg_response_time']:.2f}s\n\n")

            # Write detailed results
            f.write("## Detailed Results\n\n")
            for r in results:
                f.write(f"### Question {r.question_id}\n")
                f.write(f"**English Question:** {r.question['en']}\n")
                f.write(f"**Response Time:** {r.response_time:.2f}s\n")
                f.write(f"**Execution Success:** {r.execution_success}\n")
                f.write(f"**Missing Data Handled:** {r.missing_data_handled}\n")
                if r.error:
                    f.write(f"**Error:** {r.error}\n")
                f.write("\n")

def create_agent(model: LiteLLMModel) -> CodeAgent:
    """Create and initialize the conversational agent"""
    
    # Initialize tools
    docs_path = Path("../data/columns_documentation.json")
    cache_dir = Path("../data/cache")
    search_db_docs = SearchDatabaseDocumentationTool(docs_path, cache_dir)
    
    filtered_db_path = Path("../data/food_canada.duckdb")
    query_db = QueryDatabaseTool(db_path=filtered_db_path)
    
    search_food_guide = SearchCanadaFoodGuideTool()
    visit_webpage = VisitWebpageTool()
    
    # Create agent
    agent = CodeAgent(
        tools=[search_db_docs, query_db, search_food_guide, visit_webpage],
        model=model,
        additional_authorized_imports=["json"]
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
    engine = "ollama" # or "anthropic"
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
    print(f"Missing Data Coverage (TCM): {metrics['missing_data_coverage']:.2f}%")
    print(f"Average Response Time (TRM): {metrics['avg_response_time']:.2f}s")

if __name__ == "__main__":
    main()
