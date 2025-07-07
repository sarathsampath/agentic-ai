import asyncio
import json
import re
from typing import Dict, List, Any, Optional
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()

class IntelligentQueryClient:
    def __init__(self):
        self.servers = {
            "docs": StdioServerParameters(
                command="python3",
                args=["google-docs-reader.py"],
                env=None,
            ),
            "search": StdioServerParameters(
                command="python3",
                args=["google-search-server.py"],
                env=None,
            )
        }
        self.sessions = {}
        self.stdio_contexts = {}
        self.available_tools = {}

        if(os.getenv("GROG_API_KEY") is None):
            print("GROG_API_KEY is not set")
            exit(1)

        try:
            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=os.getenv("GROG_API_KEY")
            )
        except Exception as e:
            print(f"Warning: Could not initialize OpenAI client: {e}")
            self.client = None

    async def connect_all(self):
        """Connect to all servers."""
        print("🔌 Connecting to multiple MCP servers...")

        for name, params in self.servers.items():
            try:
                print(f"  Connecting to {name} server...")

                # Create stdio context
                self.stdio_contexts[name] = stdio_client(params)
                read, write = await self.stdio_contexts[name].__aenter__()

                # Create session
                session = ClientSession(read, write)
                await session.__aenter__()
                await session.initialize()

                self.sessions[name] = session

                # Get available tools from this server
                tools = await session.list_tools()
                self.available_tools[name] = [tool.name for tool in tools.tools]

                print(f"  ✅ {name} server connected with tools: {self.available_tools[name]}")

            except Exception as e:
                print(f"  ❌ Failed to connect to {name} server: {e}")
                self.sessions[name] = None
                self.available_tools[name] = []

    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get descriptions of available tools for AI processing."""
        tool_descriptions = {
            "read_pdf_from_drive": {
                "description": "Read PDF content from Google Drive. Use this when user wants to read or extract text from a PDF file stored in Google Drive.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "Google Drive file ID"}
                    },
                    # "required": ["file_id"]
                }
            },
            "web_search": {
                "description": "Search the web for information, news, trends, or general knowledge. Use this when user wants to find information about Presidio from the internet.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            },

        }

        # Only include tools that are actually available
        available_tools = []
        for server_name, tools in self.available_tools.items():
            for tool_name in tools:
                if tool_name in tool_descriptions:
                    tool_info = tool_descriptions[tool_name].copy()
                    tool_info["server"] = server_name
                    available_tools.append({
                        "type": "function",
                        "function": {
                            "name": f"{server_name}_{tool_name}",  # Prefix with server name
                            "description": f"[{server_name.upper()}] {tool_info['description']}",
                            "parameters": tool_info["parameters"]
                        }
                    })

        return available_tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        """Call a tool on a specific server."""
        if server_name not in self.sessions or not self.sessions[server_name]:
            raise ValueError(f"Server {server_name} not connected")

        if tool_name not in self.available_tools.get(server_name, []):
            raise ValueError(f"Tool {tool_name} not available on server {server_name}")

        return await self.sessions[server_name].call_tool(tool_name, arguments)

    async def process_intelligent_query(self, query: str) -> dict:
        try:
            # Get available tools for the AI
            available_tools = self.get_tool_descriptions()

            if not available_tools:
                return {
                    "success": False,
                    "error": "No tools available on the server"
                }

            # Ask AI to determine which tools to use
            chat_response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intelligent assistant that can use various tools from multiple servers. Analyze the user's query and determine which tools to use. Extract any necessary parameters from the query."
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}\n\nAvailable tools: {json.dumps(available_tools, indent=2)}"
                    }
                ],
                tools=available_tools,
                tool_choice="auto"
            )

            response_message = chat_response.choices[0].message
            results = []
            tool_calls_made = []

            # Execute tool calls
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    try:
                        args = json.loads(tool_call.function.arguments)

                        # Parse server and tool name from the prefixed tool name
                        tool_name_parts = tool_call.function.name.split('_', 1)
                        if len(tool_name_parts) == 2:
                            server_name, actual_tool_name = tool_name_parts

                            # Execute the appropriate tool on the correct server
                            result = await self.call_tool(server_name, actual_tool_name, args)

                            if result:
                                tool_result = result.content[0].text if result.content else "No content"
                                results.append({
                                    "server": server_name,
                                    "tool": actual_tool_name,
                                    "arguments": args,
                                    "result": tool_result
                                })
                                tool_calls_made.append(f"{server_name}_{actual_tool_name}")

                    except Exception as e:
                        results.append({
                            "tool": tool_call.function.name,
                            "error": str(e)
                        })

            # Ask AI to synthesize the results
            if results:
                synthesis_prompt = f"""
                Based on the following tool results from multiple servers, provide a comprehensive answer to the original query: "{query}"

                Tool Results:
                {json.dumps(results, indent=2)}

                Please provide a clear, well-structured response that addresses the user's query.
                If multiple tools were used, synthesize the information into a coherent answer.
                """

                final_response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": synthesis_prompt}]
                )

                final_answer = final_response.choices[0].message.content
            else:
                final_answer = "I couldn't find any relevant tools to answer your query. Please try rephrasing or ask for something more specific."

            return {
                "success": True,
                "query": query,
                "tools_used": tool_calls_made,
                "final_answer": final_answer,
                "raw_results": results
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    async def interactive_mode(self):
        """Run the client in interactive mode."""
        for tool in self.available_tools:
            print(f"  - {tool}")

        while True:
            try:
                query = input("🔍 Enter your query: ").strip()

                print("🔄 Processing query...")
                result = await self.process_intelligent_query(query)
                print(result, "result")
                if result["success"]:
                    print("✅ Result:")
                    if "method" in result and result["method"] == "direct_tool":
                        print(f" Tool used: {result['tool']}")
                        print(f"📄 Result: {result['result'][:500]}...")
                    else:
                        print(f" AI processed using tools: {', '.join(result['tools_used'])}")
                        print(f"📄 Answer: {result['final_answer']}")
                else:
                    print(f"❌ Error: {result['error']}")

                print("-" * 60)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

    async def disconnect_all(self):
        """Disconnect from all servers."""
        print("🔌 Disconnecting from all servers...")

        for name in list(self.sessions.keys()):
            try:
                if self.sessions[name]:
                    await self.sessions[name].__aexit__(None, None, None)
                if name in self.stdio_contexts:
                    await self.stdio_contexts[name].__aexit__(None, None, None)
                print(f"  ✅ Disconnected from {name} server")
            except Exception as e:
                print(f"  ❌ Error disconnecting from {name} server: {e}")



async def main():
    client = IntelligentQueryClient()

    try:
        print("🔌 Connecting to MCP server...")
        await client.connect_all()
        print("Connected successfully!")

        await client.interactive_mode()

    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        await client.disconnect_all()
        print("👋 Disconnected from server")


if __name__ == "__main__":
    asyncio.run(main())