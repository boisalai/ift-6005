#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Démonstration autonome de l'Agent Conversationnel Open Food Facts
================================================================

Ce script est une démonstration autonome des agents conversationnels
pour Open Food Facts, simulant la comparaison entre les approches 
DuckDB et NetworkX sans dépendances externes.

Conçu pour les présentations, ce script:
- Simule les réponses des agents et leurs temps d'exécution
- Affiche les requêtes SQL et GraphQL générées
- Visualise les résultats de performance
- Ne nécessite aucune connexion aux bases de données réelles

Usage:
    python demo_standalone.py

Dépendances:
    pip install rich matplotlib pandas
"""

import json
import time
import traceback
from datetime import datetime
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich import box
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

# Initialize Rich console for pretty printing
console = Console()

# Questions pour la démonstration
DEMO_QUESTIONS = [
    {
        "title": "Produits sans gluten avec bon Nutri-Score",
        "text": "Quels sont les produits sans gluten qui ont un bon Nutri-Score?",
        "duckdb": {
            "response": "D'après la base Open Food Facts, plusieurs produits sans gluten ont un Nutri-Score A ou B, notamment des légumineuses (lentilles, pois), certaines céréales sans gluten (quinoa), et quelques produits de boulangerie spécialisés.",
            "query": """
SELECT 
    p.code, 
    unnest(list_filter(p.product_name, x -> x.lang == 'fr'))['text'] AS nom_produit,
    p.nutriscore_grade
FROM 
    products p
WHERE 
    p.nutriscore_grade IN ('a', 'b')
    AND list_contains(p.labels_tags, 'en:gluten-free')
ORDER BY 
    p.nutriscore_grade ASC
LIMIT 20
            """,
            "response_time": 5.8
        },
        "networkx": {
            "response": "La base Open Food Facts contient plusieurs produits sans gluten avec un bon Nutri-Score, comme le quinoa, certaines farines spéciales, et plusieurs légumineuses naturelles.",
            "query": {
                "operation": "search_products_multi_criteria",
                "filters": {
                    "nutriscore_grade": "a"
                },
                "relations": [
                    {
                        "type": "HAS_LABEL",
                        "target": "gluten free"
                    }
                ],
                "limit": 10
            },
            "response_time": 8.4
        }
    },
    {
        "title": "Additifs fréquents dans produits avec mauvais Nutri-Score",
        "text": "Quels sont les additifs les plus fréquents dans les produits qui ont un mauvais Nutri-Score?",
        "duckdb": {
            "response": "Les additifs les plus fréquents dans les produits avec un Nutri-Score D ou E sont l'acide citrique (E330), les phosphates (E450, E451), les émulsifiants (E471, E472), les colorants (E160) et le glutamate monosodique (E621). Source: Open Food Facts.",
            "query": """
WITH bad_products AS (
    SELECT code
    FROM products
    WHERE nutriscore_grade IN ('d', 'e')
),
unnested_additives AS (
    SELECT 
        UNNEST(additives_tags) as additive
    FROM 
        products p
    JOIN 
        bad_products bp ON p.code = bp.code
    WHERE 
        additives_tags IS NOT NULL
)
SELECT 
    additive, 
    COUNT(*) as frequency
FROM 
    unnested_additives
GROUP BY 
    additive
ORDER BY 
    frequency DESC
LIMIT 10
            """,
            "response_time": 7.2
        },
        "networkx": {
            "response": "Selon Open Food Facts, dans les produits avec un Nutri-Score D ou E, les additifs les plus fréquents sont E330 (acide citrique), E471 (mono et diglycérides d'acides gras), E322 (lécithines) et E450 (diphosphates).",
            "query": {
                "operation": "count_additives_per_product",
                "filters": {
                    "nutriscore_grade": "e"
                },
                "limit": 100
            },
            "response_time": 9.5
        }
    },
    {
        "title": "Produits sans allergènes communs",
        "text": "Quels sont les produits qui ne contiennent ni gluten, ni lactose, ni fruits à coque?",
        "duckdb": {
            "response": "D'après Open Food Facts, plusieurs produits sans gluten, lactose ni fruits à coque incluent: certaines boissons végétales (à base de riz), quelques produits céréaliers spécifiques, des légumineuses naturelles et certains produits transformés avec certification 'sans allergènes'.",
            "query": """
