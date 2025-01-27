import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path("../../data")
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"  # Fichier temporaire complet
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"  # Fichier final filtré

# Connect to the database
conn = duckdb.connect(FILTERED_DB_PATH)


def get_descriptive_stats():
    # Convert DuckDB table to pandas DataFrame for easier analysis
    df = conn.execute("SELECT * FROM products").fetchdf()
    
    # Basic statistics for numerical columns
    print("\nDescriptive Statistics for Numerical Columns:")
    print(df.describe())
    
    # Missing values analysis
    missing_percentage = df.isnull().mean() * 100
    missing_percentage_sorted = missing_percentage.sort_values(ascending=False)
    
    print("\nColumns with highest percentages of missing values:")
    print(missing_percentage_sorted)
    
    return df

def analyze_eco_scores():
    # Count products with and without eco-scores
    eco_stats = conn.execute("""
        SELECT 
            COUNT(*) as total_products,
            COUNT(CASE WHEN ecoscore_score IS NOT NULL THEN 1 END) as products_with_eco_score,
            COUNT(CASE WHEN ecoscore_score IS NULL THEN 1 END) as products_without_eco_score
        FROM products
    """).fetchdf()
    
    print("\nEco-Score Coverage:")
    print(f"Total products: {eco_stats['total_products'][0]}")
    print(f"Products with eco-score: {eco_stats['products_with_eco_score'][0]}")
    print(f"Products without eco-score: {eco_stats['products_without_eco_score'][0]}")
    
    # Distribution of eco-scores
    plot_eco_score_distribution()
    plot_eco_score_grades()
    plot_category_eco_scores()

def plot_eco_score_distribution():
    df = conn.execute("""
        SELECT ecoscore_score
        FROM products 
        WHERE ecoscore_score IS NOT NULL
    """).fetchdf()
    
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='ecoscore_score', bins=30, kde=True)
    plt.title('Distribution of Eco-Scores')
    plt.xlabel('Eco-Score')
    plt.ylabel('Number of Products')
    plt.show()

def plot_eco_score_grades():
    df = conn.execute("""
        SELECT ecoscore_grade,
               COUNT(*) as count
        FROM products
        WHERE ecoscore_grade IN ('a', 'b', 'c', 'd', 'e')
        GROUP BY ecoscore_grade
        ORDER BY ecoscore_grade
    """).fetchdf()
    
    plt.figure(figsize=(12, 8))
    colors = dict(zip(df['ecoscore_grade'], ['green', 'lightgreen', 'yellow', 'orange', 'red']))
    ax = sns.barplot(x='ecoscore_grade', y='count', data=df, palette=colors)
    plt.title('Distribution of Eco-Score Grades')
    plt.xlabel('Eco-Score Grade')
    plt.ylabel('Number of Products')
    
    # Add value labels
    for i, v in enumerate(df['count']):
        ax.text(i, v, str(v), ha='center', va='bottom')
    
    plt.show()

def plot_category_eco_scores():
    df = conn.execute("""
        SELECT 
            categories,
            ecoscore_grade,
            COUNT(*) as count
        FROM products
        WHERE ecoscore_grade IN ('a', 'b', 'c', 'd', 'e')
          AND categories IS NOT NULL
        GROUP BY categories, ecoscore_grade
        HAVING categories IN (
            SELECT categories
            FROM products
            GROUP BY categories
            ORDER BY COUNT(*) DESC
            LIMIT 10
        )
        ORDER BY categories, ecoscore_grade
    """).fetchdf()
    
    plt.figure(figsize=(14, 10))
    eco_score_colors = {'a': 'green', 'b': 'lightgreen', 'c': 'yellow', 'd': 'orange', 'e': 'red'}
    ax = sns.barplot(x='categories', y='count', hue='ecoscore_grade', data=df, palette=eco_score_colors)
    plt.title('Eco-Scores Distribution across Top 10 Categories')
    plt.xlabel('Category')
    plt.ylabel('Number of Products')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Eco-Score Grade')
    plt.tight_layout()
    plt.show()

def analyze_packaging():
    packaging_stats = conn.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN packaging != 'unknown' THEN 1 END) as with_packaging,
            COUNT(CASE WHEN packaging = 'unknown' THEN 1 END) as without_packaging
        FROM products
    """).fetchdf()
    
    print("\nPackaging Information Coverage:")
    total = packaging_stats['total'][0]
    with_pkg = packaging_stats['with_packaging'][0]
    without_pkg = packaging_stats['without_packaging'][0]
    
    print(f"Products with packaging data: {with_pkg} ({(with_pkg/total)*100:.2f}%)")
    print(f"Products without packaging data: {without_pkg} ({(without_pkg/total)*100:.2f}%)")

def analyze_missing_values(df):
    # Calculer le pourcentage de valeurs NaN et vides
    missing = pd.DataFrame()
    missing['null'] = df.isna().sum()
    missing['empty'] = (df == '').sum()
    missing['total_missing'] = missing['null'] + missing['empty']
    missing['percent'] = (missing['total_missing'] / len(df)) * 100
    
    # Trier par pourcentage décroissant
    missing_sorted = missing.sort_values('percent', ascending=False)
    
    print("\nColonnes avec le plus de valeurs manquantes:")
    print(missing_sorted['percent'].round(2))
    
    return missing_sorted

if __name__ == "__main__":
    # Get general descriptive statistics
    df = get_descriptive_stats()
    
    # Analyze eco-scores
    analyze_eco_scores()
    
    # Analyze packaging information
    analyze_packaging()
    
    df = conn.execute("SELECT * FROM products").fetchdf()
    missing_analysis = analyze_missing_values(df)

    # Close the database connection
    conn.close()