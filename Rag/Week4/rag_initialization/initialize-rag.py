# from processDocs import process_document
from initializedb import initialize_db, add_to_collection
from processDocs import process_document
import os

def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """Split text into chunks for processing, avoiding infinite loops."""
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        # Always move start forward
        start += chunk_size - chunk_overlap

    return chunks

def main():
    try:
        collection = initialize_db()
        print("Collection initialized")
        ids, chunks, metadatas = process_document("Employee Handbook 2025.pdf")
        print("Documents processed")
        print("IDs:", ids)
        print("Chunks:", chunks)
        print("Metadatas:", metadatas)
        add_to_collection(collection, ids, chunks, metadatas)
        print("Documents added to collection")
        print("Collection count after ingestion:", collection.count())
    except Exception as e:
        print("Error during ingestion:", e)


if __name__ == "__main__":
    main()