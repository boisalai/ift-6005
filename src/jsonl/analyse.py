import json
import os
import logging
from collections import Counter
from datetime import datetime

def setup_logger(log_file='jsonl_analysis.log'):
    """
    Configure un logger pour écrire dans un fichier et sur la console
    
    Args:
        log_file: Nom du fichier de log
    
    Returns:
        Un objet logger configuré
    """
    # Créer le répertoire de logs s'il n'existe pas
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurer le logger
    logger = logging.getLogger('jsonl_analyzer')
    logger.setLevel(logging.INFO)
    
    # Empêcher la duplication des logs si le logger est déjà configuré
    if not logger.handlers:
        # Handler pour le fichier
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_format = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
    
    return logger

def analyze_jsonl_structure(filepath, sample_size=5, logger=None):
    """
    Analyse la structure d'un fichier JSONL volumineux sans le charger entièrement en mémoire.
    
    Args:
        filepath: Chemin vers le fichier JSONL
        sample_size: Nombre d'objets à analyser pour comprendre la structure
        logger: Logger pour enregistrer les résultats
    """
    if logger is None:
        logger = setup_logger()
    
    # Enregistrer les métadonnées de l'analyse
    logger.info(f"=== Analyse du fichier JSONL: {filepath} ===")
    logger.info(f"Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier si le fichier existe
    if not os.path.exists(filepath):
        logger.error(f"Erreur: Le fichier {filepath} n'existe pas")
        return
    
    # Obtenir la taille du fichier
    file_size = os.path.getsize(filepath) / (1024 * 1024 * 1024)  # Taille en Go
    logger.info(f"Taille du fichier: {file_size:.2f} Go")
    
    # Collecter des statistiques sur les clés
    all_keys = Counter()
    key_types = {}
    key_depths = {}
    sample_objects = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= sample_size:
                    break
                    
                try:
                    obj = json.loads(line.strip())
                    sample_objects.append(obj)
                    
                    # Analyser récursivement la structure
                    def explore_structure(data, prefix='', depth=0):
                        if isinstance(data, dict):
                            for key, value in data.items():
                                full_key = f"{prefix}.{key}" if prefix else key
                                all_keys[full_key] += 1
                                key_types[full_key] = type(value).__name__
                                key_depths[full_key] = depth
                                
                                # Exploration récursive
                                if isinstance(value, (dict, list)):
                                    explore_structure(value, full_key, depth + 1)
                        elif isinstance(data, list) and data and prefix:
                            # Pour les listes, examiner le premier élément comme exemple
                            if data and isinstance(data[0], (dict, list)):
                                explore_structure(data[0], f"{prefix}[0]", depth + 1)
                    
                    explore_structure(obj)
                    
                except json.JSONDecodeError:
                    logger.error(f"Erreur de décodage JSON à la ligne {i+1}")
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier: {str(e)}")
        return
    
    # Enregistrer les résultats
    logger.info("\nStructure du fichier JSONL (basée sur un échantillon):")
    logger.info("-" * 50)
    logger.info(f"Nombre d'objets analysés: {len(sample_objects)}")
    
    logger.info("\nClés trouvées (triées par profondeur puis par fréquence):")
    # Grouper les clés par profondeur
    depth_groups = {}
    for key, count in all_keys.items():
        depth = key_depths.get(key, 0)
        if depth not in depth_groups:
            depth_groups[depth] = []
        depth_groups[depth].append((key, count))
    
    # Afficher les clés par niveau de profondeur
    for depth in sorted(depth_groups.keys()):
        logger.info(f"\nNiveau de profondeur {depth}:")
        for key, count in sorted(depth_groups[depth], key=lambda x: x[1], reverse=True):
            logger.info(f"  - {key} ({count}/{len(sample_objects)}): {key_types.get(key, 'inconnu')}")
    
    # Enregistrer un exemple d'objet
    logger.info("\nExemple d'objet:")
    if sample_objects:
        logger.info(json.dumps(sample_objects[0], indent=2, ensure_ascii=False))
    
    logger.info("\n=== Fin de l'analyse ===\n")
    return all_keys, key_types, sample_objects

def count_total_objects(filepath, logger=None):
    """Compte le nombre total d'objets dans le fichier JSONL."""
    if logger is None:
        logger = setup_logger()
    
    count = 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for _ in f:
                count += 1
                if count % 1000000 == 0:
                    logger.info(f"Progression: {count:,} objets comptés")
    except Exception as e:
        logger.error(f"Erreur lors du comptage des objets: {str(e)}")
    
    logger.info(f"Nombre total d'objets: {count:,}")
    return count

def process_jsonl_in_chunks(filepath, chunk_size=10000, process_func=None, logger=None):
    """
    Traite un fichier JSONL en morceaux pour économiser la mémoire.
    
    Args:
        filepath: Chemin vers le fichier JSONL
        chunk_size: Nombre d'objets à traiter par lot
        process_func: Fonction appelée pour chaque lot d'objets
        logger: Logger pour enregistrer les résultats
    """
    if logger is None:
        logger = setup_logger()
    
    chunk = []
    processed_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                try:
                    obj = json.loads(line.strip())
                    chunk.append(obj)
                    
                    if len(chunk) >= chunk_size:
                        if process_func:
                            process_func(chunk, logger)
                        processed_count += len(chunk)
                        logger.info(f"Progression: {processed_count:,} objets traités")
                        chunk = []
                except json.JSONDecodeError:
                    logger.error(f"Erreur de décodage JSON à la ligne {i+1}")
        
        # Traiter le dernier lot s'il n'est pas vide
        if chunk and process_func:
            process_func(chunk, logger)
            processed_count += len(chunk)
            logger.info(f"Terminé: {processed_count:,} objets traités au total")
    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier: {str(e)}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Chemin vers le fichier JSONL
    filepath = "../data/openfoodfacts-products.jsonl"
    
    # Configurer le logger avec un nom de fichier spécifique
    log_filename = f"../logs/jsonl_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = setup_logger(log_filename)
    
    logger.info("Démarrage de l'analyse du fichier JSONL")
    
    # Analyser la structure du fichier
    analyze_jsonl_structure(filepath, sample_size=10, logger=logger)
    
    # Compter le nombre total d'objets (peut prendre du temps pour un fichier de 60 Go)
    # Décommentez pour exécuter
    # logger.info("Comptage du nombre total d'objets...")
    # count_total_objects(filepath, logger=logger)
    
    # Exemple de fonction de traitement par lot
    def process_batch(batch, logger=None):
        if logger:
            logger.info(f"Traitement d'un lot de {len(batch)} objets")
        # Votre logique de traitement ici
    
    # Décommentez pour traiter tout le fichier
    # logger.info("Traitement du fichier par lots...")
    # process_jsonl_in_chunks(filepath, chunk_size=10000, process_func=process_batch, logger=logger)
    
    logger.info("Analyse terminée. Log enregistré dans: " + log_filename)