
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
        raise ValueError("Invalid engine type.")

class PromptClassifierTool(Tool):
    name = "prompt_classifier"
    description = "Classifie et répond au prompt utilisateur."
    inputs = {
        "prompt": {
            "description": "Le prompt de l'utilisateur.",
            "type": "string"
        }
    }
    output_type = "string"

    def __init__(self, llm_engine: LiteLLMModel):
        self.llm_engine = llm_engine

    def forward(self, prompt: str) -> str:
        messages=[{
            "role": "system",
            "content": """Tu es un assistant qui répond naturellement aux utilisateurs.

Règles de réponse selon la catégorie du prompt:
- Si "salutation": Réponds poliment avec une salutation
- Si "SQL": Réponds "Je n'ai pas encore accès à la base de données."  
- Si "conversation": Réponds naturellement à la question

Important:
- Réponds toujours en français comme un humain le ferait
- Ne donne JAMAIS de code ou d'instructions techniques
- Garde un ton naturel et sympathique"""
        }, {
            "role": "user",  
            "content": prompt
        }]
        
        return self.llm_engine(messages)["content"]


# Initialisation du modèle
# Éventuellement, utiliser qwen2.5-coder:3b pour un modèle plus rapide
# Voir https://ollama.com/library/qwen2.5-coder:7b ou qwen2.5-coder:14b
# Dans les démo, on voit souvent "qwen2.5-coder-32B-Instruct"
llm_engine = create_llm_engine("ollama/qwen2.5-coder:3b")

prompt_classifier_tool = PromptClassifierTool(llm_engine)
classifier_agent = CodeAgent(
    tools=[prompt_classifier_tool],
    model=llm_engine,
    max_steps=1,
)

def classify_task():
    prompts = [
        "Bonjour", 
        "SELECT * FROM products",
        "Comment faire une tarte aux pommes?"
    ]
    for prompt in prompts:
        response = classifier_agent.run(prompt)
        print(f"Prompt: {prompt}\nClassification: {response}\n")

if __name__ == "__main__":
    classify_task()
