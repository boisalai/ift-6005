
"""
evaluate.py: Système d'évaluation comparative entre agent DuckDB et agent NetworkX

Ce script évalue les performances de deux agents conversationnels différents,
l'un utilisant DuckDB et l'autre NetworkX, pour répondre à des questions
sur des produits alimentaires d'Open Food Facts.

Le script:
1. Charge des paires questions-réponses depuis un fichier JSON
2. Interroge les deux agents avec les mêmes questions
3. Évalue la précision des réponses
4. Mesure les temps d'exécution
5. Produit un rapport comparatif détaillé

Ce script est structuré pour isoler les fonctionnalités nécessaires sans
dépendre des modules existants dans 'src/part1/' et 'src/part2/'.

Important:pip list 
- Dans le rapport, il est important d'indiquer que j'ai limité le nombre d'étapes des agents à 5 (max_steps=5).

Utilisation:
    python evaluate.py [--limit N] [--lang LANG] [--model MODEL]
    python evaluate.py --limit 10 --lang fr --model openchat

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
import time
import random
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import statistics

from tabulate import tabulate
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from nltk.translate.bleu_score import sentence_bleu
from rouge import Rouge

import duckdb

import networkx as nx
import pickle
import numpy as np

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
GRAPH_PATH = DATA_DIR / "graphs" / "food_graph_parquet_20250405_164654.pkl"

absolute_path = DATA_DIR.resolve()
print(f"Chemin relatif: {DATA_DIR}")
print(f"Chemin absolu: {absolute_path}")

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
        
        failure_count = 0
        for r in self.results:
            if r.error is not None and not r.error.startswith("Score:"):
                failure_count += 1
            elif r.agent_answer:
                # Vérifier que agent_answer est bien une chaîne de caractères
                if isinstance(r.agent_answer, str) and ("Désolé" in r.agent_answer or "Sorry" in r.agent_answer):
                    failure_count += 1
        
        return (failure_count / len(self.results)) * 100
    
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


class NetworkXQueryTool(Tool):
    """Outil pour exécuter des requêtes sur un graphe NetworkX."""
    name = "execute_graph_query"
    description = """
    Exécute des requêtes sur la base de données NetworkX Open Food Facts.
    
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
    
    OPÉRATIONS SUPPORTÉES:
    1. Rechercher des produits par attributs
    2. Rechercher des produits par relations
    3. Rechercher des produits similaires (embedding)
    4. Obtenir des informations détaillées sur un produit
    
    FORMAT DE LA REQUÊTE:
    {
        "operation": "search_products",  # Ou "get_product", "search_similar", "search_by_relation"
        "filters": {  # Filtres optionnels pour la recherche
            "property_name": "valeur",
            ...
        },
        "relation_type": "HAS_BRAND",  # Pour search_by_relation
        "relation_target": "Marque", # Pour search_by_relation
        "product_id": "12345",  # Pour get_product
        "query_text": "produit sans gluten",  # Pour search_similar
        "limit": 10  # Nombre max de résultats
    }
    
    FORMAT DE LA RÉPONSE:
    Liste de produits au format JSON.
    """

    inputs = {
        "query": {"type": "string", "description": "Requête au format JSON décrivant l'opération"}
    }
    output_type = "string"
    
    def __init__(self, graph_path: Path):
        super().__init__()
        self.graph_path = graph_path
        
        # Initialiser le modèle SentenceTransformer avec des options
        try:
            logger.info("Initialisation du modèle SentenceTransformer...")
            self.model = SentenceTransformer("all-MiniLM-L6-v2", device='cpu')  # Forcer CPU pour compatibilité
            logger.info("Modèle SentenceTransformer initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du modèle: {e}")
            # Mode de secours: utiliser une classe mock simplifiée pour les embeddings
            class MockEmbedder:
                def encode(self, text):
                    import numpy as np
                    # Renvoyer un vecteur de zéros de dimension standard
                    return np.zeros(384)  # 384 est la dimension de all-MiniLM-L6-v2
            
            self.model = MockEmbedder()
            logger.warning("Mode de secours activé pour les embeddings (vecteurs zéro)")
        
        # Cache pour les embeddings
        self._embedding_cache = {}
        
        # Charger le graphe (sans l'argument max_retries)
        self.load_graph()
        # Exécuter le diagnostic
        self.diagnose_additif_queries()
    
    def load_graph(self):
        """Charge le graphe NetworkX depuis un fichier pickle."""
        try:
            with open(self.graph_path, 'rb') as f:
                self.graph = pickle.load(f)
            
            # Logs détaillés sur le graphe chargé
            logger.info(f"Graphe chargé depuis {self.graph_path}")
            logger.info(f"Nombre total de nœuds: {self.graph.number_of_nodes()}")
            logger.info(f"Nombre total d'arêtes: {self.graph.number_of_edges()}")
            
            # Compter les types de nœuds
            node_types = {}
            for _, data in self.graph.nodes(data=True):
                node_type = data.get('type', 'unknown')
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            logger.info(f"Répartition des nœuds par type: {node_types}")
            
            # Vérifier spécifiquement les nœuds d'additifs
            additifs_count = node_types.get('Additif', 0)
            logger.info(f"Nombre d'additifs dans le graphe: {additifs_count}")
            
            # Compter les types de relations
            edge_types = {}
            for _, _, data in self.graph.edges(data=True):
                edge_type = data.get('type', 'unknown')
                edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
            
            logger.info(f"Répartition des arêtes par type: {edge_types}")
            
            # Vérifier spécifiquement les relations avec des additifs
            additif_relations = edge_types.get('CONTAINS_ADDITIF', 0)
            logger.info(f"Nombre de relations CONTAINS_ADDITIF: {additif_relations}")
            
            # Échantillonner quelques nœuds d'additifs pour vérification
            if additifs_count > 0:
                additif_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Additif']
                sample_size = min(5, len(additif_nodes))
                sample_additifs = additif_nodes[:sample_size]
                
                logger.info(f"Échantillon d'additifs: {sample_additifs}")
                for additif in sample_additifs:
                    logger.info(f"Propriétés de l'additif {additif}: {dict(self.graph.nodes[additif])}")
                    
                    # Compter combien de produits contiennent cet additif
                    products_with_additif = [s for s, t, d in self.graph.in_edges(additif, data=True) 
                                            if d.get('type') == 'CONTAINS_ADDITIF']
                    logger.info(f"Nombre de produits contenant {additif}: {len(products_with_additif)}")
            
            # Vérifier les embeddings
            embedding_count = sum(1 for _, data in self.graph.nodes(data=True) if 'embedding' in data)
            logger.info(f"Nombre de nœuds avec embeddings: {embedding_count}")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du graphe: {e}")
            self.graph = nx.MultiDiGraph()  # Créer un graphe vide en cas d'erreur
    
    def diagnose_additif_queries(self):
        """Diagnostique la capacité à effectuer des requêtes sur les additifs."""
        logger.info("Diagnostic des requêtes sur les additifs:")
        
        # 1. Tester la recherche de produits par relation avec additifs
        try:
            query = {
                "operation": "search_by_relation",
                "relation_type": "CONTAINS_ADDITIF",
                "relation_target": "E",  # Additif commun (E-numbers)
                "limit": 5
            }
            
            result = json.loads(self._search_by_relation(query))
            if "error" in result:
                logger.error(f"Erreur lors de la recherche par relation: {result['error']}")
            else:
                logger.info(f"Réussite de la recherche par relation: {len(result)} produits trouvés")
                if len(result) > 0:
                    logger.info(f"Premier produit trouvé: {result[0]}")
        except Exception as e:
            logger.error(f"Exception lors de la recherche par relation: {e}")
        
        # 2. Tester la recherche de produits sans additifs
        try:
            # Trouver des produits qui n'ont pas de relation CONTAINS_ADDITIF
            products_without_additifs = []
            product_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Product']
            
            for i, product in enumerate(product_nodes[:100]):  # Limiter à 100 produits pour l'efficacité
                has_additif = False
                for _, target, data in self.graph.out_edges(product, data=True):
                    if data.get('type') == 'CONTAINS_ADDITIF':
                        has_additif = True
                        break
                
                if not has_additif:
                    products_without_additifs.append(product)
                    if len(products_without_additifs) >= 5:
                        break
            
            logger.info(f"Nombre de produits sans additifs trouvés: {len(products_without_additifs)}")
            if products_without_additifs:
                logger.info(f"Échantillon de produits sans additifs: {products_without_additifs[:3]}")
        except Exception as e:
            logger.error(f"Exception lors de la recherche de produits sans additifs: {e}")

    def forward(self, query: str) -> str:
        """Exécute une requête sur le graphe NetworkX avec meilleure gestion d'erreurs."""
        try:
            # Analyser la requête JSON
            query_params = json.loads(query)
            operation = query_params.get("operation", "")
            
            # Journaliser la requête pour le débogage
            logger.info(f"Exécution de l'opération: {operation} avec paramètres: {query_params}")
            
            # Exécuter l'opération correspondante
            if operation == "search_products":
                return self._search_products(query_params)
            elif operation == "get_product":
                return self._get_product(query_params)
            elif operation == "search_similar":
                return self._search_similar(query_params)
            elif operation == "search_by_relation":
                return self._search_by_relation(query_params)
            elif operation == "count_nodes_by_type":
                return self._count_nodes_by_type(query_params)
            elif operation == "count_relations_by_type":
                return self._count_relations_by_type(query_params)
            elif operation == "count_additives_per_product":
                return self._count_additives_per_product(query_params)
            elif operation == "get_most_common_additives":
                return self._get_most_common_additives(query_params)
            # Nouvelles opérations
            elif operation == "count_allergens_per_product":
                return self._count_allergens_per_product(query_params)
            elif operation == "get_most_common_allergens":
                return self._get_most_common_allergens(query_params)
            elif operation == "search_products_multi_criteria":
                return self._search_products_multi_criteria(query_params)
            else:
                logger.warning(f"Opération non supportée: {operation}")
                return json.dumps({
                    "error": f"Opération non supportée: {operation}",
                    "available_operations": [
                        "search_products", "get_product", "search_similar", "search_by_relation",
                        "count_nodes_by_type", "count_relations_by_type", 
                        "count_additives_per_product", "get_most_common_additives",
                        "count_allergens_per_product", "get_most_common_allergens",
                        "search_products_multi_criteria"
                    ]
                })
        
        except json.JSONDecodeError:
            logger.error(f"Erreur de décodage JSON: {query}")
            return json.dumps({"error": "Format JSON invalide pour la requête"})
        except Exception as e:
            logger.error(f"Exception lors de l'exécution de la requête: {e}", exc_info=True)
            return json.dumps({
                "error": str(e),
                "query": query,
                "debug_info": {
                    "exception_type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
            })
        
    def _search_products(self, params):
        """Recherche des produits selon des filtres."""
        filters = params.get("filters", {})
        limit = params.get("limit", 10)
        
        results = []
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get("type") == "Product":
                # Vérifier si le produit correspond à tous les filtres
                match = True
                for prop, value in filters.items():
                    if prop in node_data:
                        # Pour les recherches textuelles, utiliser une correspondance insensible à la casse
                        if isinstance(node_data[prop], str) and isinstance(value, str):
                            if value.lower() not in node_data[prop].lower():
                                match = False
                                break
                        # Pour les autres types, utiliser une correspondance exacte
                        elif node_data[prop] != value:
                            match = False
                            break
                    else:
                        match = False
                        break
                
                if match:
                    results.append(self._format_product(node_id, node_data))
                    
                    if len(results) >= limit:
                        break
        
        return json.dumps(results)
    
    def _search_products_multi_criteria(self, params):
        """Recherche des produits selon plusieurs critères combinés."""
        filters = params.get("filters", {})
        relations = params.get("relations", [])  # Liste de dictionnaires {type, target}
        limit = params.get("limit", 10)
        
        # D'abord, filtrer par critères simples
        candidate_products = []
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get("type") == "Product":
                # Vérifier tous les filtres directs
                match = True
                for prop, value in filters.items():
                    if prop in node_data:
                        if isinstance(node_data[prop], str) and isinstance(value, str):
                            if value.lower() not in node_data[prop].lower():
                                match = False
                                break
                        elif node_data[prop] != value:
                            match = False
                            break
                    else:
                        match = False
                        break
                
                if match:
                    candidate_products.append(node_id)
        
        # Ensuite, filtrer par relations
        if relations:
            filtered_products = []
            for product_id in candidate_products:
                all_relations_match = True
                
                for relation in relations:
                    relation_type = relation.get("type")
                    relation_target = relation.get("target")
                    
                    relation_found = False
                    for _, target, edge_data in self.graph.out_edges(product_id, data=True):
                        if edge_data.get("type") == relation_type:
                            target_name = self.graph.nodes[target].get("name", "")
                            if relation_target.lower() in target_name.lower():
                                relation_found = True
                                break
                    
                    if not relation_found:
                        all_relations_match = False
                        break
                
                if all_relations_match:
                    filtered_products.append(product_id)
            
            candidate_products = filtered_products
        
        # Formater les résultats
        results = []
        for product_id in candidate_products[:limit]:
            node_data = self.graph.nodes[product_id]
            results.append(self._format_product(product_id, node_data))
        
        return json.dumps(results)

    def _get_product(self, params):
        """Récupère les informations complètes d'un produit."""
        product_id = params.get("product_id", "")
        node_id = f"Product-{product_id}"
        
        if not self.graph.has_node(node_id):
            return json.dumps({"error": f"Produit avec ID {product_id} non trouvé."})
        
        # Récupérer les propriétés du produit
        product_info = dict(self.graph.nodes[node_id])
        product_info["relations"] = {}
        
        # Récupérer toutes les relations sortantes
        for _, target, edge_data in self.graph.out_edges(node_id, data=True):
            relation_type = edge_data.get("type", "unknown")
            target_type = self.graph.nodes[target].get("type", "")
            target_name = self.graph.nodes[target].get("name", "")
            
            # Ajouter cette relation au dictionnaire des relations
            if relation_type not in product_info["relations"]:
                product_info["relations"][relation_type] = []
            
            relation_info = {
                "type": target_type,
                "name": target_name
            }
            
            # Ajouter les propriétés de la relation
            for key, value in edge_data.items():
                if key != "type":
                    relation_info[key] = value
            
            product_info["relations"][relation_type].append(relation_info)
        
        return json.dumps(product_info)
    
    def _search_similar(self, params):
        """Recherche des produits similaires à partir d'une requête textuelle."""
        query_text = params.get("query_text", "")
        limit = params.get("limit", 5)
        
        if not query_text:
            return json.dumps({"error": "La requête textuelle est vide."})
        
        # Générer l'embedding pour la requête
        query_embedding = self._create_embedding(query_text)
        
        if not query_embedding:
            return json.dumps({"error": "Impossible de générer l'embedding pour la requête."})
        
        # Convertir en numpy array pour les calculs de similarité
        query_embedding_np = np.array(query_embedding)
        
        # Parcourir tous les nœuds produits et calculer la similarité
        similarities = []
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get('type') == 'Product' and 'embedding' in node_data:
                product_embedding = np.array(node_data['embedding'])
                
                # Calculer la similarité cosinus
                norm_q = np.linalg.norm(query_embedding_np)
                norm_p = np.linalg.norm(product_embedding)
                
                if norm_q > 0 and norm_p > 0:
                    similarity = np.dot(query_embedding_np, product_embedding) / (norm_q * norm_p)
                    
                    # Stocker le résultat avec l'identifiant du produit
                    similarities.append({
                        'id': node_id,
                        'code': node_data.get('code', ''),
                        'name': node_data.get('name', 'Nom inconnu'),
                        'generic_name': node_data.get('generic_name', ''),
                        'nutriscore_grade': node_data.get('nutriscore_grade', ''),
                        'score': float(similarity)
                    })
        
        # Trier les résultats par score et limiter le nombre
        similarities.sort(key=lambda x: x['score'], reverse=True)
        return json.dumps(similarities[:limit])

    def _search_by_relation(self, params):
        """
        Recherche des produits ayant une relation spécifique de manière optimisée.
        
        Args:
            params (dict): Paramètres de recherche incluant:
                - relation_type: Type de relation (ex: "CONTAINS_ADDITIF")
                - relation_target: Cible de la relation (ex: "E330")
                - limit: Nombre maximum de résultats à retourner
                - case_sensitive: Si True, la recherche est sensible à la casse
                - exact_match: Si True, recherche des correspondances exactes uniquement
                
        Returns:
            str: Résultats au format JSON
        """
        relation_type = params.get("relation_type", "")
        relation_target = params.get("relation_target", "")
        limit = params.get("limit", 10)
        
        # Paramètres optionnels pour affiner la recherche
        case_sensitive = params.get("case_sensitive", False)
        exact_match = params.get("exact_match", False)
        include_relations = params.get("include_relations", False)
        
        logger.info(f"Recherche par relation: type={relation_type}, cible={relation_target}, limite={limit}")
        
        if not relation_type or not relation_target:
            logger.warning("Le type de relation et la cible sont requis.")
            return json.dumps({"error": "Le type de relation et la cible sont requis."})
        
        results = []
        edges_checked = 0
        matches_found = 0
        
        # Déterminer les types de nœuds à rechercher selon le type de relation
        node_types_to_check = []
        if relation_type == "CONTAINS_ADDITIF":
            node_types_to_check = ["Additif"]
        elif relation_type == "HAS_BRAND":
            node_types_to_check = ["Brand"]
        elif relation_type == "HAS_CATEGORY":
            node_types_to_check = ["Category"]
        elif relation_type == "CONTAINS":
            node_types_to_check = ["Ingredient"]
        elif relation_type == "HAS_LABEL":
            node_types_to_check = ["Label"]
        elif relation_type == "CONTAINS_ALLERGEN":
            node_types_to_check = ["Allergen"]
        elif relation_type == "SOLD_IN":
            node_types_to_check = ["Country"]
        elif relation_type == "HAS_NUTRIMENT":
            node_types_to_check = ["Nutriment"]
        else:
            # Recherche plus générique si le type de relation n'est pas reconnu
            node_types_to_check = ["Additif", "Brand", "Category", "Ingredient", "Label", "Allergen", "Country", "Nutriment"]
        
        # Optimisation: trouver d'abord les nœuds cibles potentiels
        target_nodes = []
        for node_id, node_data in self.graph.nodes(data=True):
            edges_checked += 1
            if node_data.get("type") in node_types_to_check:
                node_name = node_data.get("name", "")
                
                # Vérifier les correspondances selon les options
                match_found = False
                
                if exact_match:
                    # Correspondance exacte
                    if case_sensitive:
                        match_found = (node_name == relation_target)
                    else:
                        match_found = (node_name.lower() == relation_target.lower())
                else:
                    # Correspondance partielle
                    if case_sensitive:
                        match_found = (relation_target in node_name)
                    else:
                        match_found = (relation_target.lower() in node_name.lower())
                
                # Vérifier les traductions si aucune correspondance directe n'est trouvée
                if not match_found:
                    # Vérifier les traductions en français
                    if "translations_fr" in node_data:
                        for translation in node_data["translations_fr"]:
                            if exact_match:
                                if case_sensitive:
                                    if translation == relation_target:
                                        match_found = True
                                        break
                                else:
                                    if translation.lower() == relation_target.lower():
                                        match_found = True
                                        break
                            else:
                                if case_sensitive:
                                    if relation_target in translation:
                                        match_found = True
                                        break
                                else:
                                    if relation_target.lower() in translation.lower():
                                        match_found = True
                                        break
                    
                    # Vérifier les traductions en anglais
                    if not match_found and "translations_en" in node_data:
                        for translation in node_data["translations_en"]:
                            if exact_match:
                                if case_sensitive:
                                    if translation == relation_target:
                                        match_found = True
                                        break
                                else:
                                    if translation.lower() == relation_target.lower():
                                        match_found = True
                                        break
                            else:
                                if case_sensitive:
                                    if relation_target in translation:
                                        match_found = True
                                        break
                                else:
                                    if relation_target.lower() in translation.lower():
                                        match_found = True
                                        break
                
                # Ajouter aux nœuds cibles si correspondance
                if match_found:
                    target_nodes.append(node_id)
        
        logger.info(f"Nombre de nœuds cibles potentiels trouvés: {len(target_nodes)}")
        
        # Cas spécial: s'il n'y a pas de nœuds cibles mais que c'est une recherche pour "sans additifs"
        if len(target_nodes) == 0 and relation_type == "CONTAINS_ADDITIF" and relation_target.lower() in ["no", "none", "sans", "0"]:
            # Stratégie spéciale pour trouver les produits sans additifs
            logger.info("Recherche spéciale: produits sans additifs")
            for node_id, node_data in self.graph.nodes(data=True):
                if node_data.get("type") == "Product":
                    # Vérifier d'abord la propriété has_additives qui est peut-être définie
                    has_additives_flag = node_data.get("has_additives")
                    
                    # Si le flag existe et est False, c'est un produit sans additifs
                    if has_additives_flag is False:
                        matches_found += 1
                        results.append(self._format_product(node_id, node_data, include_relations))
                        if len(results) >= limit:
                            break
                    # Sinon, vérifier les relations comme avant
                    elif has_additives_flag is None:  # Si le flag n'est pas défini
                        has_additif = False
                        for _, _, edge_data in self.graph.out_edges(node_id, data=True):
                            if edge_data.get("type") == "CONTAINS_ADDITIF":
                                has_additif = True
                                break
                        
                        if not has_additif:
                            matches_found += 1
                            results.append(self._format_product(node_id, node_data, include_relations))
                            if len(results) >= limit:
                                break
        else:
            # Maintenant, trouver les produits liés à ces nœuds cibles
            for target_node in target_nodes:
                for source, _, edge_data in self.graph.in_edges(target_node, data=True):
                    edges_checked += 1
                    if (source.startswith("Product-") and edge_data.get("type") == relation_type):
                        matches_found += 1
                        node_data = self.graph.nodes[source]
                        results.append(self._format_product(source, node_data, include_relations))
                        
                        if len(results) >= limit:
                            break
                
                if len(results) >= limit:
                    break
        
        # Ajouter des méta-données utiles à la réponse
        response = {
            "products": results,
            "count": len(results),
            "total_matches_found": matches_found,
            "edges_checked": edges_checked,
            "query": {
                "relation_type": relation_type,
                "relation_target": relation_target,
                "limit": limit
            }
        }
        
        logger.info(f"Recherche terminée: {edges_checked} arêtes vérifiées, {matches_found} correspondances trouvées")
        return json.dumps(response)
    
    def _format_product(self, node_id, node_data, include_relations=False):
        """Formate les données d'un produit avec options avancées."""
        result = {
            "id": node_id,
            "code": node_data.get("code", ""),
            "name": node_data.get("name", "Nom inconnu"),
            "generic_name": node_data.get("generic_name", ""),
            "nutriscore_grade": node_data.get("nutriscore_grade", ""),
            "nova_group": node_data.get("nova_group", ""),
            "ecoscore_grade": node_data.get("ecoscore_grade", "")
        }
        
        # Optionnellement inclure les relations directes
        if include_relations:
            result["relations"] = {}
            
            # Récupérer les relations les plus importantes
            for relation_type in ["HAS_BRAND", "HAS_CATEGORY", "CONTAINS", "CONTAINS_ALLERGEN", "CONTAINS_ADDITIF"]:
                relations = []
                for _, target, edge_data in self.graph.out_edges(node_id, data=True):
                    if edge_data.get("type") == relation_type:
                        target_name = self.graph.nodes[target].get("name", "")
                        if target_name:
                            relations.append(target_name)
                
                if relations:
                    result["relations"][relation_type] = relations
        
        return result
    
    def _count_nodes_by_type(self, params):
        """Compte les nœuds par type."""
        node_type = params.get("node_type", "")
        
        counts = {}
        for _, data in self.graph.nodes(data=True):
            type_val = data.get('type', 'unknown')
            if not node_type or type_val == node_type:
                counts[type_val] = counts.get(type_val, 0) + 1
        
        return json.dumps(counts)

    def _count_relations_by_type(self, params):
        """Compte les relations par type."""
        counts = {}
        for _, _, data in self.graph.edges(data=True):
            type_val = data.get('type', 'unknown')
            counts[type_val] = counts.get(type_val, 0) + 1
        
        return json.dumps(counts)

    def _count_additives_per_product(self, params):
        """Calcule la distribution du nombre d'additifs par produit en tenant compte de has_additives."""
        limit = params.get("limit", 100000)
        
        # Compter les additifs pour chaque produit
        product_additives = {}
        products_checked = 0
        products_with_additives_info = 0  # Compteur pour les produits avec info sur additifs
        
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get("type") == "Product":
                products_checked += 1
                if products_checked > limit:
                    break
                    
                # Vérifier d'abord la propriété has_additives
                has_additives_flag = node_data.get("has_additives")
                
                if has_additives_flag is not None:  # Si l'information est explicitement disponible
                    products_with_additives_info += 1
                    
                    # Si has_additives est False, on sait que le produit n'a pas d'additifs
                    if has_additives_flag is False:
                        product_additives[node_id] = 0
                    else:
                        # Compter les relations CONTAINS_ADDITIF
                        additives_count = 0
                        for _, _, edge_data in self.graph.out_edges(node_id, data=True):
                            if edge_data.get("type") == "CONTAINS_ADDITIF":
                                additives_count += 1
                        
                        product_additives[node_id] = additives_count
                else:
                    # Méthode originale: compter par relations seulement si has_additives n'est pas défini
                    additives_count = 0
                    has_additives_info = False  
                    
                    for _, _, edge_data in self.graph.out_edges(node_id, data=True):
                        if edge_data.get("type") == "CONTAINS_ADDITIF":
                            additives_count += 1
                            has_additives_info = True
                    
                    if has_additives_info:
                        products_with_additives_info += 1
                        product_additives[node_id] = additives_count
        
        # Calculer la distribution uniquement sur les produits avec info d'additifs
        distribution = {}
        for count in product_additives.values():
            distribution[count] = distribution.get(count, 0) + 1
        
        # Trier les résultats pour une meilleure lisibilité
        sorted_distribution = {str(k): distribution[k] for k in sorted(distribution.keys())}
        
        # Nombre de produits avec additifs connus
        products_with_info = len(product_additives)
        products_without_additives = sum(1 for c in product_additives.values() if c == 0)
        
        result = {
            "total_products": products_checked,
            "products_with_additives_info": products_with_additives_info,
            "distribution": sorted_distribution,
            "products_with_additives": sum(1 for c in product_additives.values() if c > 0),
            "products_without_additives": products_without_additives,
            "max_additives": max(product_additives.values()) if product_additives else 0,
            "percentage_without_additives": round(products_without_additives / products_with_info * 100, 2) if products_with_info else 0
        }
        
        return json.dumps(result)

    def _get_most_common_additives(self, params):
        """Obtient les additifs les plus courants."""
        limit = params.get("limit", 10)
        
        # Compter combien de produits contiennent chaque additif
        additif_counts = {}
        
        for source, target, edge_data in self.graph.edges(data=True):
            if edge_data.get("type") == "CONTAINS_ADDITIF" and source.startswith("Product-"):
                additif_node = target
                if additif_node in self.graph.nodes:
                    additif_name = self.graph.nodes[additif_node].get("name", additif_node)
                    additif_counts[additif_name] = additif_counts.get(additif_name, 0) + 1
        
        # Trier les additifs par popularité
        sorted_additives = sorted(additif_counts.items(), key=lambda x: x[1], reverse=True)
        top_additives = sorted_additives[:limit]
        
        result = {
            "most_common_additives": [{"name": name, "count": count} for name, count in top_additives],
            "total_unique_additives": len(additif_counts)
        }
        
        return json.dumps(result)

    def _count_allergens_per_product(self, params):
        """Calcule la distribution du nombre d'allergènes par produit."""
        limit = params.get("limit", 100000)
        
        # Compter les allergènes pour chaque produit
        product_allergens = {}
        products_checked = 0
        
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get("type") == "Product":
                products_checked += 1
                if products_checked > limit:
                    break
                    
                # Compter les relations CONTAINS_ALLERGEN pour ce produit
                allergens_count = 0
                allergens_list = []
                for _, target, edge_data in self.graph.out_edges(node_id, data=True):
                    if edge_data.get("type") == "CONTAINS_ALLERGEN":
                        allergens_count += 1
                        target_name = self.graph.nodes[target].get("name", "")
                        allergens_list.append(target_name)
                
                if allergens_count > 0:
                    product_allergens[node_id] = {
                        "count": allergens_count,
                        "allergens": allergens_list,
                        "name": node_data.get("name", ""),
                        "code": node_data.get("code", "")
                    }
        
        # Trier par nombre d'allergènes décroissant
        sorted_products = sorted(product_allergens.items(), key=lambda x: x[1]["count"], reverse=True)
        
        return json.dumps({
            "products_with_allergens": len(product_allergens),
            "max_allergens": max([p[1]["count"] for p in sorted_products]) if sorted_products else 0,
            "top_products": [p[1] for p in sorted_products[:20]]  # Top 20 produits
        })

    def _get_most_common_allergens(self, params):
        """Obtient les allergènes les plus courants."""
        limit = params.get("limit", 10)
        
        allergen_counts = {}
        
        for source, target, edge_data in self.graph.edges(data=True):
            if edge_data.get("type") == "CONTAINS_ALLERGEN" and source.startswith("Product-"):
                allergen_node = target
                if allergen_node in self.graph.nodes:
                    allergen_name = self.graph.nodes[allergen_node].get("name", allergen_node)
                    allergen_counts[allergen_name] = allergen_counts.get(allergen_name, 0) + 1
        
        # Trier les allergènes par popularité
        sorted_allergens = sorted(allergen_counts.items(), key=lambda x: x[1], reverse=True)
        top_allergens = sorted_allergens[:limit]
        
        result = {
            "most_common_allergens": [{"name": name, "count": count} for name, count in top_allergens],
            "total_unique_allergens": len(allergen_counts)
        }
        
        return json.dumps(result)


    def _create_embedding(self, text):
        """Génère un embedding et le met en cache pour améliorer les performances."""
        # Utiliser un cache pour éviter de recalculer les embeddings
        if hasattr(self, '_embedding_cache'):
            if text in self._embedding_cache:
                return self._embedding_cache[text]
        else:
            # Initialiser le cache si nécessaire
            self._embedding_cache = {}
        
        try:
            if not text or text.strip() == "":
                return None
            
            if self.model is None:
                logger.warning("Tentative de création d'embedding mais le modèle n'est pas disponible")
                return None
                
            # Utiliser le modèle SentenceTransformer pour générer l'embedding
            embedding = self.model.encode(text)
            result = embedding.tolist()
            
            # Mettre en cache pour une utilisation future
            self._embedding_cache[text] = result
            
            # Limiter la taille du cache
            if len(self._embedding_cache) > 1000:
                # Supprimer l'élément le plus ancien
                self._embedding_cache.pop(next(iter(self._embedding_cache)))
                
            return result
        except Exception as e:
            logger.error(f"Erreur lors de la création d'embedding: {e}")
            return None
        


class EmbeddingTool(Tool):
    """Outil pour générer des embeddings vectoriels."""
    name = "create_embedding"
    description = """
    Génère un embedding vectoriel pour un texte donné.
    Cet outil est utilisé pour la recherche vectorielle dans NetworkX.
    
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
        max_steps=5,
    )
    
    return agent


def create_networkx_agent(model: LiteLLMModel) -> CodeAgent:
    """Crée un agent pour interroger le graphe NetworkX."""
    query_tool = NetworkXQueryTool(graph_path=GRAPH_PATH)
    embedding_tool = EmbeddingTool()
    
    agent = CodeAgent(
        tools=[query_tool, embedding_tool],
        model=model,
        additional_authorized_imports=["json"],
        max_steps=5,
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


def evaluate_agent_response_hybrid(expected: str, actual: str, model: LiteLLMModel, threshold: float = 0.5) -> dict:
    """
    Combine évaluation LLM et métriques automatiques pour une évaluation nuancée.
    
    Args:
        expected: Réponse attendue
        actual: Réponse de l'agent
        model: Modèle LLM pour l'évaluation
        threshold: Seuil pour considérer une réponse comme correcte (défaut: 0.5)
        
    Returns:
        Dictionnaire contenant les scores et l'évaluation
    """
    # 1. Calcul des métriques automatiques
    metrics = evaluate_agent_response_with_metrics(expected, actual)
    
    # 2. Évaluation par LLM
    evaluator = CodeAgent(model=model, tools=[])
    prompt = f"""
    Compare ces deux réponses et détermine si la Réponse B contient l'information 
    factuelle principale de la Réponse A, même si la formulation est différente.

    Réponse A (référence): {expected}
    
    Réponse B (à évaluer): {actual}
    
    Évalue la correspondance sur une échelle de 0 à 5, où:
    0 = Complètement incorrect ou non pertinent
    1 = Minimal, manque la plupart des informations clés
    2 = Partiellement correct, avec des omissions importantes
    3 = Majoritairement correct, avec quelques omissions mineures
    4 = Presque parfait, informations complètes avec formulation différente
    5 = Parfait, toutes les informations clés sont présentes et correctes
    
    Réponds uniquement par un chiffre entre 0 et 5.
    """
    
    llm_score_str = evaluator.run(prompt)
    
    # Extraire le score numérique
    try:
        # Convertir en chaîne d'abord, puis en float au cas où le modèle renvoie directement un entier
        llm_score_str = str(llm_score_str).strip()
        llm_score = float(llm_score_str)
        llm_normalized = llm_score / 5.0  # Normaliser entre 0 et 1
    except (ValueError, AttributeError):
        llm_normalized = 0.0
        
    # 3. Combiner les scores - AUGMENTER LE POIDS DU LLM
    combined_score = 0.0
    if "error" not in metrics:
        # Modifier ces pondérations pour donner plus d'importance au LLM
        # Avant: (metrics.get("rouge_l", 0) * 0.3) + (metrics.get("bleu_2", 0) * 0.2) + (llm_normalized * 0.5)
        # Après: Augmenter le poids du LLM à 0.7 ou 0.8
        combined_score = (metrics.get("rouge_l", 0) * 0.15) + (metrics.get("bleu_2", 0) * 0.15) + (llm_normalized * 0.7)
    else:
        combined_score = llm_normalized  # Utiliser seulement le score LLM si les métriques échouent
    
    # 4. Déterminer si la réponse est correcte selon un seuil
    is_correct = combined_score >= threshold
    
    return {
        "is_correct": is_correct,
        "combined_score": combined_score,
        "llm_score": llm_normalized,
        "llm_raw_score": llm_score if "llm_score" in locals() else None,
        "metrics": metrics
    }

def evaluate_agent_response_with_metrics(expected: str, actual: str) -> dict:
    """
    Évalue la réponse de l'agent en utilisant les métriques BLEU et ROUGE.
    
    Args:
        expected: Réponse attendue
        actual: Réponse de l'agent
        
    Returns:
        Dictionnaire contenant les scores BLEU et ROUGE
    """
    try:
        from nltk.translate.bleu_score import sentence_bleu
        from rouge import Rouge
        import nltk
        
        # S'assurer que les tokenizers NLTK sont disponibles
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        # Prétraitement des textes
        expected_tokens = expected.lower().split()
        actual_tokens = actual.lower().split()
        
        # Calcul du score BLEU
        # BLEU considère différentes longueurs de n-grammes (1, 2, 3, 4)
        weights_unigrams = (1, 0, 0, 0)  # Uniquement les unigrammes
        weights_bigrams = (0.5, 0.5, 0, 0)  # Unigrammes et bigrammes
        
        bleu_score_1 = sentence_bleu([expected_tokens], actual_tokens, weights=weights_unigrams)
        bleu_score_2 = sentence_bleu([expected_tokens], actual_tokens, weights=weights_bigrams)
        
        # Calcul des scores ROUGE
        rouge = Rouge()
        rouge_scores = rouge.get_scores(actual, expected)
        
        return {
            "bleu_1": bleu_score_1,
            "bleu_2": bleu_score_2,
            "rouge_1": rouge_scores[0]["rouge-1"]["f"],
            "rouge_2": rouge_scores[0]["rouge-2"]["f"],
            "rouge_l": rouge_scores[0]["rouge-l"]["f"]
        }
    except ImportError:
        print("Modules NLTK et/ou Rouge non installés. Exécutez: pip install nltk rouge")
        return {"error": "Modules requis non disponibles"}
    except Exception as e:
        print(f"Erreur lors du calcul des métriques: {e}")
        return {"error": str(e)}
    

def retry_with_exponential_backoff(func, max_retries=5, initial_delay=1, max_delay=60):
    """
    Exécute une fonction avec retry et backoff exponentiel en cas d'erreur de rate limit.
    
    Pour éviter une erreur de limite de débit (rate limit) lors de l'exécution du script 
    d'évaluation. Le message d'erreur indique que nous avons dépassé la limite de 
    40 000 tokens d'entrée par minute pour votre organisation Anthropic.
    """
    retries = 0
    delay = initial_delay
    
    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            if "rate_limit_error" in str(e) and retries < max_retries:
                # Ajouter un peu de jitter au délai
                sleep_time = delay * (1 + random.random() * 0.1)
                print(f"Rate limit atteint, attente de {sleep_time:.2f}s avant de réessayer...")
                time.sleep(sleep_time)
                # Augmenter le délai pour la prochaine tentative
                delay = min(delay * 2, max_delay)
                retries += 1
            else:
                raise e
    
    raise Exception(f"Échec après {max_retries} tentatives")

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
        agent_type: Type d'agent ('duckdb' ou 'networkx')
        lang: Langue d'évaluation ('fr' ou 'en')
        model: Modèle LLM pour l'évaluation
        
    Returns:
        Objet AgentPerformance contenant les résultats
    """
    performance = AgentPerformance(agent_type=agent_type)
    total_pairs = len(qa_pairs)
    
    # Préparer les instructions spécifiques pour chaque agent
    if agent_type == "duckdb":
        instructions = """
        Tu es un assistant spécialisé dans l'interrogation de la base de données DuckDB 
        Open Food Facts. Ta mission est de répondre aux questions sur les produits alimentaires
        en utilisant l'outil query_db pour exécuter des requêtes SQL.
        
        Règles importantes:
        1. Limite-toi aux informations présentes dans la base de données
        2. Réponds TOUJOURS dans la même langue que la question
        3. Garde ta réponse concise et factuelle
        4. N'inclus pas les requêtes SQL dans ta réponse
        5. Utilise uniquement les données de la base DuckDB (pas de recherche web)
        6. Si tu ne trouves pas de réponse après plusieurs tentatives de requêtes, réponds explicitement:
        - Si la question est en français: "Désolé, je ne peux pas obtenir ces informations de la base de données."
        - Si la question est en anglais: "Sorry, I cannot obtain this information from the database."
        7. Si les requêtes retournent des erreurs ou des résultats vides, n'invente pas de réponse.
        Indique clairement:
        - Si la question est en français: "Désolé, je ne peux pas obtenir ces informations de la base de données."
        - Si la question est en anglais: "Sorry, I cannot obtain this information from the database."
        8. Ne donne jamais d'informations approximatives ou générales quand tu n'as pas pu obtenir
        des données spécifiques de la base de données
        """
    else: # agent_type == "networkx":
        instructions = """
        Tu es un assistant spécialisé dans l'interrogation de la base de données NetworkX
        Open Food Facts. Ta mission est de répondre aux questions sur les produits alimentaires
        en utilisant l'outil execute_graph_query pour exécuter des requêtes sur le graphe.

        APPROCHE SYSTÉMATIQUE:
        1. Analyse d'abord le type de question posée (statistique, recherche spécifique, etc.)
        2. Détermine l'opération NetworkX la plus appropriée à utiliser
        3. Formule ta requête de manière précise en utilisant les bons paramètres
        4. Si la première requête échoue, essaie des variantes de recherche (synonymes, termes partiels)
        
        IMPORTANT - GESTION DES ÉCHECS:
        - Si après plusieurs tentatives de requêtes tu ne trouves pas de réponse, réponds explicitement:
        - Si la question est en français: "Désolé, je ne peux pas obtenir ces informations du graphe de données."
        - Si la question est en anglais: "Sorry, I cannot obtain this information from the graph database."
        - Si tes requêtes retournent des erreurs ou des résultats vides, ne génère pas d'informations 
        approximatives. Indique clairement:
        - Si la question est en français: "Désolé, je ne peux pas obtenir ces informations du graphe de données."
        - Si la question est en anglais: "Sorry, I cannot obtain this information from the graph database."
        - N'utilise jamais d'informations générales pour remplacer des données manquantes spécifiques
        - Réponds TOUJOURS dans la même langue que la question

        CONSEILS POUR LES REQUÊTES ALLERGÈNES:
        - Pour rechercher des allergènes, utilise "CONTAINS_ALLERGEN" avec différentes formes du nom
        - Essaie les variations: "lait", "milk", "lactose" ou "noix", "nuts", "tree nuts"
        - Pour les produits avec plusieurs allergènes, fais des requêtes séparées puis recoupe les résultats

        STATISTIQUES DISPONIBLES:
        - count_nodes_by_type - Utilise pour connaître le nombre total par type (Allergen, Additif, etc.)
        - count_relations_by_type - Utilise pour savoir combien de relations de chaque type existent
        - count_additives_per_product - Pour la distribution des additifs
        - get_most_common_additives - Pour le top des additifs les plus utilisés

        CONSEILS POUR DES QUESTIONS SPÉCIFIQUES:
        1. Pour "produits sans additifs": Utilise count_additives_per_product et regarde "products_without_additives"
        2. Pour "l'allergène le plus courant": Commence par search_by_relation avec CONTAINS_ALLERGEN et divers allergènes courants
        3. Pour les produits avec plusieurs attributs: Effectue des requêtes multiples et trouve les intersections
        """
    
    # Évaluer chaque paire question-réponse
    print(f"\n--- Évaluation avec l'agent {agent_type.upper()} ---")
    for idx, qa_pair in enumerate(qa_pairs, 1):
        question = qa_pair["questions"][lang]
        expected_answer = qa_pair["answers"][lang]
        
        # Afficher la progression
        progress_percent = (idx / total_pairs) * 100
        progress_bar = f"[{'=' * int(progress_percent / 5):<20}]"
        print(f"\rProgression: {progress_bar} {progress_percent:.1f}% ({idx}/{total_pairs})", end="")
        
        logger.info(f"Évaluation [{agent_type}] - Question {idx}/{len(qa_pairs)} ({progress_percent:.1f}%)")
        logger.info(f"Question: {question}")
        
        try:
            # Mesurer le temps de réponse
            start_time = time.time()
            
            # Encapsuler l'appel agent.run dans la fonction retry
            def run_agent_query():
                return agent.run(
                    question,
                    additional_args={"additional_notes": instructions}
                )
            
            agent_response = retry_with_exponential_backoff(run_agent_query)

            response_time = time.time() - start_time
            
            logger.info(f"Temps de réponse: {response_time:.2f}s")
            logger.info(f"Réponse de l'agent: {agent_response}")
            
            # Évaluation hybride (LLM + métriques)
            def evaluate_with_retry():
                return evaluate_agent_response_hybrid(
                    expected_answer, 
                    agent_response, 
                    model, 
                    threshold=0.4  # Seuil pour considérer une réponse comme correcte
                )

            evaluation_results = retry_with_exponential_backoff(evaluate_with_retry)
            
            is_correct = evaluation_results["is_correct"]
            combined_score = evaluation_results["combined_score"]
            
            # Enregistrer le résultat
            result = EvaluationResult(
                question_id=idx,
                question=question,
                expected_answer=expected_answer,
                agent_answer=agent_response,
                is_correct=is_correct,
                response_time=response_time,
                # Stockez les métriques détaillées dans l'attribut error pour l'instant
                # Idéalement, vous pourriez étendre la classe EvaluationResult pour inclure ces métriques
                error=f"Score: {combined_score:.2f}, LLM: {evaluation_results['llm_score']:.2f}, "
                      f"BLEU-2: {evaluation_results['metrics'].get('bleu_2', 'N/A')}, "
                      f"ROUGE-L: {evaluation_results['metrics'].get('rouge_l', 'N/A')}"
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
            response_time = 0.0  # Définir response_time en cas d'erreur
        
        performance.results.append(result)
        # Ajoutez un indicateur de succès/échec à la fin de chaque question
        success_indicator = "✓" if result.is_correct else "✗"
        print(f"\rQuestion {idx}/{total_pairs} {success_indicator} ({response_time:.1f}s)                  ")
        logger.info(f"Résultat: {'Correct' if result.is_correct else 'Incorrect'}")
        
        # Si nous avons des métriques détaillées, les journaliser
        if hasattr(result, 'error') and result.error and not result.error.startswith("Score:"):
            logger.info(f"Erreur: {result.error}")
        elif hasattr(result, 'error') and result.error:
            logger.info(f"Métriques: {result.error}")
            
        logger.info("-" * 50)
    
    # Afficher le résumé à la fin de l'évaluation
    print(f"\nRésumé {agent_type}:")
    print(f"  Taux de réussite : {performance.success_rate:.1f}%")
    print(f"  Temps moyen      : {performance.avg_response_time:.2f}s")
    print()
    
    return performance

def generate_report(duckdb_perf: AgentPerformance, networkx_perf: AgentPerformance, output_path: Optional[Path] = None) -> str:
    """
    Génère un rapport comparatif détaillé des performances.
    
    Args:
        duckdb_perf: Performances de l'agent DuckDB
        networkx_perf: Performances de l'agent NetworkX
        output_path: Chemin où sauvegarder le rapport (optionnel)
        
    Returns:
        Texte du rapport
    """
    # Calculer les statistiques
    duckdb_success = duckdb_perf.success_rate
    networkx_success = networkx_perf.success_rate

    duckdb_failure = duckdb_perf.failure_rate
    networkx_failure = networkx_perf.failure_rate

    duckdb_time = duckdb_perf.avg_response_time
    networkx_time = networkx_perf.avg_response_time

    # Calculer les médianes avec gestion des cas vides
    duckdb_times = [r.response_time for r in duckdb_perf.results if r.response_time > 0]
    networkx_times = [r.response_time for r in networkx_perf.results if r.response_time > 0]

    duckdb_median = statistics.median(duckdb_times) if duckdb_times else "N/A"
    networkx_median = statistics.median(networkx_times) if networkx_times else "N/A"

    # Formater la médiane selon son type
    duckdb_median_str = f"{duckdb_median:.2f}s" if isinstance(duckdb_median, (int, float)) else duckdb_median
    networkx_median_str = f"{networkx_median:.2f}s" if isinstance(networkx_median, (int, float)) else networkx_median

    # Calculer le ratio avec gestion des cas spéciaux
    if isinstance(duckdb_time, (int, float)) and isinstance(networkx_time, (int, float)) and networkx_time > 0:
        ratio = duckdb_time / networkx_time
        ratio_str = f"{ratio:.2f}x {'(DuckDB plus lent)' if duckdb_time > networkx_time else '(NetworkX plus lent)'}"
    else:
        ratio_str = "N/A"

    # Générer le rapport
    report = f"""
    ======================================================
    RAPPORT D'ÉVALUATION COMPARATIVE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ======================================================

    RÉSUMÉ:
    - Nombre de questions évaluées: {len(duckdb_perf.results)}

    TAUX DE RÉUSSITE:
    - Agent DuckDB: {duckdb_success:.2f}%
    - Agent NetworkX: {networkx_success:.2f}%
    - Différence: {abs(duckdb_success - networkx_success):.2f}% {'(DuckDB supérieur)' if duckdb_success > networkx_success else '(NetworkX supérieur)'}

    TAUX D'ÉCHEC:
    - Agent DuckDB: {duckdb_failure:.2f}%
    - Agent NetworkX: {networkx_failure:.2f}%

    TEMPS DE RÉPONSE:
    - Agent DuckDB: {duckdb_time:.2f}s (moyenne), {duckdb_median_str} (médiane)
    - Agent NetworkX: {networkx_time:.2f}s (moyenne), {networkx_median_str} (médiane)
    - Ratio: {ratio_str}

    ======================================================
    DÉTAILS PAR QUESTION
    ======================================================
    """
    
    # Ajouter les détails pour chaque question
    for i in range(len(duckdb_perf.results)):
        duckdb_result = duckdb_perf.results[i]
        networkx_result = networkx_perf.results[i] if i < len(networkx_perf.results) else None
        
        report += f"""
Question {duckdb_result.question_id}: {duckdb_result.question[:100]}{'...' if len(duckdb_result.question) > 100 else ''}

DuckDB:
- Correct: {'Oui' if duckdb_result.is_correct else 'Non'}
- Temps: {duckdb_result.response_time:.2f}s
- Erreur: {duckdb_result.error if duckdb_result.error else 'Aucune'}

NetworkX:
- Correct: {'Oui' if networkx_result and networkx_result.is_correct else 'Non'}
- Temps: {f"{networkx_result.response_time:.2f}s" if networkx_result else 'N/A'}
- Erreur: {networkx_result.error if networkx_result and networkx_result.error else 'Aucune'}

------------------------------------------------------
"""
    
    # Sauvegarder le rapport si demandé
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    return report

def extract_detailed_metrics(results: List[EvaluationResult]) -> Dict:
    """
    Extrait les métriques détaillées des résultats d'évaluation.
    
    Args:
        results: Liste des résultats d'évaluation
        
    Returns:
        Dictionnaire contenant les métriques moyennes
    """
    metrics = {
        "avg_combined_score": 0.0,
        "avg_llm_score": 0.0,
        "avg_bleu_2": 0.0,
        "avg_rouge_l": 0.0,
        "count": 0
    }
    
    for result in results:
        if hasattr(result, 'error') and result.error and result.error.startswith("Score:"):
            try:
                # Extraire les métriques à partir de la chaîne stockée dans error
                error_parts = result.error.split(", ")
                for part in error_parts:
                    if "Score:" in part:
                        metrics["avg_combined_score"] += float(part.split(": ")[1])
                    elif "LLM:" in part:
                        metrics["avg_llm_score"] += float(part.split(": ")[1])
                    elif "BLEU-2:" in part:
                        bleu = part.split(": ")[1]
                        if bleu != "N/A":
                            metrics["avg_bleu_2"] += float(bleu)
                    elif "ROUGE-L:" in part:
                        rouge = part.split(": ")[1]
                        if rouge != "N/A":
                            metrics["avg_rouge_l"] += float(rouge)
                
                metrics["count"] += 1
            except Exception:
                pass
    
    # Calculer les moyennes
    if metrics["count"] > 0:
        metrics["avg_combined_score"] /= metrics["count"]
        metrics["avg_llm_score"] /= metrics["count"]
        metrics["avg_bleu_2"] /= metrics["count"]
        metrics["avg_rouge_l"] /= metrics["count"]
    
    return metrics

def visualize_results(duckdb_perf: AgentPerformance, networkx_perf: AgentPerformance, output_path: Optional[Path] = None):
    """
    Génère des visualisations et un tableau récapitulatif pour comparer les performances.
    
    Args:
        duckdb_perf: Performances de l'agent DuckDB
        networkx_perf: Performances de l'agent NetworkX
        output_path: Chemin où sauvegarder les visualisations (optionnel)
    """
    # Extraire les métriques détaillées si disponibles
    duckdb_metrics = extract_detailed_metrics(duckdb_perf.results)
    networkx_metrics = extract_detailed_metrics(networkx_perf.results)
    
    # Générer un tableau récapitulatif des métriques
    try:
        from tabulate import tabulate
        
        # Préparer les données du tableau
        headers = ["Métrique", "DuckDB", "NetworkX", "Différence"]
        metrics_data = [
            ["Taux de réussite (%)", 
             f"{duckdb_perf.success_rate:.2f}", 
             f"{networkx_perf.success_rate:.2f}", 
             f"{abs(duckdb_perf.success_rate - networkx_perf.success_rate):.2f}"],
            
            ["Taux d'échec (%)", 
             f"{duckdb_perf.failure_rate:.2f}", 
             f"{networkx_perf.failure_rate:.2f}", 
             f"{abs(duckdb_perf.failure_rate - networkx_perf.failure_rate):.2f}"],
            
            ["Temps moyen (s)", 
             f"{duckdb_perf.avg_response_time:.2f}", 
             f"{networkx_perf.avg_response_time:.2f}", 
             f"{abs(duckdb_perf.avg_response_time - networkx_perf.avg_response_time):.2f}"],
            
            ["Temps médian (s)", 
             f"{statistics.median([r.response_time for r in duckdb_perf.results if r.response_time > 0]):.2f}", 
             f"{statistics.median([r.response_time for r in networkx_perf.results if r.response_time > 0]):.2f}", 
             ""]
        ]
        
        # Ajouter les métriques détaillées si disponibles
        if duckdb_metrics.get("avg_combined_score") and networkx_metrics.get("avg_combined_score"):
            metrics_data.extend([
                ["Score combiné moyen", 
                 f"{duckdb_metrics['avg_combined_score']:.2f}", 
                 f"{networkx_metrics['avg_combined_score']:.2f}", 
                 f"{abs(duckdb_metrics['avg_combined_score'] - networkx_metrics['avg_combined_score']):.2f}"],
                
                ["Score LLM moyen", 
                 f"{duckdb_metrics['avg_llm_score']:.2f}", 
                 f"{networkx_metrics['avg_llm_score']:.2f}", 
                 f"{abs(duckdb_metrics['avg_llm_score'] - networkx_metrics['avg_llm_score']):.2f}"],
                
                ["BLEU-2 moyen", 
                 f"{duckdb_metrics['avg_bleu_2']:.4f}", 
                 f"{networkx_metrics['avg_bleu_2']:.4f}", 
                 f"{abs(duckdb_metrics['avg_bleu_2'] - networkx_metrics['avg_bleu_2']):.4f}"],
                
                ["ROUGE-L moyen", 
                 f"{duckdb_metrics['avg_rouge_l']:.4f}", 
                 f"{networkx_metrics['avg_rouge_l']:.4f}", 
                 f"{abs(duckdb_metrics['avg_rouge_l'] - networkx_metrics['avg_rouge_l']):.4f}"]
            ])
        
        # Créer et afficher le tableau
        table = tabulate(metrics_data, headers=headers, tablefmt="grid")
        print("\nTABLEAU RÉCAPITULATIF DES MÉTRIQUES")
        print(table)
        
        # Sauvegarder le tableau dans un fichier si demandé
        if output_path:
            metrics_file = output_path / "metrics_summary.txt"
            with open(metrics_file, 'w', encoding='utf-8') as f:
                f.write("TABLEAU RÉCAPITULATIF DES MÉTRIQUES\n\n")
                f.write(table)
            print(f"\nTableau des métriques sauvegardé dans {metrics_file}")
            
            # Créer un fichier CSV pour une utilisation ultérieure
            csv_file = output_path / "metrics_summary.csv"
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write("Metric,DuckDB,NetworkX,Difference\n")
                for row in metrics_data:
                    f.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")
            print(f"CSV des métriques sauvegardé dans {csv_file}")
            
    except ImportError:
        print("\nModule 'tabulate' non installé. Impossible de générer le tableau formaté.")
        print("Installez-le avec: pip install tabulate\n")
        
        # Affichage simple sans tabulate
        print("\nRÉCAPITULATIF DES MÉTRIQUES:")
        print(f"Taux de réussite:  DuckDB={duckdb_perf.success_rate:.2f}%, NetworkX={networkx_perf.success_rate:.2f}%")
        print(f"Taux d'échec:      DuckDB={duckdb_perf.failure_rate:.2f}%, NetworkX={networkx_perf.failure_rate:.2f}%")
        print(f"Temps moyen:       DuckDB={duckdb_perf.avg_response_time:.2f}s, NetworkX={networkx_perf.avg_response_time:.2f}s")
        duckdb_median = statistics.median([r.response_time for r in duckdb_perf.results if r.response_time > 0])
        networkx_median = statistics.median([r.response_time for r in networkx_perf.results if r.response_time > 0])
        print(f"Temps médian:      DuckDB={duckdb_median:.2f}s, NetworkX={networkx_median:.2f}s")

    try:        
        sns.set(style="whitegrid")
        
        # Créer le répertoire de sortie si nécessaire
        if output_path:
            output_path.mkdir(exist_ok=True, parents=True)
        
        # 1. Taux de réussite
        plt.figure(figsize=(10, 6))
        agents = ["DuckDB", "NetworkX"]
        success_rates = [duckdb_perf.success_rate, networkx_perf.success_rate]
        failure_rates = [duckdb_perf.failure_rate, networkx_perf.failure_rate]
        
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
        networkx_times = [r.response_time for r in networkx_perf.results if r.response_time > 0]
        
        sns.boxplot(data=[duckdb_times, networkx_times], orient="h")
        plt.yticks([0, 1], ["DuckDB", "NetworkX"])
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
        networkx_correct = []
        
        for i, duckdb_result in enumerate(duckdb_perf.results):
            if i < len(networkx_perf.results):
                networkx_result = networkx_perf.results[i]
                
                question_ids.append(duckdb_result.question_id)
                duckdb_correct.append(1 if duckdb_result.is_correct else 0)
                networkx_correct.append(1 if networkx_result.is_correct else 0)
        
        width = 0.35
        x = np.arange(len(question_ids))
        
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.bar(x - width/2, duckdb_correct, width, label='DuckDB')
        ax.bar(x + width/2, networkx_correct, width, label='NetworkX')
        
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
    parser = argparse.ArgumentParser(description="Évaluation comparative des agents DuckDB et NetworkX")
    
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
        # See https://docs.anthropic.com/en/docs/about-claude/models/all-models
        # claude-3-7-sonnet-20250219: $3.00 / $15.00 MTok
        # claude-3-5-haiku-20241022: $0.80 / $4.00 MTok
        # See Anthropic Credit balance: https://console.anthropic.com/settings/billing
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
    
    logger.info("Création de l'agent NetworkX...")
    networkx_agent = create_networkx_agent(model)
    
    # Évaluer les agents
    logger.info("Démarrage de l'évaluation de l'agent DuckDB...")
    duckdb_perf = evaluate_agent(
        agent=duckdb_agent,
        qa_pairs=qa_pairs,
        agent_type="duckdb",
        lang=args.lang,
        model=model
    )
    
    logger.info("Démarrage de l'évaluation de l'agent NetworkX...")
    networkx_perf = evaluate_agent(
        agent=networkx_agent,
        qa_pairs=qa_pairs,
        agent_type="networkx",
        lang=args.lang,
        model=model
    )
    
    # Générer le rapport
    logger.info("Génération du rapport comparatif...")
    report = generate_report(duckdb_perf, networkx_perf)
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
        visualize_results(duckdb_perf, networkx_perf, vis_dir)
        logger.info(f"Visualisations générées dans {vis_dir}")
    except Exception as e:
        logger.warning(f"Impossible de générer les visualisations: {e}")
        
    logger.info("Évaluation terminée.")


def test():
    """Fonction de test pour vérifier le bon fonctionnement du NetworkXQueryTool."""
    print("Démarrage des tests de diagnostic...")
    
    # Initialiser l'outil avec le graphe
    query_tool = NetworkXQueryTool(graph_path=GRAPH_PATH)
    
    # Test 1: Vérifier que le graphe est chargé correctement
    if len(query_tool.graph) == 0:
        print("ERREUR: Le graphe n'a pas été chargé correctement!")
        return
    
    print(f"Graphe chargé avec succès: {len(query_tool.graph.nodes())} nœuds, {len(query_tool.graph.edges())} arêtes")
    
    # Test 2: Compter les nœuds par type
    node_types = {}
    for _, data in query_tool.graph.nodes(data=True):
        node_type = data.get('type', 'unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    print("Distribution des nœuds par type:")
    for type_name, count in node_types.items():
        print(f"  - {type_name}: {count}")
    
    # Test 3: Vérifier la présence d'additifs
    additifs_count = node_types.get('Additif', 0)
    print(f"Nombre d'additifs dans le graphe: {additifs_count}")
    
    # Test 4: Vérifier les relations CONTAINS_ADDITIF
    additif_relations = 0
    for _, _, data in query_tool.graph.edges(data=True):
        if data.get('type') == 'CONTAINS_ADDITIF':
            additif_relations += 1
    
    print(f"Nombre de relations CONTAINS_ADDITIF: {additif_relations}")
    
    # Test 5: Vérifier les produits sans additifs
    no_additives_count = 0
    for _, data in query_tool.graph.nodes(data=True):
        if data.get('type') == 'Product' and data.get('has_additives') is False:
            no_additives_count += 1
    
    print(f"Nombre de produits explicitement marqués sans additifs: {no_additives_count}")
    
    # Test 6: Tester la recherche par relation pour les additifs
    print("\nTest de recherche par relation CONTAINS_ADDITIF:")
    additif_query = {"operation": "search_by_relation", "relation_type": "CONTAINS_ADDITIF", "relation_target": "E", "limit": 5}
    additif_result = query_tool.forward(json.dumps(additif_query))
    additif_data = json.loads(additif_result)
    
    if "error" in additif_data:
        print(f"ERREUR: {additif_data['error']}")
    else:
        print(f"Résultat: {additif_data['count']} produits trouvés")
    
    # Test 7: Tester la recherche de produits sans additifs
    print("\nTest de recherche de produits sans additifs:")
    no_additif_query = {"operation": "search_by_relation", "relation_type": "CONTAINS_ADDITIF", "relation_target": "sans", "limit": 5}
    no_additif_result = query_tool.forward(json.dumps(no_additif_query))
    no_additif_data = json.loads(no_additif_result)
    
    if "error" in no_additif_data:
        print(f"ERREUR: {no_additif_data['error']}")
    else:
        print(f"Résultat: {no_additif_data['count']} produits sans additifs trouvés")
    
    # Test 8: Tester la distribution des additifs
    print("\nTest de distribution des additifs par produit:")
    distribution_query = {"operation": "count_additives_per_product", "limit": 1000}
    distribution_result = query_tool.forward(json.dumps(distribution_query))
    distribution_data = json.loads(distribution_result)
    
    if "error" in distribution_data:
        print(f"ERREUR: {distribution_data['error']}")
    else:
        print(f"Produits avec additifs: {distribution_data.get('products_with_additives', 'N/A')}")
        print(f"Produits sans additifs: {distribution_data.get('products_without_additives', 'N/A')}")
        print(f"Pourcentage sans additifs: {distribution_data.get('percentage_without_additives', 'N/A')}%")
    
    print("\nTests terminés.")

if __name__ == "__main__":
    try:
        main()
        # test()
    except Exception as e:
        print(f"ERREUR FATALE: {e}")
        logger.error(f"ERREUR FATALE: {e}", exc_info=True)