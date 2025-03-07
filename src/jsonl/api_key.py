import os
from dotenv import load_dotenv
from pathlib import Path

# Chemin vers le répertoire racine du projet (2 niveaux au-dessus de ce script)
root_dir = Path(__file__).parent.parent.parent.absolute()
dotenv_path = os.path.join(root_dir, '.env')
print(f"Chargement des variables d'environnement depuis : {dotenv_path}")

# Chargement des variables d'environnement depuis la racine
load_dotenv(dotenv_path)


# Vérifier si la variable d'environnement système existe déjà
# Si oui, faire "unset OPENAI_API_KEY" et redémarrer le terminal
import subprocess
result = subprocess.run(['env'], stdout=subprocess.PIPE, text=True)
env_vars = result.stdout.split('\n')
for var in env_vars:
    if 'OPENAI_API_KEY' in var:
        print(f"Variable système trouvée: {var}")

import openai
from openai import OpenAI

client = OpenAI(api_key="votre-clé-api")

try:
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input="Hello world"
    )
    print("Succès! La clé fonctionne pour les embeddings.")
    print(f"Dimension du vecteur: {len(response.data[0].embedding)}")
except Exception as e:
    print(f"Erreur: {e}")