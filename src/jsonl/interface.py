import streamlit as st
from food_agent import OpenFoodFactsAgent
import pandas as pd
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialiser l'agent
@st.cache_resource
def get_agent():
    return OpenFoodFactsAgent()

# Configuration de la page
st.set_page_config(
    page_title="Assistant OpenFoodFacts",
    page_icon="🥗",
    layout="wide"
)

# Titre et description
st.title("Assistant OpenFoodFacts 🍏")
st.markdown("""
Posez des questions sur les produits alimentaires et obtenez des informations nutritionnelles,
des recommandations de produits similaires ou plus sains, et plus encore.
""")

# Initialiser la session state pour le chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les messages précédents
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "data" in message:
            st.dataframe(message["data"])
        else:
            st.markdown(message["content"])

# Obtenir l'agent
agent = get_agent()

# Fonction pour formatter les résultats en dataframe
def format_results(results):
    if isinstance(results, list) and len(results) > 0 and isinstance(results[0], dict):
        return pd.DataFrame(results)
    elif isinstance(results, str):
        return results
    else:
        return "Aucun résultat trouvé."

# Onglets fonctionnels
tab1, tab2, tab3, tab4 = st.tabs(["Chat général", "Recommandations", "Nutrition", "Régimes spéciaux"])

with tab1:
    # Zone de chat principale
    prompt = st.chat_input("Posez une question sur les produits alimentaires...")
    
    if prompt:
        # Afficher la question de l'utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Obtenir la réponse de l'agent
        with st.chat_message("assistant"):
            with st.spinner("Recherche en cours..."):
                response = agent.query(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

with tab2:
    st.header("Recommandations de produits")
    col1, col2 = st.columns(2)
    
    with col1:
        product_name = st.text_input("Nom du produit:", key="rec_product")
    
    with col2:
        criteria = st.selectbox(
            "Critère de recommandation:",
            ["Plus sains", "Similaires"],
            key="rec_criteria"
        )
    
    if st.button("Trouver des recommandations", key="rec_button"):
        with st.spinner("Recherche de recommandations..."):
            criteria_value = "healthier" if criteria == "Plus sains" else "similar"
            results = agent.get_product_recommendations(product_name, criteria_value)
            
            if results:
                st.success(f"Recommandations pour '{product_name}':")
                st.dataframe(format_results(results))
            else:
                st.info("Aucune recommandation trouvée. Essayez un autre produit.")

with tab3:
    st.header("Analyse nutritionnelle")
    product_name = st.text_input("Nom du produit:", key="nutr_product")
    
    if st.button("Analyser", key="nutr_button"):
        with st.spinner("Analyse nutritionnelle en cours..."):
            results = agent.get_nutritional_analysis(product_name)
            
            if results:
                st.success(f"Analyse nutritionnelle pour '{product_name}':")
                st.dataframe(format_results(results))
            else:
                st.info("Aucune information nutritionnelle trouvée. Essayez un autre produit.")

with tab4:
    st.header("Produits adaptés aux régimes spéciaux")
    diet_type = st.selectbox(
        "Type de régime:",
        ["Végétalien", "Végétarien"],
        key="diet_type"
    )
    
    if st.button("Rechercher", key="diet_button"):
        with st.spinner(f"Recherche de produits {diet_type.lower()}s..."):
            results = agent.get_dietary_info(diet_type.lower())
            
            if isinstance(results, list) and len(results) > 0:
                st.success(f"Produits adaptés au régime {diet_type.lower()}:")
                st.dataframe(format_results(results))
            else:
                st.info(f"Aucun produit {diet_type.lower()} trouvé dans la base de données.")

# Sidebar avec informations supplémentaires
with st.sidebar:
    st.header("À propos")
    st.markdown("""
    Cet assistant utilise:
    - Une base de données Neo4j contenant les produits d'OpenFoodFacts
    - LangChain pour traiter les requêtes en langage naturel
    - Des modèles de langage pour comprendre vos questions
    """)
    
    st.header("Statistiques")
    with st.spinner("Chargement des statistiques..."):
        try:
            product_count = agent.execute_custom_cypher("MATCH (p:Product) RETURN count(p) AS count")[0]["count"]
            brand_count = agent.execute_custom_cypher("MATCH (b:Brand) RETURN count(b) AS count")[0]["count"]
            ingredient_count = agent.execute_custom_cypher("MATCH (i:Ingredient) RETURN count(i) AS count")[0]["count"]
            
            st.metric("Produits", product_count)
            st.metric("Marques", brand_count)
            st.metric("Ingrédients", ingredient_count)
        except:
            st.warning("Erreur lors du chargement des statistiques")
    
    st.header("Exemples de questions")
    st.markdown("""
    - Quels sont les produits de la marque Kroger?
    - Quels produits contiennent du sucre?
    - Quels sont les produits avec un bon Nutri-Score?
    - Quels produits sont sans gluten?
    """)