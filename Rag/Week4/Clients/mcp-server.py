from fastmcp import FastMCP
import requests


# Create an MCP server
mcp = FastMCP("Demo")

# Add a tool, will be converted into JSON spec for function calling
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a data resource, e.g. displayed on new chats
@mcp.resource("user://{id}")
def get_user(id: str) -> str:
    """Get a personalized greeting"""
    api_url = f"https://dummyjson.com/users/{id}"
    response = requests.get(api_url)
    return response.json()

# Specific prompt templates for better use
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"

# Add this to make the server actually run
if __name__ == "__main__":
    mcp.run()