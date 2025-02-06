# DuckDB Guide for Open Food Facts

## Introduction

Open Food Facts stores its data in a Parquet file that contains various formats (string, list, struct, timestamp). This guide explains how to use DuckDB to analyze this data.

## Prerequisites

1. Download the Parquet file:
```bash
wget -P data/ https://huggingface.co/datasets/openfoodfacts/product-database/resolve/main/food.parquet
```

2. Convert to DuckDB database:

```python
from pathlib import Path
import duckdb

DATA_DIR = Path("../data")
PARQUET_PATH = DATA_DIR / "food.parquet"
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"

def create_full_db():
    """Creates a DuckDB database containing all data from the Parquet file."""    
    con = duckdb.connect(str(FULL_DB_PATH), config={'memory_limit': '8GB'})
    con.execute(f"CREATE TABLE products AS SELECT * FROM '{PARQUET_PATH}'")
    con.close()
```

To create adatabase with only Canadian products, you can use the following code:

```python
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

def create_filtered_db():
    con = duckdb.connect(str(FILTERED_DB_PATH))

    try:
        con.execute(f"ATTACH DATABASE '{FULL_DB_PATH}' AS full_db")
        con.execute(f"""
            CREATE TABLE products AS 
            SELECT * FROM full_db.products
            WHERE array_contains(countries_tags, 'en:canada')
        """)
        count = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        print(f"✅ {count} Canadian products transferred.")
    finally:
        con.execute("DETACH full_db")
        con.close()
```

## Basic Queries

### 1. Exploring the structure

```sql
-- List all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'main';
```text
┌────────────┐
│ table_name │
│  varchar   │
├────────────┤
│ products   │
└────────────┘
```

```sql
-- Show columns in products table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'products';
```
| column_name | data_type |
| --- | --- |
| additives_n | INTEGER |
| additives_tags | VARCHAR[] |
| allergens_tags | VARCHAR[] |
| brands_tags | VARCHAR[] |
| brands | VARCHAR |
... (truncated for brevity)

See complete results in appendix.


### 2. Working with arrays and structs

```sql
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
```

### 3. Nutrition analysis

```sql
-- Products by NOVA group
SELECT nova_group, count(*) AS count
FROM products
WHERE nova_group IS NOT NULL
GROUP BY nova_group
ORDER BY nova_group;

-- Products with good Nutri-Score and no palm oil
SELECT code, 
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    nutriscore_grade
FROM products 
WHERE ingredients_from_palm_oil_n = 0
AND nutriscore_grade IN ('a','b')
LIMIT 10;
```

### 4. Product analysis

```sql
-- Most common vitamins
SELECT 
    unnest AS vitamin,
    count(*) AS count
FROM products,
    unnest(vitamins_tags) AS unnest
GROUP BY vitamin
ORDER BY count DESC;

-- Product completeness
SELECT 
    complete,
    count(*) as count,
    avg(completeness) as avg_completeness
FROM products
GROUP BY complete;
```

## Advanced features

### Working with JSON

Example with vegan ingredients:
```sql
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
```

### Time-based analysis

```sql
-- Product creation trends by month
SELECT 
    DATE_TRUNC('month', to_timestamp(created_t)) AS month,
    COUNT(*) as new_products
FROM products
WHERE created_t >= 1704067200  -- Jan 1, 2024
GROUP BY month
ORDER BY month;
```

## Best Practices

1. Use `list_filter` for structured arrays with language codes
2. Convert arrays to strings with `array_to_string` for text searches
3. Use `unnest` to work with array elements
4. Cast timestamps using `to_timestamp` for date operations
5. Handle NULL values appropriately in aggregations

## Schema Reference

Key data types in the products table:
- VARCHAR[]: Used for tags and lists
- STRUCT: For complex data like product names and images
- INTEGER/FLOAT: For numerical values and scores
- BOOLEAN: For binary flags
- BIGINT: For timestamps

## Appendix

### List all tables in the database
```sql
-- List all tables in the database
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'main';
```
```text
┌────────────┐
│ table_name │
│  varchar   │
├────────────┤
│ products   │
└────────────┘
```
### Show columns in the products table
```sql
-- Show columns in the products table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'products';
```
| column_name | data_type |
| --- | --- |
| additives_n | INTEGER |
| additives_tags | VARCHAR[] |
| allergens_tags | VARCHAR[] |
| brands_tags | VARCHAR[] |
| brands | VARCHAR |
| categories | VARCHAR |
| categories_tags | VARCHAR[] |
| checkers_tags | VARCHAR[] |
| ciqual_food_name_tags | VARCHAR[] |
| cities_tags | VARCHAR[] |
| code | VARCHAR |
| compared_to_category | VARCHAR |
| complete | INTEGER |
| completeness | FLOAT |
| correctors_tags | VARCHAR[] |
| countries_tags | VARCHAR[] |
| created_t | BIGINT |
| creator | VARCHAR |
| data_quality_errors_tags | VARCHAR[] |
| data_quality_info_tags | VARCHAR[] |
| data_quality_warnings_tags | VARCHAR[] |
| data_sources_tags | VARCHAR[] |
| ecoscore_data | VARCHAR |
| ecoscore_grade | VARCHAR |
| ecoscore_score | INTEGER |
| ecoscore_tags | VARCHAR[] |
| editors | VARCHAR[] |
| emb_codes_tags | VARCHAR[] |
| emb_codes | VARCHAR |
| entry_dates_tags | VARCHAR[] |
| food_groups_tags | VARCHAR[] |
| generic_name | STRUCT(lang VARCHAR, "text" VARCHAR)[] |
| images | STRUCT("key" VARCHAR, imgid INTEGER, sizes STRUCT("100" STRUCT(h INTEGER, w INTEGER), "200" STRUCT(h INTEGER, w INTEGER), "400" STRUCT(h INTEGER, w INTEGER), "full" STRUCT(h INTEGER, w INTEGER)), uploaded_t BIGINT, uploader VARCHAR)[] |
| informers_tags | VARCHAR[] |
| ingredients_analysis_tags | VARCHAR[] |
| ingredients_from_palm_oil_n | INTEGER |
| ingredients_n | INTEGER |
| ingredients_original_tags | VARCHAR[] |
| ingredients_percent_analysis | INTEGER |
| ingredients_tags | VARCHAR[] |
| ingredients_text | STRUCT(lang VARCHAR, "text" VARCHAR)[] |
| ingredients_with_specified_percent_n | INTEGER |
| ingredients_with_unspecified_percent_n | INTEGER |
| ingredients_without_ciqual_codes_n | INTEGER |
| ingredients_without_ciqual_codes | VARCHAR[] |
| ingredients | VARCHAR |
| known_ingredients_n | INTEGER |
| labels_tags | VARCHAR[] |
| labels | VARCHAR |
| lang | VARCHAR |
| languages_tags | VARCHAR[] |
| last_edit_dates_tags | VARCHAR[] |
| last_editor | VARCHAR |
| last_image_t | BIGINT |
| last_modified_by | VARCHAR |
| last_modified_t | BIGINT |
| last_updated_t | BIGINT |
| link | VARCHAR |
| main_countries_tags | VARCHAR[] |
| manufacturing_places_tags | VARCHAR[] |
| manufacturing_places | VARCHAR |
| max_imgid | INTEGER |
| minerals_tags | VARCHAR[] |
| misc_tags | VARCHAR[] |
| new_additives_n | INTEGER |
| no_nutrition_data | BOOLEAN |
| nova_group | INTEGER |
| nova_groups_tags | VARCHAR[] |
| nova_groups | VARCHAR |
| nucleotides_tags | VARCHAR[] |
| nutrient_levels_tags | VARCHAR[] |
| nutriments | STRUCT("name" VARCHAR, "value" FLOAT, "100g" FLOAT, serving FLOAT, unit VARCHAR, prepared_value FLOAT, prepared_100g FLOAT, prepared_serving FLOAT, prepared_unit VARCHAR)[] |
| nutriscore_grade | VARCHAR |
| nutriscore_score | INTEGER |
| nutrition_data_per | VARCHAR |
| obsolete | BOOLEAN |
| origins_tags | VARCHAR[] |
| origins | VARCHAR |
| owner_fields | STRUCT(field_name VARCHAR, "timestamp" BIGINT)[] |
| owner | VARCHAR |
| packagings_complete | BOOLEAN |
| packaging_recycling_tags | VARCHAR[] |
| packaging_shapes_tags | VARCHAR[] |
| packaging_tags | VARCHAR[] |
| packaging_text | STRUCT(lang VARCHAR, "text" VARCHAR)[] |
| packaging | VARCHAR |
| packagings | STRUCT(material VARCHAR, number_of_units BIGINT, quantity_per_unit VARCHAR, quantity_per_unit_unit VARCHAR, quantity_per_unit_value VARCHAR, recycling VARCHAR, shape VARCHAR, weight_measured FLOAT)[] |
| photographers | VARCHAR[] |
| popularity_key | BIGINT |
| popularity_tags | VARCHAR[] |
| product_name | STRUCT(lang VARCHAR, "text" VARCHAR)[] |
| product_quantity_unit | VARCHAR |
| product_quantity | VARCHAR |
| purchase_places_tags | VARCHAR[] |
| quantity | VARCHAR |
| rev | INTEGER |
| scans_n | INTEGER |
| serving_quantity | VARCHAR |
| serving_size | VARCHAR |
| states_tags | VARCHAR[] |
| stores_tags | VARCHAR[] |
| stores | VARCHAR |
| traces_tags | VARCHAR[] |
| unique_scans_n | INTEGER |
| unknown_ingredients_n | INTEGER |
| unknown_nutrients_tags | VARCHAR[] |
| vitamins_tags | VARCHAR[] |
| with_non_nutritive_sweeteners | INTEGER |
| with_sweeteners | INTEGER |

Total number of rows: 109
### Count all rows in the products table
```sql
-- Count all rows in the products table 
SELECT COUNT(*) AS count FROM products;
```
```text
┌─────────┐
│  count  │
│  int64  │
├─────────┤
│ 3601655 │
└─────────┘
```
### Product names sample and type
```sql
-- Product names sample and type
SELECT 
    product_name,
    typeof(product_name) AS type_colonne
