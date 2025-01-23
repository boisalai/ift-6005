from pymongo import MongoClient
from ollama import Client
import json
import re

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['test_db']
collection = db['test_collection']

# Initialiser Ollama
ollama = Client(host='http://localhost:11434')

def extract_json_from_text(text):
    """Extrait la première structure JSON valide trouvée dans le texte."""
    try:
        # Cherche un pattern qui ressemble à du JSON entre accolades
        json_pattern = r'\{[^{}]*\}'
        match = re.search(json_pattern, text)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    return {"type": "general_query"}

def classify_question(question):
    try:
        prompt = f"""Analyze this question and respond with ONLY a JSON object (no other text):
        Question: {question}
        
        Return a JSON with:
        - type: 'age_query' or 'general_query'
        - comparison: 'gt', 'lt', 'eq', 'gte', 'lte' (if age query)
        - value: numeric value (if age query)
        
        Example responses:
        {{"type": "age_query", "comparison": "gt", "value": 30}}
        {{"type": "age_query", "comparison": "lt", "value": 25}}
        {{"type": "age_query", "comparison": "eq", "value": 35}}"""
        
        response = ollama.chat(model='mistral:7b', messages=[{
            'role': 'user',
            'content': prompt
        }])
        
        response_text = response['message']['content'].strip()
        print(f"Raw response: {response_text}")  # Debug
        
        # Extraire et parser le JSON
        classification = extract_json_from_text(response_text)
        print(f"Parsed classification: {classification}")  # Debug
        return classification
        
    except Exception as e:
        print(f"Error classifying question: {e}")
        return {"type": "general_query"}

def generate_query(question_info):
    if question_info["type"] == "age_query":
        comparison = question_info.get("comparison")
        value = question_info.get("value")
        
        comparison_operators = {
            "gt": "$gt",
            "lt": "$lt",
            "eq": "$eq",
            "gte": "$gte",
            "lte": "$lte"
        }
        
        mongo_operator = comparison_operators.get(comparison)
        if mongo_operator:
            query = {"age": {mongo_operator: value}}
            print(f"Generated MongoDB query: {query}")  # Debug
        else:
            query = {}
    else:
        query = {}
    
    return query

def generate_response(results):
    if not results:
        return "No records found matching your query."
    
    response = f"Found {len(results)} records:\n"
    for record in results:
        response += f"Name: {record.get('name')}, Age: {record.get('age')}, City: {record.get('city')}\n"
    return response

def main():
    try:
        question = "Who are the people older than 30?"
        
        print("Classifying question...")
        question_info = classify_question(question)
        print(f"Question classified as: {question_info}")
        
        query = generate_query(question_info)
        results = list(collection.find(query))
        
        response = generate_response(results)
        print(response)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()