import json
import os

def count_products_in_file(filepath):
    """
    Compte le nombre de produits (lignes) dans un fichier JSONL.
    
    Args:
        filepath: Chemin vers le fichier JSONL
        
    Returns:
        Le nombre de produits dans le fichier ou 0 en cas d'erreur
    """
    if not os.path.exists(filepath):
        print(f"Erreur: Le fichier {filepath} n'existe pas")
        return 0
    
    try:
        count = 0
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                count += 1
        return count
    except Exception as e:
        print(f"Erreur lors du comptage des produits dans {filepath}: {str(e)}")
        return 0


def extract_first_n_products(input_filepath, output_filepath, n=10):
    """
    Extrait les n premiers produits d'un fichier JSONL et les écrire dans un nouveau fichier.
    
    Args:
        input_filepath: Chemin vers le fichier JSONL d'origine
        output_filepath: Chemin où écrire le nouveau fichier JSONL
        n: Nombre de produits à extraire

    Returns:
        Un tuple (succès, nombre de produits extraits)
    """
    # Vérifier si le fichier d'entrée existe
    if not os.path.exists(input_filepath):
        print(f"Erreur: Le fichier {input_filepath} n'existe pas")
        return False, 0
    
    # Compter le nombre total de produits dans le fichier d'entrée
    total_products = count_products_in_file(input_filepath)
    print(f"Le fichier d'entrée contient {total_products} produits au total")
    
    # Créer le répertoire de sortie s'il n'existe pas
    output_dir = os.path.dirname(output_filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    count = 0
    try:
        # Ouvrir le fichier d'entrée en lecture et le fichier de sortie en écriture
        with open(input_filepath, 'r', encoding='utf-8') as infile, \
             open(output_filepath, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                # Écrire la ligne dans le fichier de sortie
                outfile.write(line)
                count += 1
                
                # Arrêter après avoir extrait n produits
                if count >= n:
                    break
        
        # Vérifier le nombre réel de produits dans le fichier de sortie
        output_products = count_products_in_file(output_filepath)
        print(f"Extraction réussie: {count} produits ont été extraits")
        print(f"Le fichier de sortie contient {output_products} produits")
        
        return True, count
    
    except Exception as e:
        print(f"Erreur lors de l'extraction des produits: {str(e)}")
        return False, 0

if __name__ == "__main__":
    # Chemins des fichiers
    input_filepath = "../../data/openfoodfacts-canadian-products.jsonl"
    output_filepath = "../../data/openfoodfacts-canadian-products-first-10.jsonl"
    
    # Extraire les 10 premiers produits
    success, extracted = extract_first_n_products(input_filepath, output_filepath, 100)
    
    if success:
        print(f"Opération terminée avec succès.")