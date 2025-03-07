import json
import os

def extract_first_n_products(input_filepath, output_filepath, n=10):
    """
    Extrait les n premiers produits d'un fichier JSONL et les écrit dans un nouveau fichier.
    
    Args:
        input_filepath: Chemin vers le fichier JSONL d'origine
        output_filepath: Chemin où écrire le nouveau fichier JSONL
        n: Nombre de produits à extraire
    """
    # Vérifier si le fichier d'entrée existe
    if not os.path.exists(input_filepath):
        print(f"Erreur: Le fichier {input_filepath} n'existe pas")
        return False
    
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
        
        print(f"Extraction réussie: {count} produits ont été extraits vers {output_filepath}")
        return True
    
    except Exception as e:
        print(f"Erreur lors de l'extraction des produits: {str(e)}")
        return False

if __name__ == "__main__":
    # Chemins des fichiers
    input_filepath = "../../data/openfoodfacts-canadian-products.jsonl"
    output_filepath = "../../data/openfoodfacts-canadian-products-first-10.jsonl"
    
    # Extraire les 10 premiers produits
    extract_first_n_products(input_filepath, output_filepath, 10)