FROM products 
LIMIT 20;
```
```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬────────────────────────────────────────┐
│                                                                     product_name                                                                     │              type_colonne              │
│                                                        struct(lang varchar, "text" varchar)[]                                                        │                varchar                 │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────┤
│ [{'lang': main, 'text': Véritable pâte à tartiner noisettes chocolat noir}, {'lang': fr, 'text': Véritable pâte à tartiner noisettes chocolat noir}] │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Lagg's, chamomile herbal tea}, {'lang': en, 'text': Lagg's, chamomile herbal tea}]                                           │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Lagg's, herbal tea, peppermint}, {'lang': en, 'text': Lagg's, herbal tea, peppermint}]                                       │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Linden Flowers Tea}, {'lang': en, 'text': Linden Flowers Tea}]                                                               │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Herbal Tea, Hibiscus}, {'lang': en, 'text': Herbal Tea, Hibiscus}]                                                           │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Apple & Cinnamon Tea}, {'lang': en, 'text': Apple & Cinnamon Tea}]                                                           │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Lagg's, green tea}, {'lang': en, 'text': Lagg's, green tea}]                                                                 │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Lagg's, shave grass herbal tea}, {'lang': en, 'text': Lagg's, shave grass herbal tea}]                                       │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Lagg's, herbal tea, chamomile * mint}, {'lang': en, 'text': Lagg's, herbal tea, chamomile * mint}]                           │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Artichoke Herbal Tea}, {'lang': en, 'text': Artichoke Herbal Tea}]                                                           │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Lagg's, dieter's herbal tea}, {'lang': en, 'text': Lagg's, dieter's herbal tea}]                                             │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Lagg's, kidneytea, herbal tea}, {'lang': en, 'text': Lagg's, kidneytea, herbal tea}]                                         │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Lagg's, bronchtea}, {'lang': en, 'text': Lagg's, bronchtea}]                                                                 │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': 100% Pure Canola Oil}, {'lang': en, 'text': 100% Pure Canola Oil}]                                                           │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Original Buttery Spread}, {'lang': la, 'text': Original Buttery Spread}, {'lang': en, 'text': Original Buttery Spread}]      │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Canola harvest, buttery spread, with flaxseed oil}, {'lang': en, 'text': Canola harvest, buttery spread, with flaxseed oil}] │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Today's temptations, lithuanian rye bread}, {'lang': en, 'text': Today's temptations, lithuanian rye bread}]                 │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Escalope de dinde}, {'lang': fr, 'text': Escalope de dinde}]                                                                 │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Madeleine Framboise}, {'lang': fr, 'text': Madeleine Framboise}]                                                             │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
│ [{'lang': main, 'text': Croissants margarine}, {'lang': fr, 'text': Croissants margarine}]                                                           │ STRUCT(lang VARCHAR, "text" VARCHAR)[] │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴────────────────────────────────────────┤
│ 20 rows                                                                                                                                                                             2 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Gets distinct data types from the products table
```sql
-- Gets distinct data types from the products table
SELECT DISTINCT data_type
FROM information_schema.columns 
WHERE table_name = 'products'
ORDER BY data_type;
```
```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                             data_type                                                                                             │
│                                                                                              varchar                                                                                              │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ BIGINT                                                                                                                                                                                            │
│ BOOLEAN                                                                                                                                                                                           │
│ FLOAT                                                                                                                                                                                             │
│ INTEGER                                                                                                                                                                                           │
│ STRUCT("key" VARCHAR, imgid INTEGER, sizes STRUCT("100" STRUCT(h INTEGER, w INTEGER), "200" STRUCT(h INTEGER, w INTEGER), "400" STRUCT(h INTEGER, w INTEGER), "full" STRUCT(h INTEGER, w INTEGE…  │
│ STRUCT("name" VARCHAR, "value" FLOAT, "100g" FLOAT, serving FLOAT, unit VARCHAR, prepared_value FLOAT, prepared_100g FLOAT, prepared_serving FLOAT, prepared_unit VARCHAR)[]                      │
│ STRUCT(field_name VARCHAR, "timestamp" BIGINT)[]                                                                                                                                                  │
│ STRUCT(lang VARCHAR, "text" VARCHAR)[]                                                                                                                                                            │
│ STRUCT(material VARCHAR, number_of_units BIGINT, quantity_per_unit VARCHAR, quantity_per_unit_unit VARCHAR, quantity_per_unit_value VARCHAR, recycling VARCHAR, shape VARCHAR, weight_measured …  │
│ VARCHAR                                                                                                                                                                                           │
│ VARCHAR[]                                                                                                                                                                                         │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              11 rows                                                                                              │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Products with milk category (French/English)
```sql
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
```

### Search categories with 'chocolat' or 'chocolate'
```sql

-- Search categories with 'chocolat' or 'chocolate'
SELECT DISTINCT
    unnest AS category
FROM products,
    unnest(categories_tags) AS unnest 
WHERE category LIKE 'fr:%chocolat%' 
OR category LIKE 'en:%chocolate%'
ORDER BY category
LIMIT 10;
```
```text
┌──────────────────────────────────────────────────────────────┐
│                           category                           │
│                           varchar                            │
├──────────────────────────────────────────────────────────────┤
│ en:100-calories-per-bar-milk-chocolate-no-artificial-colours │
│ en:100-cocoa-solids-dark-chocolate                           │
│ en:45-cocoa-dark-milk-chocolate                              │
│ en:50-dark-chocolate-drops                                   │
│ en:70-dark-chocolate-bar                                     │
│ en:70-dark-chocolate-topped-butter-biscuits-cookies          │
│ en:70-dark-chocolate-with-raspberry-and-meringue-pieces      │
│ en:70-dk-chocolate-topped-butter-cookies-biscuits            │
│ en:75-dark-columbia-sierra-nevada-drinking-chocolate         │
│ en:85-chocolate                                              │
├──────────────────────────────────────────────────────────────┤
│                           10 rows                            │
└──────────────────────────────────────────────────────────────┘
```
### Products containing 'chocolat' or 'chocolate' in their French/English categories
```sql
-- Products containing 'chocolat' or 'chocolate' in their French/English categories
SELECT DISTINCT
    code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    categories_tags
FROM products
WHERE array_to_string(categories_tags, ',') LIKE 'fr:%chocolat%' 
OR array_to_string(categories_tags, ',') LIKE 'en:%chocolate%'
LIMIT 10;
```
```text
┌───────────────┬──────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│     code      │         name         │                                                                      categories_tags                                                                       │
│    varchar    │       varchar        │                                                                         varchar[]                                                                          │
├───────────────┼──────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 0085239814383 │ Dark chocolate alm…  │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:chocolates, en:dark-chocolates, en:chocolates-with-almonds, en:dark-chocolates-with-almonds]    │
│ 0086158472005 │ M&M's                │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies, en:bonbons, en:chocolate-covered-nuts, en:chocolate-co…  │
│ 0086232310032 │ Gerrit J. Verburg …  │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies]                                                          │
│ 0086232310254 │ Milk Chocolate       │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies, en:chocolates, en:milk-chocolates]                       │
│ 0088468573069 │ Minz Taler Pepperm…  │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies]                                                          │
│ 0088671105071 │ Almond Bark Milk C…  │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies]                                                          │
│ 0088671110020 │ Gardners Candies, …  │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies]                                                          │
│ 0088671110051 │ Milk Chocolate Cov…  │ [en:milk-chocolate-covered-pretzel]                                                                                                                        │
│ 0089449700016 │ Milk chocolate       │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies]                                                          │
│ 0089449925945 │ Milk Chocolate       │ [en:snacks, en:sweet-snacks, en:cocoa-and-its-products, en:confectioneries, en:chocolate-candies, en:chocolates, en:milk-chocolates]                       │
├───────────────┴──────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 10 rows                                                                                                                                                                                 3 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Search in the list `allergen_tags` values containing `fr`
```sql
-- Search in the list `allergen_tags` values containing `fr`
SELECT count(code) AS nb, ANY_VALUE(code) AS code, allergens_tags
FROM products
WHERE regexp_matches(array_to_string(allergens_tags, ','), 'fr:')
GROUP BY allergens_tags
ORDER BY nb DESC
LIMIT 10
```
```text
┌───────┬───────────────┬──────────────────────────────────────────────┐
│  nb   │     code      │                allergens_tags                │
│ int64 │    varchar    │                  varchar[]                   │
├───────┼───────────────┼──────────────────────────────────────────────┤
│   343 │ 00818964      │ [en:gluten, fr:avoine]                       │
│   131 │ 3445731110364 │ [fr:non]                                     │
│   116 │ 00842990      │ [en:gluten, en:milk, en:soybeans, fr:avoine] │
│   104 │ 00964395      │ [en:gluten, en:milk, fr:avoine]              │
│   104 │ 2000000024279 │ [en:gluten, en:nuts, fr:avoine]              │
│    55 │ 2020000338741 │ [en:gluten, en:soybeans, fr:avoine]          │
│    55 │ 3700389705158 │ [fr:non-renseigne]                           │
│    50 │ 0203251017050 │ [en:gluten, en:sesame-seeds, fr:avoine]      │
│    49 │ 0065633433281 │ [en:gluten, fr:avoine, fr:avoine]            │
│    40 │ 2225653026636 │ [en:milk, fr:ferments]                       │
├───────┴───────────────┴──────────────────────────────────────────────┤
│ 10 rows                                                    3 columns │
└──────────────────────────────────────────────────────────────────────┘
```
### Products avec allergies aux arachides
```sql
-- Products avec allergies aux arachides
SELECT
    code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
allergens_tags
FROM products
WHERE list_contains(allergens_tags, 'en:peanuts') 
OR list_contains(allergens_tags, 'fr:arachides')
LIMIT 10;
```
```text
┌───────────────┬─────────────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────┐
│     code      │                              name                               │                     allergens_tags                     │
│    varchar    │                             varchar                             │                       varchar[]                        │
├───────────────┼─────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 0000281756504 │ Piasten, Chocolate Assortment                                   │ [en:eggs, en:gluten, en:milk, en:nuts, en:peanuts]     │
│ 0000433821500 │ The Best Peanut Butter Cookies                                  │ [en:eggs, en:peanuts]                                  │
│ 0000790430018 │ Welch's, pb&j trail mix, grape                                  │ [en:milk, en:peanuts, en:soybeans]                     │
│ 0000790430063 │ Welch's, pb & j trail mix, strawberry                           │ [en:milk, en:peanuts, en:soybeans]                     │
│ 0000790430070 │ Welch's, pb&j trail mix, grape                                  │ [en:milk, en:peanuts, en:soybeans]                     │
│ 0002859037565 │ Maitre truffout, assorted pralines chocolates                   │ [en:gluten, en:milk, en:nuts, en:peanuts, en:soybeans] │
│ 0002859063557 │ Maitre truffout, assorted pralines                              │ [en:gluten, en:milk, en:nuts, en:peanuts, en:soybeans] │
│ 0008346048953 │ Peanut Butter                                                   │ [en:milk, en:peanuts, en:soybeans]                     │
│ 0008346640027 │ Dark chocolate sea salt meal replacement bars                   │ [en:gluten, en:milk, en:nuts, en:peanuts, en:soybeans] │
│ 0008346800025 │ Peanut butter chocolate flavored advanced nutrition snack bites │ [en:milk, en:peanuts, en:soybeans]                     │
├───────────────┴─────────────────────────────────────────────────────────────────┴────────────────────────────────────────────────────────┤
│ 10 rows                                                                                                                        3 columns │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Number of products per NOVA group
```sql
-- Number of products per NOVA group
SELECT nova_group, count(*) AS count
FROM products
WHERE nova_group IS NOT NULL
GROUP BY nova_group
ORDER BY nova_group;
```
```text
┌────────────┬────────┐
│ nova_group │ count  │
│   int32    │ int64  │
├────────────┼────────┤
│          1 │ 108854 │
│          2 │  60427 │
│          3 │ 180500 │
│          4 │ 592498 │
└────────────┴────────┘
```
### Average Nutri-Score by brand with more than 100 products
```sql
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
```
```text
┌────────────────────────────┬─────────────────────┬──────────┐
│           brand            │      avg_score      │ products │
│          varchar           │       double        │  int64   │
├────────────────────────────┼─────────────────────┼──────────┤
│ muller-s-muhle             │  -8.248175182481752 │      179 │
│ alliance-bio               │              -7.425 │      116 │
│ sabarot                    │ -6.6369426751592355 │      288 │
│ vivien-paille              │  -6.504424778761062 │      163 │
│ driscoll-s                 │  -5.516129032258065 │      147 │
│ terra-e-sole               │                -5.5 │      117 │
│ grain-de-frais             │ -4.9186046511627906 │      119 │
│ les-fermiers-de-loue       │  -4.793103448275862 │      115 │
│ once-again                 │  -4.041666666666667 │      172 │
│ edora                      │                -4.0 │      105 │
│   ·                        │                  ·  │       ·  │
│   ·                        │                  ·  │       ·  │
│   ·                        │                  ·  │       ·  │
│ tiesta-tea                 │                NULL │      125 │
│ rsw-home                   │                NULL │      154 │
│ セブンイレブン             │                NULL │      115 │
│ botanical-interests        │                NULL │      693 │
│ now-essential-oils         │                NULL │      172 │
│ convar-feldkuche           │                NULL │      102 │
│ la-cave-d-augustin-florent │                NULL │      101 │
│ apta                       │                NULL │      155 │
│ franklin-baker             │                NULL │      493 │
│ messegue                   │                NULL │      119 │
├────────────────────────────┴─────────────────────┴──────────┤
│ 3120 rows (20 shown)                              3 columns │
└─────────────────────────────────────────────────────────────┘
```
### Products without palm oil and good Nutri-Score
```sql
-- Products without palm oil and good Nutri-Score
SELECT code, 
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    nutriscore_grade
FROM products 
WHERE ingredients_from_palm_oil_n = 0
AND nutriscore_grade IN ('a','b')
LIMIT 10;
```
```text
┌───────────────┬────────────────────────────────────────────┬──────────────────┐
│     code      │                    name                    │ nutriscore_grade │
│    varchar    │                  varchar                   │     varchar      │
├───────────────┼────────────────────────────────────────────┼──────────────────┤
│ 0000651003214 │ Romaine Hearts                             │ a                │
│ 0000651041001 │ Romaine lettuce                            │ a                │
│ 0000651041025 │ Green Leaf Lettuce                         │ a                │
│ 0000651213019 │ Fresh Spinach                              │ a                │
│ 0000651213026 │ Cooking Spinach                            │ a                │
│ 0000651319018 │ Quick cook sprout halves, brussels sprouts │ a                │
│ 0000651511016 │ Celery                                     │ a                │
│ 0000850600108 │ Raw Shrimp                                 │ a                │
│ 0000946909078 │ Augason Farms, Vital Wheat Gluten          │ a                │
│ 0002000000714 │ Yaourt nature brebis                       │ a                │
├───────────────┴────────────────────────────────────────────┴──────────────────┤
│ 10 rows                                                             3 columns │
└───────────────────────────────────────────────────────────────────────────────┘
```
### Products by ecoscore grade
```sql
-- Products by ecoscore grade
SELECT 
    ecoscore_grade,
    count(*) as count,
    avg(ecoscore_score) as avg_score
