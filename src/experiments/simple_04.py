import warnings

warnings.filterwarnings("ignore", category=UserWarning)

import json
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

import os
from smolagents import (
    CodeAgent,
    ManagedAgent,
    Tool,
    tool,
    ToolCallingAgent,
    DuckDuckGoSearchTool,
    LiteLLMModel,
)

load_dotenv()


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
        llm_engine = LiteLLMModel(model_id="openai/gpt-4o")
        return llm_engine
    elif type_engine == "anthropic/claude-3-5-sonnet-latest":
        llm_engine = LiteLLMModel(
            model_id="anthropic/claude-3-5-sonnet-latest",
            temperature=0.2,
            max_tokens=2048) # Max 4096.
        return llm_engine
    elif type_engine == "ollama/qwen2.5-coder:3b":
        llm_engine = LiteLLMModel(
            model_id="ollama/qwen2.5-coder:3b",
            api_base="http://localhost:11434",
            temperature=0.2,
            max_tokens=8096)
        return llm_engine
    elif type_engine == "ollama/deepseek-r1:latest":
        llm_engine = LiteLLMModel(
            model_id="ollama/deepseek-r1:latest",
            api_base="http://localhost:11434",
            temperature=0.1,
            max_tokens=8096)
        return llm_engine
    else:
        raise ValueError("Invalid engine type.")

class PromptClassifierTool(Tool):
    name = "prompt_classifier"
    description = "Répond aux questions utilisateur de façon naturelle."
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
            "content": """Tu es un assistant conversationnel. Voici les règles à suivre:

1. Pour une salutation ("Bonjour", etc.):
   Réponds simplement "Bonjour! Comment puis-je vous aider?"

2. Pour une requête SQL:
   Réponds "Désolé, je n'ai pas encore accès à la base de données."

3. Pour une question conversation:
   Réponds naturellement à la question, sans code ni format technique

IMPORTANT:
- Réponds UNIQUEMENT avec du texte, pas de code
- Pas de "Thought:", "Answer:" ou autres marqueurs
- Pas de blocs de code ou formatting"""
        }, {
            "role": "user",  
            "content": prompt
        }]
        
        response = self.llm_engine(messages)
        # Extrait uniquement le texte de la réponse
        return response["content"].strip()



# Initialisation du modèle
# Éventuellement, utiliser qwen2.5-coder:3b pour un modèle plus rapide
# Voir https://ollama.com/library/qwen2.5-coder:7b ou qwen2.5-coder:14b
# Dans les démo, on voit souvent "qwen2.5-coder-32B-Instruct"
llm_engine = create_llm_engine("anthropic/claude-3-5-sonnet-latest")

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
    # classify_task()
    agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=llm_engine)
    agent.run("How many seconds would it take for a leopard at full speed to run through Pont des Arts?")

# https://github.com/huggingface/smolagents/blob/main/docs/source/en/guided_tour.md#talk-with-your-agent-and-visualize-its-thoughts-in-a-cool-gradio-interface

