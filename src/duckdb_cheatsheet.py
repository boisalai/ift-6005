import json
from pathlib import Path
from textwrap import dedent
from typing import Dict, Any

import duckdb

# Define file paths
DATA_DIR = Path("../data")
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

DOCS_DATA_DIR = Path("../docs/data")
OUTPUT_PATH = DOCS_DATA_DIR / "duckdb_cheatsheet.md"
DATA_DICT_PATH = DOCS_DATA_DIR / "data_dict.json"

def load_dict() -> None:
    # Load data dictionary
    with open(DATA_DICT_PATH, 'r', encoding='utf-8') as f:
        data_dict = json.load(f)

    output = ""
    for k, v in data_dict.items():
        output += f"- {k} ({v['type']}): {v['description']}\n"
    print(output)

def print_title(query: str, output_file: Path) -> None:
    comment = ""
    for line in query.split('\n'):
        if line.strip().startswith('--'):
            comment = line.strip().replace('--', '').strip()
            break
    
    # Print comment as markdown title
    if comment:
        with open(output_file, 'a') as f:
            f.write(f"\n### {comment}\n")

def execute_query(duckdb_path: Path, query: str, output_file: Path, indent: int = None) -> str:
    print_title(query, output_file)

    with open(output_file, 'a') as f:
        f.write(f"```sql\n{query}```\n")
        try:
            with duckdb.connect(str(duckdb_path)) as con:
                result = con.sql(query)
                f.write(f"```text\n{result}```")
        except Exception as e:
            return f"Error executing query: {e}"

def execute_query_list(duckdb_path: Path, query: str, output_file: Path, ) -> str:
    print_title(query, output_file)

    with open(output_file, 'a') as f:
        f.write(f"```sql\n{query}```\n")
        try:
            with duckdb.connect(str(duckdb_path)) as con:
                result = con.sql(query)
                # Get all results
                all_results = result.fetchall()
                columns = result.columns
                
                # Create markdown table header
                header = "| " + " | ".join(columns) + " |"
                separator = "| " + " | ".join(["---" for _ in columns]) + " |"
                
                # Print table header
                f.write(f"{header}\n")
                f.write(f"{separator}\n")
                
                # Print rows
                for row in all_results:
                    # Convert all values to strings and handle None values
                    row_values = [str(val) if val is not None else "" for val in row]
                    f.write(f"| " + " | ".join(row_values) + " |\n")
                
                # Print total rows count
                f.write(f"\nTotal number of rows: {len(all_results)}")
                
        except Exception as e:
            return f"Error executing query: {e}"
       
