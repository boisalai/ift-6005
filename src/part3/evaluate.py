
"""
evaluate.py: Système d'évaluation comparative entre agent DuckDB et agent Neo4j

Ce script évalue les performances de deux agents conversationnels différents,
l'un utilisant DuckDB et l'autre Neo4j, pour répondre à des questions
sur des produits alimentaires d'Open Food Facts.

Le script:
1. Charge des paires questions-réponses depuis un fichier JSON
2. Interroge les deux agents avec les mêmes questions
3. Évalue la précision des réponses
4. Mesure les temps d'exécution
5. Produit un rapport comparatif détaillé

Ce script est structuré pour isoler les fonctionnalités nécessaires sans
dépendre des modules existants dans 'src/part1/' et 'src/part2/'.

Utilisation:
    python evaluate.py [--limit N] [--lang LANG] [--model MODEL]

Options:
    --limit N     Limite l'évaluation aux N premières questions (défaut: toutes)
    --lang LANG   Langue d'évaluation: 'fr' ou 'en' (défaut: 'fr')
    --model MODEL Spécifie le modèle à utiliser: 'claude' ou 'openchat'... (défaut: 'claude')
"""

import os
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import statistics

import duckdb
from neo4j import GraphDatabase
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from smolagents import (
    CodeAgent,
    Tool,
    LiteLLMModel,
)

# Chargement des variables d'environnement
load_dotenv()

# Configuration des chemins
DATA_DIR = Path("../../data")
QA_PAIRS_PATH = DATA_DIR / "qa_pairs.json"
DUCKDB_PATH = DATA_DIR / "food_canada.duckdb"

absolute_path = DATA_DIR.resolve()
print(f"Chemin relatif: {DATA_DIR}")
print(f"Chemin absolu: {absolute_path}")

# Configuration de Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Configuration du modèle
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Configuration des logs
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = log_dir / f"evaluation_comparison_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(str(log_path), encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("comparison_eval")

@dataclass
class EvaluationResult:
    """Stocke les résultats d'évaluation pour une question."""
    question_id: int
    question: str
    expected_answer: str
    agent_answer: str
    is_correct: bool
    response_time: float
    error: Optional[str] = None

