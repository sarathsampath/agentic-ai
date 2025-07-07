from googleapiclient.discovery import build
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
load_dotenv()


mcp = FastMCP("google-search-server")


@mcp.tool()
async def web_search(query: str, search_type: str = "general") -> dict:
    """
    Search the web for industry information, trends, and regulatory updates.

    Args:
        query: Search query (e.g., "AI industry benchmarks 2024", "GDPR regulatory updates")
        search_type: Type of search - "general", "trends", "regulatory", "benchmarks"
    """
    try:
        # Google Custom Search API
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

        # Build search query based on type
        if search_type == "trends":
            query += " trends 2024 latest"
        elif search_type == "regulatory":
            query += " regulatory compliance updates"
        elif search_type == "benchmarks":
            query += " industry benchmarks metrics"

        service = build("customsearch", "v1", developerKey=api_key)
        result = service.cse().list(q=query, cx=search_engine_id, num=10).execute()

        return {
            "success": True,
            "results": result.get("items", []),
            "search_type": search_type
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    mcp.run()