SELECT 
    p.code,
    unnest(list_filter(p.product_name, x -> x.lang == 'fr'))['text'] AS nom_produit,
    p.brands
FROM 
    products p
WHERE 
    NOT list_contains(p.allergens_tags, 'en:gluten')
    AND NOT list_contains(p.allergens_tags, 'en:milk')
    AND NOT list_contains(p.allergens_tags, 'en:nuts')
    AND NOT list_contains(p.ingredients_tags, 'en:gluten')
    AND NOT list_contains(p.ingredients_tags, 'en:milk')
    AND NOT list_contains(p.ingredients_tags, 'en:nuts')
LIMIT 15
            """,
            "response_time": 6.9
        },
        "networkx": {
            "response": "Désolé, je ne peux pas obtenir ces informations du graphe de données. La structure actuelle du graphe ne permet pas de combiner efficacement plusieurs critères d'absence d'allergènes de cette façon.",
            "query": {
                "operation": "search_by_relation",
                "relation_type": "CONTAINS_ALLERGEN",
                "relation_target": "gluten",
                "case_sensitive": false,
                "exact_match": false,
                "limit": 10
            },
            "response_time": 7.8,
            "error": "Requête incomplète - ne teste qu'un seul allergène"
        }
    },
    {
        "title": "Question complexe sur allergies croisées",
        "text": "Quels produits contiennent des ingrédients qui pourraient provoquer des allergies croisées avec les arachides mais qui ne contiennent pas directement d'arachides?",
        "duckdb": {
            "response": "Désolé, je ne peux pas obtenir ces informations de la base de données. Les données sur les allergies croisées ne sont pas explicitement stockées dans Open Food Facts.",
            "query": """
-- Tentative de requête pour allergies croisées
SELECT 
    p.code,
    unnest(list_filter(p.product_name, x -> x.lang == 'fr'))['text'] AS nom_produit
FROM 
    products p
WHERE 
    NOT list_contains(p.allergens_tags, 'en:peanuts')
    AND NOT list_contains(p.ingredients_tags, 'en:peanuts')
    AND (
        list_contains(p.ingredients_tags, 'en:legumes')
        OR list_contains(p.ingredients_tags, 'en:soy')
        OR list_contains(p.ingredients_tags, 'en:lupin')
    )
