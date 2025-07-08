from rag_initialization.initializedb import initialize_db
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("rag-search-server")


@mcp.tool()
def get_context_with_sources(query):
        collection = initialize_db()
        results =  semantic_search(collection, query)
        return results


def semantic_search(collection, query, k=5):

    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    return results

if __name__ == "__main__":
    print("RAG Search Server started")
    mcp.run()
    # print(get_context_with_sources("What are the benefits of Presidio?"))