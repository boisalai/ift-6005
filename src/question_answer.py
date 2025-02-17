import argparse
import json
import logging
from dotenv import load_dotenv
from pathlib import Path
from textwrap import dedent
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

import duckdb
from smolagents import Tool, CodeAgent, LiteLLMModel

# Configure logging
# See https://docs.python.org/3/library/logging.html
logging.basicConfig(filename='myapp.log', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Chemins des fichiers
DATA_DIR = Path("../data")
DOCS_PATH = DATA_DIR / "columns_documentation.json"

@dataclass
class SQLQuery:
    """Structure pour stocker une requête SQL et ses métadonnées"""
    column: str
    description: str
    sql: str
    results: Optional[List[tuple]] = None
    is_relevant: bool = False
    reasoning: Optional[str] = None
    questions: Dict[str, str] = None  # {'fr': '...', 'en': '...'}
    answers: Dict[str, str] = None    # {'fr': '...', 'en': '...'}

class QueryExecutionTool(Tool):
    """Outil pour exécuter les requêtes SQL"""
    name = "sql_executor"
    description = dedent(
        """\
    Executes SQL queries against the Open Food Facts database"
    Execute SQL queries using DuckDB syntax. The database contains a single table named `products` with
    detailed information about food items.

    RESPONSE FORMAT:
    The tool returns a JSON object with the following structure:
    ```json
    {
        "columns": ["col1", "col2", ...],     // Array of column names
        "rows": [                             // Array of row values (max 10)
            ["val1", "val2", ...],            // Each value converted to string
            ...
        ],
        "row_count": 42,                      // Total number of results
        "error": "error message"              // Present only if query fails
    }
    ```

    IMPORTANT: Since this tool returns a JSON-formatted string, you must first parse it with:
    ```python
    import json
    results_str = sql_executor(query)
    results = json.loads(results_str)
    count = results["row_count"]
    ```

    ERROR HANDLING:
    - Check "error" field in response for query execution problems
    - Common errors: syntax errors, invalid column names, type mismatches
    - Use TRY_CAST() for safer type conversions
    - Always validate array access with list_contains() before using
    """
    )

    inputs = {
        "query": {
            "type": "string", 
            "description": "Valid DuckDB SQL query to execute"}
    }
    output_type = "string"

    def __init__(self, db_path: Path):
        super().__init__()
        self.db_path = db_path
        self.setup()
        
    def setup(self) -> None:
        """Initialize the DuckDB connection"""
        if not self.db_path.exists():
            print(f"Database file does not exist: {self.db_path}")
        try:
            self.connection = duckdb.connect(str(self.db_path))
            self.is_initialized = True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            raise

    def format_output(self, columns: list, rows: list) -> Dict[str, Any]:
        """Format output as JSON dictionary, limiting to 10 rows"""
        return {
            "columns": columns,
            "rows": [tuple(str(item) for item in row) for row in rows[:10]],
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


def load_queries_from_json(json_path: Path) -> List[SQLQuery]:
    """Load all SQL queries from documentation"""
    with open(json_path, 'r', encoding='utf-8') as f:
        doc = json.load(f)
    
    queries = []
    for column_name, column_info in doc['tables']['products']['columns'].items():
        if 'common_queries' in column_info:
            for query_info in column_info['common_queries']:
                queries.append(SQLQuery(
                    column=column_name,
                    description=query_info['description'],
                    sql=query_info['sql'].strip()
                ))
    
    return queries

def process_query(query: SQLQuery, sql_executor: QueryExecutionTool, agent: CodeAgent) -> Optional[int]:
    """Process a single SQL query and generate Q&A data"""
    output_path = DATA_DIR / "qa_pairs.json"

    # Execute query
    result_str = sql_executor.forward(query.sql)
    result_dict = json.loads(result_str)

    # Skip if query execution failed
    if 'error' in result_dict:
        print(f"Error executing query for column {query.column}: {result_dict['error']}")
        return None

    query.results = result_dict['rows']
    prompt = dedent(
    """\
    Analyze this SQL query and its results:
    Column: "{query.column}"
    Description: "{query.description}"
    SQL: "{query.sql}"
    
    Determine if this query would be DIRECTLY useful for consumers making food choices.

    EVALUATION CRITERIA:
    1. Consumer Value:
    - Does it help consumers make INFORMED FOOD CHOICES?
    - Does it provide nutritional, health, or dietary insights?
    - Does it help identify suitable products for specific needs (allergies, diets)?
    - Is it about actual food characteristics, not database technicalities?

    2. Direct Actionability:
    - Can consumers immediately use this information for food decisions?
    - Does it answer a real consumer question about food products?
    - Is it about the food itself, not metadata or database statistics?

    3. Practical Relevance:
    - Would a typical consumer actually ask this question?
    - Does it address common food shopping concerns?
    - Is it about product characteristics that matter to consumers?

    AUTOMATIC REJECTION CRITERIA:
    - Database metadata (codes, IDs, technical fields)
    - Data quality statistics
    - Contributor/editor information 
    - Data entry timestamps
    - Technical product identifiers
    - Database maintenance information

    If relevant based on these strict criteria, generate:
    1. A natural consumer question in French and English
    2. A clear, consumer-focused answer in both languages based on the query results

    RESPONSE FORMAT:
    Returns a JSON-formatted string that must be parsed using json.loads() before use. The parsed structure will be:
    {{
        "column": "Name of the column being queried",
        "description": "Short description of the query",
        "sql": "SQL query",
        "results": "Results of the SQL query",
        "is_relevant": true/false,
        "reasoning": "Explanation of decision",
        "suggested_question_fr": "Question en français",
        "suggested_question_en": "Question in English",
        "suggested_answer_fr": "Réponse en français",
        "suggested_answer_en": "Answer in English"
    }}
    """
    ).format(query=query)

    # Analyze relevance and generate Q&A
    analysis = agent.run(prompt)
    
    # Process agent response
    try:
        analysis_dict = json.loads(analysis)
        query.is_relevant = analysis_dict['is_relevant']
        if query.is_relevant:
            query.reasoning = analysis_dict['reasoning']
            query.questions = {
                'fr': analysis_dict['suggested_question_fr'],
                'en': analysis_dict['suggested_question_en']
            }
            query.answers = {
                'fr': analysis_dict['suggested_answer_fr'],
                'en': analysis_dict['suggested_answer_en']
            }
            # Add to JSON file
            add_qa_pair(query, output_path)
    except json.JSONDecodeError:
        print(f"Error parsing analysis for column {query.column}")
        return None

    return 1

def initialize_agent() -> Tuple[QueryExecutionTool, CodeAgent]:
    """Initialize the SQL executor and agent"""

    # model = LiteLLMModel(
    #     model_id="ollama/llama3.1:8b-instruct-q8_0",
    #     api_base="http://localhost:11434",
    # )

    model = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-20240620")
    filtered_db_path = DATA_DIR / "food_canada.duckdb"
    sql_executor = QueryExecutionTool(db_path=filtered_db_path)
    
    agent = CodeAgent(
        tools=[sql_executor],
        model=model, 
        additional_authorized_imports=["json"]
    )
    
    return sql_executor, agent



def process_queries(start_index: int = 0) -> Optional[int]:
    """Process SQL queries to generate the Q&A dataset, one at a time"""
    # Initialize tools and agent
    sql_executor, agent = initialize_agent()
    
    # Load queries
    docs_path = DATA_DIR / "columns_documentation.json"
    queries = load_queries_from_json(docs_path)
    print(f"Loaded {len(queries)} queries from documentation")
    print(f"Starting from index {start_index}")

    # Process single query
    if start_index >= len(queries):
        print("All queries have been processed")
        return None
    
    query = queries[start_index]
    result = process_query(query, sql_executor, agent)
    
    if result is not None:
        return start_index + 1
    return None

def load_existing_qa_pairs(output_path: Path) -> list:
    """Load existing QA pairs from JSON file"""
    if output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse {output_path}, starting fresh")
    return []

def add_qa_pair(query: SQLQuery, output_path: Path):
    """Add a new QA pair to the JSON file"""
    if query.is_relevant and query.questions and query.answers:
        # Load existing pairs
        qa_pairs = load_existing_qa_pairs(output_path)
        
        # Add new pair
        new_pair = {
            'column': query.column,
            'sql': query.sql,
            'questions': query.questions,
            'answers': query.answers
        }
        
        # Check if this query is already present
        exists = any(pair['sql'] == query.sql for pair in qa_pairs)
        if not exists:
            qa_pairs.append(new_pair)
            
            # Save updated pairs
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
            print(f"Added new QA pair for column: {query.column}")
        else:
            print(f"QA pair for column {query.column} already exists, skipping")

def save_qa_pairs(queries: List[SQLQuery], output_path: Path):
    """Sauvegarde les paires questions-réponses au format JSON"""
    qa_pairs = []
    for query in queries:
        if query.is_relevant and query.questions and query.answers:
            qa_pairs.append({
                'column': query.column,
                'sql': query.sql,
                'questions': query.questions,
                'answers': query.answers
            })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Process SQL queries to generate Q&A pairs for food products database'
    )
    parser.add_argument(
        'index', 
        type=int, 
        nargs='?',  # Makes the argument optional
        default=None,
        help='Index of the query to process (default: continue from last processed)'
    )
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Get current progress if no index specified
    output_path = DATA_DIR / "qa_pairs.json"
    if args.index is None:
        current_pairs = load_existing_qa_pairs(output_path)
        start_index = len(current_pairs)
    else:
        start_index = args.index
    
    # Process next query
    next_index = process_queries(start_index)
    
    if next_index is not None:
        print(f"Processed query {start_index + 1}")
        print(f"Next index to process: {next_index}")
    else:
        print("Processing complete or error occurred")

def single_query():
    """Process a single custom query"""
    # Initialize tools and agent
    sql_executor, agent = initialize_agent()

    query = SQLQuery(
        column="product_name",
        description="Quels produits sans sucres ajoutés ont un bon score nutritionnel?",
        sql=dedent("""\
            SELECT code, product_name 
            FROM products 
            WHERE NOT array_contains(ingredients_original_tags, 'en:sugar')
            AND nutriscore_grade IN ('a', 'b')
            LIMIT 50;
            """)
    )

    # Process query
    result = process_query(query, sql_executor, agent)
    print("Finished processing query")

if __name__ == "__main__":
    # main()
    single_query()