FROM products
WHERE ecoscore_grade IS NOT NULL
GROUP BY ecoscore_grade
ORDER BY avg_score DESC;
```
```text
┌────────────────┬─────────┬────────────────────┐
│ ecoscore_grade │  count  │     avg_score      │
│    varchar     │  int64  │       double       │
├────────────────┼─────────┼────────────────────┤
│ a-plus         │   41590 │  99.06446261120462 │
│ a              │   94699 │  79.42858953104046 │
│ b              │  161568 │  67.84212839176074 │
│ c              │  119697 │  51.63913047110621 │
│ d              │  152004 │  37.51514433830689 │
│ e              │  117800 │ 21.908870967741937 │
│ f              │   57740 │  2.854970557672324 │
│ unknown        │ 2249705 │               NULL │
│ not-applicable │   33622 │               NULL │
└────────────────┴─────────┴────────────────────┘
```
### Products with palm oil
```sql
-- Products with palm oil
SELECT 
    code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    ingredients_from_palm_oil_n
FROM products 
WHERE ingredients_from_palm_oil_n > 0;
```
```text
┌───────────────┬───────────────────────────────────────────────────────┬─────────────────────────────┐
│     code      │                         name                          │ ingredients_from_palm_oil_n │
│    varchar    │                        varchar                        │            int32            │
├───────────────┼───────────────────────────────────────────────────────┼─────────────────────────────┤
│ 0003004032145 │ Chinois Nature Décongelé                              │                           1 │
│ 00023092      │ 4 Indulgent & Chewy Maple Syrup & Pecan Giant Cookies │                           1 │
│ 00027083      │ Made Without Wheat Blueberry Muffins                  │                           1 │
│ 00027137      │ Paupiette de volaille sauce forestière brocolis purée │                           1 │
│ 00035460      │ 6 Breaded Jumbo Tiger Prawns                          │                           1 │
│ 00052283      │ Arachides enrobées chocolat au lait                   │                           1 │
│ 00087728      │ Lemon meringue fudge                                  │                           1 │
│ 00088749      │ Dolly Mixtures                                        │                           1 │
│ 00088992      │ Blackcurrant sponge roll                              │                           1 │
│ 00096225      │ Made Without Wheat New York Cheesecake                │                           1 │
│    ·          │          ·                                            │                           · │
│    ·          │          ·                                            │                           · │
│    ·          │          ·                                            │                           · │
│ 8003340095134 │ Lait assorti de Noël                                  │                           1 │
│ 8003340095172 │ Lindor Noix De Coco                                   │                           1 │
│ 8003340095233 │ Bonbons chocolat lait Lindor                          │                           1 │
│ 8003340095288 │ Cornet lindor blanc fraise                            │                           1 │
│ 8003340095301 │ Lindor Blanc Fraise                                   │                           1 │
│ 8003340095318 │ Lindor                                                │                           1 │
│ 8003340095325 │ Lindor Assortiment fondant                            │                           1 │
│ 8003340095400 │ Pushbag Œufs Moyens Lindor Lait                       │                           1 │
│ 8003340095417 │ Œufs Lindor Assorti                                   │                           1 │
│ 8003340095424 │ LINDOR NOIR                                           │                           1 │
├───────────────┴───────────────────────────────────────────────────────┴─────────────────────────────┤
│ ? rows (>9999 rows, 20 shown)                                                             3 columns │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Products with most ingredients
```sql
-- Products with most ingredients
SELECT 
    code, 
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    ingredients_n
FROM products
WHERE ingredients_n IS NOT NULL
ORDER BY ingredients_n DESC
LIMIT 10;
```
```text
┌──────────────────────┬──────────────────────────────────┬───────────────┐
│         code         │               name               │ ingredients_n │
│       varchar        │             varchar              │     int32     │
├──────────────────────┼──────────────────────────────────┼───────────────┤
│ 9340784007491        │ Lo bros kombucha                 │           751 │
│ 80247937043707854551 │ qauwi                            │           684 │
│ 5400265040899        │ Chocolats caramel                │           414 │
│ 0732346467239        │ hot sauce                        │           410 │
│ 5601066602013        │ + Linha                          │           386 │
│ 5900915026759        │ Chilli flavoured dark chocholate │           373 │
│ 0072470003225        │ Krispy Kreme Donuts              │           373 │
│ 9002859091872        │ Marshmallow Konfekt              │           367 │
│ 8720812770107        │ Sun Kissed Tomato Flavour Ramen  │           360 │
│ 6935133800682        │ Mondkuchen Mixer Obst und Tee    │           358 │
├──────────────────────┴──────────────────────────────────┴───────────────┤
│ 10 rows                                                       3 columns │
└─────────────────────────────────────────────────────────────────────────┘
```
### Most common vitamins
```sql
-- Most common vitamins
SELECT 
    unnest AS vitamin,
    count(*) AS count
FROM products,
    unnest(vitamins_tags) AS unnest
GROUP BY vitamin
ORDER BY count DESC;
```
```text
┌──────────────────────────────────────┬───────┐
│               vitamin                │ count │
│               varchar                │ int64 │
├──────────────────────────────────────┼───────┤
│ en:niacin                            │ 69821 │
│ en:folic-acid                        │ 64349 │
│ en:riboflavin                        │ 63139 │
│ en:thiamin-mononitrate               │ 52584 │
│ en:thiamin                           │ 32385 │
│ en:l-ascorbic-acid                   │ 28630 │
│ en:vitamin-c                         │ 21479 │
│ en:retinyl-palmitate                 │ 16669 │
│ en:vitamin-b6                        │ 16387 │
│ en:vitamin-b12                       │ 16227 │
│       ·                              │     · │
│       ·                              │     · │
│       ·                              │     · │
│ en:beta-carotene-dye                 │    29 │
│ en:d-alpha-tocopheryl-acid-succinate │    12 │
│ en:dexpanthenol                      │    11 │
│ en:potassium-l-ascorbate             │     8 │
│ en:hydroxocobalamin                  │     6 │
│ en:l-ascorbyl-6-palmitate            │     5 │
│ en:pyridoxine-5-phosphate            │     3 │
│ en:vitamin-k3                        │     2 │
│ da:vitamin-a-og-d                    │     2 │
│ en:pyridoxine-dipalmitate            │     1 │
├──────────────────────────────────────┴───────┤
│ 50 rows (20 shown)                 2 columns │
└──────────────────────────────────────────────┘
```
### Products by serving size
```sql
-- Products by serving size
SELECT serving_size, count(*) AS count
FROM products
WHERE serving_size IS NOT NULL
GROUP BY serving_size
ORDER BY count DESC
LIMIT 10;
```
```text
┌───────────────────┬───────┐
│   serving_size    │ count │
│      varchar      │ int64 │
├───────────────────┼───────┤
│ 100.0g            │ 49266 │
│ 100g              │ 24521 │
│ 100 g             │ 20767 │
│ 1 ONZ (28 g)      │ 19482 │
│ 30.0g             │ 11742 │
│ 30 g              │ 10802 │
│ 1 portion (100 g) │ 10542 │
│ 8 OZA (240 ml)    │  8281 │
│ 50.0g             │  7533 │
│ 30g               │  6043 │
├───────────────────┴───────┤
│ 10 rows         2 columns │
└───────────────────────────┘
```
### Most used labels
```sql
-- Most used labels
SELECT 
    unnest AS label,
    count(*) AS count
FROM products,
    unnest(labels_tags) as unnest
GROUP BY label
ORDER BY count DESC
LIMIT 10;
```
```text
┌──────────────────────────────┬────────┐
│            label             │ count  │
│           varchar            │ int64  │
├──────────────────────────────┼────────┤
│ en:organic                   │ 254493 │
│ en:no-gluten                 │ 191498 │
│ en:eu-organic                │ 169186 │
│ en:green-dot                 │ 136851 │
│ en:vegetarian                │ 127835 │
│ en:vegan                     │ 112530 │
│ en:nutriscore                │  89326 │
│ en:no-gmos                   │  78665 │
│ fr:ab-agriculture-biologique │  72633 │
│ en:no-preservatives          │  70093 │
├──────────────────────────────┴────────┤
│ 10 rows                     2 columns │
└───────────────────────────────────────┘
```
### Organic products
```sql
-- Organic products
SELECT code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name
FROM products
WHERE list_contains(labels_tags, 'en:organic')
LIMIT 10;
```
```text
┌───────────────┬────────────────────────────────────────────────────────┐
│     code      │                          name                          │
│    varchar    │                        varchar                         │
├───────────────┼────────────────────────────────────────────────────────┤
│ 0000557910210 │ Flocon d'avoine - complète                             │
│ 0000682009841 │ Pain de campagne bio nature                            │
│ 0000764114944 │ Ryan's, Organic Juice, Apple                           │
│ 0000901000017 │ All Natural Baked Not Fried Yellow Corn Tortilla Chips │
│ 0000901005005 │ Guiltless Gourmet, Organic Unsweetened Coconut Water   │
│ 0001390000007 │ Espirulina En Comprimidos Ecologica Salud Viva         │
│ 0002000000448 │ Jabra Jabra JX-10 Xtra Earhook Bulk                    │
│ 0002000000592 │ Ravioli                                                │
│ 0002000000608 │ Le bio                                                 │
│ 0002000000714 │ Yaourt nature brebis                                   │
├───────────────┴────────────────────────────────────────────────────────┤
│ 10 rows                                                      2 columns │
└────────────────────────────────────────────────────────────────────────┘
```
### Products by store
```sql
-- Products by store
SELECT 
    unnest as store_name,
    count(*) as count
FROM products,
    unnest(stores_tags) as unnest
GROUP BY store_name
ORDER BY count DESC
LIMIT 5;
```
```text
┌──────────────┬───────┐
│  store_name  │ count │
│   varchar    │ int64 │
├──────────────┼───────┤
│ carrefour    │ 29799 │
│ magasins-u   │ 23588 │
│ lidl         │ 21200 │
│ carrefour-fr │ 20158 │
│ auchan       │ 19192 │
└──────────────┴───────┘
```
### Complete vs incomplete products
```sql
-- Complete vs incomplete products
SELECT 
    complete,
    count(*) as count,
    avg(completeness) as avg_completeness
FROM products
GROUP BY complete;
```
```text
┌──────────┬─────────┬─────────────────────┐
│ complete │  count  │  avg_completeness   │
│  int32   │  int64  │       double        │
├──────────┼─────────┼─────────────────────┤
│        0 │ 3586082 │ 0.42028756940551326 │
│        1 │   15573 │  1.0050086700479197 │
└──────────┴─────────┴─────────────────────┘
```
### Products by food group
```sql
-- Products by food group
SELECT 
    unnest AS food_group,
    count(*) AS count
FROM products,
    unnest(food_groups_tags) AS unnest
GROUP BY food_group
ORDER BY count DESC;
```
```text
┌─────────────────────────────────────┬────────┐
│             food_group              │ count  │
│               varchar               │ int64  │
├─────────────────────────────────────┼────────┤
│ en:sugary-snacks                    │ 257611 │
│ en:fish-meat-eggs                   │ 165182 │
│ en:cereals-and-potatoes             │ 160465 │
│ en:milk-and-dairy-products          │ 153141 │
│ en:sweets                           │ 117731 │
│ en:fats-and-sauces                  │ 114765 │
│ en:beverages                        │ 113193 │
│ en:biscuits-and-cakes               │ 100602 │
│ en:fruits-and-vegetables            │  93543 │
│ en:composite-foods                  │  85396 │
│       ·                             │     ·  │
│       ·                             │     ·  │
│       ·                             │     ·  │
│ en:sandwiches                       │   7627 │
│ en:fruit-juices                     │   6980 │
│ en:eggs                             │   6321 │
│ en:waters-and-flavored-waters       │   5597 │
│ en:potatoes                         │   5533 │
│ en:soups                            │   4687 │
│ en:teas-and-herbal-teas-and-coffees │   3571 │
│ en:lean-fish                        │   1819 │
│ en:offals                           │   1759 │
│ en:fruit-nectars                    │   1675 │
├─────────────────────────────────────┴────────┤
│ 52 rows (20 shown)                 2 columns │
└──────────────────────────────────────────────┘
```
### Recently added products
```sql
-- Recently added products
SELECT code,
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    to_timestamp(created_t) AS added_date
FROM products
WHERE created_t IS NOT NULL
ORDER BY created_t DESC
LIMIT 10;
```
```text
┌───────────────┬──────────────────────────────────┬──────────────────────────┐
│     code      │               name               │        added_date        │
│    varchar    │             varchar              │ timestamp with time zone │
├───────────────┼──────────────────────────────────┼──────────────────────────┤
│ 4532789991188 │ 玄米100%お米ニョッキ にょっこ    │ 2025-01-22 05:33:39-05   │
│ 5607047008966 │ amêndoas chocolate negro e leite │ 2025-01-22 05:33:27-05   │
│ 8906009071138 │ Unibic butter cookies            │ 2025-01-22 05:31:27-05   │
│ 4909368396113 │ pl barni blag                    │ 2025-01-22 05:30:57-05   │
│ 5941865007283 │ Castraveti Rondele In Otet       │ 2025-01-22 05:30:17-05   │
│ 8008703162256 │ Zuppa con Pomodoro e Farro       │ 2025-01-22 05:29:43-05   │
│ 5607047008935 │ Amêndoas chocolate negro         │ 2025-01-22 05:29:35-05   │
│ 8906009079356 │ unibic choco nut cookies         │ 2025-01-22 05:26:26-05   │
│ 0035046135843 │ Organic Super Greens             │ 2025-01-22 05:24:01-05   │
│ 8908003115375 │ Rusk crispy and fresh            │ 2025-01-22 05:23:57-05   │
├───────────────┴──────────────────────────────────┴──────────────────────────┤
│ 10 rows                                                           3 columns │
└─────────────────────────────────────────────────────────────────────────────┘
```
### Top 10 best contributors in Open Food Facts
```sql
-- Top 10 best contributors in Open Food Facts
SELECT creator, count(*) AS count
FROM products
GROUP BY creator
ORDER BY count DESC
LIMIT 10;
```
```text
┌────────────────────────────┬─────────┐
│          creator           │  count  │
│          varchar           │  int64  │
├────────────────────────────┼─────────┤
│ kiliweb                    │ 1900284 │
│ foodvisor                  │  212103 │
│ openfoodfacts-contributors │  210729 │
│ usda-ndb-import            │  169562 │
│ macrofactor                │  142320 │
│ org-database-usda          │  134463 │
│ prepperapp                 │  124195 │
│ foodless                   │  101234 │
│ smoothie-app               │   85346 │
│ inf                        │   38483 │
├────────────────────────────┴─────────┤
│ 10 rows                    2 columns │
└──────────────────────────────────────┘
```
### Number of added products per year
```sql
-- Number of added products per year
SELECT
    entry_dates_tags[3] AS year, count(*) AS count
FROM products
GROUP BY year
ORDER BY year DESC;
```
```text
┌─────────┬────────┐
│  year   │ count  │
│ varchar │ int64  │
├─────────┼────────┤
│ 2025    │  42783 │
│ 2024    │ 559704 │
│ 2023    │ 358791 │
│ 2022    │ 596429 │
│ 2021    │ 511976 │
│ 2020    │ 465690 │
│ 2019    │ 363708 │
│ 2018    │ 317786 │
│ 2017    │ 279691 │
│ 2016    │  44567 │
│ 2015    │  33906 │
│ 2014    │  12851 │
│ 2013    │   9554 │
│ 2012    │   4215 │
│ 1970    │      3 │
│ NULL    │      1 │
├─────────┴────────┤
│     16 rows      │
└──────────────────┘
```
### Products containing 'café', 'cafe', or 'coffee' in their generic name
```sql
-- Products containing 'café', 'cafe', or 'coffee' in their generic name
SELECT product_name, generic_name
FROM products
WHERE lower(generic_name::VARCHAR) LIKE '%café%'
   OR lower(generic_name::VARCHAR) LIKE '%cafe%'
   OR lower(generic_name::VARCHAR) LIKE '%coffee%';
```
```text
┌──────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│     product_name     │                                                                                generic_name                                                                                │
│ struct(lang varcha…  │                                                                   struct(lang varchar, "text" varchar)[]                                                                   │
├──────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [{'lang': main, 't…  │ [{'lang': main, 'text': chilled coffee drink caramel flavored.}, {'lang': en, 'text': chilled coffee drink caramel flavored.}]                                             │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': energy coffee beverage}, {'lang': en, 'text': energy coffee beverage}]                                                                             │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Premium Coffee Beverage}, {'lang': en, 'text': Premium Coffee Beverage}]                                                                           │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Sparkling green coffee energy beverage}, {'lang': en, 'text': Sparkling green coffee energy beverage}]                                             │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': chilled coffee drink.}, {'lang': en, 'text': chilled coffee drink.}]                                                                               │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Bière britannique au café - Flat White Porter}, {'lang': fr, 'text': Bière britannique au café - Flat White Porter}]                               │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Ground coffee}, {'lang': en, 'text': Ground coffee}]                                                                                               │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': ground coffee}, {'lang': en, 'text': ground coffee}]                                                                                               │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Instant Coffee}, {'lang': fr, 'text': Instant Coffee}]                                                                                             │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Coffee cookie crumble ice cream}, {'lang': en, 'text': Coffee cookie crumble ice cream}]                                                           │
│          ·           │                                                        ·                                                                                                                   │
│          ·           │                                                        ·                                                                                                                   │
│          ·           │                                                        ·                                                                                                                   │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': 18 capsules de café torréfié et moulu pour système NESPRESSO.}, {'lang': fr, 'text': 18 capsules de café torréfié et moulu pour système NESPRESS…  │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': 10 capsules de café torréfié et moulu pour système NESPRESSO.}, {'lang': fr, 'text': 10 capsules de café torréfié et moulu pour système NESPRESS…  │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Preparado à Base de Leite em Pó, com Açúcar e Café Solúvel}, {'lang': pt, 'text': Preparado à Base de Leite em Pó, com Açúcar e Café Solúvel}]     │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': 10 capsules de café décaféiné torréfié et moulu pour système Nespresso.}, {'lang': fr, 'text': 10 capsules de café décaféiné torréfié et moulu p…  │
│ [{'lang': th, 'tex…  │ [{'lang': th, 'text': INSTANT COFFEE MIXED POWDER}]                                                                                                                        │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': 20 capsules de café torréfié et moulu pour système Nespresso}, {'lang': fr, 'text': 20 capsules de café torréfié et moulu pour système Nespresso}] │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': 20 capsules de café torréfié et moulu pour système Nespresso}, {'lang': fr, 'text': 20 capsules de café torréfié et moulu pour système Nespresso}] │
│ [{'lang': fr, 'tex…  │ [{'lang': fr, 'text': Préparation instantanée pour boisson au café}]                                                                                                       │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': Capsules de café moulu.}, {'lang': it, 'text': Capsule di caffè macinato.}, {'lang': ro, 'text': Capsule cu cafea măcinată.}, {'lang': fr, 'text…  │
│ [{'lang': main, 't…  │ [{'lang': main, 'text': helado de crema de leche con café.}, {'lang': es, 'text': helado de crema de leche con café.}]                                                     │
├──────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2282 rows (20 shown)                                                                                                                                                                    2 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Find products with all ingredients marked as vegan (no non-vegan or maybe-vegan ingredients)
```sql
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
```
```text
┌────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                 brands                 │                                                ingredients_list                                                │
│                varchar                 │                                                    varchar                                                     │
├────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Lagg's                                 │ Chamomile flowers"]                                                                                            │
│ Lagg's                                 │ Peppermint"]                                                                                                   │
│ Lagg's                                 │ Hibiscus flowers"]                                                                                             │
│ Lagg's                                 │ Green tea"]                                                                                                    │
│ Lagg's                                 │ Andropogon citratus", "uva ursi", "hibiscus flowers", "cinnamon", "equisetum arvense", "flourensia cernua"]    │
│ Lagg's                                 │ Shave grass", "corn silk", "uva ursi", "juliana adstringen", "boldo", "hibiscus flowers", "orange blossom"]    │
│ Today's Temptations                    │ Rye flour", "water", "wheat", "flour", "malt", "molasses", "sugar", "onion", "yeast", "caraway seeds", "salt"] │
│ Sharwood's                             │ Black chickpea gram flour", "salt", "raising agent", "calcium oxide", "rice flour", "sunflower oil"]           │
│ Tetley,  American Power Products  Inc. │ tea", "passion"]                                                                                               │
│ Chio                                   │ Wheat flour", "salt", "palm oil", "acidity regulator", "malted wheat flour", "emulsifier"]                     │
├────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 10 rows                                                                                                                                       2 columns │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
``````sql
SELECT last_editor, COUNT(*) as frequency
FROM products 
WHERE last_editor IS NOT NULL
GROUP BY last_editor
ORDER BY frequency DESC
LIMIT 10;
```
```text
┌───────────────────┬───────────┐
│    last_editor    │ frequency │
│      varchar      │   int64   │
├───────────────────┼───────────┤
│ kiliweb           │    541094 │
│ roboto-app        │    498702 │
│ org-database-usda │    214760 │
│ macrofactor       │    182845 │
│ foodvisor         │    161875 │
│ teolemon          │    153758 │
│ prepperapp        │    112412 │
│ packbot           │    108171 │
│ telperion87       │     97837 │
│ foodless          │     94433 │
├───────────────────┴───────────┤
│ 10 rows             2 columns │
└───────────────────────────────┘
``````sql
SELECT 
    COUNT(*) as total_products,
    COUNT(DISTINCT last_editor) as unique_editors,
    COUNT(CASE WHEN last_editor IS NOT NULL THEN 1 END) as products_with_editor
