from pathlib import Path
import duckdb
import json
from typing import Dict, List, Any
import numpy as np
from datetime import datetime
# pip install pdfplumber
import pdfplumber
import re

DATA_DIR = Path("../data")
PARQUET_PATH = DATA_DIR / "food.parquet"
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

class FieldInfoExtractor:
    def __init__(self, data_fields_path: Path, wiki_path: Path):
        self.data_fields_path = data_fields_path
        self.wiki_path = wiki_path
        self.field_descriptions = {}
        self.load_descriptions()
        self.load_wiki_info()
    
    def load_descriptions(self):
        """Charge les descriptions depuis le fichier data-fields.txt"""
        with open(self.data_fields_path, 'r', encoding='utf-8') as f:
            content = f.read()
                
        # Ignore les sections générales au début du fichier
        start_idx = content.find("List of fields:")
        if start_idx != -1:
            content = content[start_idx:]
        
        # Parse le contenu ligne par ligne
        lines = content.split('\n')
        
        for line in lines:
            # Nouveau champ trouvé avec sa description
            if ' : ' in line and not line.startswith(('#', '-', ' ')):
                field_name, description = line.split(' : ', 1)
                field_name = field_name.strip()
                description = description.strip()
                
                self.field_descriptions[field_name] = {
                    'description': description,
                    'format': '',
                    'rules': [],
                    'examples': []
                }
        
    def load_wiki_info(self):
        """Charge les informations complémentaires depuis le PDF du wiki"""
        try:
            with pdfplumber.open(self.wiki_path) as pdf:
                content = ""
                for page in pdf.pages:
                    content += page.extract_text() + "\n"

                # Parse le contenu par sections
                sections = content.split('\n\n')
                current_field = None
                
                for section in sections:
                    # Cherche les titres de champs (en gras ou suivis de ':')
                    field_match = re.search(r'^([A-Za-z_]+)[:|\n]', section, re.MULTILINE)
                    if field_match:
                        current_field = field_match.group(1).lower()
                        
                        # Si le champ existe déjà, enrichit sa description
                        if current_field in self.field_descriptions:
                            # Nettoie et ajoute les nouvelles informations
                            wiki_info = self.clean_wiki_text(section)
                            
                            # Enrichit la description existante
                            if wiki_info:
                                current_desc = self.field_descriptions[current_field]['description']
                                if not current_desc.endswith('.'): 
                                    current_desc += '.'
                                self.field_descriptions[current_field]['description'] = \
                                    f"{current_desc} {wiki_info}"
                            
                            # Cherche des exemples
                            examples = re.findall(r'Example[s]?:\s*([^\n]+)', section, re.IGNORECASE)
                            if examples:
                                self.field_descriptions[current_field]['examples'].extend(examples)
                            
                            # Cherche des règles ou contraintes
                            rules = re.findall(r'Rule[s]?:|Constraint[s]?:\s*([^\n]+)', section, re.IGNORECASE)
                            if rules:
                                self.field_descriptions[current_field]['rules'].extend(rules)
                            
        except Exception as e:
            print(f"Erreur lors de la lecture du PDF: {str(e)}")
    
    def clean_wiki_text(self, text: str) -> str:
        """Nettoie le texte extrait du PDF"""
        # Supprime les en-têtes et pieds de page communs
        text = re.sub(r'Page \d+ of \d+', '', text)
        # Supprime les caractères spéciaux
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
        # Normalise les espaces
        text = ' '.join(text.split())
        return text

    def get_field_info(self, field_name: str) -> dict:
        """Récupère les informations pour un champ donné"""
        base_name = field_name.split('_')[0]  # Gère les variantes (e.g., brands et brands_tags)
        
        if field_name in self.field_descriptions:
            return self.field_descriptions[field_name]
        elif base_name in self.field_descriptions:
            return self.field_descriptions[base_name]
        else:
            return {
                'description': f'Description of {field_name}',
                'format': '',
                'rules': [],
                'examples': []
            }

