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
            f.write(f"Error executing query: {e}")
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
    # Requêtes simples (sélections basiques)
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
            TYPEOF(product_name) AS type_colonne
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
    
    elif index == 6:
        query = dedent("""\
        -- Columns by data type
        SELECT 
            data_type,
            ARRAY_AGG(column_name) AS columns
        FROM information_schema.columns 
        WHERE table_name = 'products'
        GROUP BY data_type
        ORDER BY data_type;
        """)
        execute_query_list(duckdb_path, query, output_file)

    elif index == 7:
        query = dedent("""\
        -- Products by serving size
        SELECT serving_size, COUNT(*) AS count
        FROM products
        WHERE serving_size IS NOT NULL
        GROUP BY serving_size
        ORDER BY count DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 8:
        query = dedent("""\
        -- Find top 10 most active product editors/maintainers by number of products edited
        SELECT last_editor, COUNT(*) AS frequency
        FROM products 
        WHERE last_editor IS NOT NULL
        GROUP BY last_editor
        ORDER BY frequency DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 9:
        query = dedent("""\
        -- Get overview of product editor statistics: total products, number of unique editors, and products with editors assigned
        SELECT 
            COUNT(*) AS total_products,
            COUNT(DISTINCT last_editor) AS unique_editors,
            COUNT(CASE WHEN last_editor IS NOT NULL THEN 1 END) AS products_with_editor
        FROM products;
        """)
        execute_query(duckdb_path, query, output_file)

    # Complexités intermédiaires (filtres et agrégations simples) 
    elif index == 10:
        query = dedent("""\
        -- Number of products per NOVA group
        SELECT nova_group, COUNT(*) AS count
        FROM products
        WHERE nova_group IS NOT NULL
        GROUP BY nova_group
        ORDER BY nova_group;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 11:
        query = dedent("""\
        -- Most used labels
        SELECT 
            a.label,
            COUNT(*) AS count
        FROM products,
            UNNEST(labels_tags) AS a(label)
        GROUP BY label
        ORDER BY count DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 12:
        query = dedent("""\
        -- Products by store
        SELECT 
            store_name,
            COUNT(*) AS count
        FROM products,
            UNNEST(stores_tags) AS unnest(store_name)
        GROUP BY store_name
        ORDER BY count DESC
        LIMIT 5;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 13:
        query = dedent("""\
        -- Complete vs incomplete products
        SELECT 
            complete,
            COUNT(*) AS count,
            AVG(completeness) AS avg_completeness
        FROM products
        GROUP BY complete;
        """)
        execute_query(duckdb_path, query, output_file)
    
    elif index == 14:
        query = dedent("""\
        -- Products by food group
        SELECT 
            food_group,
            COUNT(*) AS count
        FROM products,
            UNNEST(food_groups_tags) AS unnest(food_group)
        GROUP BY food_group
        ORDER BY count DESC;
        """)
        execute_query(duckdb_path, query, output_file)

    # Complexes (jointures, sous-requêtes ou fonctions complexes)
    elif index == 15:
        query = dedent("""\
        -- Products with milk category (French/English)
        SELECT DISTINCT
            code,
            UNNEST(LIST_FILTER(product_name, x -> x.lang == 'main'))['text'] AS product_name,
            categories_tags
        FROM products, UNNEST(categories_tags) AS a(category)
        WHERE a.category LIKE 'en:%milk%'
           OR a.category LIKE 'fr:%lait%';
        """)
        execute_query(duckdb_path, query, output_file)
    
    elif index == 16:
        query = dedent("""
        -- Search categories with 'chocolat' or 'chocolate'
        SELECT DISTINCT category
        FROM products,
             UNNEST(categories_tags) AS unnest(category)
        WHERE category LIKE 'fr:%chocolat%' 
           OR category LIKE 'en:%chocolate%'
        ORDER BY category
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)
    
    elif index == 17:
        query = dedent("""\
        -- Products containing 'chocolat' or 'chocolate' in their French/English categories
        SELECT DISTINCT
            code,
            UNNEST(LIST_FILTER(product_name, x -> x.lang == 'main'))['text'] AS name,
            categories_tags
        FROM products,
             UNNEST(categories_tags) AS a(category)
        WHERE a.category LIKE 'fr:%chocolat%' 
           OR a.category LIKE 'en:%chocolate%'
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 19:
        query = dedent("""\
        -- Products with peanut allergies
        SELECT
            code,
            UNNEST(LIST_FILTER(product_name, x -> x.lang == 'main'))['text'] AS name,
        allergens_tags
        FROM products
        WHERE LIST_CONTAINS(allergens_tags, 'en:peanuts') 
           OR LIST_CONTAINS(allergens_tags, 'fr:arachides')
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 20:
        query = dedent("""\
        -- Average Nutri-Score by brand with more than 100 products
        SELECT 
            brand,
            AVG(nutriscore_score) AS avg_score,
            COUNT(*) AS products
        FROM products,
             UNNEST(brands_tags) AS unnest(brand)
        GROUP BY brand
        HAVING COUNT(*) > 100
        ORDER BY avg_score;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 21:
        query = dedent("""\
        -- Products without palm oil and good Nutri-Score
        SELECT code, 
            UNNEST(LIST_FILTER(product_name, x -> x.lang == 'main'))['text'] AS name,
            nutriscore_grade
        FROM products 
        WHERE ingredients_from_palm_oil_n = 0
        AND nutriscore_grade IN ('a','b')
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 22:
        query = dedent("""\
        -- Products by ecoscore grade
        SELECT 
            ecoscore_grade,
            COUNT(*) AS count,
            AVG(ecoscore_score) AS avg_score
        FROM products
        WHERE ecoscore_grade IS NOT NULL
        GROUP BY ecoscore_grade
        ORDER BY avg_score DESC;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 23:
        query = dedent("""\
        -- Products with palm oil
        SELECT 
            code,
            UNNEST(LIST_FILTER(product_name, x -> x.lang == 'main'))['text'] AS name,
            ingredients_from_palm_oil_n
        FROM products 
        WHERE ingredients_from_palm_oil_n > 0;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 24:
        query = dedent("""\
        -- Products with most ingredients
        SELECT 
            code, 
            UNNEST(LIST_FILTER(product_name, x -> x.lang == 'main'))['text'] AS name,
            ingredients_n
        FROM products
        WHERE ingredients_n IS NOT NULL
        ORDER BY ingredients_n DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 25:            
        query = dedent("""\
        -- Most common vitamins
        SELECT 
            vitamin,
            COUNT(*) AS count
        FROM products,
            UNNEST(vitamins_tags) AS unnest(vitamin)
        GROUP BY vitamin
        ORDER BY count DESC;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 26:
        query = dedent("""\
        -- Organic products
        SELECT code,
            UNNEST(LIST_FILTER(product_name, x -> x.lang == 'main'))['text'] AS name
        FROM products
        WHERE LIST_CONTAINS(labels_tags, 'en:organic')
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)
    
    elif index == 27:
        query = dedent("""\
        -- Recently added products
        SELECT code,
            UNNEST(LIST_FILTER(product_name, x -> x.lang == 'main'))['text'] AS name,
            TO_TIMESTAMP(created_t) AS added_date
        FROM products
        WHERE created_t IS NOT NULL
        ORDER BY created_t DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 28:
        query = dedent("""\
        -- Top 10 best contributors in Open Food Facts
        SELECT creator, COUNT(*) AS count
        FROM products
        GROUP BY creator
        ORDER BY count DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)
    
    elif index == 29:
        query = dedent("""\
        -- Number of added products per year
        SELECT
            entry_dates_tags[3] AS year, COUNT(*) AS count
        FROM products
        GROUP BY year
        ORDER BY year DESC;
        """)
        execute_query(duckdb_path, query, output_file)

    # Requêtes plus complexes (multiples jointures, sous-requêtes imbriquées, ou logique complexe)
    elif index == 30:
        query = dedent("""\
        -- Products containing 'café', 'cafe', or 'coffee' in their generic name
        SELECT product_name, generic_name
        FROM products
        WHERE LOWER(generic_name::VARCHAR) LIKE '%café%'
           OR LOWER(generic_name::VARCHAR) LIKE '%cafe%'
           OR LOWER(generic_name::VARCHAR) LIKE '%coffee%';
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 31:
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
                ) AS ingredients_list
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

    elif index == 32:
        query = dedent("""\
        -- Find popular products (>100 scans) with good nutrition score (A or B)
        SELECT 
            code,
            UNNEST(LIST_FILTER(product_name, x -> x.lang == 'main'))['text'] AS name,
            scans_n,
            nutriscore_grade
        FROM products
        WHERE scans_n > 100 
        AND nutriscore_grade IN ('a', 'b')
        ORDER BY scans_n DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 33:
        query = dedent("""\
        -- Average number of additives by brand (for brands with >50 products)
        SELECT 
            brand,
            AVG(additives_n) AS avg_additives,
            COUNT(*) AS total_products
        FROM products,
            UNNEST(brands_tags) AS unnest(brand)
        WHERE additives_n IS NOT NULL
        GROUP BY brand
        HAVING COUNT(*) > 50
        ORDER BY avg_additives DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 34:
        query = dedent("""\
        -- Product creation trends by month in 2024
        SELECT 
            DATE_TRUNC('month', TO_TIMESTAMP(created_t)) AS month,
            COUNT(*) AS new_products
        FROM products
        WHERE created_t >= 1704067200  -- Jan 1, 2024
        GROUP BY month
        ORDER BY month;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 35:
        query = dedent("""\
        -- Products with complete information and images
        SELECT 
            code,
            UNNEST(LIST_FILTER(product_name, x -> x.lang == 'main'))['text'] AS name,
            completeness
        FROM products
        WHERE complete = 1 
        AND images IS NOT NULL
        AND completeness > 0.9
        ORDER BY completeness DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 36:
        query = dedent("""\
        -- Correlation between Nutri-Score and Eco-Score
        SELECT 
            nutriscore_grade,
            ecoscore_grade,
            COUNT(*) AS count
        FROM products
        WHERE nutriscore_grade IS NOT NULL 
        AND ecoscore_grade IS NOT NULL
        GROUP BY nutriscore_grade, ecoscore_grade
        ORDER BY nutriscore_grade, ecoscore_grade;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 37:
        query = dedent("""\
        -- Average number of ingredients by food group
        SELECT 
            food_group,
            AVG(ingredients_n) AS avg_ingredients,
            MIN(ingredients_n) AS min_ingredients,
            MAX(ingredients_n) AS max_ingredients
        FROM products,
            UNNEST(food_groups_tags) AS unnest(food_group)
        WHERE ingredients_n IS NOT NULL
        GROUP BY food_group
        ORDER BY avg_ingredients DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 38:
        query = dedent("""\
        -- Categories with the most products without additives
        SELECT 
            category,
            COUNT(*) AS count
        FROM products,
             UNNEST(categories_tags) AS unnest(category)
        WHERE additives_n = 0
        GROUP BY category
        ORDER BY count DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 40:
        query = dedent("""\
        -- Products with multiple allergens
        SELECT 
            code,
            UNNEST(LIST_FILTER(product_name, x -> x.lang == 'main'))['text'] AS name,
            ARRAY_LENGTH(allergens_tags) AS allergen_count,
            allergens_tags
        FROM products
        WHERE allergens_tags IS NOT NULL
        AND ARRAY_LENGTH(allergens_tags) > 3
        ORDER BY ARRAY_LENGTH(allergens_tags) DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 41:
        query = dedent("""\
        -- Brands distribution by country
        SELECT 
            a.country,
            COUNT(DISTINCT b.brand) AS unique_brands,
            COUNT(*) AS total_products
        FROM products,
            UNNEST(countries_tags) AS a(country),
            UNNEST(brands_tags) AS b(brand)
        GROUP BY country
        HAVING COUNT(*) > 100
        ORDER BY unique_brands DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 42:
        query = dedent("""\
        -- Analyze products with complete nutritional data
        SELECT COUNT(*) AS count,
            COUNT(*) FILTER (WHERE no_nutrition_data = false) AS with_nutrition,
            COUNT(*) FILTER (WHERE no_nutrition_data = true) AS without_nutrition
        FROM products;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 43:
        query = dedent("""\
        -- Examine la structure des nutriments pour les 5 premiers produits
        SELECT code, nutriments 
        FROM products 
        WHERE nutriments IS NOT NULL 
          AND ARRAY_LENGTH(nutriments) > 0 
        LIMIT 2;
        """)
        # execute_query_list(duckdb_path, query, output_file)

        query = dedent("""\
        -- Get all nutrients for a specific product with its name
        SELECT p.code,
            UNNEST(LIST_FILTER(product_name, x -> x.lang = 'main'))['text'] AS name,
            UNNEST(nutriments).name AS nutrient,
            UNNEST(nutriments).value AS value,
            UNNEST(nutriments)."100g" AS per_100g,
            UNNEST(nutriments).unit AS unit
        FROM products p
        WHERE code = '0000101209159'
        AND nutriments IS NOT NULL;
        """)
        # execute_query(duckdb_path, query, output_file)

        query = dedent("""\
        -- Calculate nutrient distribution: shows nutrient types, their measurement units, occurrence count, and average value per 100g across all products, ordered by frequency
        SELECT 
            unnest.name as nutrient_name,
            unnest.unit,
            COUNT(*) as count,
            AVG(unnest."100g") as avg_per_100g
        FROM products, UNNEST(nutriments) as unnest
        GROUP BY unnest.name, unnest.unit
        ORDER BY count DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

        query = dedent("""\
        -- Find top 5 products with highest energy content per 100g, displaying product code, main name and energy value in kcal
        SELECT code,
            UNNEST(LIST_FILTER(product_name, x -> x.lang = 'main'))['text'] AS name,
            unnest."100g" AS energy_100g
        FROM products,
             UNNEST(nutriments) AS unnest
        WHERE unnest.name = 'energy-kcal'
        ORDER BY unnest."100g" DESC
        LIMIT 5;
        """)
        execute_query(duckdb_path, query, output_file)

        query = dedent("""\
        -- Average, minimum and maximum sugar content per 100g across all products
        SELECT 
            AVG(unnest."100g") AS avg_sugar,
            MIN(unnest."100g") AS min_sugar,
            MAX(unnest."100g") AS max_sugar
        FROM products p,
             UNNEST(nutriments) AS unnest
        WHERE unnest.name = 'sugars';
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 44:
        query = dedent("""\
        -- Count obsolete products
        SELECT obsolete, COUNT(*) AS count 
        FROM products
        GROUP BY obsolete;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 45:
        query = dedent("""\
        -- Products with complete packaging info
        SELECT code,
            packagings_complete,
            ARRAY_LENGTH(packagings) AS packaging_count
        FROM products
        WHERE packagings_complete = true
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 46:
        query = dedent("""\
        -- Analyze packaging materials
        SELECT unnest.material,
               COUNT(*) AS count
        FROM products,
             UNNEST(packagings) AS unnest
        GROUP BY unnest.material
        ORDER BY count DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 47:
        query = dedent("""\
        -- Check modification history via owner_fields 
        SELECT code,
            unnest.field_name,
            TO_TIMESTAMP(unnest.timestamp) AS modified_at
        FROM products,
             UNNEST(owner_fields) AS unnest
        ORDER BY unnest.timestamp DESC
        LIMIT 10;
        """)
        execute_query(duckdb_path, query, output_file)

    elif index == 50:
        query = dedent("""\
        SELECT brands 
FROM products 
WHERE brands 
LIKE '%organic%';
                       """)
        execute_query(duckdb_path, query, output_file)

    
if __name__ == "__main__":
    output_file = OUTPUT_PATH
    duckdb_path = FILTERED_DB_PATH
    duckdb_path = FULL_DB_PATH

    open(output_file, 'w').close()
    for index in range(1, 99):
        sql(duckdb_path, index, output_file)