LIMIT 10
            """,
            "response_time": 8.5,
            "error": "Les informations sur les allergies croisées ne sont pas disponibles"
        },
        "networkx": {
            "response": "Désolé, je ne peux pas obtenir ces informations du graphe de données. Open Food Facts ne contient pas de données structurées sur les allergies croisées potentielles.",
            "query": {
                "operation": "search_products_multi_criteria",
                "filters": {},
                "relations": [
                    {
                        "type": "CONTAINS",
                        "target": "legume"
                    }
                ],
                "limit": 10
            },
            "response_time": 10.2,
            "error": "Les informations sur les allergies croisées ne sont pas disponibles"
        }
    }
]

# Résultats d'évaluation pour visualisation
EVALUATION_RESULTS = {
    'Métrique': ['Taux de réussite (%)', 'Taux d\'échec (%)', 'Temps moyen (s)', 'Score combiné'],
    'DuckDB': [43.00, 21.00, 26.37, 0.34],
    'NetworkX': [17.00, 48.00, 26.69, 0.19],
    'Différence': [26.00, 27.00, 0.32, 0.15]
}

class AgentDemo:
    """Class to simulate and display the comparison between the two agent approaches"""
    
    def __init__(self):
        """Initialize the demo with simulated data"""
        self.questions = DEMO_QUESTIONS
        self.evaluation_results = EVALUATION_RESULTS
    
    def simulate_loading(self, message="Chargement", duration=1.5):
        """Simulate loading with a spinner animation"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(description=message, total=100)
            
            # Simulate progress
            chunk = 100 / (duration * 10)
            while not progress.finished:
                progress.update(task, advance=chunk)
                time.sleep(0.1)
    
    def simulate_agent_execution(self, agent_name, question, duration_range=(1.0, 3.0)):
        """Simulate agent execution with a progress bar"""
        duration = random.uniform(*duration_range)
        
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold {'blue' if agent_name=='DuckDB' else 'orange'}]{{task.description}}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(
                description=f"Agent {agent_name} analyse la question...", 
                total=100
            )
            
            # Simulate steps of analysis
            steps = [
                (30, f"Agent {agent_name} identifie les entités..."),
                (60, f"Agent {agent_name} formule une requête..."),
                (90, f"Agent {agent_name} exécute la requête...")
            ]
            
            # Update progress through the steps
            current = 0
            for target, description in steps:
                # Calculate time needed to reach this target
                step_duration = duration * (target - current) / 100
                chunk = (target - current) / (step_duration * 10)
                
                # Update description
                progress.update(task, description=description)
                
                # Update progress gradually
                while current < target:
                    time.sleep(0.1)
                    current += chunk
                    progress.update(task, completed=min(current, target))
            
            # Complete progress
            progress.update(task, 
                         description=f"Agent {agent_name} formule la réponse...",
                         completed=100)
            time.sleep(0.5)
            
        return duration
        
    def display_agent_comparison(self, question_data):
        """Display a full comparison of both agents on a single question"""
        question = question_data["text"]
        title = question_data["title"]
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="title"),
            Layout(name="question"),
            Layout(name="results", ratio=3)
        )
        
        # Add title
        layout["title"].update(Panel(
            f"[bold cyan]Comparaison des agents sur: {title}[/bold cyan]", 
            box=box.DOUBLE
        ))
        
        # Add question
        layout["question"].update(Panel(
            f"[bold yellow]Question: [/bold yellow]{question}", 
            box=box.ROUNDED
        ))
        
        # Split results section for side-by-side comparison
        layout["results"].split_row(
            Layout(name="duckdb", ratio=1),
            Layout(name="networkx", ratio=1)
        )
        
        # Run both simulated agents
        console.print("[bold]Interrogation de l'agent DuckDB...[/bold]")
        duckdb_time = self.simulate_agent_execution("DuckDB", question, 
                                               duration_range=(1.0, 2.0))
        
        console.print("[bold]Interrogation de l'agent NetworkX...[/bold]")
        networkx_time = self.simulate_agent_execution("NetworkX", question, 
                                                 duration_range=(1.5, 3.0))
        
        # Get pre-defined results
        duckdb_result = question_data["duckdb"]
        networkx_result = question_data["networkx"]
        
        # Override simulated times with pre-defined ones if available
        if "response_time" in duckdb_result:
            duckdb_time = duckdb_result["response_time"]
        if "response_time" in networkx_result:
            networkx_time = networkx_result["response_time"]
        
        # Create DuckDB panel content
        duckdb_content = Layout()
        duckdb_content.split_column(
            Layout(name="duckdb_title"),
            Layout(name="duckdb_response", ratio=1),
            Layout(name="duckdb_query", ratio=2),
            Layout(name="duckdb_time")
        )
        
        duckdb_content["duckdb_title"].update(Panel("[bold blue]Agent DuckDB[/bold blue]"))
        
        # Show error if present
        if "error" in duckdb_result:
            duckdb_content["duckdb_response"].update(Panel(
                f"[bold red]{duckdb_result['response']}[/bold red]\n\n[italic]Erreur: {duckdb_result['error']}[/italic]",
                title="Réponse",
                border_style="blue"
            ))
        else:
            duckdb_content["duckdb_response"].update(Panel(
                Markdown(duckdb_result["response"]),
                title="Réponse",
                border_style="blue"
            ))
            
        duckdb_content["duckdb_query"].update(Panel(
            Syntax(duckdb_result["query"], "sql", theme="monokai", line_numbers=True),
            title="Requête SQL générée",
            border_style="blue"
        ))
        duckdb_content["duckdb_time"].update(Panel(
            f"[bold blue]Temps de réponse:[/bold blue] {duckdb_time:.2f} secondes",
            border_style="blue"
        ))
        
        # Create NetworkX panel content
        networkx_content = Layout()
        networkx_content.split_column(
            Layout(name="networkx_title"),
            Layout(name="networkx_response", ratio=1),
            Layout(name="networkx_query", ratio=2),
            Layout(name="networkx_time")
        )
        
        networkx_content["networkx_title"].update(Panel("[bold orange]Agent NetworkX[/bold orange]"))
        
        # Show error if present
        if "error" in networkx_result:
            networkx_content["networkx_response"].update(Panel(
                f"[bold red]{networkx_result['response']}[/bold red]\n\n[italic]Erreur: {networkx_result['error']}[/italic]",
                title="Réponse",
                border_style="orange"
            ))
        else:
            networkx_content["networkx_response"].update(Panel(
                Markdown(networkx_result["response"]),
                title="Réponse",
                border_style="orange"
            ))
            
        # Format the query based on whether it's a string or dictionary
        query_string = ""
        if isinstance(networkx_result["query"], dict):
            query_string = json.dumps(networkx_result["query"], indent=2)
        else:
            query_string = str(networkx_result["query"])
            
        networkx_content["networkx_query"].update(Panel(
            Syntax(query_string, "json", theme="monokai", line_numbers=True),
            title="Requête GraphQL générée",
            border_style="orange"
        ))
        networkx_content["networkx_time"].update(Panel(
            f"[bold orange]Temps de réponse:[/bold orange] {networkx_time:.2f} secondes",
            border_style="orange"
        ))
        
        # Update main layout with content
        layout["results"]["duckdb"].update(duckdb_content)
        layout["results"]["networkx"].update(networkx_content)
        
        # Render the complete layout
        console.print(layout)
        
        # Display time comparison
        self.display_time_comparison(duckdb_time, networkx_time)
        
        # Return both results for further analysis
        return {
            "duckdb": duckdb_result,
            "networkx": networkx_result
        }
    
    def display_time_comparison(self, duckdb_time, networkx_time):
        """Display a visual comparison of response times"""
        console.print("\n[bold cyan]Comparaison des temps de réponse[/bold cyan]")
        
        # Create comparison table
        table = Table(title="Temps de réponse", box=box.SIMPLE_HEAVY)
        table.add_column("Agent", style="cyan")
        table.add_column("Temps (s)", justify="right")
        
        table.add_row("DuckDB", f"{duckdb_time:.2f}")
        table.add_row("NetworkX", f"{networkx_time:.2f}")
        
        console.print(table)
        
        # Create comparison chart if running in environment that supports it
        try:
            plt.figure(figsize=(10, 4))
            bars = plt.bar(['DuckDB', 'NetworkX'], [duckdb_time, networkx_time], 
                         color=['#3366CC', '#FF9900'])
            
            # Add values on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height+0.1,
                        f'{height:.2f}s', ha='center', va='bottom')
                
            plt.ylabel('Temps (secondes)')
            plt.title('Comparaison des temps de réponse')
            plt.tight_layout()
            
            # Save the plot to a file
            plot_filename = f'response_time_comparison_{int(time.time())}.png'
            plt.savefig(plot_filename)
            console.print(f"[green]Graphique sauvegardé dans '{plot_filename}'[/green]")
        except Exception as e:
            console.print(f"[yellow]Note: Graphique non généré ({str(e)})[/yellow]")
    
    def display_evaluation_results(self):
        """Display overall evaluation results from previous benchmarks"""
        console.print("\n\n[bold cyan]RÉSULTATS D'ÉVALUATION COMPARATIVE COMPLÈTE[/bold cyan]")
        console.print("[italic]Basé sur 100 questions en français[/italic]\n")
        
        # Create a table with the results
        table = Table(title="Comparaison des performances", box=box.DOUBLE)
        table.add_column("Métrique", style="cyan")
        table.add_column("DuckDB", justify="right", style="blue")
        table.add_column("NetworkX", justify="right", style="orange")
        table.add_column("Différence", justify="right", style="green")
        
        for i, metric in enumerate(self.evaluation_results['Métrique']):
            duckdb_val = f"{self.evaluation_results['DuckDB'][i]:.2f}"
            networkx_val = f"{self.evaluation_results['NetworkX'][i]:.2f}"
            diff_val = f"{self.evaluation_results['Différence'][i]:.2f}"
            
            # Add units where appropriate
            if "Temps" in metric:
                duckdb_val += "s"
                networkx_val += "s" 
                diff_val += "s"
            elif "%" in metric:
                duckdb_val += "%"
                networkx_val += "%"
                diff_val += "%"
                
            table.add_row(metric, duckdb_val, networkx_val, diff_val)
            
        console.print(table)
        
        # Create comparison chart if running in environment that supports it
        try:
            metrics = self.evaluation_results['Métrique']
            x = np.arange(len(metrics))
            width = 0.35

            fig, ax = plt.subplots(figsize=(12, 6))
            rects1 = ax.bar(x - width/2, self.evaluation_results['DuckDB'], width, 
                         label='DuckDB', color='#3366CC')
            rects2 = ax.bar(x + width/2, self.evaluation_results['NetworkX'], width, 
                         label='NetworkX', color='#FF9900')

            # Add labels, title and legend
            ax.set_ylabel('Valeur')
            ax.set_title('Comparaison des performances DuckDB vs NetworkX')
            ax.set_xticks(x)
            ax.set_xticklabels(metrics)
            ax.legend()

            # Add values on top of bars
            def autolabel(rects):
                for rect in rects:
                    height = rect.get_height()
                    ax.annotate(f'{height:.2f}',
                                xy=(rect.get_x() + rect.get_width() / 2, height),
                                xytext=(0, 3),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom')

            autolabel(rects1)
            autolabel(rects2)

            fig.tight_layout()
            # Save with timestamp to avoid overwriting
            plot_filename = f'overall_performance_comparison_{int(time.time())}.png'
            plt.savefig(plot_filename)
            console.print(f"[green]Graphique global sauvegardé dans '{plot_filename}'[/green]")
        except Exception as e:
            console.print(f"[yellow]Note: Graphique global non généré ({str(e)})[/yellow]")
    
    def display_key_insights(self):
        """Display key insights from the comparison"""
        console.print("\n\n[bold cyan]POINTS CLÉS DE LA COMPARAISON[/bold cyan]\n")
        
        insights = [
            {
                "title": "Points forts de l'approche DuckDB",
                "items": [
                    "Meilleur taux de réussite global (43% vs 17%)",
                    "Requêtes analytiques plus efficaces (agrégations, statistiques)",
                    "Meilleure gestion des requêtes complexes à multiples critères",
                    "Temps de réponse légèrement meilleur sur la plupart des requêtes"
                ],
                "style": "blue"
            },
            {
                "title": "Points forts de l'approche NetworkX",
                "items": [
                    "Navigation naturelle dans les relations entre entités",
                    "Meilleure gestion des requêtes de connectivité (chemins entre entités)",
                    "Potentiel pour la recherche de similarité par embeddings",
                    "Structure adaptée aux requêtes sur les relations directes"
                ],
                "style": "orange"
            },
            {
                "title": "Limitations communes",
                "items": [
                    "Difficulté à traiter des questions nécessitant des inférences (ex: allergies croisées)",
                    "Performance limitée des modèles de langage légers",
                    "Dépendance à la qualité des données dans Open Food Facts",
                    "Complexité d'interprétation des structures de données imbriquées"
                ],
                "style": "yellow"
            },
            {
                "title": "Leçons apprises",
                "items": [
                    "Importance cruciale de la documentation précise de la structure des données",
                    "Valeur d'une méthode d'évaluation rigoureuse et reproductible",
                    "Avantage des approches SQL pour des questions analytiques sur données tabulaires",
                    "Importance de présenter les limites du système aux utilisateurs"
                ],
                "style": "green"
            }
        ]
        
        for insight in insights:
            panel = Panel(
                "\n".join([f"• {item}" for item in insight["items"]]),
                title=f"[bold {insight['style']}]{insight['title']}[/bold {insight['style']}]",
                border_style=insight["style"],
                box=box.ROUNDED
            )
            console.print(panel)
    
    def run_demo(self):
        """Run the full demonstration"""
        console.print(Panel.fit(
            "[bold cyan]DÉMONSTRATION DES AGENTS CONVERSATIONNELS OPEN FOOD FACTS[/bold cyan]\n\n"
            "Cette démonstration compare deux approches:\n"
            "1. [bold blue]Agent DuckDB[/bold blue] - Transformation des questions en requêtes SQL\n"
            "2. [bold orange]Agent NetworkX[/bold orange] - Utilisation d'un graphe de connaissances\n\n"
            "Chaque question sera traitée par les deux agents pour comparaison directe.",
            title=f"Open Food Facts Conversational Agent - {datetime.now().strftime('%d/%m/%Y')}",
            border_style="cyan",
            box=box.DOUBLE
        ))
        
        # Simulate initialization
        self.simulate_loading("Initialisation des agents...", duration=2.0)
        
        # Ask the user which question to demo
        console.print("\n[bold]Choisissez une question à démontrer:[/bold]")
        for i, q in enumerate(self.questions, 1):
            console.print(f"  {i}. {q['title']}")
        console.print(f"  {len(self.questions)+1}. Toutes les questions")
        console.print(f"  {len(self.questions)+2}. Afficher uniquement les résultats d'évaluation")
        console.print(f"  {len(self.questions)+3}. Afficher uniquement les points clés")
        
        try:
            choice = int(input("\nVotre choix (1-6): "))
            
            if choice == len(self.questions) + 3:
                # Show only key insights
                self.display_key_insights()
                return
                
            if choice == len(self.questions) + 2:
                # Show only evaluation results
                self.display_evaluation_results()
                return
                
            if choice == len(self.questions) + 1:
                # Run all questions
                for question in self.questions:
                    self.display_agent_comparison(question)
                    console.print("\n" + "-" * 80 + "\n")
                    
                    # Ask if user wants to continue
                    if question != self.questions[-1]:  # Not the last question
                        cont = input("Appuyez sur Entrée pour continuer, ou 'q' pour quitter: ")
                        if cont.lower() == 'q':
                            break
                        
            elif 1 <= choice <= len(self.questions):
                # Run the selected question
                self.display_agent_comparison(self.questions[choice-1])
            else:
                console.print("[bold red]Choix invalide[/bold red]")
                return
                
            # Display overall evaluation results
            self.display_evaluation_results()
            
            # Display key insights
            self.display_key_insights()
            
        except ValueError:
            console.print("[bold red]Veuillez entrer un nombre valide[/bold red]")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Démonstration interrompue[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]Erreur: {str(e)}[/bold red]")
            traceback.print_exc()

if __name__ == "__main__":
    # Run the demo
    demo = AgentDemo()
    demo.run_demo()