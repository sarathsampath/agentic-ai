import asyncio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


async def main():
    # Commands for running/connecting to MCP Server
    server_params = StdioServerParameters(
        command="python3",  # Executable
        args=["google-search-server.py"],  # Optional command line arguments
        env=None,  # Optional environment variables
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write
        ) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(tools, "tools")
            result = await session.call_tool("web_search", arguments={"query": "AI industry benchmarks 2024", "search_type": "general"})

            print(result, "result-tool")


            # print(resources)
            # print(tools)
            # print(prompts)
            # # Read a resource
            # content, mime_type = await session.read_resource("file://some/path")

            # # Call a tool
            # result = await session.call_tool("tool-name", arguments={"arg1": "value"})

if __name__ == "__main__":
    asyncio.run(main())



# <script async src="https://cse.google.com/cse.js?cx=50c0ca2eb594a4ae8">
# </script>
# <div class="gcse-search"></div>

# AIzaSyAMufu4HKw4vuIezpe6StQ9VtjUWHirniE