class DataDictionaryGenerator:
    def __init__(self, db_path: Path, field_info_extractor: FieldInfoExtractor):
        self.db_path = db_path
        self.con = duckdb.connect(str(db_path))
        self.total_rows = self.con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        self.field_info = field_info_extractor
        
        # Mapping des types exacts depuis le schéma Parquet
        # Source : https://wiki.openfoodfacts.org/DuckDB_Cheatsheet
        self.type_mapping = {
            'additives_n': 'INTEGER',
            'additives_tags': 'VARCHAR[]',
            'allergens_tags': 'VARCHAR[]',
            'brands_tags': 'VARCHAR[]',
            'brands': 'VARCHAR',
            'categories': 'VARCHAR',
            'categories_tags': 'VARCHAR[]',
            'checkers_tags': 'VARCHAR[]',
            'ciqual_food_name_tags': 'VARCHAR[]',
            'cities_tags': 'VARCHAR[]',
            'code': 'VARCHAR',
            'compared_to_category': 'VARCHAR',
            'complete': 'INTEGER',
            'completeness': 'FLOAT',
            'correctors_tags': 'VARCHAR[]',
            'countries_tags': 'VARCHAR[]',
            'created_t': 'BIGINT',
            'creator': 'VARCHAR',
            'data_quality_errors_tags': 'VARCHAR[]',
            'data_quality_info_tags': 'VARCHAR[]',
            'data_quality_warnings_tags': 'VARCHAR[]',
            'data_sources_tags': 'VARCHAR[]',
            'ecoscore_data': 'VARCHAR',
            'ecoscore_grade': 'VARCHAR',
            'ecoscore_score': 'INTEGER',
            'ecoscore_tags': 'VARCHAR[]',
            'editors': 'VARCHAR[]',
            'emb_codes_tags': 'VARCHAR[]',
            'emb_codes': 'VARCHAR',
            'entry_dates_tags': 'VARCHAR[]',
            'food_groups_tags': 'VARCHAR[]',
            'generic_name': 'STRUCT(lang VARCHAR, "text" VARCHAR)[]',
            'images': 'STRUCT("key" VARCHAR, imgid INTEGER, sizes STRUCT("100" STRUCT(h INTEGER, w INTEGER), "200" STRUCT(h INTEGER, w INTEGER), "400" STRUCT(h INTEGER, w INTEGER), "full" STRUCT(h INTEGER, w INTEGER)), uploaded_t BIGINT, uploader VARCHAR)[]',
            'informers_tags': 'VARCHAR[]',
            'ingredients_analysis_tags': 'VARCHAR[]',
            'ingredients_from_palm_oil_n': 'INTEGER',
            'ingredients_n': 'INTEGER',
            'ingredients_original_tags': 'VARCHAR[]',
            'ingredients_percent_analysis': 'INTEGER',
            'ingredients_tags': 'VARCHAR[]',
            'ingredients_text': 'STRUCT(lang VARCHAR, "text" VARCHAR)[]',
            'ingredients_with_specified_percent_n': 'INTEGER',
            'ingredients_with_unspecified_percent_n': 'INTEGER',
            'ingredients_without_ciqual_codes_n': 'INTEGER',
            'ingredients_without_ciqual_codes': 'VARCHAR[]',
            'ingredients': 'VARCHAR',
            'known_ingredients_n': 'INTEGER',
            'labels_tags': 'VARCHAR[]',
            'labels': 'VARCHAR',
            'lang': 'VARCHAR',
            'languages_tags': 'VARCHAR[]',
            'last_edit_dates_tags': 'VARCHAR[]',
            'last_editor': 'VARCHAR',
            'last_image_t': 'BIGINT',
            'last_modified_by': 'VARCHAR',
            'last_modified_t': 'BIGINT',
            'last_updated_t': 'BIGINT',
            'link': 'VARCHAR',
            'main_countries_tags': 'VARCHAR[]',
            'manufacturing_places_tags': 'VARCHAR[]',
            'manufacturing_places': 'VARCHAR',
            'max_imgid': 'INTEGER',
            'minerals_tags': 'VARCHAR[]',
            'misc_tags': 'VARCHAR[]',
            'new_additives_n': 'INTEGER',
            'no_nutrition_data': 'BOOLEAN',
            'nova_group': 'INTEGER',
            'nova_groups_tags': 'VARCHAR[]',
            'nova_groups': 'VARCHAR',
            'nucleotides_tags': 'VARCHAR[]',
            'nutrient_levels_tags': 'VARCHAR[]',
            'nutriments': 'STRUCT("name" VARCHAR, "value" FLOAT, "100g" FLOAT, serving FLOAT, unit VARCHAR, prepared_value FLOAT, prepared_100g FLOAT, prepared_serving FLOAT, prepared_unit VARCHAR)[]',
            'nutriscore_grade': 'VARCHAR',
            'nutriscore_score': 'INTEGER',
            'nutrition_data_per': 'VARCHAR',
            'obsolete': 'BOOLEAN',
            'origins_tags': 'VARCHAR[]',
            'origins': 'VARCHAR',
            'owner_fields': 'STRUCT(field_name VARCHAR, "timestamp" BIGINT)[]',
            'owner': 'VARCHAR',
            'packagings_complete': 'BOOLEAN',
            'packaging_recycling_tags': 'VARCHAR[]',
            'packaging_shapes_tags': 'VARCHAR[]',
            'packaging_tags': 'VARCHAR[]',
            'packaging_text': 'STRUCT(lang VARCHAR, "text" VARCHAR)[]',
            'packaging': 'VARCHAR',
            'packagings': 'STRUCT(material VARCHAR, number_of_units BIGINT, quantity_per_unit VARCHAR, quantity_per_unit_unit VARCHAR, quantity_per_unit_value VARCHAR, recycling VARCHAR, shape VARCHAR, weight_measured FLOAT)[]',
            'photographers': 'VARCHAR[]',
            'popularity_key': 'BIGINT',
            'popularity_tags': 'VARCHAR[]',
            'product_name': 'STRUCT(lang VARCHAR, "text" VARCHAR)[]',
            'product_quantity_unit': 'VARCHAR',
            'product_quantity': 'VARCHAR',
            'purchase_places_tags': 'VARCHAR[]',
            'quantity': 'VARCHAR',
            'rev': 'INTEGER',
            'scans_n': 'INTEGER',
            'serving_quantity': 'VARCHAR',
            'serving_size': 'VARCHAR',
            'states_tags': 'VARCHAR[]',
            'stores_tags': 'VARCHAR[]',
            'stores': 'VARCHAR',
            'traces_tags': 'VARCHAR[]',
            'unique_scans_n': 'INTEGER',
            'unknown_ingredients_n': 'INTEGER',
            'unknown_nutrients_tags': 'VARCHAR[]',
            'vitamins_tags': 'VARCHAR[]',
            'with_non_nutritive_sweeteners': 'INTEGER',
            'with_sweeteners': 'INTEGER'
        }
    
    def generate_data_dictionary(self) -> Dict:
        """Génère un dictionnaire de données simplifié"""
        columns = self.con.execute("SELECT * FROM products LIMIT 0").description
        
        data_dict = {}
        
        for col in columns:
            col_name = col[0]
            data_dict[col_name] = self.analyze_field(col)
        
        return data_dict
    
    def analyze_field(self, column: tuple) -> Dict:
        """Analyse simplifiée d'un champ avec informations enrichies"""
        col_name, col_type = column[0], column[1]
        
        # Utilise le type exact du schéma Parquet s'il existe
        if col_name in self.type_mapping:  # Changé de parquet_types à type_mapping
            display_type = self.type_mapping[col_name]
        else:
            display_type = str(col_type)

        # Récupération des statistiques de base
        stats = self.con.execute(f"""
            SELECT 
                COUNT(DISTINCT {col_name}) as unique_count,
                COUNT(*) - COUNT({col_name}) as null_count
            FROM products
        """).fetchone()
        
        null_percentage = (stats[1] / self.total_rows) * 100
        completeness_score = 100 - null_percentage
        
        # Récupère les informations additionnelles
        field_info = self.field_info.get_field_info(col_name)
        
        # Structure simplifiée du champ avec informations enrichies
        result = {
            "description": field_info['description'],
            "type": display_type,
            "format": field_info['format'],
            "is_nullable": True,
            "unique_values_count": stats[0],
            "completeness_score": round(completeness_score, 1),
            "known_issues": self.get_known_issues(col_name, null_percentage),
            "examples": self.get_examples(col_name)
        }
        
        return result

    def get_struct_description(self, struct_type: str) -> str:
        """Génère une description lisible pour les types STRUCT"""
        # Extrait les champs de la structure depuis le type
        # Exemple: STRUCT(lang VARCHAR, "text" VARCHAR) -> "Structure with fields: lang (VARCHAR), text (VARCHAR)"
        match = re.search(r'STRUCT\((.*)\)', struct_type)
        if match:
            fields = match.group(1)
            fields_list = [f.strip().replace('"', '') for f in fields.split(',')]
            return f"Structure with fields: {', '.join(fields_list)}"
        return struct_type
    
    def get_known_issues(self, col_name: str, null_percentage: float) -> List[str]:
        """Identifie les problèmes connus pour le champ"""
        issues = []
        
        if null_percentage > 50:
            issues.append(f"High percentage of null values: {round(null_percentage, 1)}%")
        
        return issues
    
    def get_examples(self, col_name: str) -> List[str]:
        """Récupère des exemples de valeurs avec un format amélioré"""
        try:
            # Utilise une sous-requête pour éviter les problèmes avec les caractères spéciaux
            query = f"""
                WITH sample_data AS (
                    SELECT CAST({col_name} AS VARCHAR) as value
                    FROM products
                    WHERE {col_name} IS NOT NULL
                    LIMIT 5
                )
                SELECT value FROM sample_data
            """
            
            results = self.con.execute(query).fetchall()
            examples = []
            
            for r in results:
                if r[0] is not None:
                    example = str(r[0])
                    
                    # Pour les champs JSON complexes
                    if col_name in ['ecoscore_data', 'images'] and example.startswith('{'):
                        try:
                            data = json.loads(example)
                            example = "{ " + ", ".join(f'"{k}": ...' for k in data.keys()) + " }"
                        except json.JSONDecodeError:
                            pass
                    
                    # Tronque les exemples trop longs
                    if len(example) > 100:
                        example = example[:97] + "..."
                    
                    examples.append(example)
            
            return examples
            
        except Exception as e:
            print(f"Erreur lors de la récupération des exemples pour {col_name}: {str(e)}")
            return []


def main():
    """Fonction principale"""
    db_path = FILTERED_DB_PATH
    data_fields_path = DATA_DIR / "data-fields.txt"
    wiki_path = DATA_DIR / "Data_fields_wiki.pdf"
    output_file = Path("../docs/data_dictionary.json")
    
    # Création de l'extracteur d'informations
    field_info = FieldInfoExtractor(data_fields_path, wiki_path)

    # Création du dictionnaire de données
    generator = DataDictionaryGenerator(db_path, field_info)
    data_dict = generator.generate_data_dictionary()
    
    # Écriture du fichier JSON
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data_dict, f, indent=2, ensure_ascii=False)
    
    print(f"Dictionnaire de données généré dans {output_file}")

if __name__ == "__main__":
    main()