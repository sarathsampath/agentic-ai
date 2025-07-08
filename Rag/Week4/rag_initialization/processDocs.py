from docx import Document
import PyPDF2
import os

def read_document(file_path: str) -> str:
    """Read content from a document file"""
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.docx':
        # Read Word document
        doc = Document(file_path)
        content = []
        for paragraph in doc.paragraphs:
            content.append(paragraph.text)
        return '\n'.join(content)

    elif file_extension == '.pdf':
        # Read PDF document
        content = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content.append(page.extract_text())
        return '\n'.join(content)

    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """Split text into chunks for processing"""
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")
    print(f"Chunk size: {chunk_size}, Chunk overlap: {chunk_overlap}")
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        if end > text_length:
            end = text_length

        chunk = text[start:end]
        chunks.append(chunk)

        # Move start position considering overlap
        start += chunk_size - chunk_overlap
        if start <= 0:
            start = end

    return [chunk.strip() for chunk in chunks if chunk.strip()]

def process_document(file_path: str):
    """Process a single document and prepare it for ChromaDB"""
    try:
        # Read the document
        content = read_document(file_path)
        print("Raw document content:", repr(content))

        # Split into chunks
        chunks = split_text(content)
        print("Number of Chunks:", len(chunks))
        print("First chunk:", chunks[0] if chunks else "No chunks")

        # Prepare metadata
        file_name = os.path.basename(file_path)
        metadatas = [{"source": file_name, "chunk": i} for i in range(len(chunks))]
        ids = [f"{file_name}_chunk_{i}" for i in range(len(chunks))]

        return ids, chunks, metadatas
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return [], [], []
