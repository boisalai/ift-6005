
"""
pip install litellm
pip install smolagents python-dotenv sqlalchemy --upgrade -q

https://huggingface.co/learn/cookbook/en/agent_data_analyst
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import json
from pathlib import Path
import os
from dotenv import load_dotenv
import duckdb
import litellm
from smolagents import CodeAgent, LiteLLMModel, Tool


# Configuration
load_dotenv()
os.environ['LITELLM_LOG'] = 'DEBUG'

DATA_DIR = Path("../data")
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

class DuckDBTool(Tool):
    name = "sql_engine"
    description = """
    Outil pour exécuter des requêtes SQL sur la base DuckDB.
    Retourne les résultats au format JSON avec la structure :
    {
        "columns": [noms des colonnes],
        "rows": [valeurs des lignes],
        "row_count": nombre de résultats,
        "error": "(optionnel) message d'erreur"
    }
    """
    inputs = {
        "query": {
            "type": "string",
            "description": "Requête SQL DuckDB valide à exécuter"
        }
    }
    output_type = "string"

    def setup(self):
        self.is_initialized = True

    def forward(self, query: str) -> str:
        if not query.strip():
            return json.dumps({"error": "Requête vide"})

        try:
            with duckdb.connect(str(FILTERED_DB_PATH)) as con:
                # Exécution de la requête
                result = con.sql(query)
                
                # Récupération des résultats
                rows = result.fetchall()
                columns = result.columns
                
                # Construction de la sortie
                output = {
                    "columns": columns,
                    "rows": [tuple(str(item) for item in row) for row in rows],
                    "row_count": len(rows)
                }
            
                return json.dumps(output)
                
        except duckdb.Error as e:
            return json.dumps({"error": f"Erreur DuckDB: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Erreur inattendue: {str(e)}"})

# Initialisation du modèle
model = LiteLLMModel(
    model_id="ollama/phi4:latest",
    api_base="http://localhost:11434",
    temperature=0.1,
    max_tokens=8096,
)

# Création de l'agent
sql_engine = DuckDBTool()
agent = CodeAgent(tools=[sql_engine], model=model, 
    additional_authorized_imports=['json'])

# Instructions pour l'agent
ADDITIONAL_NOTES = """
TU PARLES FRANÇAIS. Réponds toujours dans la langue de l'utilisateur.

Procédure d'analyse :
1. Exécuter la requête SQL avec sql_engine()
2. Charger le résultat avec json.loads(result)
3. Vérifier la présence d'erreur
4. Analyser la structure des résultats :
   - Si row_count == 0 → "Aucun résultat trouvé"
   - Si row_count == 1 et 1 colonne → Valeur unique
   - Si plusieurs colonnes → Tableau de résultats
5. Formater la réponse de manière claire et professionnelle

Exemples de code valides :
```py
# Requête simple
result = sql_engine("SELECT COUNT(*) FROM products")
data = json.loads(result)

if 'error' in data:
    final_answer(f"Erreur : {data['error']}")
elif data['row_count'] == 0:
    final_answer("Aucun produit trouvé")
else:
    count = data['rows'][0][0]
    final_answer(f"Il y a {count} produits dans la base")

# Requête complexe
result = sql_engine("SELECT product_name, sugars_value FROM products ORDER BY sugars_value DESC LIMIT 3")
data = json.loads(result)

if data['row_count'] > 0:
    response = "Produits les plus sucrés :\\n"
    for row in data['rows']:
        response += f"- {row[0]} : {row[1]}g\\n"
    final_answer(response)
```
"""

def load_dict() -> str:
    # Chargement du dictionnaire de données
    with open(DATA_DICT_PATH, 'r', encoding='utf-8') as f:
        data_dict = json.load(f)

    output = ""
    for k, v in data_dict.items():
        output += f"- {k} ({v['type']}): {v['description']}\n"
    return output

def query(query: str) -> str:
    output = sql_engine(query)
    print(f"Output:\n{output}")

def test():
    prompt = "Quelle est la moyenne des sucres par produit?"
    prompt = "Combien de produits dans la table?"

    response = agent.run(
        prompt,
        additional_args={
            "additional_notes": ADDITIONAL_NOTES,
            "language": "french"
        }
    )
    
    print("Réponse finale :", response)

if __name__ == "__main__":
    test()
    # print(load_dict())
    # result = sql_engine("SELECT COUNT(*) FROM products")                                                                         
    # data = json.loads(result)
    # print(data) 
    # query("SELECT additives_n, additives_tags, product_name FROM products LIMIT 5")
