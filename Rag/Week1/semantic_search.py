from typing import Optional
from Rag.Week1.initializedb import initialize_db
from Rag.Week1.ai_client import contextualize_query, generate_response, initialize_ai
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from session import create_session, add_message, get_conversation_history, format_history_for_prompt

app = FastAPI()

@app.get("/stream")
async def stream_response(prompt: str, sessionId: Optional[str] = None):
    try:
        print(f"Prompt: {prompt}")
        collection = initialize_db()
        if(sessionId is None):
            sessionId = create_session()

        print(f"Session ID: {sessionId}")


        results = semantic_search(collection, prompt)
        context, sources = get_context_with_sources(results)
        ai = initialize_ai()

        conversation_history = format_history_for_prompt(sessionId)

        result = contextualize_query(prompt, conversation_history, ai)
        print(f"Result: {result}")
        # Collect the full response
        full_response = ""

        def generate_stream():
            nonlocal full_response
            try:
                print("--------------------------------",conversation_history,"--------------------------------")
                for chunk in generate_response(ai, result, context, conversation_history):
                    full_response += chunk
                    yield chunk
            finally:
                # Ensure the response is saved even if streaming stops
                if full_response.strip():
                    add_message(sessionId, "assistant", full_response)
                    print(f"Saved response to session {sessionId}: {full_response[:100]}...")

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        print(f"Error in stream_response: {e}")
        return {"error": str(e)}

def semantic_search(collection, query, k=5):
    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    return results

def get_context_with_sources(results):
    """Extract context and source information from search results"""
    # Check if results contain documents
    if not results or not results.get('documents') or not results['documents'][0]:
        return "No relevant documents found.", []

    # Combine document chunks into a single context
    context = "\n\n".join(results['documents'][0])

    # Format sources with metadata
    sources = []
    if results.get('metadatas') and results['metadatas'][0]:
        sources = [
            f"{meta['source']} (chunk {meta['chunk']})"
            for meta in results['metadatas'][0]
        ]

    return context, sources