FROM products;
```
```text
┌────────────────┬────────────────┬──────────────────────┐
│ total_products │ unique_editors │ products_with_editor │
│     int64      │     int64      │        int64         │
├────────────────┼────────────────┼──────────────────────┤
│        3601655 │          40701 │              3486909 │
└────────────────┴────────────────┴──────────────────────┘
```
### Find popular products (>100 scans) with good nutrition score (A or B)
```sql
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
```
```text
┌───────────────┬──────────────────────────────┬─────────┬──────────────────┐
│     code      │             name             │ scans_n │ nutriscore_grade │
│    varchar    │           varchar            │  int32  │     varchar      │
├───────────────┼──────────────────────────────┼─────────┼──────────────────┤
│ 3274080005003 │ Eau de source                │    2536 │ a                │
│ 3268840001008 │ Eau de source                │     911 │ a                │
│ 5411188112709 │ Geröstete Mandel Ohne Zucker │     801 │ b                │
│ 20724696      │ Almonds                      │     759 │ a                │
│ 7300400481588 │ FIBRES                       │     754 │ a                │
│ 8002270014901 │ S. Pellegrino Water          │     751 │ a                │
│ 3168930163480 │ Alvalle Gazpacho l'original  │     740 │ a                │
│ 20267605      │ Cashewkerne Naturbelassen    │     672 │ b                │
│ 3057640257773 │ Volvic                       │     667 │ a                │
│ 3068320123264 │ La salvetat                  │     667 │ a                │
├───────────────┴──────────────────────────────┴─────────┴──────────────────┤
│ 10 rows                                                         4 columns │
└───────────────────────────────────────────────────────────────────────────┘
```
### Average number of additives by brand (for brands with >50 products)
```sql
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
```
```text
┌──────────────────────┬────────────────────┬────────────────┐
│        brand         │   avg_additives    │ total_products │
│       varchar        │       double       │     int64      │
├──────────────────────┼────────────────────┼────────────────┤
│ mrs-freshley-s       │ 14.598130841121495 │            107 │
│ entenmann-s          │  14.18867924528302 │            106 │
│ tastykake            │ 12.967948717948717 │            156 │
│ tasty-baking-company │  12.89344262295082 │            122 │
│ hostess              │  12.88950276243094 │            181 │
│ flowers-foods-inc    │ 12.047297297297296 │            148 │
│ lofthouse-cookies    │ 11.709090909090909 │             55 │
│ bakehuset-direkte    │ 11.402985074626866 │             67 │
│ lofthouse-foods      │  11.18840579710145 │             69 │
│ totino-s             │  11.02020202020202 │             99 │
├──────────────────────┴────────────────────┴────────────────┤
│ 10 rows                                          3 columns │
└────────────────────────────────────────────────────────────┘
```
### Product creation trends by month in 2024
```sql
-- Product creation trends by month in 2024
SELECT 
    DATE_TRUNC('month', to_timestamp(created_t)) AS month,
    COUNT(*) as new_products
