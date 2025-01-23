from pymongo import MongoClient
from ollama import Client

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['test_db']
collection = db['test_collection']

# Initialiser Ollama
ollama = Client(host='http://localhost:11434')

def classify_question(question):
    try:
        # Utiliser Ollama pour classifier la question
        prompt = f"""Classify the following question as either 'age_query' or 'general_query': 
        Question: {question}
        Return ONLY 'age_query' or 'general_query' without any additional text."""
        response = ollama.chat(model='mistral:7b', messages=[{
            'role': 'user',
            'content': prompt
        }])
        return response['message']['content'].strip()
    except Exception as e:
        print(f"Error classifying question: {e}")
        return "general_query"

def generate_query(question_info):
    # Générer une requête MongoDB basée sur la classification
    if question_info == "age_query":
        query = {"age": {"$gt": 30}}
    else:
        query = {}
    return query

def generate_response(results):
    # Générer une réponse basée sur les résultats de la requête
    if not results:
        return "No records found matching your query."
    
    response = f"Found {len(results)} records:\n"
    for record in results:
        response += f"Name: {record.get('name')}, Age: {record.get('age')}, City: {record.get('city')}\n"
    return response

def main():
    try:
        question = "Who are the people older than 30?"
        
        # Classifier la question
        print("Classifying question...")
        question_info = classify_question(question)
        print(f"Question classified as: {question_info}")
        
        # Générer et exécuter la requête MongoDB
        query = generate_query(question_info)
        results = list(collection.find(query))
        
        # Générer la réponse
        response = generate_response(results)
        
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()