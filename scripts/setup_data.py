"""Setup script to generate and index financial documents."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.document_generator import generate_financial_documents
from src.rag.chunking import chunk_documents
from src.rag.embeddings import embed_texts
from src.rag.vector_store import VectorStore
from src.tools.rag_search import init_rag_search


def main():
    print("="*50)
    print("BIST Analysis Agent - Data Setup")
    print("="*50)

    # Step 1: Generate documents from API data
    print("\n[1/4] Generating financial documents...")
    documents = generate_financial_documents()

    # Step 2: Chunk documents
    print("\n[2/4] Chunking documents...")
    chunks = chunk_documents(documents)

    # Step 3: Generate embeddings
    print("\n[3/4] Generating embeddings...")
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts, is_query=False)
    print(f"Generated {len(embeddings)} embeddings")

    # Step 4: Index in vector store
    print("\n[4/4] Indexing in LanceDB...")
    vector_store = VectorStore()
    vector_store.create_index(chunks, embeddings)

    # Initialize RAG search tool
    init_rag_search(vector_store)

    print("\n" + "="*50)
    print("Data setup complete!")
    print("="*50)

    # Test search
    print("\nTesting search...")
    results = vector_store.search("THYAO finansal analiz", top_k=3)
    print(f"Found {len(results)} results for test query")


if __name__ == "__main__":
    main()
