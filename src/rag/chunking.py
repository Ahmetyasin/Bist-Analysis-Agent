"""Document chunking for RAG."""
from typing import List
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


def chunk_documents(documents: list) -> list:
    """
    Chunk documents into smaller pieces for embedding.

    Args:
        documents: List of document dictionaries

    Returns:
        List of chunk dictionaries with metadata
    """
    chunks = []
    chunk_id = 0

    for doc in documents:
        ticker = doc.get("ticker", "GENERAL")
        doc_type = doc.get("document_type", "unknown")
        sector = doc.get("sector", "N/A")

        for section in doc.get("sections", []):
            section_name = section.get("section", "Unknown")
            content = section.get("content", "")

            # Split content into chunks
            words = content.split()
            current_chunk = []
            current_length = 0

            for word in words:
                current_chunk.append(word)
                current_length += len(word) + 1

                if current_length >= config.CHUNK_SIZE:
                    chunk_text = " ".join(current_chunk)
                    chunks.append({
                        "id": f"chunk_{chunk_id}",
                        "text": chunk_text,
                        "ticker": ticker,
                        "document_type": doc_type,
                        "section": section_name,
                        "sector": sector,
                    })
                    chunk_id += 1

                    # Overlap
                    overlap_words = current_chunk[-config.CHUNK_OVERLAP:]
                    current_chunk = overlap_words
                    current_length = sum(len(w) + 1 for w in overlap_words)

            # Remaining content
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                if len(chunk_text.strip()) > 50:  # Minimum chunk size
                    chunks.append({
                        "id": f"chunk_{chunk_id}",
                        "text": chunk_text,
                        "ticker": ticker,
                        "document_type": doc_type,
                        "section": section_name,
                        "sector": sector,
                    })
                    chunk_id += 1

    print(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks
