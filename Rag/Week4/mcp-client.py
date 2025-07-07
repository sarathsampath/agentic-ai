import asyncio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


async def main():
    # Commands for running/connecting to MCP Server
    server_params = StdioServerParameters(
        command="python3",  # Executable
        args=["mcp-server.py"],  # Optional command line arguments
        env=None,  # Optional environment variables
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write
        ) as session:
            # Initialize the connection
            await session.initialize()

            # List available prompts
            prompts = await session.list_prompts()

            # # Get a prompt
            # prompt = await session.get_prompt(
            #     "example-prompt", arguments={"arg1": "value"}
            # )

            # List available resources
            resources = await session.list_resources()

            resource_result = await session.read_resource("user://1")
            print(resource_result, "resource_result")

            # List available tools
            tools = await session.list_tools()

            result = await session.call_tool("add", arguments={"a": 1, "b": 2})

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