@dataclass
class AgentPerformance:
    """Agrège les résultats de performance pour un agent."""
    agent_type: str
    results: List[EvaluationResult] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Pourcentage de questions répondues correctement."""
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.is_correct) / len(self.results) * 100
    
    @property
    def failure_rate(self) -> float:
        """Pourcentage de questions où l'agent n'a pas pu répondre."""
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.error is not None) / len(self.results) * 100
    
    @property
    def avg_response_time(self) -> float:
        """Temps de réponse moyen en secondes."""
        if not self.results:
            return 0.0
        return statistics.mean(r.response_time for r in self.results)
    
    @property
    def median_response_time(self) -> float:
        """Temps de réponse médian en secondes."""
        if not self.results:
            return 0.0
        return statistics.median(r.response_time for r in self.results)


class DuckDBQueryTool(Tool):
    """Outil pour exécuter des requêtes SQL sur DuckDB."""
    name = "query_db"
    description = """
    Exécute des requêtes SQL sur la base de données DuckDB Open Food Facts.
    La base contient une seule table 'products' avec les informations sur les produits alimentaires.
    
    RÈGLES IMPORTANTES:
    1. TOUJOURS inclure une clause LIMIT dans vos requêtes (maximum 100 lignes)
    2. JAMAIS utiliser de clauses de modification (INSERT, UPDATE, DELETE, ALTER, etc.)
    3. Pour les champs multilingues, utiliser list_filter() pour sélectionner la langue
    4. Pour les tableaux, utiliser list_contains() pour les correspondances exactes
    5. Gérer les valeurs NULL avec COALESCE()
    6. Utiliser LOWER() pour les recherches insensibles à la casse
    
    FORMAT DE LA RÉPONSE:
    Les résultats sont retournés au format JSON avec la structure suivante:
    {
        "columns": ["col1", "col2", ...],     // Noms des colonnes
        "rows": [                             // Valeurs des lignes (max 10)
            ["val1", "val2", ...],            // Chaque valeur convertie en chaîne
            ...
        ],
        "row_count": 42,                      // Nombre total de résultats
        "error": "message d'erreur"           // Présent uniquement en cas d'erreur
    }
    """
    
    inputs = {
        "query": {"type": "string", "description": "Requête SQL valide pour DuckDB"}
    }
    output_type = "string"
    
    def __init__(self, db_path: Path):
        super().__init__()
        self.db_path = db_path
        self.connection = duckdb.connect(str(db_path))
    
    def forward(self, query: str) -> str:
        """Exécute une requête SQL et retourne les résultats."""
        try:
            result = self.connection.sql(query)
            rows = result.fetchall()
            
            # Formater la sortie
            output = {
                "columns": result.columns,
                "rows": [tuple(str(item) for item in row) for row in rows[:10]],
                "row_count": len(rows),
            }
            return json.dumps(output)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def __del__(self):
        """Ferme la connexion à la base de données."""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()


class Neo4jQueryTool(Tool):
    """Outil pour exécuter des requêtes Cypher sur Neo4j."""
    name = "execute_cypher_query"
    description = """
    Exécute des requêtes Cypher sur la base de données Neo4j Open Food Facts.
    
    SCHÉMA DE LA BASE DE DONNÉES:
    - Nœuds:
      - Product: Produits alimentaires (propriétés: code, name, generic_name, etc.)
      - Brand: Marques (propriété: name)
      - Category: Catégories (propriété: name)
      - Ingredient: Ingrédients (propriété: name)
      - Allergen: Allergènes (propriété: name)
      - Nutriment: Nutriments (propriété: name)
      - Label: Labels (propriété: name)
    
    - Relations:
      - (Product)-[:HAS_BRAND]->(Brand)
      - (Product)-[:HAS_CATEGORY]->(Category)
      - (Product)-[:CONTAINS]->(Ingredient)
      - (Product)-[:CONTAINS_ALLERGEN]->(Allergen)
      - (Product)-[:HAS_NUTRIMENT]->(Nutriment) avec propriétés: value, unit
      - (Product)-[:HAS_LABEL]->(Label)
    
    RÈGLES IMPORTANTES:
    1. TOUJOURS limiter les résultats avec LIMIT (maximum 100)
    2. Utiliser MATCH pour les requêtes (pas de CREATE, DELETE, etc.)
    3. Utiliser WHERE pour filtrer et affiner les résultats
    
    FORMAT DE LA RÉPONSE:
    Les résultats sont retournés au format JSON avec la structure suivante:
    [
        {"field1": "value1", "field2": "value2", ...},
        {"field1": "value1", "field2": "value2", ...},
        ...
    ]
    """

    inputs = {
        "query": {"type": "string", "description": "Requête Cypher valide"},
        "params": {
            "type": "object", 
            "description": "Paramètres de la requête (optionnel)", 
            "nullable": True
        }
    }
    output_type = "string"
    
    def __init__(self, uri: str, user: str, password: str):
        super().__init__()
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def forward(self, query: str, params: Dict = None) -> str:
        """Exécute une requête Cypher et retourne les résultats."""
        if params is None:
            params = {}
            
        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                records = [record.data() for record in result]
                return json.dumps(records, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def __del__(self):
        """Ferme la connexion à la base de données."""
        if hasattr(self, 'driver') and self.driver:
            self.driver.close()


class EmbeddingTool(Tool):
    """Outil pour générer des embeddings vectoriels."""
    name = "create_embedding"
    description = """
    Génère un embedding vectoriel pour un texte donné.
    Cet outil est utilisé pour la recherche vectorielle dans Neo4j.
    
    L'embedding est un vecteur numérique qui représente le sens sémantique du texte.
    """
    
    inputs = {
        "text": {"type": "string", "description": "Texte à convertir en embedding"}
    }
    output_type = "string"
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        super().__init__()
        self.model = SentenceTransformer(model_name)
    
    def forward(self, text: str) -> str:
        """Génère un embedding et le retourne comme JSON."""
        try:
            embedding = self.model.encode(text)
            return json.dumps(embedding.tolist())
        except Exception as e:
            return json.dumps({"error": str(e)})


def create_duckdb_agent(model: LiteLLMModel) -> CodeAgent:
    """Crée un agent pour interroger DuckDB."""
    query_tool = DuckDBQueryTool(db_path=DUCKDB_PATH)
    
    agent = CodeAgent(
        tools=[query_tool],
        model=model,
        additional_authorized_imports=["json"],
    )
    
    return agent


def create_neo4j_agent(model: LiteLLMModel) -> CodeAgent:
    """Crée un agent pour interroger Neo4j."""
    query_tool = Neo4jQueryTool(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD
    )
    embedding_tool = EmbeddingTool()
    
    agent = CodeAgent(
        tools=[query_tool, embedding_tool],
        model=model,
        additional_authorized_imports=["json"],
    )
    
    return agent


def load_qa_pairs(qa_path: Path, lang: str = "fr", limit: Optional[int] = None) -> List[Dict]:
    """
    Charge les paires questions-réponses depuis un fichier JSON.
    
    Args:
        qa_path: Chemin vers le fichier JSON
        lang: Langue des questions-réponses ('fr' ou 'en')
        limit: Nombre maximum de paires à charger
        
    Returns:
        Liste de dictionnaires contenant les paires questions-réponses
    """
    if not qa_path.exists():
        logger.error(f"Fichier de paires QA introuvable: {qa_path}")
        return []
    
    try:
        with open(qa_path, 'r', encoding='utf-8') as f:
            qa_pairs = json.load(f)
        
        # Filtrer les paires qui ont des questions et réponses dans la langue spécifiée
        valid_pairs = [
            pair for pair in qa_pairs 
            if "questions" in pair and lang in pair["questions"] 
            and "answers" in pair and lang in pair["answers"]
        ]
        
        # Limiter le nombre de paires si demandé
        if limit is not None and limit > 0:
            valid_pairs = valid_pairs[:limit]
        
        logger.info(f"Chargement de {len(valid_pairs)} paires QA en {lang}")
        return valid_pairs
    
    except Exception as e:
        logger.error(f"Erreur lors du chargement des paires QA: {e}")
        return []


def evaluate_agent_response(expected: str, actual: str, model: LiteLLMModel) -> bool:
    """
    Évalue si la réponse de l'agent est correcte en utilisant le LLM.
    
    Args:
        expected: Réponse attendue
        actual: Réponse de l'agent
        model: Modèle LLM pour l'évaluation
        
    Returns:
        True si la réponse est considérée comme correcte, False sinon
    """
    evaluator = CodeAgent(model=model, tools=[])
    
    prompt = f"""
    Compare ces deux réponses et détermine si la Réponse B contient l'information 
    factuelle principale de la Réponse A, même si la formulation est différente.

    Réponse A (référence): {expected}
    
    Réponse B (à évaluer): {actual}
    
    Réponds par exactement un mot: 'oui' si les informations clés sont présentes 
    et factuellement correctes, ou 'non' si des informations essentielles sont 
    manquantes ou incorrectes.
    """
    
    evaluation = evaluator.run(prompt)
    logger.debug(f"Évaluation: {evaluation}")
    
    # Analyse de la réponse
    evaluation = evaluation.lower().strip()
    is_correct = 'oui' in evaluation or 'correct' in evaluation or 'equivalent' in evaluation
    
    return is_correct


def evaluate_agent(
    agent: CodeAgent,
    qa_pairs: List[Dict],
    agent_type: str,
    lang: str,
    model: LiteLLMModel
) -> AgentPerformance:
    """
    Évalue les performances d'un agent sur un ensemble de paires questions-réponses.
    
    Args:
        agent: Agent à évaluer
        qa_pairs: Liste des paires questions-réponses
        agent_type: Type d'agent ('duckdb' ou 'neo4j')
        lang: Langue d'évaluation ('fr' ou 'en')
        model: Modèle LLM pour l'évaluation
        
    Returns:
        Objet AgentPerformance contenant les résultats
    """
    performance = AgentPerformance(agent_type=agent_type)
    
    # Préparer les instructions spécifiques pour chaque agent
    if agent_type == "duckdb":
        instructions = """
        Tu es un assistant spécialisé dans l'interrogation de la base de données DuckDB 
        Open Food Facts. Ta mission est de répondre aux questions sur les produits alimentaires
        en utilisant l'outil query_db pour exécuter des requêtes SQL.
        
        Règles importantes:
        1. Limite-toi aux informations présentes dans la base de données
        2. Ne génère pas d'informations sans source
        3. Réponds dans la même langue que la question
        4. Garde ta réponse concise et factuelle
        5. N'inclus pas les requêtes SQL dans ta réponse
        6. Utilise uniquement les données de la base DuckDB (pas de recherche web)
        """
    else:  # neo4j
        instructions = """
        Tu es un assistant spécialisé dans l'interrogation de la base de données Neo4j
        Open Food Facts. Ta mission est de répondre aux questions sur les produits alimentaires
        en utilisant l'outil execute_cypher_query pour exécuter des requêtes Cypher.
        
        Règles importantes:
        1. Limite-toi aux informations présentes dans la base de données
        2. Ne génère pas d'informations sans source
        3. Réponds dans la même langue que la question
        4. Garde ta réponse concise et factuelle
        5. N'inclus pas les requêtes Cypher dans ta réponse
        6. Utilise uniquement les données de la base Neo4j (pas de recherche web)
        """
    
    # Évaluer chaque paire question-réponse
    for idx, qa_pair in enumerate(qa_pairs, 1):
        question = qa_pair["questions"][lang]
        expected_answer = qa_pair["answers"][lang]
        
        logger.info(f"Évaluation [{agent_type}] - Question {idx}/{len(qa_pairs)}")
        logger.info(f"Question: {question}")
        
        try:
            # Mesurer le temps de réponse
            start_time = time.time()
            agent_response = agent.run(
                question,
                additional_args={"additional_notes": instructions}
            )
            response_time = time.time() - start_time
            
            logger.info(f"Temps de réponse: {response_time:.2f}s")
            logger.info(f"Réponse de l'agent: {agent_response}")
            
            # Évaluer la réponse
            is_correct = evaluate_agent_response(expected_answer, agent_response, model)
            
            # Enregistrer le résultat
            result = EvaluationResult(
                question_id=idx,
                question=question,
                expected_answer=expected_answer,
                agent_answer=agent_response,
                is_correct=is_correct,
                response_time=response_time
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation: {e}")
            
            # Enregistrer l'erreur
            result = EvaluationResult(
                question_id=idx,
                question=question,
                expected_answer=expected_answer,
                agent_answer="",
                is_correct=False,
                response_time=0.0,
                error=str(e)
            )
        
        performance.results.append(result)
        logger.info(f"Résultat: {'Correct' if result.is_correct else 'Incorrect'}")
        logger.info("-" * 50)
    
    return performance


def generate_report(duckdb_perf: AgentPerformance, neo4j_perf: AgentPerformance, output_path: Optional[Path] = None) -> str:
    """
    Génère un rapport comparatif détaillé des performances.
    
    Args:
        duckdb_perf: Performances de l'agent DuckDB
        neo4j_perf: Performances de l'agent Neo4j
        output_path: Chemin où sauvegarder le rapport (optionnel)
        
    Returns:
        Texte du rapport
    """
    # Calculer les statistiques
    duckdb_success = duckdb_perf.success_rate
    neo4j_success = neo4j_perf.success_rate
    
    duckdb_failure = duckdb_perf.failure_rate
    neo4j_failure = neo4j_perf.failure_rate
    
    duckdb_time = duckdb_perf.avg_response_time
    neo4j_time = neo4j_perf.avg_response_time
    
    # Générer le rapport
    report = f"""
    ======================================================
    RAPPORT D'ÉVALUATION COMPARATIVE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ======================================================
    
    RÉSUMÉ:
    - Nombre de questions évaluées: {len(duckdb_perf.results)}
    
    TAUX DE RÉUSSITE:
    - Agent DuckDB: {duckdb_success:.2f}%
    - Agent Neo4j: {neo4j_success:.2f}%
    - Différence: {abs(duckdb_success - neo4j_success):.2f}% {'(DuckDB supérieur)' if duckdb_success > neo4j_success else '(Neo4j supérieur)'}
    
    TAUX D'ÉCHEC:
    - Agent DuckDB: {duckdb_failure:.2f}%
    - Agent Neo4j: {neo4j_failure:.2f}%
    
    TEMPS DE RÉPONSE:
    - Agent DuckDB: {duckdb_time:.2f}s (moyenne), {statistics.median([r.response_time for r in duckdb_perf.results if r.response_time > 0]):.2f}s (médiane)
    - Agent Neo4j: {neo4j_time:.2f}s (moyenne), {statistics.median([r.response_time for r in neo4j_perf.results if r.response_time > 0]):.2f}s (médiane)
    - Ratio: {duckdb_time/neo4j_time if neo4j_time > 0 else 'N/A':.2f}x {'(DuckDB plus lent)' if duckdb_time > neo4j_time else '(Neo4j plus lent)'}
    
    ======================================================
    DÉTAILS PAR QUESTION
    ======================================================
    """
    
    # Ajouter les détails pour chaque question
    for i in range(len(duckdb_perf.results)):
        duckdb_result = duckdb_perf.results[i]
        neo4j_result = neo4j_perf.results[i] if i < len(neo4j_perf.results) else None
        
        report += f"""
    Question {duckdb_result.question_id}: {duckdb_result.question[:100]}{'...' if len(duckdb_result.question) > 100 else ''}
    
    DuckDB:
    - Correct: {'Oui' if duckdb_result.is_correct else 'Non'}
    - Temps: {duckdb_result.response_time:.2f}s
    - Erreur: {duckdb_result.error if duckdb_result.error else 'Aucune'}
    
    Neo4j:
    - Correct: {'Oui' if neo4j_result and neo4j_result.is_correct else 'Non'}
    - emps: {f"{neo4j_result.response_time:.2f}s" if neo4j_result else 'N/A'}
    - Erreur: {neo4j_result.error if neo4j_result and neo4j_result.error else 'Aucune'}
    
    ------------------------------------------------------
    """
    
    # Sauvegarder le rapport si demandé
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    return report


def visualize_results(duckdb_perf: AgentPerformance, neo4j_perf: AgentPerformance, output_path: Optional[Path] = None):
    """
    Génère des visualisations pour comparer les performances.
    Nécessite matplotlib et seaborn.
    
    Args:
        duckdb_perf: Performances de l'agent DuckDB
        neo4j_perf: Performances de l'agent Neo4j
        output_path: Chemin où sauvegarder les visualisations (optionnel)
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        
        sns.set(style="whitegrid")
        
        # Créer le répertoire de sortie si nécessaire
        if output_path:
            output_path.mkdir(exist_ok=True, parents=True)
        
        # 1. Taux de réussite
        plt.figure(figsize=(10, 6))
        agents = ["DuckDB", "Neo4j"]
        success_rates = [duckdb_perf.success_rate, neo4j_perf.success_rate]
        failure_rates = [duckdb_perf.failure_rate, neo4j_perf.failure_rate]
        
        x = np.arange(len(agents))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width/2, success_rates, width, label='Taux de réussite')
        ax.bar(x + width/2, failure_rates, width, label='Taux d\'échec')
        
        ax.set_xlabel('Agent')
        ax.set_ylabel('Pourcentage (%)')
        ax.set_title('Taux de réussite et d\'échec par agent')
        ax.set_xticks(x)
        ax.set_xticklabels(agents)
        ax.legend()
        
        plt.tight_layout()
        if output_path:
            plt.savefig(output_path / "success_rates.png", dpi=300)
        
        # 2. Temps de réponse
        plt.figure(figsize=(10, 6))
        
        # Filtrer les temps de réponse valides
        duckdb_times = [r.response_time for r in duckdb_perf.results if r.response_time > 0]
        neo4j_times = [r.response_time for r in neo4j_perf.results if r.response_time > 0]
        
        sns.boxplot(data=[duckdb_times, neo4j_times], orient="h")
        plt.yticks([0, 1], ["DuckDB", "Neo4j"])
        plt.xlabel('Temps de réponse (secondes)')
        plt.title('Distribution des temps de réponse')
        
        plt.tight_layout()
        if output_path:
            plt.savefig(output_path / "response_times.png", dpi=300)
        
        # 3. Comparaison question par question
        plt.figure(figsize=(12, 8))
        
        # Créer des données pour la comparaison
        question_ids = []
        duckdb_correct = []
        neo4j_correct = []
        
        for i, duckdb_result in enumerate(duckdb_perf.results):
            if i < len(neo4j_perf.results):
                neo4j_result = neo4j_perf.results[i]
                
                question_ids.append(duckdb_result.question_id)
                duckdb_correct.append(1 if duckdb_result.is_correct else 0)
                neo4j_correct.append(1 if neo4j_result.is_correct else 0)
        
        width = 0.35
        x = np.arange(len(question_ids))
        
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.bar(x - width/2, duckdb_correct, width, label='DuckDB')
        ax.bar(x + width/2, neo4j_correct, width, label='Neo4j')
        
        ax.set_ylabel('Correct (1) / Incorrect (0)')
        ax.set_title('Comparaison des réponses par question')
        ax.set_xticks(x)
        ax.set_xticklabels([f"Q{qid}" for qid in question_ids], rotation=45)
        ax.legend()
        
        plt.tight_layout()
        if output_path:
            plt.savefig(output_path / "question_comparison.png", dpi=300)
        
        plt.close('all')
    
    except ImportError:
        logger.warning("Matplotlib et/ou seaborn non disponibles. Pas de visualisations générées.")


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Évaluation comparative des agents DuckDB et Neo4j")
    
    parser.add_argument("--limit", type=int, default=None, 
                        help="Nombre maximum de questions à évaluer")
    
    parser.add_argument("--lang", type=str, choices=["fr", "en"], default="fr",
                        help="Langue d'évaluation (fr ou en)")
    
    parser.add_argument("--model", type=str, choices=["claude", "openchat", "mistral-openorca", "openhermes"], 
                        default="claude", help="Modèle LLM à utiliser")
    
    parser.add_argument("--output", type=str, default=None,
                        help="Chemin où enregistrer les résultats")
    
    
    return parser.parse_args()


