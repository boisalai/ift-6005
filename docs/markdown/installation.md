# Documentation technique

## Créer l'environnement de travail

Voici des instructions pour créer votre répertoire de travail local en utilisant Git et en le connectant à votre dépôt GitHub.

Ouvrez le Terminal et créez et accédez au répertoire où vous voulez placer votre projet :

```bash
mkdir ~/Projects  # si ce n'est pas déjà fait
cd ~/Projects
```

Clonez le dépôt GitHub :

```bash
git clone https://github.com/votre-username/nom-du-repo.git
cd nom-du-repo
```

Créez un environnement virtuel Python :

```bash
python -m venv venv
source venv/bin/activate
```

Créez la structure initiale du projet :

```bash
mkdir -p src/agents tests data docs notebooks
touch requirements.txt
```

Cette commande créera :

- `src/agents/` pour votre code source
- `tests/` pour vos tests
- `data/` pour les données Open Food Facts
- `docs/` pour la documentation
- `notebooks/` pour les notebooks Jupyter
- `requirements.txt` pour les dépendances

Créez un fichier `.gitignore` :

```bash
cat << EOF > .gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
.Python
venv/
.env

# Notebooks
.ipynb_checkpoints

# VS Code
.vscode/

# Data
data/*.db
data/*.csv

# Mac
.DS_Store
EOF
```

Installez les dépendances initiales :

```bash
pip install pytest smolagents duckdb matplotlib pandas jupyter
pip freeze > requirements.txt
```

Faites votre premier commit :

```bash
git add .
git commit -m "Initial project structure"
git push origin main
```

Votre structure de répertoire devrait maintenant ressembler à ceci :

```
votre-repo/
├── LICENSE
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   └── agents/
├── tests/
├── data/
├── docs/
└── notebooks/
```

Pour la documentation Markdown :

```
docs/markdown/
├── README.md              # Vue d'ensemble
├── installation.md        # Guide d'installation
├── architecture.md        # Architecture du système
├── agents/               
│   ├── main_agent.md     # Agent principal
│   ├── query_agent.md    # Agent de requêtes
│   ├── enrichment_agent.md # Agent d'enrichissement
│   └── viz_agent.md      # Agent de visualisation
└── database/
    ├── schema.md         # Structure de la base de données
    └── queries.md        # Exemples de requêtes
```

Pour la documentation LaTeX :

```
docs/latex/
├── main.tex              # Document principal
├── chapters/
│   ├── introduction.tex
│   ├── architecture.tex
│   ├── implementation.tex
│   ├── evaluation.tex
│   └── conclusion.tex
├── images/               # Figures et diagrammes
├── appendices/           # Code source, exemples
└── bibliography.bib      # Références
```