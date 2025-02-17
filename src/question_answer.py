import os
import json
from pathlib import Path
from textwrap import dedent
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import duckdb
from smolagents import Tool, CodeAgent, LiteLLMModel

# Chemins des fichiers
DATA_DIR = Path("../data")
DOCS_DIR = Path("../docs")
DB_PATH = DATA_DIR / "food_canada.duckdb"
DOCS_PATH = DOCS_DIR / "data" / "columns_documentation.json"

@dataclass
class SQLQuery:
    """Structure pour stocker une requête SQL et ses métadonnées"""
    column: str
    description: str
    sql: str
    results: Optional[List[tuple]] = None
    is_relevant: bool = False
    reasoning: str
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
        "query": {
            "type": "string", 
            "description": "Valid DuckDB SQL query to execute"}
    }
    output_type = "string"


    def __init__(self, db_path: Path):
        super().__init__()
        self.db_path = db_path
        self.connection = None
        
    def setup(self) -> None:
        self.connection = duckdb.connect(str(self.db_path))
        self.is_initialized = True
    
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

def process_queries() -> List[SQLQuery]:
    """Process SQL queries to generate the Q&A dataset"""
    # Initialize tools and agent
    model = LiteLLMModel(
        model_id="ollama/llama3.1:8b-instruct-q8_0",
        api_base="http://localhost:11434",
    )
    
    sql_executor = QueryExecutionTool(DB_PATH)
    
    agent = CodeAgent(
        tools=[sql_executor],
        model=model
    )
    
    # Load and process queries
    queries = load_queries_from_json(DOCS_PATH)
    processed_queries = []

    for query in queries:
        # Execute query
        result_str = sql_executor.forward(query.sql)
        result_dict = json.loads(result_str)

        if not result_dict['success']:
            continue
        
        query.results = result_dict['rows']
        
        # 2. Analyze relevance and generate Q&A
        analysis = agent.run(
            f"""
            Analyze this SQL query and its results:
            Column: {query.column}
            Description: {query.description}
            SQL: {query.sql}
            Results: {query.results}
            
            Determine if this query would be useful for users interested in food products.
            If relevant, generate a natural question in French and English that this query answers,
            and generate appropriate responses in both languages based on the query results.

            EVALUATION CRITERIA:
            1. Usefulness: Would the information help users make food choices?
            2. Clarity: Are the results clear and interpretable?
            3. Scope: Does it address a specific, focused question?
            4. Actionability: Can users act on this information?

            RESPONSE FORMAT:
            Returns a JSON-formatted string that must be parsed using json.loads() before use. The parsed structure will be:
            ```json
            {
                "column": "Name of the column being queried",
                "description": "Short description of the query",
                "sql": "SQL query being analyzed",
                "results": "Results of the SQL query",
                "is_relevant": true/false,
                "reasoning": "Explanation of decision",
                "suggested_question_fr": "Question en français",
                "suggested_question_en": "Question in English",
                "suggested_answer_fr": "Réponse en français",
                "suggested_answer_en": "Answer in English"
            }
            """
        )
        
        print(f"DEBUG: analysis={analysis}")

        # Process agent response
        try:
            analysis_dict = json.loads(analysis)
            query.is_relevant = analysis_dict['is_relevant']
            if query.is_relevant:
                query.questions = {
                    'fr': analysis_dict['suggested_question_fr'],
                    'en': analysis_dict['suggested_question_en']
                }
                query.answers = {
                    'fr': analysis_dict['suggested_answer_fr'],
                    'en': analysis_dict['suggested_answer_en']
                }
                processed_queries.append(query)
        except json.JSONDecodeError:
            continue
            
    return processed_queries

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

def main():
    # Traiter les requêtes
    processed_queries = process_queries()
    
    # Sauvegarder les résultats
    output_path = DATA_DIR / "qa_pairs.json"
    save_qa_pairs(processed_queries, output_path)
    
    # Afficher les statistiques
    print(f"Total queries processed: {len(processed_queries)}")
    print(f"Relevant queries: {sum(1 for q in processed_queries if q.is_relevant)}")
    print(f"QA pairs generated: {sum(1 for q in processed_queries if q.questions and q.answers)}")

if __name__ == "__main__":
    main()