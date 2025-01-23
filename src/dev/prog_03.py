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
    try:
        json_pattern = r'\{[^{}]*\}'
        match = re.search(json_pattern, text)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    return {"type": "unknown_query"}

def classify_question(question):
    try:
        prompt = f"""Analyze this question and respond with ONLY a JSON object (no other text).
        Question: "{question}"
        
        Classify the question into one of these types:
        1. age_query: Questions about age (with comparison and value)
        2. city_query: Questions about cities (with city name)
        3. name_query: Questions about specific names
        4. count_query: Questions about counting or statistics
        5. multi_criteria: Questions combining multiple criteria
        
        Return JSON format based on type:
        
        For age_query:
        {{"type": "age_query", "comparison": "gt/lt/eq/gte/lte", "value": number}}
        
        For city_query:
        {{"type": "city_query", "city": "city_name"}}
        
        For name_query:
        {{"type": "name_query", "name": "person_name"}}
        
        For count_query:
        {{"type": "count_query", "group_by": "age/city/none"}}
        
        For multi_criteria:
        {{"type": "multi_criteria", "criteria": [
            {{"field": "age/city/name", "comparison": "gt/lt/eq/gte/lte", "value": value}},
            {{"field": "age/city/name", "comparison": "gt/lt/eq/gte/lte", "value": value}}
        ]}}
        
        Examples:
        "Who are people older than 30?"
        {{"type": "age_query", "comparison": "gt", "value": 30}}
        
        "Who lives in New York?"
        {{"type": "city_query", "city": "New York"}}
        
        "Is there someone named Alice?"
        {{"type": "name_query", "name": "Alice"}}
        
        "How many people are there in each city?"
        {{"type": "count_query", "group_by": "city"}}
        
        "Who is older than 25 and lives in San Francisco?"
        {{"type": "multi_criteria", "criteria": [
            {{"field": "age", "comparison": "gt", "value": 25}},
            {{"field": "city", "comparison": "eq", "value": "San Francisco"}}
        ]}}"""

        response = ollama.chat(model='mistral:7b', messages=[{
            'role': 'user',
            'content': prompt
        }])
        
        response_text = response['message']['content'].strip()
        print(f"Raw response: {response_text}")
        return extract_json_from_text(response_text)

    except Exception as e:
        print(f"Error classifying question: {e}")
        return {"type": "unknown_query"}

def generate_query(question_info):
    if question_info["type"] == "age_query":
        comparison = question_info.get("comparison")
        value = question_info.get("value")
        comparison_operators = {
            "gt": "$gt", "lt": "$lt", "eq": "$eq",
            "gte": "$gte", "lte": "$lte"
        }
        mongo_operator = comparison_operators.get(comparison)
        if mongo_operator:
            return {"age": {mongo_operator: value}}

    elif question_info["type"] == "city_query":
        city = question_info.get("city")
        if city:
            return {"city": city}

    elif question_info["type"] == "name_query":
        name = question_info.get("name")
        if name:
            return {"name": name}

    elif question_info["type"] == "count_query":
        # La requête réelle sera gérée différemment dans execute_query
        return {"group_by": question_info.get("group_by")}

    elif question_info["type"] == "multi_criteria":
        criteria = question_info.get("criteria", [])
        query = {"$and": []}
        for criterion in criteria:
            field = criterion.get("field")
            comparison = criterion.get("comparison")
            value = criterion.get("value")
            
            if comparison == "eq":
                query["$and"].append({field: value})
            else:
                mongo_operator = {
                    "gt": "$gt", "lt": "$lt",
                    "gte": "$gte", "lte": "$lte"
                }.get(comparison)
                if mongo_operator:
                    query["$and"].append({field: {mongo_operator: value}})
        
        return query

    return {}

def execute_query(query, question_info):
    if question_info["type"] == "count_query":
        group_by = query.get("group_by")
        if group_by == "city":
            pipeline = [
                {"$group": {"_id": "$city", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            return list(collection.aggregate(pipeline))
        elif group_by == "age":
            pipeline = [
                {"$group": {"_id": "$age", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            return list(collection.aggregate(pipeline))
        else:
            return [{"count": collection.count_documents({})}]
    else:
        return list(collection.find(query))

def generate_response(results, question_info):
    if not results:
        return "No records found matching your query."

    if question_info["type"] == "count_query":
        group_by = question_info.get("group_by")
        if group_by in ["city", "age"]:
            response = f"Count by {group_by}:\n"
            for result in results:
                response += f"{result['_id']}: {result['count']} people\n"
        else:
            response = f"Total count: {results[0]['count']} people"
    else:
        response = f"Found {len(results)} records:\n"
        for record in results:
            if isinstance(record, dict) and "name" in record:
                response += f"Name: {record.get('name')}, Age: {record.get('age')}, City: {record.get('city')}\n"
    
    return response

def main():
    try:
        # Exemples de questions à tester :
        questions = [
            "Who are the people older than 30?",
            "Who lives in San Francisco?",
            "Is there someone named Alice?",
            "How many people are there in each city?",
            "Who is older than 25 and lives in San Francisco?"
        ]

        for question in questions:
            print(f"\nQuestion: {question}")
            print("Classifying question...")
            question_info = classify_question(question)
            print(f"Question classified as: {question_info}")
            
            query = generate_query(question_info)
            print(f"Generated query: {query}")
            
            results = execute_query(query, question_info)
            response = generate_response(results, question_info)
            print(response)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()