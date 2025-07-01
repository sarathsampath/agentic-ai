import os
import json
import boto3
from dotenv import load_dotenv

def initialize_ai():
    load_dotenv()
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',  # or your specific region
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    return bedrock

def get_prompt(context, conversation_history, query):
  prompt = f"""Based on the following context and conversation history, please provide a relevant and contextual response.
    If the answer cannot be derived from the context, only use the conversation history or say "I cannot answer this based on the provided information."

    Context from documents:
    {context}

    Previous conversation:
    {conversation_history}

    Human: {query}

    Assistant:"""
  return prompt

def generate_response(client, query: str, context: str, conversation_history: str = ""):
    """Generate a streaming response using AWS Bedrock Claude"""
    prompt = get_prompt(context, conversation_history, query)
    print("--------------------------------",prompt,"--------------------------------")
    body = json.dumps({
        "prompt": f"\n\nHuman: You are a helpful assistant that answers questions based on the provided context.\n\n{prompt}\n\nAssistant:",
        "max_tokens_to_sample": 500,
        "temperature": 0.1,
        "top_k": 50,
        "top_p": 0.7,
        "stop_sequences": ["\n\nHuman:"]
    })

    try:
        response = client.invoke_model_with_response_stream(
            body=body,
            modelId="anthropic.claude-v2",  # or claude-v3, claude-3-sonnet, etc.
            accept="application/json",
            contentType="application/json"
        )

        for event in response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if "completion" in chunk:
                completion_text = chunk["completion"]
                print(completion_text, end="", flush=True)
                yield completion_text  # Yield each chunk for streaming

    except Exception as e:
        yield f"Error generating response from Claude: {str(e)}"



def contextualize_query(query: str, conversation_history: str, client: any):
    """Convert follow-up questions into standalone queries"""
    prompt = f"""\
    Human: Given a chat history and the latest user question
    which might reference context in the chat history, formulate a standalone
    question which can be understood without the chat history. Do NOT answer
    the question, just reformulate it if needed and otherwise return it as is.

    Chat history:
    {conversation_history}


    Question:
    {query}

    Assistant:"""



    try:
        body = json.dumps({
            "prompt": f"\n\nHuman: You are a helpful assistant that answers questions based on the provided context.\n\n{prompt}\n\nAssistant:",
            "max_tokens_to_sample": 500,
            "temperature": 0.1,
            "top_k": 50,
            "top_p": 0.7,
            "stop_sequences": ["\n\nHuman:"]
        })
        response = client.invoke_model_with_response_stream(
            body=body,
            modelId="anthropic.claude-v2",  # or claude-v3, claude-3-sonnet, etc.
            accept="application/json",
            contentType="application/json"
        )

        for event in response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if "completion" in chunk:
                completion_text = chunk["completion"]
                print(completion_text, end="", flush=True)
                yield completion_text  # Yield each chunk for streaming

    except Exception as e:
        yield f"Error generating response from Claude: {str(e)}"