FROM products
WHERE created_t >= 1704067200  -- Jan 1, 2024
GROUP BY month
ORDER BY month;
```
```text
┌──────────────────────────┬──────────────┐
│          month           │ new_products │
│ timestamp with time zone │    int64     │
├──────────────────────────┼──────────────┤
│ 2023-12-01 00:00:00-05   │           33 │
│ 2024-01-01 00:00:00-05   │        33422 │
│ 2024-02-01 00:00:00-05   │        29689 │
│ 2024-03-01 00:00:00-05   │        31773 │
│ 2024-04-01 00:00:00-04   │        38917 │
│ 2024-05-01 00:00:00-04   │        42571 │
│ 2024-06-01 00:00:00-04   │        81527 │
│ 2024-07-01 00:00:00-04   │        49811 │
│ 2024-08-01 00:00:00-04   │        47053 │
│ 2024-09-01 00:00:00-04   │        48895 │
│ 2024-10-01 00:00:00-04   │        54394 │
│ 2024-11-01 00:00:00-04   │        47107 │
│ 2024-12-01 00:00:00-05   │        54667 │
│ 2025-01-01 00:00:00-05   │        42631 │
├──────────────────────────┴──────────────┤
│ 14 rows                       2 columns │
└─────────────────────────────────────────┘
```
### Products with complete information and images
```sql
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
```
```text
┌───────────────┬──────────────────────────────────────────┬──────────────┐
│     code      │                   name                   │ completeness │
│    varchar    │                 varchar                  │    float     │
├───────────────┼──────────────────────────────────────────┼──────────────┤
│ 4021234402336 │ Barnhouse Cornflakes, 375 GR Packung     │          1.1 │
│ 4036300005311 │ Müritzer                                 │          1.1 │
│ 4044889000610 │ Edel Bitter 70% Cacao                    │          1.1 │
│ 4044889002119 │ Edel Bitter Cranberry 70% Ecuador-Caribe │          1.1 │
│ 4044889002904 │ Feine Bitter 99% Cacao Panama            │          1.1 │
│ 4045317058593 │ Frische Milch 3,8% Fett                  │          1.1 │
│ 4045357008190 │ Sahnig mit Allgäuer Milch laktosfrei     │          1.1 │
│ 4046700004265 │ BIO Sahne                                │          1.1 │
│ 4046700500972 │ Bio Frische fettarme Milch 🍀            │          1.1 │
│ 4062300163904 │ Petits Macaroni, Tomates, Colin d'Alaska │          1.1 │
├───────────────┴──────────────────────────────────────────┴──────────────┤
│ 10 rows                                                       3 columns │
└─────────────────────────────────────────────────────────────────────────┘
```
### Correlation between Nutri-Score and Eco-Score
```sql
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
```
```text
┌──────────────────┬────────────────┬─────────┐
│ nutriscore_grade │ ecoscore_grade │  count  │
│     varchar      │    varchar     │  int64  │
├──────────────────┼────────────────┼─────────┤
│ a                │ a              │   16965 │
│ a                │ a-plus         │    9206 │
│ a                │ b              │   15060 │
│ a                │ c              │    6653 │
│ a                │ d              │    8405 │
│ a                │ e              │   12564 │
│ a                │ f              │    3809 │
│ a                │ not-applicable │    6340 │
│ a                │ unknown        │   61929 │
│ b                │ a              │   11220 │
│ ·                │ ·              │     ·   │
│ ·                │ ·              │     ·   │
│ ·                │ ·              │     ·   │
│ not-applicable   │ unknown        │   19991 │
│ unknown          │ a              │   22448 │
│ unknown          │ a-plus         │    9712 │
│ unknown          │ b              │   32950 │
│ unknown          │ c              │   19157 │
│ unknown          │ d              │   23063 │
│ unknown          │ e              │   20748 │
│ unknown          │ f              │   13974 │
│ unknown          │ not-applicable │    7886 │
│ unknown          │ unknown        │ 1797394 │
├──────────────────┴────────────────┴─────────┤
│ 63 rows (20 shown)                3 columns │
└─────────────────────────────────────────────┘
```
### Average number of ingredients by food group
```sql
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
```
```text
┌───────────────────────────┬────────────────────┬─────────────────┬─────────────────┐
│        food_group         │  avg_ingredients   │ min_ingredients │ max_ingredients │
│          varchar          │       double       │      int32      │      int32      │
├───────────────────────────┼────────────────────┼─────────────────┼─────────────────┤
│ en:sandwiches             │ 49.196983758700696 │               1 │             327 │
│ en:pizza-pies-and-quiches │  41.50930362116991 │               0 │             252 │
│ en:composite-foods        │ 31.888402544651964 │               0 │             327 │
│ en:one-dish-meals         │ 27.927298680842686 │               0 │             327 │
│ en:biscuits-and-cakes     │ 26.591992815984433 │               0 │             386 │
│ en:ice-cream              │ 25.647228062410093 │               0 │             233 │
│ en:pastries               │  24.36563209689629 │               1 │             341 │
│ en:sugary-snacks          │  19.69416375852909 │               0 │             386 │
│ en:bread                  │ 19.520799871506586 │               0 │             165 │
│ en:breakfast-cereals      │  17.98976313233206 │               0 │             266 │
├───────────────────────────┴────────────────────┴─────────────────┴─────────────────┤
│ 10 rows                                                                  4 columns │
└────────────────────────────────────────────────────────────────────────────────────┘
```
### Categories with the most products without additives
```sql
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
```
```text
┌──────────────────────────────────────┬────────┐
│               category               │ count  │
│               varchar                │ int64  │
├──────────────────────────────────────┼────────┤
│ en:plant-based-foods-and-beverages   │ 167357 │
│ en:plant-based-foods                 │ 146812 │
│ en:cereals-and-potatoes              │  52271 │
│ en:beverages                         │  49383 │
│ en:snacks                            │  48712 │
│ en:dairies                           │  45488 │
│ en:fruits-and-vegetables-based-foods │  43761 │
│ en:cereals-and-their-products        │  38927 │
│ en:fermented-foods                   │  34061 │
│ en:fermented-milk-products           │  33123 │
├──────────────────────────────────────┴────────┤
│ 10 rows                             2 columns │
└───────────────────────────────────────────────┘
```
### Most common conservation conditions
```sql
-- Most common conservation conditions
SELECT 
    unnest AS condition,
    COUNT(*) as count
