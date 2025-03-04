import json
from tqdm import tqdm
import os

def filter_products_by_country(input_filepath, output_filepath, country="en:canada", batch_size=10000):
    """
    Filtre un fichier JSONL pour ne garder que les produits d'un pays spécifique.
    
    Args:
        input_filepath: Chemin vers le fichier JSONL d'entrée
        output_filepath: Chemin vers le fichier JSONL de sortie
        country: Code du pays à filtrer (par défaut: "en:canada")
        batch_size: Nombre de lignes à traiter avant d'afficher la progression
    
    Returns:
        tuple: (total_products, filtered_products) - Nombres de produits total et filtrés
    """
    total_products = 0
    filtered_products = 0
    
    # Obtenir la taille du fichier
    file_size = os.path.getsize(input_filepath)
    print(f"Taille du fichier: {file_size / (1024*1024*1024):.2f} Go")
    
    # Traiter le fichier ligne par ligne
    with open(input_filepath, 'r', encoding='utf-8') as infile, \
         open(output_filepath, 'w', encoding='utf-8') as outfile:
        
        # Utiliser une barre de progression simple
        progress_bar = tqdm(desc="Filtrage des produits", unit="produits")
        
        while True:
            line = infile.readline()
            if not line:  # Fin du fichier
                break
                
            total_products += 1
            
            try:
                product = json.loads(line.strip())
                
                # Vérifier si le pays est dans countries_tags
                if "countries_tags" in product and country in product["countries_tags"]:
                    outfile.write(line)
                    filtered_products += 1
            except json.JSONDecodeError:
                pass  # Ignorer les lignes avec du JSON invalide
            
            # Mettre à jour la barre de progression
            if total_products % batch_size == 0:
                progress_bar.update(batch_size)
                progress_bar.set_postfix({
                    "total": f"{total_products:,}", 
                    "filtrés": f"{filtered_products:,}",
                    "ratio": f"{filtered_products/total_products*100:.2f}%"
                })
        
        # Mettre à jour une dernière fois pour les lignes restantes
        progress_bar.update(total_products % batch_size)
        progress_bar.close()
    
    print(f"\nFiltrage terminé!")
    print(f"Produits traités: {total_products:,}")
    print(f"Produits canadiens: {filtered_products:,} ({filtered_products/total_products*100:.2f}%)")
    print(f"Fichier de sortie: {output_filepath}")
    
    return total_products, filtered_products

if __name__ == "__main__":
    # Chemins des fichiers d'entrée et de sortie
    input_file = "../../data/openfoodfacts-products.jsonl"
    output_file = "../../data/openfoodfacts-canadian-products.jsonl"
    
    # Filtrer les produits canadiens
    filter_products_by_country(input_file, output_file, country="en:canada")

    """
    Vous devriez voir ceci dans le terminal:
    $ python filter.py
    Taille du fichier: 54.64 Go
    Filtrage des produits: 820000produits [02:25, 6856.33produits/s, total=820,000, filtrés=5,772, ratio=0.70%]
    """