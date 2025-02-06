import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates

def get_github_stars_history(repo, token=None):
    """
    Récupère l'historique des étoiles d'un dépôt GitHub
    https://x.com/_ai_reviews/status/1886152326009819372
    """
    headers = {
        'Accept': 'application/vnd.github.v3.star+json'  # Header spécial pour obtenir les dates
    }
    if token:
        headers['Authorization'] = f'token {token}'
    
    stars = []
    page = 1
    while True:
        url = f'https://api.github.com/repos/{repo}/stargazers'
        params = {'per_page': 100, 'page': page}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 403:
            print(f"Limite d'API atteinte. Utilisez un token GitHub.")
            break
        elif response.status_code != 200:
            print(f"Erreur {response.status_code}: {response.json().get('message', '')}")
            break
            
        data = response.json()
        if not data:
            break
            
        stars.extend([item['starred_at'] for item in data])
        page += 1
        
        # Petit délai pour éviter de surcharger l'API
        if page % 10 == 0:
            print(f"Récupération de {len(stars)} étoiles...")
    
    if not stars:
        print(f"Aucune donnée récupérée pour {repo}")
        return pd.Series(dtype='float64')
    
    df = pd.DataFrame(stars, columns=['date'])
    df['date'] = pd.to_datetime(df['date'])
    
    daily_counts = df.groupby(df['date'].dt.date).size()
    cumulative_counts = daily_counts.cumsum()
    
    return pd.Series(cumulative_counts, name='stars')


def get_github_stars_history_test(repo, token=None):
    """
    Génère un historique fictif d'étoiles GitHub
    """
    # Générer des dates sur 1 an
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Paramètres de croissance différents selon le repo
    if 'langgraph' in repo:
        # Croissance plus rapide
        initial_stars = 100
        daily_growth = np.random.normal(20, 5, size=len(dates))
    else:
        # Croissance plus lente puis explosion
        initial_stars = 0
        daily_growth = np.random.normal(5, 2, size=len(dates))
        # Simulation d'une explosion de popularité sur les derniers jours
        daily_growth[-30:] = np.random.normal(200, 20, size=30)
    
    # Assurer que la croissance est toujours positive
    daily_growth = np.maximum(daily_growth, 0)
    
    # Calculer le cumul
    cumulative_stars = initial_stars + np.cumsum(daily_growth)
    
    # Créer la série avec les dates comme index
    stars = pd.Series(cumulative_stars, index=dates.date, name='stars')
    
    return stars

def plot_stars_history(repos, output_file=None):
    """
    Crée un graphique de l'historique des étoiles style xkcd
    """
    def format_func(x, p):
        return f'{int(x/1000)}k'

    # Configuration du style xkcd
    plt.rcParams['font.family'] = ['xkcd Script', 'Comic Neue', 'Comic Sans MS']
    
    with plt.xkcd():
        fig, ax = plt.subplots(figsize=(12, 7))
        colors = ['#1f77b4', '#ff7f0e']  # Bleu et Orange
        
        for repo, color in zip(repos, colors):
            print(f"\nGénération des données pour {repo}...")
            stars = get_github_stars_history_test(repo)
            
            # Tracer avec des lignes pointillées et sans marqueurs
            ax.plot(stars.index, stars.values, 
                    linestyle=':', 
                    linewidth=1.5,
                    color=color,
                    label=repo.split('/')[-1],
                    alpha=0.8)

        # Titre et étiquettes
        ax.set_title('Star History', fontsize=14, pad=20)
        ax.set_ylabel('GitHub Stars', fontsize=12)
        
        # Formatage des axes
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_func))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%B\n%Y'))
        
        # Suppression de la grille
        ax.grid(False)
        
        # Modification des bordures
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1)
        ax.spines['bottom'].set_linewidth(1)
        
        # Légende à l'intérieur du graphique
        legend = ax.legend(
            title="Projets",
            loc='upper right',
            frameon=True,
            fancybox=True,
            framealpha=1,
            bbox_to_anchor=(0.99, 0.99)
        )
        
        # Attribution star-history.com avec une étoile
        ax.text(0.99, -0.1, '⭐ star-history.com', 
                transform=ax.transAxes,
                fontsize=8,
                ha='right', va='bottom',
                color='#2ecc71')  # Vert plus clair
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"\nGraphique sauvegardé dans {output_file}")
        else:
            plt.show()

"""
import os
os.environ['GITHUB_TOKEN'] = 'votre_token_ici'
token = os.getenv('GITHUB_TOKEN')
plot_stars_history(repos, token=token)
export GITHUB_TOKEN='votre_token_ici'
"""

if __name__ == "__main__":
    repos = [
        'langchain-ai/langgraph',
        'huggingface/smolagents'
    ]
    
    # Pour utiliser un token GitHub (recommandé)
    # import os
    # token = os.getenv('GITHUB_TOKEN')
    # plot_stars_history(repos, token=token)
    
    plot_stars_history(repos, 'star_history_xkcd.png')





