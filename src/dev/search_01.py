import warnings

warnings.filterwarnings("ignore", category=UserWarning)

from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Union


import os
from smolagents import (
    ToolCallingAgent,
    DuckDuckGoSearchTool,
    LiteLLMModel,
    HfApiModel
)

load_dotenv()

os.environ['LITELLM_LOG'] = 'INFO'

DATA_DIR = Path("../data")
FILTERED_DB_PATH = DATA_DIR / "food_canada.duckdb"
DATA_DICT_PATH = DATA_DIR / "data_dictionary.json"

def create_llm_engine(type_engine: str, api_key: str = None) -> Union[HfApiModel, LiteLLMModel]:
    configs = {
        "Qwen/Qwen2.5-Coder-32B-Instruct": {
            "class": HfApiModel,
            "params": {"model_id": os.environ["HUGGINGFACE_ENDPOINT_ID_QWEN"]}
        },
        "meta-llama/Llama-3.3-70B-Instruct": {
            "class": HfApiModel, 
            "params": {"model_id": os.environ["HUGGINGFACE_ENDPOINT_ID_LLAMA"]}
        },
        "openai/gpt-4o": {
            "class": LiteLLMModel,
            "params": {"model_id": "openai/gpt-4o"}
        },
        "anthropic/claude-3-5-sonnet-latest": {
            "class": LiteLLMModel,
            "params": {
                "model_id": "anthropic/claude-3-5-sonnet-latest",
                "temperature": 0.2,
                "max_tokens": 2048
            }
        },
        "ollama/qwen2.5-coder:3b": {
            "class": LiteLLMModel,
            "params": {
                "model_id": "ollama/qwen2.5-coder:3b",
                "api_base": "http://localhost:11434",
                "temperature": 0.2,
                "max_tokens": 8096
            }
        },
        "ollama/deepseek-r1:latest": {
            "class": LiteLLMModel, 
            "params": {
                "model_id": "ollama/deepseek-r1:latest",
                "api_base": "http://localhost:11434",
                "temperature": 0.1,
                "max_tokens": 8096
            }
        }
    }

    if type_engine not in configs:
        raise ValueError(f"Invalid engine type. Choose from: {list(configs.keys())}")
   
    config = configs[type_engine]
    return config["class"](**config["params"])

model = create_llm_engine("anthropic/claude-3-5-sonnet-latest")

class FoodGuideSearchTool(DuckDuckGoSearchTool):
    description = """Performs a web search in the Canadian Food Guide website based on your query."""
    
    def forward(self, query: str) -> str:
        en_results = self.ddgs.text("site:https://food-guide.canada.ca/en/ " + query, max_results=self.max_results)
        fr_results = self.ddgs.text("site:https://guide-alimentaire.canada.ca/fr/ " + query, max_results=self.max_results)
        results = en_results + fr_results

        if len(results) == 0:
            raise Exception("No results found! Try a less restrictive/shorter query.")
        postprocessed_results = [f"[{result['title']}]({result['href']})\n{result['body']}" for result in results]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)


if __name__ == "__main__":
    web_search_tool = FoodGuideSearchTool()
    agent = ToolCallingAgent(tools=[web_search_tool], model=model, max_steps=3)
    agent.run("Quelles sont les qualités nutritives des pommes?")