def sql(duckdb_path: Path, index: int, output_file: Path) -> None:    
    if index == 1:
        query = dedent("""\
        -- List all tables in the database
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main';
        """)
        execute_query(duckdb_path, query, output_file)
    
    elif index == 2:
        query = dedent("""\
        -- Show columns in the products table
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'products';
        """)
        execute_query_list(duckdb_path, query, output_file)
    
    elif index == 3:
        query = dedent("""\
        -- Count all rows in the products table 
        SELECT COUNT(*) AS count FROM products;
        """)
        execute_query(duckdb_path, query, output_file)
    
    elif index == 4:
        query = dedent("""\
        -- Product names sample and type
        SELECT 
            product_name,
            typeof(product_name) AS type_colonne
        FROM products 
        LIMIT 20;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 5:
        query = dedent("""\
        -- Gets distinct data types from the products table
        SELECT DISTINCT data_type
        FROM information_schema.columns 
        WHERE table_name = 'products'
        ORDER BY data_type;
        """)
        execute_query(duckdb_path, query, output_file)
    
    # Categories
    elif index == 6:
        query = dedent("""\
        -- Products with milk category (French/English)
        SELECT
            code,
            unnest(
                list_filter (product_name, x -> x.lang == 'main')
            )['text'] AS product_name
        FROM products
        WHERE list_contains(lower(categories_tags), 'en:%milks%')
           OR list_contains(lower(categories_tags), 'fr:%laits%')
        LIMIT 20;
        """)
        execute_query(duckdb_path, query, output_file)
    
    elif index == 7:
        query = dedent("""
        -- Search categories with 'chocolat' or 'chocolate'
        SELECT DISTINCT
            unnest AS category
        FROM products,
            unnest(categories_tags) AS unnest 
        WHERE category LIKE 'fr:%chocolat%' 
        OR category LIKE 'en:%chocolate%'
        ORDER BY category
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)
    elif index == 8:
        query = dedent("""\
        -- Products containing 'chocolat' or 'chocolate' in their French/English categories
        SELECT DISTINCT
            code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            categories_tags
        FROM products
        WHERE array_to_string(categories_tags, ',') LIKE 'fr:%chocolat%' 
        OR array_to_string(categories_tags, ',') LIKE 'en:%chocolate%'
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    # Allergen tags
    elif index == 9:
        query = dedent("""\
        -- Search in the list `allergen_tags` values containing `fr`
        SELECT count(code) AS nb, ANY_VALUE(code) AS code, allergens_tags
        FROM products
        WHERE regexp_matches(array_to_string(allergens_tags, ','), 'fr:')
        GROUP BY allergens_tags
        ORDER BY nb DESC
        LIMIT 10
        """)
        execute_query(duckdb_path, query, output_file)
    elif index == 10:
        query = dedent("""\
        -- Products avec allergies aux arachides
        SELECT
            code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
        allergens_tags
        FROM products
        WHERE list_contains(allergens_tags, 'en:peanuts') 
        OR list_contains(allergens_tags, 'fr:arachides')
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    # NOVA groups
    elif index == 11:
        query = dedent("""\
        -- Number of products per NOVA group
        SELECT nova_group, count(*) AS count
        FROM products
        WHERE nova_group IS NOT NULL
        GROUP BY nova_group
        ORDER BY nova_group;
        """)
        execute_query(duckdb_path, query, output_file)

    # Scores
    elif index == 12:
        query = dedent("""\
        -- Average Nutri-Score by brand with more than 100 products
        SELECT 
            unnest AS brand,
            avg(nutriscore_score) AS avg_score,
            count(*) AS products
        FROM products,
             unnest(brands_tags) AS unnest
        GROUP BY brand
        HAVING count(*) > 100
        ORDER BY avg_score;
        """)
        execute_query(duckdb_path, query, output_file)
    elif index == 13:
        query = dedent("""\
        -- Products without palm oil and good Nutri-Score
        SELECT code, 
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            nutriscore_grade
        FROM products 
        WHERE ingredients_from_palm_oil_n = 0
        AND nutriscore_grade IN ('a','b')
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)
    elif index == 14:
        query = dedent("""\
        -- Products by ecoscore grade
        SELECT 
            ecoscore_grade,
            count(*) as count,
            avg(ecoscore_score) as avg_score
        FROM products
        WHERE ecoscore_grade IS NOT NULL
        GROUP BY ecoscore_grade
        ORDER BY avg_score DESC;
        """)
        execute_query(duckdb_path, query, output_file)

    # Ingredients 
    elif index == 15:
        query = dedent("""\
        -- Products with palm oil
        SELECT 
            code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            ingredients_from_palm_oil_n
        FROM products 
        WHERE ingredients_from_palm_oil_n > 0;
        """)
        execute_query(duckdb_path, query, output_file)
    elif index == 16:
        query = dedent("""\
        -- Products with most ingredients
        SELECT 
            code, 
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            ingredients_n
        FROM products
        WHERE ingredients_n IS NOT NULL
        ORDER BY ingredients_n DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    # Vitamins
    elif index == 17:            
        query = dedent("""\
        -- Most common vitamins
        SELECT 
            unnest AS vitamin,
            count(*) AS count
        FROM products,
            unnest(vitamins_tags) AS unnest
        GROUP BY vitamin
        ORDER BY count DESC;
        """)
        execute_query(duckdb_path, query, output_file)

    # Serving size
    elif index == 18:
        query = dedent("""\
        -- Products by serving size
        SELECT serving_size, count(*) AS count
        FROM products
        WHERE serving_size IS NOT NULL
        GROUP BY serving_size
        ORDER BY count DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    # Labels
    elif index == 19:
        query = dedent("""\
        -- Most used labels
        SELECT 
            unnest AS label,
            count(*) AS count
        FROM products,
            unnest(labels_tags) as unnest
        GROUP BY label
        ORDER BY count DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)
    elif index == 20:
        query = dedent("""\
        -- Organic products
        SELECT code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name
        FROM products
        WHERE list_contains(labels_tags, 'en:organic')
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)
    
    # Stores
    elif index == 21:
        query = dedent("""\
        -- Products by store
        SELECT 
            unnest as store_name,
            count(*) as count
        FROM products,
            unnest(stores_tags) as unnest
        GROUP BY store_name
        ORDER BY count DESC
        LIMIT 5;
        """)
        execute_query(duckdb_path, query, output_file)

    # Completeness
    elif index == 22:
        query = dedent("""\
        -- Complete vs incomplete products
        SELECT 
            complete,
            count(*) as count,
            avg(completeness) as avg_completeness
        FROM products
        GROUP BY complete;
        """)
        execute_query(duckdb_path, query, output_file)
    
    # Food group
    elif index == 23:
        query = dedent("""\
        -- Products by food group
        SELECT 
            unnest AS food_group,
            count(*) AS count
        FROM products,
            unnest(food_groups_tags) AS unnest
        GROUP BY food_group
        ORDER BY count DESC;
        """)
        execute_query(duckdb_path, query, output_file)

    # Creation dates
    elif index == 24:
        query = dedent("""\
        -- Recently added products
        SELECT code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            to_timestamp(created_t) AS added_date
        FROM products
        WHERE created_t IS NOT NULL
        ORDER BY created_t DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)
    elif index == 25:
        query = dedent("""\
        -- Top 10 best contributors in Open Food Facts
        SELECT creator, count(*) AS count
        FROM products
        GROUP BY creator
        ORDER BY count DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)
    elif index == 26:
        query = dedent("""\
        -- Number of added products per year
        SELECT
            entry_dates_tags[3] AS year, count(*) AS count
        FROM products
        GROUP BY year
        ORDER BY year DESC;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 27:
        query = dedent("""\
        -- Products containing 'café', 'cafe', or 'coffee' in their generic name
        SELECT product_name, generic_name
        FROM products
        WHERE lower(generic_name::VARCHAR) LIKE '%café%'
           OR lower(generic_name::VARCHAR) LIKE '%cafe%'
           OR lower(generic_name::VARCHAR) LIKE '%coffee%';
        """)
        execute_query(duckdb_path, query, output_file)
    elif index == 28:
        query = dedent("""\
        -- Find products with all ingredients marked as vegan (no non-vegan or maybe-vegan ingredients)
        -- The ingredients column contains a JSON array where each ingredient has a "vegan" property
        -- that can be "yes", "no", or "maybe". We extract and clean the "text" field of each ingredient.
        --
        -- Example of ingredients JSON structure:
        -- [{"text": "water", "vegan": "yes"}, {"text": "sugar", "vegan": "yes"}]
        --
        -- The query:
        -- 1. Filters for products with only vegan ingredients using LIKE on the raw JSON
        -- 2. Extracts the text field for each ingredient using json_extract
        -- 3. Cleans up the extracted text by removing brackets and quotes
        -- 4. Returns the brand and a comma-separated list of ingredients
        WITH ingredient_array AS (
            SELECT 
                brands,
                TRY_CAST(ingredients AS JSON) AS ingredients_json
            FROM products
            WHERE ingredients IS NOT NULL
            AND ingredients != '[]'
            AND ingredients LIKE '%"vegan":"yes"%'    -- Has at least one vegan ingredient
            AND NOT ingredients LIKE '%"vegan":"no"%'  -- No non-vegan ingredients
            AND NOT ingredients LIKE '%"vegan":"maybe"%' -- No maybe-vegan ingredients
        ),
        clean_ingredients AS (
            SELECT 
                brands,
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        json_extract(ingredients_json, '$[*].text')::VARCHAR,
                        '[\[\]]',
                        ''
                    ),
                    '"',
                    ''
                ) as ingredients_list
            FROM ingredient_array
        )
        SELECT 
            brands,
            ingredients_list
        FROM clean_ingredients
        WHERE LENGTH(ingredients_list) > 0
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 29:
        query = dedent("""\
        SELECT last_editor, COUNT(*) as frequency
        FROM products 
        WHERE last_editor IS NOT NULL
        GROUP BY last_editor
        ORDER BY frequency DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

        query = dedent("""\
        SELECT 
            COUNT(*) as total_products,
            COUNT(DISTINCT last_editor) as unique_editors,
            COUNT(CASE WHEN last_editor IS NOT NULL THEN 1 END) as products_with_editor
        FROM products;
        """)
        execute_query(duckdb_path, query, output_file)

    # =-=-=-=-=-=-=-=-=-

    elif index == 30:
        query = dedent("""\
        -- Find popular products (>100 scans) with good nutrition score (A or B)
        SELECT 
            code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            scans_n,
            nutriscore_grade
        FROM products
        WHERE scans_n > 100 
        AND nutriscore_grade IN ('a', 'b')
        ORDER BY scans_n DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 31:
        query = dedent("""\
        -- Average number of additives by brand (for brands with >50 products)
        SELECT 
            unnest AS brand,
            AVG(additives_n) as avg_additives,
            COUNT(*) as total_products
        FROM products,
            unnest(brands_tags) AS unnest
        WHERE additives_n IS NOT NULL
        GROUP BY brand
        HAVING COUNT(*) > 50
        ORDER BY avg_additives DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 32:
        query = dedent("""\
        -- Product creation trends by month in 2024
        SELECT 
            DATE_TRUNC('month', to_timestamp(created_t)) AS month,
            COUNT(*) as new_products
        FROM products
        WHERE created_t >= 1704067200  -- Jan 1, 2024
        GROUP BY month
        ORDER BY month;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 33:
        query = dedent("""\
        -- Products with complete information and images
        SELECT 
            code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            completeness
        FROM products
        WHERE complete = 1 
        AND images IS NOT NULL
        AND completeness > 0.9
        ORDER BY completeness DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 34:
        query = dedent("""\
        -- Correlation between Nutri-Score and Eco-Score
        SELECT 
            nutriscore_grade,
            ecoscore_grade,
            COUNT(*) as count
        FROM products
        WHERE nutriscore_grade IS NOT NULL 
        AND ecoscore_grade IS NOT NULL
        GROUP BY nutriscore_grade, ecoscore_grade
        ORDER BY nutriscore_grade, ecoscore_grade;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 35:
        query = dedent("""\
        -- Average number of ingredients by food group
        SELECT 
            unnest AS food_group,
            AVG(ingredients_n) as avg_ingredients,
            MIN(ingredients_n) as min_ingredients,
            MAX(ingredients_n) as max_ingredients
        FROM products,
            unnest(food_groups_tags) AS unnest
        WHERE ingredients_n IS NOT NULL
        GROUP BY food_group
        ORDER BY avg_ingredients DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 36:
        query = dedent("""\
        -- Categories with the most products without additives
        SELECT 
            unnest AS category,
            COUNT(*) as count
        FROM products,
            unnest(categories_tags) AS unnest
        WHERE additives_n = 0
        GROUP BY category
        ORDER BY count DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 37:
        query = dedent("""\
        -- Most common conservation conditions
        SELECT 
            unnest AS condition,
            COUNT(*) as count
        FROM products,
            unnest(conservation_conditions_tags) AS unnest
        GROUP BY condition
        ORDER BY count DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 38:
        query = dedent("""\
        -- Products with multiple allergens
        SELECT 
            code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            ARRAY_LENGTH(allergens_tags) as allergen_count,
            allergens_tags
        FROM products
        WHERE allergens_tags IS NOT NULL
        AND ARRAY_LENGTH(allergens_tags) > 3
        ORDER BY ARRAY_LENGTH(allergens_tags) DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 39:
        query = dedent("""\
        -- Brands distribution by country
        SELECT 
            unnest as country,
            COUNT(DISTINCT b.brand) as unique_brands,
            COUNT(*) as total_products
        FROM products,
            unnest(countries_tags) as unnest,
            unnest(brands_tags) as b(brand)
        GROUP BY country
        HAVING COUNT(*) > 100
        ORDER BY unique_brands DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)


    elif index == 40:
        query = dedent("""\
        -- Filter products by category (using list_contains)
        SELECT
            code,
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name
        FROM products
        WHERE list_contains(categories_tags, 'en:milks');

        -- Search in array (using array_to_string)
        SELECT count(code) as nb, allergens_tags
        FROM products
        WHERE regexp_matches(array_to_string(allergens_tags, ','), 'fr:')
        GROUP BY allergens_tags
        ORDER BY nb DESC;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 41:
        query = dedent("""\
        -- Products by NOVA group
        SELECT nova_group, count(*) AS count
        FROM products
        WHERE nova_group IS NOT NULL
        GROUP BY nova_group
        ORDER BY nova_group;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 42:
        query = dedent("""\
        -- Products with good Nutri-Score and no palm oil
        SELECT code, 
            unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
            nutriscore_grade
        FROM products 
        WHERE ingredients_from_palm_oil_n = 0
        AND nutriscore_grade IN ('a','b')
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 43:
        query = dedent("""\
        -- Most common vitamins
        SELECT 
            unnest AS vitamin,
            count(*) AS count
        FROM products,
            unnest(vitamins_tags) AS unnest
        GROUP BY vitamin
        ORDER BY count DESC;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 44:
        query = dedent("""\
        -- Product completeness
        SELECT 
            complete,
            count(*) as count,
            avg(completeness) as avg_completeness
        FROM products
        GROUP BY complete;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 45:
        query = dedent("""\
        -- Product creation trends by month
        SELECT 
            DATE_TRUNC('month', to_timestamp(created_t)) AS month,
            COUNT(*) as new_products
        FROM products
        WHERE created_t >= 1704067200  -- Jan 1, 2024
        GROUP BY month
        ORDER BY month;
        """)
        execute_query(duckdb_path, query, output_file)

    
if __name__ == "__main__":
    output_file = OUTPUT_PATH
    duckdb_path = FILTERED_DB_PATH
    duckdb_path = FULL_DB_PATH

    open(output_file, 'w').close()
    for index in range(1, 46):
        sql(duckdb_path, index, output_file)