def main():
    """Fonction principale."""
    # Analyser les arguments
    args = parse_arguments()
    logger.info(f"Arguments: {args}")

    # Configurer le modèle
    if args.model == "claude":
        model = LiteLLMModel(model_id="anthropic/claude-3-5-haiku-20241022")
        # Cost $0.80/$4.00 MTok. See https://docs.anthropic.com/en/docs/about-claude/models/all-models
    elif args.model == "openchat":
        model = LiteLLMModel(model_id="ollama/openchat:latest", api_base="http://localhost:11434", num_ctx=8192)
    elif args.model == "mistral-openorca":
        model = LiteLLMModel(model_id="ollama/mistral-openorca:latest", api_base="http://localhost:11434", num_ctx=8192)
    elif args.model == "openhermes":
        model = LiteLLMModel(model_id="ollama/openhermes:7b-v2.5", api_base="http://localhost:11434", num_ctx=8192)
    else:
        model = LiteLLMModel(model_id="anthropic/claude-3-5-haiku-20241022")
    logger.info("Modèle configuré avec succès")
    
    # Charger les paires questions-réponses
    qa_pairs = load_qa_pairs(QA_PAIRS_PATH, lang=args.lang, limit=args.limit)
    
    if not qa_pairs:
        logger.error("Aucune paire question-réponse chargée. Arrêt.")
        return
    
    # Créer les agents
    logger.info("Création de l'agent DuckDB...")
    duckdb_agent = create_duckdb_agent(model)
    
    logger.info("Création de l'agent Neo4j...")
    neo4j_agent = create_neo4j_agent(model)
    
    # Évaluer les agents
    logger.info("Démarrage de l'évaluation de l'agent DuckDB...")
    duckdb_perf = evaluate_agent(
        agent=duckdb_agent,
        qa_pairs=qa_pairs,
        agent_type="duckdb",
        lang=args.lang,
        model=model
    )
    
    logger.info("Démarrage de l'évaluation de l'agent Neo4j...")
    neo4j_perf = evaluate_agent(
        agent=neo4j_agent,
        qa_pairs=qa_pairs,
        agent_type="neo4j",
        lang=args.lang,
        model=model
    )
    
    # Générer le rapport
    logger.info("Génération du rapport comparatif...")
    report = generate_report(duckdb_perf, neo4j_perf)
    print(report)
    
    # Sauvegarder le rapport si demandé
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Rapport sauvegardé dans {output_path}")
    
    # Générer des visualisations si possible
    try:
        vis_dir = Path("visualizations")
        visualize_results(duckdb_perf, neo4j_perf, vis_dir)
        logger.info(f"Visualisations générées dans {vis_dir}")
    except Exception as e:
        logger.warning(f"Impossible de générer les visualisations: {e}")
        
    logger.info("Évaluation terminée.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERREUR FATALE: {e}")
        logger.error(f"ERREUR FATALE: {e}", exc_info=True)