"""
See https://huggingface.co/docs/smolagents/examples/text_to_sql
pip install litellm
pip install smolagents python-dotenv sqlalchemy --upgrade -q

Ce code fonctionne bien. Il retourne ceci:
python chatbot_08.py
Using Hugging Face API token: None
/Users/alain/Workspace/GitHub/ift-6005/venv/lib/python3.11/site-packages/pydantic/_internal/_config.py:345: UserWarning: Valid config keys have changed in V2:
* 'fields' has been removed
  warnings.warn(message, UserWarning)
╭───────────────────────────────────────────────────────────────────────────────────────────────────── New run ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                                    │
│ Can you give me the name of the client who got the most expensive receipt?                                                                                                                                         │
│                                                                                                                                                                                                                    │
╰─ LiteLLMModel - ollama/phi4:latest ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Step 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ─ Executing parsed code: ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 
  # SQL query to find the customer name of the most expensive receipt                                                                                                                                                 
  query = "SELECT customer_name FROM receipts ORDER BY price DESC LIMIT 1"                                                                                                                                            
  most_expensive_customer = sql_engine(query=query)                                                                                                                                                                   
  final_answer(most_expensive_customer)                                                                                                                                                                               
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 
Out - Final answer: 
('Woodrow Wilson',)
[Step 0: Duration 49.89 seconds| Input tokens: 2,048 | Output tokens: 253]
"""
from dotenv import load_dotenv
import os

load_dotenv()

hf_api_token = os.getenv("HF_API_TOKEN")
print(f"Using Hugging Face API token: {hf_api_token}")

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    Float,
    insert,
    inspect,
    text,
)

engine = create_engine("sqlite:///:memory:")
metadata_obj = MetaData()

def insert_rows_into_table(rows, table, engine=engine):
    for row in rows:
        stmt = insert(table).values(**row)
        with engine.begin() as connection:
            connection.execute(stmt)

table_name = "receipts"
receipts = Table(
    table_name,
    metadata_obj,
    Column("receipt_id", Integer, primary_key=True),
    Column("customer_name", String(16)),
    Column("price", Float),
    Column("tip", Float),
)
metadata_obj.create_all(engine)

rows = [
    {"receipt_id": 1, "customer_name": "Alan Payne", "price": 12.06, "tip": 1.20},
    {"receipt_id": 2, "customer_name": "Alex Mason", "price": 23.86, "tip": 0.24},
    {"receipt_id": 3, "customer_name": "Woodrow Wilson", "price": 53.43, "tip": 5.43},
    {"receipt_id": 4, "customer_name": "Margaret James", "price": 21.11, "tip": 1.00},
]
insert_rows_into_table(rows, receipts)

from smolagents import tool

@tool
def sql_engine(query: str) -> str:
    """
    Allows you to perform SQL queries on the table.
    Returns a string representation of the result.
    The table is named 'receipts'. Its description is as follows:
        Columns:
        - receipt_id (INTEGER): Unique receipt identifier, primary key
        - customer_name (VARCHAR(16)): Customer's name
        - price (FLOAT): Total receipt amount
        - tip (FLOAT): Tip amount

    Args:
        query: The query to perform. This should be correct SQL.
    """
    output = ""
    with engine.connect() as con:
        rows = con.execute(text(query))
        for row in rows:
            output += "\n" + str(row)
    return output

import litellm
from smolagents import CodeAgent, LiteLLMModel

os.environ['LITELLM_LOG'] = 'DEBUG'

model = LiteLLMModel(
    model_id="ollama/phi4:latest", # This model is a bit weak for agentic behaviours though
    api_base="http://localhost:11434", # replace with 127.0.0.1:11434 or remote open-ai compatible server if necessary
    temperature=0.1,  # Réduit les hallucinations
)

agent = CodeAgent(
    tools=[sql_engine],
    model=model,
)
agent.run("Can you give me the name of the client who got the most expensive receipt?")
