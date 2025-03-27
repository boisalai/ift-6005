import json
from collections import Counter, defaultdict
import pandas as pd

def list_jsonl_fields(file_path, sample_lines=10):
    fields = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= sample_lines:
                break
            try:
                record = json.loads(line)
                fields.update(record.keys())
            except json.JSONDecodeError:
                continue
    return sorted(fields)

def analyze_json_structure(file_path):
    """Analyser la structure des données JSON pour identifier les champs pertinents"""
    
    # Dictionnaires pour stocker les statistiques
    all_keys = Counter()
    field_types = defaultdict(Counter)
    field_examples = {}
    field_non_empty = Counter()
    
    # Chargement des produits
    products = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                products.append(json.loads(line))
    
    # Analyse de chaque produit
    total_products = len(products)
    print(f"Analyse de {total_products} produits...")
    
    # Parcourir chaque produit et collecter des statistiques
    for product in products:
        # Compter les clés présentes
        for key in product.keys():
            all_keys[key] += 1
            
            # Déterminer le type de chaque champ
            field_type = type(product[key]).__name__
            field_types[key][field_type] += 1
            
            # Sauvegarder un exemple de valeur non vide
            if product[key] and key not in field_examples:
                field_examples[key] = product[key]
            
            # Compter les champs non vides
            if product[key]:
                field_non_empty[key] += 1
    
    # Créer un DataFrame pour l'analyse
    analysis_data = []
    for key in all_keys:
        presence_percentage = (all_keys[key] / total_products) * 100
        non_empty_percentage = (field_non_empty[key] / all_keys[key]) * 100 if all_keys[key] > 0 else 0
        
        # Déterminer les types de données les plus courants pour ce champ
        most_common_type = field_types[key].most_common(1)[0][0] if field_types[key] else "N/A"
        
        # Obtenir un exemple de valeur
        example = str(field_examples.get(key, ""))
        if len(example) > 50:  # Tronquer les exemples trop longs
            example = example[:50] + "..."
            
        analysis_data.append({
            "Champ": key,
            "Présence (%)": round(presence_percentage, 1),
            "Non vide (%)": round(non_empty_percentage, 1),
            "Type le plus courant": most_common_type,
            "Exemple": example
        })
    
    # Convertir en DataFrame et trier par présence
    df = pd.DataFrame(analysis_data)
    df = df.sort_values(by=["Présence (%)", "Non vide (%)"], ascending=False)
    
    return df

def suggest_important_fields(df, threshold=50):
    """Suggérer les champs les plus importants basés sur leur présence et leur contenu"""
    
    # Filtrer les champs qui sont présents et non vides dans au moins X% des produits
    important_fields = df[(df["Présence (%)"] >= threshold) & (df["Non vide (%)"] >= threshold)]
    
    return important_fields

def analyze_nested_structures(file_path, nested_fields=["nutriments", "ingredients"]):
    """Analyser la structure des champs imbriqués importants"""
    
    nested_analysis = {}
    
    # Chargement des produits
    products = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                products.append(json.loads(line))
    
    # Pour chaque champ imbriqué
    for field in nested_fields:
        keys_counter = Counter()
        
        # Parcourir chaque produit
        for product in products:
            if field in product and isinstance(product[field], dict):
                # Compter les clés présentes dans ce champ imbriqué
                for nested_key in product[field].keys():
                    keys_counter[nested_key] += 1
        
        # Stocker les résultats
        nested_analysis[field] = keys_counter
    
    return nested_analysis

def main():
    file_path = "../../data/openfoodfacts-canadian-products.jsonl"
    
    # Analyser la structure générale
    print("Analyse de la structure des données...")
    df = analyze_json_structure(file_path)
    
    # Afficher les 20 premiers champs les plus courants
    print("\nLes 20 champs les plus courants:")
    print(df.head(20).to_string(index=False))
    
    # Suggestion de champs importants
    print("\nChamps suggérés comme importants (présents dans au moins 80% des produits):")
    important_df = suggest_important_fields(df, 80)
    print(important_df.to_string(index=False))
    
    # Analyser les structures imbriquées
    print("\nAnalyse des structures imbriquées...")
    nested_analysis = analyze_nested_structures(file_path)
    
    for field, counter in nested_analysis.items():
        print(f"\nChamps présents dans '{field}':")
        for key, count in counter.most_common(10):
            print(f"  - {key}: présent dans {count} produits")

def describe():
    file_path = "../../data/openfoodfacts-canadian-products.jsonl"
    fields = list_jsonl_fields(file_path)
    print("Champs présents dans le fichier JSONL :", fields)

if __name__ == "__main__":
    # main()
    describe()