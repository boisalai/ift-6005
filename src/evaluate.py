"""
Evaluation script for the Open Food Facts conversational agent.
Calculates three performance metrics:
- Execution Accuracy (EX)
- Missing Data Coverage Rate (TCM)
- Average Response Time (TRM)
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging
from dotenv import load_dotenv
from statistics import mean
import duckdb

# Import agent components from chatbot script
from chatbot_18 import (
    create_model,
    FaissDocumentationTool,
    DuckDBSearchTool,
    FoodGuideSearchTool,
    VisitWebpageTool,
    CodeAgent,
    AGENT_INSTRUCTIONS
)


from smolagents import (
    Tool,
    CodeAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    LiteLLMModel,
)


# Load environment variables
load_dotenv()

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
    def __init__(self, db_path: Path, qa_path: Path):
        self.db_path = db_path
        self.qa_pairs = self._load_qa_pairs(qa_path)
        self.connection = duckdb.connect(str(db_path))
        self.logger = logging.getLogger(__name__)

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

    def evaluate_single_case(self, agent, qa_pair: Dict, lang: str ) -> EvaluationResult:
        """
        Evaluates a single Q&A test case.

        Args:
            qa_pair: Test case containing the question and answer
            lang (str): Language code ('en' or 'fr'). Defaults to 'en'
        """
        if lang not in ['en', 'fr']:
            raise ValueError("Language must be 'en' or 'fr'")
        
        question = qa_pair['questions'][lang]

        print(f"DEBUG Question: {question_en}")

        # Measure response time
        start_time = time.time()
        agent_response = agent.run(
            question,
            additional_args={
                "additional_notes": AGENT_INSTRUCTIONS,
            },
        )
        response_time = time.time() - start_time

        # Extract SQL query from agent response (implementation depends on agent output format)
        sql_query = self._extract_sql_query(agent_response)

        # Execute reference and agent queries
        ref_result = self.execute_query(qa_pair['sql'])
        agent_result = self.execute_query(sql_query) if sql_query else None

        # Check execution success
        execution_success = False
        if agent_result and ref_result.success and agent_result.success:
            execution_success = self._compare_results(ref_result.results, agent_result.results)

        # Check missing data handling
        missing_data_handled = self._check_missing_data_handling(
            agent_response, 
            qa_pair['answers']['en']
        )

        return EvaluationResult(
            question_id=qa_pair.get('id', 0),
            question=qa_pair['questions'],
            expected_answer=qa_pair['answers'],
            agent_answer={'en': agent_response},
            sql_query=sql_query,
            response_time=response_time,
            execution_success=execution_success,
            missing_data_handled=missing_data_handled
        )

    def _extract_sql_query(self, agent_response: str) -> str:
        """Extract SQL query from agent response"""
        # Implementation depends on how your agent formats its response
        # This is a simple example - adapt based on your agent's output format
        try:
            if "SELECT" in agent_response:
                # Very basic extraction - improve based on your needs
                start = agent_response.find("SELECT")
                end = agent_response.find(";", start)
                if end == -1:
                    end = len(agent_response)
                return agent_response[start:end].strip()
            return None
        except Exception as e:
            self.logger.error(f"Error extracting SQL query: {e}")
            return None

    def _compare_results(self, ref_results: List[Tuple], agent_results: List[Tuple]) -> bool:
        """Compare query results for equality"""
        # Convert tuples to sets for comparison
        ref_set = set(ref_results)
        agent_set = set(agent_results)

        # Calculate overlap
        overlap = len(ref_set.intersection(agent_set))
        total = len(ref_set.union(agent_set))

        # Consider results equal if they have high overlap
        return overlap / total >= 0.9 if total > 0 else False

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

    def evaluate_all(self, agent, lang: str) -> Dict[str, float]:
        """Evaluate agent on all Q&A pairs"""
        results = []
        for qa_pair in self.qa_pairs[:1]:  # ?? Limit to 1 for testing
            try:
                result = self.evaluate_single_case(agent, qa_pair, lang='en')
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

def create_agent() -> CodeAgent:
    """Create and initialize the conversational agent"""
    # Initialize model
    if True:
        model = LiteLLMModel(
            model_id="ollama/llama3.1:8b-instruct-q8_0",
            api_base="http://localhost:11434",
            num_ctx=8192
        )
    else:
        model = create_model("claude-sonnet")
    
    # Initialize tools
    docs_path = Path("../data/columns_documentation.json")
    cache_dir = Path("../data/cache")
    faiss_docs = FaissDocumentationTool(docs_path, cache_dir)
    
    filtered_db_path = Path("../data/food_canada.duckdb")
    sql_db = DuckDBSearchTool(db_path=filtered_db_path)
    
    search_webpage = FoodGuideSearchTool()
    visit_webpage = VisitWebpageTool()
    
    # Create agent
    agent = CodeAgent(
        tools=[faiss_docs, sql_db, search_webpage, visit_webpage],
        model=model,
        additional_authorized_imports=["json"]
    )
    
    return agent

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize paths
    db_path = Path("../data/food_canada.duckdb")
    qa_path = Path("../data/qa_pairs.json")
    
    # Create evaluator
    evaluator = AgentEvaluator(db_path, qa_path)
    
    # Initialize agent
    try:
        agent = create_agent()
        logging.info("Agent initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize agent: {e}")
        return
    
    # Run evaluation
    lang = 'en'
    metrics = evaluator.evaluate_all(agent, lang)
    
    # Print results
    print("\nEvaluation Results:")
    print(f"Language: {lang}")
    print(f"Execution Accuracy (EX): {metrics['execution_accuracy']:.2f}%")
    print(f"Missing Data Coverage (TCM): {metrics['missing_data_coverage']:.2f}%")
    print(f"Average Response Time (TRM): {metrics['avg_response_time']:.2f}s")

if __name__ == "__main__":
    main()
