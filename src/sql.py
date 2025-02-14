from pathlib import Path
from textwrap import dedent

import duckdb

DATA_DIR = Path("../data")
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

def execute_query(duckdb_path: Path, query: str) -> str:
    try:
        with duckdb.connect(str(duckdb_path)) as con:
            result = con.sql(query)
            print(result)
    except Exception as e:
        return f"Error executing query: {e}"
 
if __name__ == "__main__":
    duckdb_path = FULL_DB_PATH
    duckdb_path = FILTERED_DB_PATH

    query = dedent("""\
        SELECT unnested_category, COUNT(*) as product_count FROM products, UNNEST(categories_tags) as unnested_category GROUP BY unnested_category ORDER BY product_count DESC LIMIT 1000;
        """)
    execute_query(duckdb_path, query)
