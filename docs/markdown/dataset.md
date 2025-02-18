# Dataset Preparation

This document explains how we prepare and process the Open Food Facts dataset for our conversational agent project.

## Overview

The data preparation process involves:
1. Downloading the Open Food Facts Parquet file
2. Creating a full DuckDB database
3. Creating a filtered database containing only Canadian products
4. Analyzing data completeness
5. Generating data visualizations

## Data Source

The Open Food Facts dataset is available as a Parquet file from Hugging Face:
```bash
wget -P data/ https://huggingface.co/datasets/openfoodfacts/product-database/resolve/main/food.parquet
```

The Parquet format was chosen for its column-oriented storage, making it efficient for handling large datasets on machines with limited RAM.

## Database Creation Process

See the `src/data.py` script for the full code.

### 1. Creating the Full Database

The `create_full_db()` function converts the Parquet file into a DuckDB database:

```python
DATA_DIR = Path("../data")
PARQUET_PATH = DATA_DIR / "food.parquet"
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"

def create_full_db():
    """Creates a DuckDB database containing all data from the Parquet file."""
    if FULL_DB_PATH.exists():
        os.remove(FULL_DB_PATH)
    
    con = duckdb.connect(str(FULL_DB_PATH), config={'memory_limit': '8GB'})
    con.execute(f"CREATE TABLE products AS SELECT * FROM '{PARQUET_PATH}'")
    con.close()
```

This step creates a complete database containing all 3.6 million products.

### 2. Creating the Filtered Database

The `create_filtered_db()` function creates a smaller database containing only Canadian products:

```python
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

def create_filtered_db():
    """Creates a DuckDB database containing only Canadian products."""
    con = duckdb.connect(str(FILTERED_DB_PATH))
    try:
        con.execute(f"ATTACH DATABASE '{FULL_DB_PATH}' AS full_db")
        con.execute("""
            CREATE TABLE products AS 
            SELECT * FROM full_db.products
            WHERE array_contains(countries_tags, 'en:canada')
        """)
    finally:
        con.execute("DETACH full_db")
        con.close()
```

This filtering reduces the dataset to approximately 94,802 Canadian products, making it more manageable for development and testing.

## Data Analysis

### Database Description

The `describe_db()` function generates a detailed description of the database structure:
- Number of rows and columns
- Column types and statistics
- Sample values for each column
- Null value counts and percentages
- Basic statistical measures for numeric columns

The description is saved as a Markdown file for easy reference.

### Data Completeness Analysis

The `create_missing_values_plot()` function analyzes and visualizes data completeness:
- Generates a histogram of column completeness
- Groups columns by completeness percentage
- Identifies data quality issues
- Creates a visualization saved as missing_values.pdf

Key findings from the completeness analysis:
- Strong bimodal distribution
- Many columns are either very complete (>95%) or very sparse (<30%)
- Critical nutritional information tends to be well-populated
- Optional fields like eco-score have significant missing data

## Dataset Statistics

The filtered Canadian dataset includes:
- Total products: 94,802
- Total columns: 109
- Key data types:
  - Text fields (product names, descriptions)
  - Numeric fields (nutritional values)
  - Array fields (categories, labels)
  - Structured fields (multilingual content)

## Usage Notes

When working with this dataset, consider:
1. Always handle NULL values appropriately
2. Account for multilingual content (French/English)
3. Be aware of array field structures
4. Consider data completeness when designing queries

## Data Quality Considerations

1. Missing Values:
   - Some fields have high percentages of missing data
   - Critical fields (product name, code) are well populated
   - Optional fields (eco-score, packaging) often incomplete

2. Data Consistency:
   - Multilingual fields may have varying completeness
   - Array fields may contain duplicates or variations
   - Numeric fields may need validation

3. Performance Optimization:
   - Filtered database significantly reduces query times
   - Index creation may be needed for frequent queries
   - Consider caching for common operations

## Directory Structure

```
data/
├── food.parquet             # Original dataset
├── food_full.duckdb         # Complete database
├── food_canada.duckdb       # Filtered Canadian products
└── cache/                   # Cache directory for operations
```

## References

- Open Food Facts Data: [Official Documentation](https://world.openfoodfacts.org/data)
