from sentence_transformers import SentenceTransformer

# Load the Nomic MoE model
model = SentenceTransformer(
    "nomic-ai/nomic-embed-text-v2-moe",
    trust_remote_code=True,
)

# Prepare questions and answers
queries = ["¿Dónde puedo comprar café?"]  # Where can I buy coffee?
documents = [
    "The local grocery store potatoes and other foods.",
    "The library has a small café where you can purchase coffee.",
    "Gum is available at the gas station convenience store."
]

# Encode the questions and answers using the required prompts
query_embeddings = model.encode(queries, prompt_name="query")
document_embeddings = model.encode(documents, prompt_name="passage")
print(query_embeddings.shape, document_embeddings.shape)
# (1, 768) (3, 768)

# Compute the similarity between the questions and answers
similarity = model.similarity(query_embeddings, document_embeddings)
print(similarity)
# tensor([[0.2718, 0.5288, 0.3059]])
# As expected, the second document is deemed the most similar to the query