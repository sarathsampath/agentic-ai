import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "chroma_db")
)

def initialize_db():
    # Initialize ChromaDB client with persistence
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # Configure sentence transformer embeddings
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Create or get existing collection
    collection = client.get_or_create_collection(
        name="rag_collection",
        embedding_function=sentence_transformer_ef
    )
    return collection


def add_to_collection(collection, ids, texts, metadatas):
    """Add documents to collection in batches"""
    if not texts:
        return

    batch_size = 100
    for i in range(0, len(texts), batch_size):
        end_idx = min(i + batch_size, len(texts))
        collection.add(
            documents=texts[i:end_idx],
            metadatas=metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )
