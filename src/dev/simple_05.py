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

@tool 
def search_food_guide(query: str) -> str:
   """Effectue une recherche uniquement dans le Guide alimentaire canadien.
   
   Args:
       query: La recherche à effectuer, limitée au Guide alimentaire canadien
   """
   from duckduckgo_search import ddg
   results = ddg(f"site:guide-alimentaire.canada.ca {query}", max_results=3)
   return "\n".join(r['title'] + ': ' + r['link'] for r in results)


# Initialisation du modèle
# Éventuellement, utiliser qwen2.5-coder:3b pour un modèle plus rapide
# Voir https://ollama.com/library/qwen2.5-coder:7b ou qwen2.5-coder:14b
# Dans les démo, on voit souvent "qwen2.5-coder-32B-Instruct"
model = create_llm_engine("anthropic/claude-3-5-sonnet-latest")

class WebSearchTool(Tool):
    name = "web_search"
    description = """Performs a duckduckgo web search based on your query (think a Google search) seulement dans le site du guide alimentaire canadien then returns the top search results."""
    inputs = {"query": {"type": "string", "description": "The search query to perform."}}
    output_type = "string"

    def __init__(self, max_results=10, **kwargs):
        super().__init__()
        self.max_results = max_results
        try:
            from duckduckgo_search import DDGS
        except ImportError as e:
            raise ImportError(
                "You must install package `duckduckgo_search` to run this tool: for instance run `pip install duckduckgo-search`."
            ) from e
        self.ddgs = DDGS(**kwargs)

    def forward(self, query: str) -> str:
        results = self.ddgs.text("site:https://guide-alimentaire.canada.ca/fr/ " + query, max_results=self.max_results)
        if len(results) == 0:
            raise Exception("No results found! Try a less restrictive/shorter query.")
        postprocessed_results = [f"[{result['title']}]({result['href']})\n{result['body']}" for result in results]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)


class FoodGuideSearchTool(DuckDuckGoSearchTool):
    description = """Performs a web search in the Canadian Food Guide website based on your query."""
    
    def forward(self, query: str) -> str:
        results = self.ddgs.text("site:https://guide-alimentaire.canada.ca/fr/ " + query, max_results=self.max_results)
        if len(results) == 0:
            raise Exception("No results found! Try a less restrictive/shorter query.")
        postprocessed_results = [f"[{result['title']}]({result['href']})\n{result['body']}" for result in results]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)


prompt_classifier_tool = PromptClassifierTool(model)
classifier_agent = CodeAgent(
    tools=[prompt_classifier_tool],
    model=model,
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
    # agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=llm_engine)
    web_search_tool = FoodGuideSearchTool()
    agent = ToolCallingAgent(tools=[web_search_tool], model=model, max_steps=3)
    agent.run("Quelles sont les qualités nutritives des pommes?")

# https://github.com/huggingface/smolagents/blob/main/docs/source/en/guided_tour.md#talk-with-your-agent-and-visualize-its-thoughts-in-a-cool-gradio-interface

