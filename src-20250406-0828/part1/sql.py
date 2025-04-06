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
        WITH unnested AS ( SELECT unnest(additives_tags) as additive FROM products WHERE additives_tags IS NOT NULL ) SELECT additive, COUNT(*) as frequency FROM unnested GROUP BY additive ORDER BY frequency DESC LIMIT 10;
        """)
    execute_query(duckdb_path, query)
