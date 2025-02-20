# Question-Answer Pairs Generation

This document explains how we generate a dataset of question-answer pairs for evaluating our conversational agent. The process is implemented in the `question_answer.py` script.

## Overview

The Q&A generation process uses the previously documented SQL queries from `columns_documentation.json` to create realistic question-answer pairs. Each query is analyzed to determine if it represents a meaningful consumer question about food products.

## Key Components

### 1. Query Execution Tool

The `QueryExecutionTool` class provides safe database access with result formatting:

```python
def forward(self, query: str) -> str:
    """Execute SQL query and return results"""
    try:
        result = self.connection.sql(query)
        output = self.format_output(result.columns, result.fetchall())
        return json.dumps(output)
    except Exception as e:
        return json.dumps({"error": f"Database error: {str(e)}"})
```

### 2. Query Structure

The `SQLQuery` dataclass defines the structure for storing queries and their metadata:

```python
@dataclass
class SQLQuery:
    column: str
    description: str
    sql: str
    results: Optional[List[tuple]] = None
    is_relevant: bool = False
    reasoning: Optional[str] = None
    questions: Dict[str, str] = None  # {'fr': '...', 'en': '...'}
    answers: Dict[str, str] = None    # {'fr': '...', 'en': '...'}
```

### 3. Agent Evaluation Process

For each SQL query from the documentation, the agent:

1. Evaluates Query Relevance:
   - Determines if query answers a real consumer question
   - Checks if results provide actionable food information
   - Verifies practical relevance for consumers

2. Automatic Rejection Criteria:
   - Database metadata queries
   - Data quality statistics
   - Technical maintenance queries
   - Internal identifiers queries

3. For Relevant Queries:
   - Generates natural questions in French and English
   - Creates clear consumer-focused answers
   - Validates query results support the answers

## Q&A Generation Process

The process follows these steps:

1. Load Queries from Documentation:
```python
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
```

2. Process Each Query:
```python
def process_query(query: SQLQuery, sql_executor: QueryExecutionTool, agent: CodeAgent) -> Optional[int]:
    """Process a single SQL query and generate Q&A data"""
    # Execute query
    result = sql_executor.forward(query.sql)
    
    prompt = dedent(
    """\
    Analyze this SQL query and its results:
    Column: "{query.column}"
    Description: "{query.description}"
    SQL: "{query.sql}"
    
    Determine if this query would be DIRECTLY useful for consumers making food choices.

    etc.
    """
    ).format(query=query)

    # Agent analyzes results and determines relevance
    analysis = agent.run(prompt)
    
    if query.is_relevant:
        # Generate questions and answers
        add_qa_pair(query, output_path)
```

3. Save Q&A Pairs:
```python
def add_qa_pair(query: SQLQuery, output_path: Path):
    """Add a new QA pair to the JSON file"""
    if query.is_relevant and query.questions and query.answers:
        qa_pairs = load_existing_qa_pairs(output_path)
        
        new_pair = {
            'column': query.column,
            'sql': query.sql,
            'questions': query.questions,
            'answers': query.answers
        }
        
        if not any(pair['sql'] == query.sql for pair in qa_pairs):
            qa_pairs.append(new_pair)
            save_qa_pairs(qa_pairs, output_path)
```

## Q&A Pairs Structure

The Q&A pairs are stored in `qa_pairs.json` with the following structure:

```json
[
    {
        "column": "product_name",
        "sql": "SELECT code, UNNEST(...) FROM products WHERE ...",
        "questions": {
            "fr": "Quels sont les produits bio disponibles?",
            "en": "What organic products are available?"
        },
        "answers": {
            "fr": "Voici la liste des produits biologiques...",
            "en": "Here is the list of organic products..."
        }
    },
    {
        "column": "nutriscore_grade",
        "sql": "SELECT code, product_name FROM products WHERE...",
        "questions": {
            "fr": "Quels produits ont un Nutri-Score A?",
            "en": "Which products have a Nutri-Score A?"
        },
        "answers": {
            "fr": "Les produits suivants ont un Nutri-Score A...",
            "en": "The following products have a Nutri-Score A..."
        }
    }
    // ... more Q&A pairs
]
```


## Usage for Evaluation

These Q&A pairs will be used to:
1. Test the agent's SQL query generation
2. Verify answer accuracy
3. Evaluate multilingual capabilities
4. Assess response quality

The evaluation process will compare the agent's responses to these pre-validated answers to measure:
- Query correctness
- Answer accuracy
- Language consistency
- Response relevance
