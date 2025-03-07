import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from food_agent import OpenFoodFactsAgent

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
        if message["role"] == "assistant" and "data" in message and isinstance(message["data"], pd.DataFrame):
            st.markdown(message["content"])
            st.dataframe(message["data"])
        else:
            st.markdown(message["content"])

# Obtenir l'agent
agent = get_agent()

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
                response, data = agent.query(prompt)
                st.markdown(response)
                
                # Afficher les données tabulaires si disponibles
                if data is not None and isinstance(data, pd.DataFrame) and not data.empty:
                    st.dataframe(data)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response, "data": data}
                    )
                else:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )

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
            results, data = agent.get_product_recommendations(product_name, criteria_value)
            
            if isinstance(data, pd.DataFrame) and not data.empty:
                st.success(f"Recommandations pour '{product_name}':")
                st.dataframe(data)
            else:
                st.info(results)

with tab3:
    st.header("Analyse nutritionnelle")
    product_name = st.text_input("Nom du produit:", key="nutr_product")
    
    if st.button("Analyser", key="nutr_button"):
        with st.spinner("Analyse nutritionnelle en cours..."):
            results, data = agent.get_nutritional_analysis(product_name)
            
            if isinstance(data, pd.DataFrame) and not data.empty:
                st.success(f"Analyse nutritionnelle pour '{product_name}':")
                st.dataframe(data)
            else:
                st.info(results)

with tab4:
    st.header("Produits adaptés aux régimes spéciaux")
    diet_type = st.selectbox(
        "Type de régime:",
        ["Végétalien", "Végétarien", "Sans gluten", "Biologique"],
        key="diet_type"
    )
    
    if st.button("Rechercher", key="diet_button"):
        with st.spinner(f"Recherche de produits {diet_type.lower()}s..."):
            results, data = agent.get_dietary_info(diet_type.lower())
            
            if isinstance(data, pd.DataFrame) and not data.empty:
                st.success(f"Produits adaptés au régime {diet_type.lower()}:")
                st.dataframe(data)
            else:
                st.info(results)

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
            product_count_result = agent.execute_custom_cypher("MATCH (p:Product) RETURN count(p) AS count")
            product_count = product_count_result[0]["count"] if product_count_result else 0
            
            brand_count_result = agent.execute_custom_cypher("MATCH (b:Brand) RETURN count(b) AS count")
            brand_count = brand_count_result[0]["count"] if brand_count_result else 0
            
            ingredient_count_result = agent.execute_custom_cypher("MATCH (i:Ingredient) RETURN count(i) AS count")
            ingredient_count = ingredient_count_result[0]["count"] if ingredient_count_result else 0
            
            st.metric("Produits", product_count)
            st.metric("Marques", brand_count)
            st.metric("Ingrédients", ingredient_count)
        except Exception as e:
            st.warning(f"Erreur lors du chargement des statistiques: {str(e)}")
    
    st.header("Exemples de questions")
    st.markdown("""
    - Quels sont les produits de la marque Kroger?
    - Quels produits contiennent du sucre?
    - Quels sont les produits avec un bon Nutri-Score?
    - Quels produits sont sans gluten?
    - Compare le lait 1% et le sirop d'érable
    - Donne-moi des informations nutritionnelles sur le lait 1%
    """)

if __name__ == "__main__":
    # Afficher le message de bienvenue uniquement au premier chargement
    if len(st.session_state.messages) == 0:
        with st.chat_message("assistant"):
            st.markdown("""
            👋 Bonjour! Je suis votre assistant OpenFoodFacts.
            
            Je peux vous aider à:
            - Trouver des informations sur des produits alimentaires
            - Rechercher des produits par marque, ingrédient ou allergène
            - Obtenir des informations nutritionnelles
            - Recommander des produits similaires ou plus sains
            - Et plus encore!
            
            Comment puis-je vous aider aujourd'hui?
            """)
            st.session_state.messages.append(
                {"role": "assistant", "content": "👋 Bonjour! Je suis votre assistant OpenFoodFacts. Comment puis-je vous aider aujourd'hui?"}
            )