import wikipedia
import os
from openai import OpenAI
from dotenv import load_dotenv
from mail_send import send_email
from fastapi import FastAPI

load_dotenv()

app = FastAPI()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROG_API_KEY")
)

def get_wikipedia_summary(topic: str, sentences: int = 3) -> str:
    try:
        return wikipedia.summary(topic, sentences=sentences)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Ambiguous topic. Options include: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for the given topic."


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_wikipedia_summary",
            "description": "Get information about people, places, concepts, historical events, organizations, or any general knowledge topic from Wikipedia. Use this when the user asks 'who is', 'what is', 'tell me about', or needs factual information about any topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The person, place, concept, or topic to search for on Wikipedia"
                    },
                    "sentences": {
                        "type": "integer",
                        "description": "Number of sentences in the summary",
                        "default": 3
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to a recipient",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "The email address of the recipient"},
                    "subject": {"type": "string", "description": "The subject of the email"},
                    "body": {"type": "string", "description": "The body of the email"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    }
]

@app.get("/user_input")
def user_input(query: str):
    try:
        chat_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": query}
            ],
            tools=tools,
            tool_choice="auto"
        )

        response_message = chat_response.choices[0].message
        final_response = ""

        # Handle tool calls
        if response_message.tool_calls:
            print("AI wants to use tools:")
            tool_results = []

            for tool_call in response_message.tool_calls:
                print(f"Calling tool: {tool_call.function.name}")

                import json
                args = json.loads(tool_call.function.arguments)

                if tool_call.function.name == "get_wikipedia_summary":
                    result = get_wikipedia_summary(args["topic"], args.get("sentences", 3))
                    tool_results.append(f"Wikipedia: {result}")
                    print(f"Wikipedia result: {result}")

                elif tool_call.function.name == "send_email":
                    result = send_email(args["to"], args["subject"], args["body"])
                    tool_results.append(f"Email: {result}")
                    print(f"Email result: {result}")

                else:
                    tool_results.append(f"Unknown tool: {tool_call.function.name}")
                    print(f"Unknown tool: {tool_call.function.name}")

            # Return the tool results
            final_response = " | ".join(tool_results)

        else:
            print("Response without tools:")
            print(response_message.content)
            final_response = response_message.content or "No response generated"

        return {
            "query": query,
            "response": final_response,
            "tools_used": bool(response_message.tool_calls)
        }

    except Exception as e:
        return {
            "query": query,
            "response": f"Error: {str(e)}",
            "tools_used": False
        }