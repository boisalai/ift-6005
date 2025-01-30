from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import duckdb
from tqdm import tqdm
import os

"""
Téléchargez le fichier `food.parquet` à partir de Hugging Face et placez-le dans le dossier `data`.
wget -P data/ https://huggingface.co/datasets/openfoodfacts/product-database/resolve/main/food.parquet
"""

DATA_DIR = Path("../data")
PARQUET_PATH = DATA_DIR / "food.parquet"
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

def create_full_db():
    """
    Crée une base de données DuckDB contenant toutes les données du fichier Parquet.
    """
    if FULL_DB_PATH.exists():
        os.remove(FULL_DB_PATH)
    
    con = duckdb.connect(str(FULL_DB_PATH), config={'memory_limit': '8GB'})
    con.execute(f"CREATE TABLE products AS SELECT * FROM '{PARQUET_PATH}'")
    con.close()

def create_filtered_db():
    """
    Crée une base de données DuckDB contenant uniquement les produits canadiens.
    """
    if FILTERED_DB_PATH.exists():
        os.remove(FILTERED_DB_PATH)

    con = duckdb.connect(str(FILTERED_DB_PATH))

    try:
        con.execute(f"ATTACH DATABASE '{FULL_DB_PATH}' AS full_db")

        con.execute(f"""
            CREATE TABLE products AS 
            SELECT * FROM full_db.products
            WHERE array_contains(countries_tags, 'en:canada')
        """)

        count = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        print(f"✅ {count} produits canadiens transférés.")

    finally:
        con.execute("DETACH full_db")
        con.close()

def describe_db(db_path: Path):
    """
    Génère une description des données stockées dans la base de données DuckDB spécifiée.
    """
    output_file = Path("../docs/markdown/description.md")

    with duckdb.connect(str(db_path)) as con:
        columns = con.execute("SELECT * FROM products LIMIT 0").description
        total_rows = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]

        with output_file.open("w", encoding="utf-8") as f:
            f.write(f"# Description de {db_path}\n\n")
            f.write(f"- Nombre de lignes: {total_rows:,}\n")
            f.write(f"- Nombre de colonnes: {len(columns)}\n\n")

            for col in columns:
                col_name = col[0]
                col_type = col[1]

                stats = con.execute(
                    f"""
                    SELECT 
                        COUNT(DISTINCT {col_name}) as unique_count,
                        COUNT(*) - COUNT({col_name}) as null_count,
                        MIN({col_name}) as min_val,
                        MAX({col_name}) as max_val,
                        AVG(CASE WHEN {col_name} IS NOT NULL AND typeof({col_name}) in ('INTEGER', 'DOUBLE') 
                            THEN CAST({col_name} AS DOUBLE) END) as mean,
                        STDDEV(CASE WHEN {col_name} IS NOT NULL AND typeof({col_name}) in ('INTEGER', 'DOUBLE') 
                            THEN CAST({col_name} AS DOUBLE) END) as std
                    FROM products
                """
                ).fetchone()

                samples = con.execute(
                    f"""
                    SELECT {col_name}
                    FROM products
                    WHERE {col_name} IS NOT NULL
                    LIMIT 10
                """
                ).fetchall()

                # Écriture des métadonnées
                f.write(f"## {col_name}\n")
                f.write(f"- **Type**: `{col_type}`\n")
                f.write(f"- **Valeurs uniques**: {stats[0]:,}\n")
                f.write(
                    f"- **Valeurs nulles**: {stats[1]:,} ({stats[1]/total_rows*100:.2f}%)\n"
                )

                if col_type in ("INTEGER", "DOUBLE"):
                    f.write("- **Statistiques descriptives**:\n")
                    f.write(f"  - Minimum: {stats[2]}\n")
                    f.write(f"  - Maximum: {stats[3]}\n")
                    f.write(f"  - Moyenne: {stats[4]:.2f if stats[4] else 'N/A'}\n")
                    f.write(f"  - Écart-type: {stats[5]:.2f if stats[5] else 'N/A'}\n")

                f.write("- **Exemples de valeurs**:\n")
                for sample in samples:
                    f.write(f"  - `{sample[0]}`\n")
                f.write("\n")

    print(f"Description générée dans {output_file}")

def create_missing_values_plot(db_path: Path):
    """
    Crée un graphique montrant la distribution de la complétude des colonnes 
    dans la base de données DuckDB spécifiée.
    """
    with duckdb.connect(str(db_path)) as con:
        # Récupérer les statistiques des colonnes
        columns = con.execute("SELECT * FROM products LIMIT 0").description
        total_rows = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        
        # Calculer les taux de remplissage
        column_stats = []
        for col in columns:
            col_name = col[0]
            stats = con.execute(f"""
                SELECT 
                    COUNT({col_name}) as non_null_count
                FROM products
            """).fetchone()
            
            non_null_count = stats[0]
            non_null_percentage = (non_null_count / total_rows) * 100
            column_stats.append(non_null_percentage)

        # Définir les tranches de pourcentage
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
        labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', 
                 '50-60%', '60-70%', '70-80%', '80-90%', '90-95%', '95-100%']

        # Créer le graphique
        plt.figure(figsize=(8, 5))
        
        # Calculer l'histogramme
        hist, edges = np.histogram(column_stats, bins=bins)
        
        # Créer le graphique en barres
        x = range(len(labels))
        bars = plt.bar(x, hist, align='center')
        
        # Personnaliser l'apparence
        plt.xticks(x, labels, rotation=45, ha='right')
        plt.xlabel('Complétude des données (%)')
        plt.ylabel('Nombre de colonnes')
        plt.title('Distribution de la complétude des colonnes')
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        # Ajuster la mise en page
        plt.tight_layout()
        
        # Sauvegarder le graphique
        plot_path = Path("../docs/latex/plan/figures/missing_values.pdf")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Graphique sauvegardé dans {plot_path}")


if __name__ == "__main__":
    # create_full_db()
    # create_filtered_db()
    # describe_db(FILTERED_DB_PATH)
    # describe_db(FULL_DB_PATH)
    create_missing_values_plot(FULL_DB_PATH)
