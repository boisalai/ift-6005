# pip install duckdb
import duckdb

def prog1():
    # Requête sur le fichier Parquet en utilisant le chemin complet
    query = f"SELECT * FROM '{data_path}' LIMIT 5"  # J'ai ajouté LIMIT 5 pour tester
    result = con.execute(query).fetchall()

    # Afficher les résultats
    print(result)

    # Pour voir les colonnes disponibles
    columns = con.execute(f"SELECT * FROM '{data_path}' LIMIT 0").description
    print("Colonnes disponibles:")
    for col in columns:
        print(f"- {col[0]}")

def prog2():
    # Créer une connexion
    with duckdb.connect() as con:
        # Requête modifiée pour utiliser LIKE au lieu de SIMILAR TO
        query = f"""
        SELECT 
            brands,
            product_name,
            quantity,
            countries_tags,
            nutriscore_grade
        FROM '{data_path}'
        WHERE EXISTS (
            SELECT * 
            FROM UNNEST(countries_tags) AS t(country) 
            WHERE country LIKE '%:canada'
        )
        LIMIT 10
        """

        # Exécuter la requête
        result = con.execute(query).fetchall()

        # Afficher les résultats de façon formatée
        for row in result:
            print("\n---")
            print(f"Marque: {row[0]}")
            print(f"Produit: {row[1]}")
            print(f"Quantité: {row[2]}")
            print(f"Pays: {row[3]}")
            print(f"Nutriscore: {row[4]}")

def prog3():
    # Requête pour compter toutes les lignes
    query_total = f"""
    SELECT COUNT(*) as total_rows
    FROM '{data_path}'
    """

    # Requête pour compter les produits canadiens
    query_canada = f"""
    SELECT COUNT(*) as canadian_products
    FROM '{data_path}'
    WHERE array_contains(countries_tags, 'en:canada')
    """

    # Exécuter les requêtes
    total_rows = con.execute(query_total).fetchone()[0]
    canadian_products = con.execute(query_canada).fetchone()[0]

    print(f"Nombre total de produits dans la base: {total_rows:,}")
    print(f"Nombre de produits canadiens: {canadian_products:,}")
    print(f"Pourcentage de produits canadiens: {(canadian_products/total_rows)*100:.2f}%")
    # Nombre total de produits dans la base: 3,594,901
    # Nombre de produits canadiens: 94,591
    # Pourcentage de produits canadiens: 2.63%


if __name__ == "__main__":
    # Définir le chemin du fichier
    data_path = "/Users/alain/Workspace/OpenFoodFacts/food.parquet"

    # Créer une connexion
    con = duckdb.connect()

    prog3()

    # Fermer la connexion
    con.close()