FROM products,
    unnest(conservation_conditions_tags) AS unnest
GROUP BY condition
ORDER BY count DESC
LIMIT 10;
```

### Products with multiple allergens
```sql
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
```
```text
┌───────────────┬──────────────────────┬────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│     code      │         name         │ allergen_count │                                                              allergens_tags                                                               │
│    varchar    │       varchar        │     int64      │                                                                 varchar[]                                                                 │
├───────────────┼──────────────────────┼────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 8711812407285 │ 20 Kruiden oplosthee │             45 │ [en:gluten, nl:braamblad, nl:druivensuiker, nl:duizendbladbloesem, nl:eucalyptus, nl:goudbloembloesem, nl:heemst, nl:kaasjeskruidbloese…  │
│ 2317689111773 │ Pastrami Beef, Roa…  │             37 │ [en:eggs, de:くん-液, de:さけ大豆-鶏肉-豚肉-りんご, de:アルギン酸エステル, de:カゼインna, de:カラメル-色素, de:クチナシ色素, de:ゼラ-チ…  │
│ 3368955876369 │ Poêlée de St Jacqu…  │             33 │ [en:crustaceans, en:fish, en:milk, en:molluscs, fr:4, en:molluscs, fr:jacques, fr:saint, fr:ail-en-puree, fr:amidon-transforme-de-riz-o…  │
│ 4902105901120 │ 日清ラ王　たれたっ…  │             28 │ [en:chicken, en:eggs, en:milk, en:sesame-seeds, en:soybeans, ja:かんすい, ja:しょうゆ, ja:たん白加水分解物, ja:ねりごま-加工でん粉, ja:…  │
│ 8410416005063 │ Paella marinera      │             24 │ [en:crustaceans, en:fish, en:molluscs, es:aroma, es:calmars, es:crevettes, es:crustace, es:fruits-de-mer, es:marisco, es:mollusques, es…  │
│ 8710482532174 │ Oerknäck waldkorn    │             23 │ [en:gluten, en:sesame-seeds, en:soybeans, nl:gerstegrutten, en:gluten, en:gluten, nl:havermeel, nl:havervlokken, nl:roggebloem, nl:rogg…  │
│ 2134025004496 │ Bageta šunková       │             22 │ [en:gluten, en:milk, cs:kvásek, cs:majonéza, cs:mléčné, en:gluten, cs:pšeničná-sladová-mouka, cs:pšeničný-kvas, en:gluten, en:milk, en:…  │
│ 3270160890507 │ Couronne de Noël A…  │             21 │ [en:crustaceans, en:eggs, en:fish, en:gluten, en:milk, en:molluscs, en:mustard, en:nuts, en:sesame-seeds, en:milk, fr:chevre, fr:farine…  │
│ 2000000132402 │ Cubic 19 Grains Sa…  │             19 │ [en:gluten, en:milk, en:peanuts, en:sesame-seeds, en:soybeans, th:ข้าวโพด, th:ข้าวโอ๊ต, th:งาขาว, th:งาดำ, th:งานม่อน, th:ถั่วขาว, th:ถั่วดำ-ถั่วเขี…  │
│ 2100100082062 │ Крекер ржаной        │             19 │ [en:gluten, en:milk, en:peanuts, en:sesame-seeds, ru:концентрат-солодовый-ржаной, en:gluten, en:gluten, ru:мука-ржаная-обдирная, ru:про…  │
├───────────────┴──────────────────────┴────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 10 rows                                                                                                                                                                                 4 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Brands distribution by country
```sql
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
```
```text
┌───────────────────┬───────────────┬────────────────┐
│      country      │ unique_brands │ total_products │
│      varchar      │     int64     │     int64      │
├───────────────────┼───────────────┼────────────────┤
│ en:france         │         68548 │         668870 │
│ en:united-states  │         54879 │         408434 │
│ en:germany        │         47079 │         286493 │
│ en:spain          │         22865 │         191249 │
│ en:ireland        │         16032 │          51203 │
│ en:united-kingdom │         14126 │          93316 │
│ en:italy          │         13186 │         173862 │
│ en:switzerland    │          9551 │          74438 │
│ en:canada         │          8995 │          43146 │
│ en:japan          │          7931 │          16411 │
├───────────────────┴───────────────┴────────────────┤
│ 10 rows                                  3 columns │
└────────────────────────────────────────────────────┘
```
### Filter products by category (using list_contains)
```sql
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
```
```text
┌───────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  nb   │                                                                 allergens_tags                                                                  │
│ int64 │                                                                    varchar[]                                                                    │
├───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│   343 │ [en:gluten, fr:avoine]                                                                                                                          │
│   131 │ [fr:non]                                                                                                                                        │
│   116 │ [en:gluten, en:milk, en:soybeans, fr:avoine]                                                                                                    │
│   104 │ [en:gluten, en:nuts, fr:avoine]                                                                                                                 │
│   104 │ [en:gluten, en:milk, fr:avoine]                                                                                                                 │
│    55 │ [fr:non-renseigne]                                                                                                                              │
│    55 │ [en:gluten, en:soybeans, fr:avoine]                                                                                                             │
│    50 │ [en:gluten, en:sesame-seeds, fr:avoine]                                                                                                         │
│    49 │ [en:gluten, fr:avoine, fr:avoine]                                                                                                               │
│    40 │ [en:milk, fr:ferments]                                                                                                                          │
│     · │           ·                                                                                                                                     │
│     · │           ·                                                                                                                                     │
│     · │           ·                                                                                                                                     │
│     1 │ [en:milk, fr:lactoserique]                                                                                                                      │
│     1 │ [en:eggs, en:gluten, en:milk, en:nuts, en:soybeans, fr:cajou, fr:fruits-a-coques-moulus, en:milk, fr:cajou, fr:fruits-a-coques-moulus, en:milk] │
│     1 │ [en:eggs, en:gluten, en:milk, en:nuts, en:soybeans, fr:cajou, fr:fruit-a-coque-moulus, en:milk]                                                 │
│     1 │ [en:milk, fr:laitlait-et-produit-a-base-de-lait-y-compris-le-lactose]                                                                           │
│     1 │ [en:eggs, en:gluten, en:milk, en:sesame-seeds, en:soybeans, en:sulphur-dioxide-and-sulphites, fr:avoine]                                        │
│     1 │ [en:gluten, en:milk, en:soybeans, fr:citron]                                                                                                    │
│     1 │ [en:milk, fr:noisettes-20]                                                                                                                      │
│     1 │ [en:gluten, en:milk, fr:specialite-fromagere]                                                                                                   │
│     1 │ [en:eggs, en:gluten, en:milk, en:nuts, fr:proteine-de-lait-de-vache]                                                                            │
│     1 │ [en:gluten, en:milk, en:soybeans, fr:一部に-乳成分, fr:大豆を含む, fr:小麦]                                                                     │
├───────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2294 rows (20 shown)                                                                                                                          2 columns │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Products by NOVA group
```sql
-- Products by NOVA group
SELECT nova_group, count(*) AS count
FROM products
WHERE nova_group IS NOT NULL
GROUP BY nova_group
ORDER BY nova_group;
```
```text
┌────────────┬────────┐
│ nova_group │ count  │
│   int32    │ int64  │
├────────────┼────────┤
│          1 │ 108854 │
│          2 │  60427 │
│          3 │ 180500 │
│          4 │ 592498 │
└────────────┴────────┘
```
### Products with good Nutri-Score and no palm oil
```sql
-- Products with good Nutri-Score and no palm oil
SELECT code, 
    unnest(list_filter(product_name, x -> x.lang == 'main'))['text'] AS name,
    nutriscore_grade
FROM products 
WHERE ingredients_from_palm_oil_n = 0
AND nutriscore_grade IN ('a','b')
LIMIT 10;
```
```text
┌───────────────┬────────────────────────────────────────────┬──────────────────┐
│     code      │                    name                    │ nutriscore_grade │
│    varchar    │                  varchar                   │     varchar      │
├───────────────┼────────────────────────────────────────────┼──────────────────┤
│ 0000651003214 │ Romaine Hearts                             │ a                │
│ 0000651041001 │ Romaine lettuce                            │ a                │
│ 0000651041025 │ Green Leaf Lettuce                         │ a                │
│ 0000651213019 │ Fresh Spinach                              │ a                │
│ 0000651213026 │ Cooking Spinach                            │ a                │
│ 0000651319018 │ Quick cook sprout halves, brussels sprouts │ a                │
│ 0000651511016 │ Celery                                     │ a                │
│ 0000850600108 │ Raw Shrimp                                 │ a                │
│ 0000946909078 │ Augason Farms, Vital Wheat Gluten          │ a                │
│ 0002000000714 │ Yaourt nature brebis                       │ a                │
├───────────────┴────────────────────────────────────────────┴──────────────────┤
│ 10 rows                                                             3 columns │
└───────────────────────────────────────────────────────────────────────────────┘
```
### Most common vitamins
```sql
-- Most common vitamins
SELECT 
    unnest AS vitamin,
    count(*) AS count
FROM products,
    unnest(vitamins_tags) AS unnest
GROUP BY vitamin
ORDER BY count DESC;
```
```text
┌──────────────────────────────────────┬───────┐
│               vitamin                │ count │
│               varchar                │ int64 │
├──────────────────────────────────────┼───────┤
│ en:niacin                            │ 69821 │
│ en:folic-acid                        │ 64349 │
│ en:riboflavin                        │ 63139 │
│ en:thiamin-mononitrate               │ 52584 │
│ en:thiamin                           │ 32385 │
│ en:l-ascorbic-acid                   │ 28630 │
│ en:vitamin-c                         │ 21479 │
│ en:retinyl-palmitate                 │ 16669 │
│ en:vitamin-b6                        │ 16387 │
│ en:vitamin-b12                       │ 16227 │
│       ·                              │     · │
│       ·                              │     · │
│       ·                              │     · │
│ en:beta-carotene-dye                 │    29 │
│ en:d-alpha-tocopheryl-acid-succinate │    12 │
│ en:dexpanthenol                      │    11 │
│ en:potassium-l-ascorbate             │     8 │
│ en:hydroxocobalamin                  │     6 │
│ en:l-ascorbyl-6-palmitate            │     5 │
│ en:pyridoxine-5-phosphate            │     3 │
│ da:vitamin-a-og-d                    │     2 │
│ en:vitamin-k3                        │     2 │
│ en:pyridoxine-dipalmitate            │     1 │
├──────────────────────────────────────┴───────┤
│ 50 rows (20 shown)                 2 columns │
└──────────────────────────────────────────────┘
```
### Product completeness
```sql
-- Product completeness
SELECT 
    complete,
    count(*) as count,
    avg(completeness) as avg_completeness
FROM products
GROUP BY complete;
```
```text
┌──────────┬─────────┬─────────────────────┐
│ complete │  count  │  avg_completeness   │
│  int32   │  int64  │       double        │
├──────────┼─────────┼─────────────────────┤
│        0 │ 3586082 │ 0.42028756940551326 │
│        1 │   15573 │  1.0050086700479197 │
└──────────┴─────────┴─────────────────────┘
```
### Product creation trends by month
```sql
-- Product creation trends by month
SELECT 
    DATE_TRUNC('month', to_timestamp(created_t)) AS month,
    COUNT(*) as new_products
FROM products
WHERE created_t >= 1704067200  -- Jan 1, 2024
GROUP BY month
ORDER BY month;
```
```text
┌──────────────────────────┬──────────────┐
│          month           │ new_products │
│ timestamp with time zone │    int64     │
├──────────────────────────┼──────────────┤
│ 2023-12-01 00:00:00-05   │           33 │
│ 2024-01-01 00:00:00-05   │        33422 │
│ 2024-02-01 00:00:00-05   │        29689 │
│ 2024-03-01 00:00:00-05   │        31773 │
│ 2024-04-01 00:00:00-04   │        38917 │
│ 2024-05-01 00:00:00-04   │        42571 │
│ 2024-06-01 00:00:00-04   │        81527 │
│ 2024-07-01 00:00:00-04   │        49811 │
│ 2024-08-01 00:00:00-04   │        47053 │
│ 2024-09-01 00:00:00-04   │        48895 │
│ 2024-10-01 00:00:00-04   │        54394 │
│ 2024-11-01 00:00:00-04   │        47107 │
│ 2024-12-01 00:00:00-05   │        54667 │
│ 2025-01-01 00:00:00-05   │        42631 │
├──────────────────────────┴──────────────┤
│ 14 rows                       2 columns │
└─────────────────────────────────────────┘
```