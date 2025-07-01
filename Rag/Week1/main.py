from processDocs import process_document
from Rag.Week1.initializedb import initialize_db, add_to_collection

def main():
    collection = initialize_db();
    print("Collection initialized")
    ids, chunks, metadatas = process_document("Employee Handbook 2025.pdf")
    print("Documents processed")
    add_to_collection(collection, ids, chunks, metadatas)
    print("Documents added to collection")


if __name__ == "__main__":
    main()