
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import json
from pathlib import Path
from typing import Dict, Any
import os
from smolagents import (
    CodeAgent, ManagedAgent,
    Tool, tool, ToolCallingAgent, 
    DuckDuckGoSearchTool,
    LiteLLMModel, 
)

import re



# Configuration
os.environ['LITELLM_LOG'] = 'INFO'

DATA_DIR = Path("../data")
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"
DATA_DICT_PATH = DATA_DIR / "data_dictionary.json"

def create_llm_engine(type_engine: str, api_key: str = None):
    # See https://huggingface.co/blog/florentgbelidji/alpine-agent for more details
    if type_engine == "Qwen/Qwen2.5-Coder-32B-Instruct":
        return None
    elif type_engine == "openai/gpt-4o" and api_key:
        llm_engine = LiteLLMModel(model_id="openai/gpt-4o", api_key=api_key)
        return llm_engine
    elif type_engine == "ollama/qwen2.5-coder:3b":
        llm_engine = LiteLLMModel(
            model_id="ollama/qwen2.5-coder:3b",
            api_base="http://localhost:11434",
            temperature=0.1,
            max_tokens=8096)
        return llm_engine
    else:
        raise ValueError("Invalid engine type. Please choose either 'Qwen/Qwen2.5-Coder-32B-Instruct' or 'ollama/qwen2.5-coder:3b'.")

def task_classifier(prompt: str, llm_engine: LiteLLMModel) -> str:
    """
    Classify the user prompt into one of the following categories: "salutation", "conversation", or "SQL".
    
    Args:
        prompt (str): The user prompt to classify.
        llm_engine (Union[HfApiModel, LiteLLMModel]): The language model to use.
    Returns:
        str: The category of the user_prompt. 
    """
    messages=[
           {
            "role": "system",
            "content": """You're an expert at categorizing a user prompt.
            Your task is to classify the user prompt into one of the following categories: "salutation", "conversation", or "SQL". 
            """
        }, 
        {
            "role": "user",
            "content": prompt,
        }
    ]

    summary = llm_engine(messages)
    return summary["content"]

class PromptClassifierTool(Tool):
    name = "prompt_classifier"
    description = "Classify the user prompt into one of the following categories: 'salutation', 'conversation', or 'SQL'."
    inputs = {
        "prompt": {
            "description": "The user prompt to classify.",
            "type": "string"
        }
    }
    output_type = "string"

    def __init__(self, llm_engine: LiteLLMModel):
        self.llm_engine = llm_engine

    def forward(self, prompt: str) -> str:
        category = task_classifier(prompt, self.llm_engine)
        return {
            "category": category
        }


# Initialisation du modèle
# Éventuellement, utiliser qwen2.5-coder:3b pour un modèle plus rapide
# Voir https://ollama.com/library/qwen2.5-coder:7b ou qwen2.5-coder:14b
# Dans les démo, on voit souvent "qwen2.5-coder-32B-Instruct"
llm_engine = create_llm_engine("ollama/qwen2.5-coder:3b")

prompt_classifier_tool = PromptClassifierTool(llm_engine)
classifier_agent = CodeAgent(
    tools=[prompt_classifier_tool],
    model=llm_engine,
    max_steps=3,
)

additionnal_notes = """
Instructions de classification :
- Ton unique tâche est de classifier le prompt de l'utilisateur dans UNE SEULE de ces trois catégories :
    * "salutation" : pour les formules de politesse comme bonjour, au revoir, merci
    * "conversation" : pour les questions générales ou discussions
    * "SQL" : pour les requêtes contenant du code SQL (commençant souvent par SELECT, INSERT, UPDATE, DELETE)

Règles importantes :
1. Tu dois répondre UNIQUEMENT avec un de ces trois mots : "salutation", "conversation" ou "SQL"  
2. Ne fournis aucune explication ou texte supplémentaire
3. Chaque prompt doit être classé dans une seule catégorie
4. Si un prompt contient du SQL mélangé à de la conversation, priorise la catégorie "SQL"

Exemples de classification :
- "Bonjour" -> "salutation"
- "SELECT * FROM table" -> "SQL"
- "Comment faire X?" -> "conversation"
"""

def classify_task() -> None:
    prompt = "Bonjour"
    prompt = "SELECT * FROM products"
    prompt = "Comment faire une tarte aux pommes?"


    response = classifier_agent.run(
        prompt,
        additional_args={
            "additional_notes": additionnal_notes
        }
    )
    print(f"Classification de la tâche: {response}")

if __name__ == "__main__":
    classify_task()
