"""Embedding generation using Gemini."""
from typing import List
import google.generativeai as genai
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

# Configure Gemini
genai.configure(api_key=config.GEMINI_API_KEY)


def get_embeddings(texts: List[str], task_type: str = "retrieval_document") -> List[List[float]]:
    """
    Generate embeddings for a list of texts using Gemini.

    Args:
        texts: List of texts to embed
        task_type: Either "retrieval_document" or "retrieval_query"

    Returns:
        List of embedding vectors
    """
    embeddings = []

    # Process in batches (Gemini has limits)
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        for text in batch:
            try:
                result = genai.embed_content(
                    model=config.EMBEDDING_MODEL,
                    content=text,
                    task_type=task_type
                )
                embeddings.append(result['embedding'])
            except Exception as e:
                print(f"Embedding error: {e}")
                # Return zero vector on error
                embeddings.append([0.0] * config.EMBEDDING_DIMENSION)

    return embeddings


def embed_texts(texts: List[str], is_query: bool = False) -> List[List[float]]:
    """
    Convenience function for embedding texts.

    Args:
        texts: Texts to embed
        is_query: True if embedding a query, False for documents

    Returns:
        Embedding vectors
    """
    task_type = "retrieval_query" if is_query else "retrieval_document"
    return get_embeddings(texts, task_type)
