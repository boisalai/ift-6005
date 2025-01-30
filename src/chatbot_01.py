import os
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import duckdb

DATA_DIR = Path("../data")
PARQUET_PATH = DATA_DIR / "food.parquet"
FULL_DB_PATH = DATA_DIR / "food_full.duckdb"
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"

# _ = load_dotenv(find_dotenv()) # read local .env file
# openai.api_key  = os.getenv('OPENAI_API_KEY')


def get_connection(db_path: Path):
    conn = duckdb.connect(str(db_path))
    return conn

# Création du jeu de test
def create_test_set():
    test_questions = [
        {"question": "Quels en-cas sans allergènes ont un Nutri-score A ?", "sql": "SELECT * FROM food_facts WHERE NutriScore = 'A' AND Allergens = 'None'"},
        # Ajouter d'autres questions ici
    ]
    return test_questions

from transformers import AutoModelForCausalLM, AutoTokenizer

# Chargement du modèle Qwen2-7B-Instruct
def load_dialogue_model():
    model_name = "Qwen/Qwen2-7B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return model, tokenizer

# Gestion des interactions utilisateur
def handle_user_input(model, tokenizer, user_input):
    inputs = tokenizer(user_input, return_tensors="pt")
    outputs = model.generate(**inputs)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

import sqlglot

# Schéma de la base de données Open Food Facts
DATABASE_SCHEMA = """
La base de données contient une table appelée `food_facts` avec les colonnes suivantes :
- `product_name` (texte) : Le nom du produit.
- `brand` (texte) : La marque du produit.
- `quantity` (texte) : La quantité du produit (par exemple, "500g").
- `nutrients` (texte) : Les nutriments présents dans le produit.
- `allergens` (texte) : Les allergènes présents dans le produit (par exemple, "gluten, lait").
- `additives` (texte) : Les additifs présents dans le produit.
- `nutri_score` (texte) : Le Nutri-Score du produit (par exemple, "A", "B", "C").
- `eco_score` (texte) : L'Eco-Score du produit (par exemple, "A", "B", "C").
- `origin_country` (texte) : Le pays d'origine du produit.
- `stores` (texte) : Les magasins où le produit est disponible.
"""

def text_to_sql(question, model, tokenizer, conversation_history):
    """
    Convertit une question en langage naturel en requête SQL en tenant compte du contexte de la conversation.
    :param question: La question de l'utilisateur
    :param model: Le modèle LLM
    :param tokenizer: Le tokenizer du modèle
    :param conversation_history: L'historique de la conversation
    :return: La requête SQL générée
    """
    # Préparation du prompt pour le LLM
    prompt = f"""
    Vous êtes un assistant intelligent capable de convertir des questions en langage naturel en requêtes SQL.
    Voici le schéma de la base de données :
    
    {DATABASE_SCHEMA}
    
    Voici l'historique de la conversation :
    """
    
    # Ajout de l'historique de la conversation au prompt
    for message in conversation_history:
        prompt += f"\n{message['role'].capitalize()}: {message['content']}"
    
    # Ajout de la nouvelle question
    prompt += f"""
    
    Voici la nouvelle question en langage naturel :
    {question}
    
    Veuillez générer une requête SQL pour répondre à cette question.
    La requête SQL doit être compatible avec une base de données DuckDB.
    """
    
    # Conversion de la question en SQL en utilisant le LLM
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=500)
    sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Nettoyage de la requête SQL
    sql_query = sql_query.strip()
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:-3].strip()  # Supprime les balises ```sql si elles sont présentes
    
    return sql_query

# Conversion de la question en SQL
def transpile(question):
    # Utilisation de sqlglot pour valider et optimiser la requête SQL
    try:
        sql = sqlglot.transpile(question, read="sql", write="sql")
        return sql
    except sqlglot.errors.ParseError as e:
        return str(e)

# Exécution de la requête SQL sur DuckDB
def execute_query(conn, sql):
    try:
        result = conn.execute(sql).fetchdf()
        return result
    except Exception as e:
        return str(e)

# Génération de la réponse en langage naturel
def generate_response(query_result):
    if isinstance(query_result, str):
        return f"Erreur lors de l'exécution de la requête : {query_result}"
    else:
        return f"Résultat de la requête : {query_result.to_string()}"

# Initialisation de l'historique de la conversation
conversation_history = []

def update_conversation_history(role, message, conversation_history):
    """
    Ajoute un message à l'historique de la conversation.
    :param role: "user" ou "assistant"
    :param message: Le contenu du message
    :param conversation_history: La liste contenant l'historique de la conversation
    """
    conversation_history.append({"role": role, "content": message})

def chatbot(db_path: Path):
    conn = get_connection(str(db_path))
    
    # Chargement du modèle de dialogue
    model, tokenizer = load_dialogue_model()
    
    # Initialisation de l'historique de la conversation
    conversation_history = []

    # Boucle de conversation
    while True:
        user_input = input("Vous: ")
        if user_input.lower() == "exit":
            break
        
        # Exemple de question en langage naturel
        question = "Quels en-cas sans allergènes ont un Nutri-score A ?"

        # Conversion de la question en SQL
        sql_query = text_to_sql(question, model, tokenizer)
        print(f"Requête SQL générée : {sql_query}")

        # Exécution de la requête SQL
        query_result = execute_query(conn, sql_query)
        print(f"Résultat de la requête : {query_result}")
        
        # Génération de la réponse
        response = generate_response(query_result)
        print(f"Agent: {response}")

        # Ajout de la réponse du LLM à l'historique
        update_conversation_history("assistant", response, conversation_history)

def evaluate_system(db_path: Path):
    conn = get_connection(str(db_path))

    # Création du jeu de test
    test_questions = create_test_set()

    execution_accuracy = 0
    coverage_rate = 0
    response_time = 0
    
    for question in test_questions:
        start_time = time.time()
        
        # Conversion de la question en SQL
        sql_query = text_to_sql(question["question"])
        
        # Exécution de la requête SQL
        query_result = execute_query(conn, sql_query)
        
        # Génération de la réponse
        response = generate_response(query_result)
        
        end_time = time.time()
        response_time += end_time - start_time
        
        # Comparaison des résultats
        if query_result == question["expected_result"]:
            execution_accuracy += 1
        
        # Calcul du taux de couverture des données manquantes
        if isinstance(query_result, pd.DataFrame) and not query_result.empty:
            coverage_rate += 1
    
    execution_accuracy /= len(test_questions)
    coverage_rate /= len(test_questions)
    response_time /= len(test_questions)
    
    return execution_accuracy, coverage_rate, response_time



if __name__ == "__main__":
    # Exécution du chatbot
    chatbot(FILTERED_DB_PATH)
    
    # Évaluation du système
    # execution_accuracy, coverage_rate, response_time = evaluate_system(test_questions, conn)
    # print(f"Précision d'exécution: {execution_accuracy}")
    # print(f"Taux de couverture des données manquantes: {coverage_rate}")
    # print(f"Temps de réponse moyen: {response_time}")
    