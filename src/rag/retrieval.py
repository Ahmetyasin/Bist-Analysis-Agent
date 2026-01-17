"""RAG retrieval with reranking."""
from typing import List, Optional
from .vector_store import VectorStore
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


class RAGRetriever:
    """RAG retriever with optional reranking."""

    def __init__(self, vector_store: VectorStore = None):
        """Initialize retriever."""
        self.vector_store = vector_store or VectorStore()

    def retrieve(
        self,
        query: str,
        ticker: Optional[str] = None,
        top_k: int = None,
        use_hybrid: bool = True
    ) -> List[dict]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Search query
            ticker: Optional ticker filter
            top_k: Number of results
            use_hybrid: Use hybrid search

        Returns:
            List of relevant documents with scores
        """
        if top_k is None:
            top_k = config.TOP_K_RETRIEVAL

        # Build filter
        filter_str = None
        if ticker:
            filter_str = f"ticker = '{ticker.upper()}'"

        # Search
        if use_hybrid:
            results = self.vector_store.hybrid_search(query, top_k, filter_str)
        else:
            results = self.vector_store.search(query, top_k, filter_str)

        return results

    def retrieve_with_context(
        self,
        query: str,
        ticker: Optional[str] = None,
        top_k: int = None
    ) -> dict:
        """
        Retrieve documents and format as context.

        Args:
            query: Search query
            ticker: Optional ticker filter
            top_k: Number of results

        Returns:
            Dictionary with context string and sources
        """
        results = self.retrieve(query, ticker, top_k)

        if not results:
            return {
                "context": "Ilgili dokuman bulunamadi.",
                "sources": [],
                "num_results": 0
            }

        # Format context
        context_parts = []
        sources = []

        for i, r in enumerate(results, 1):
            source = f"{r['ticker']} - {r['document_type']} - {r['section']}"
            context_parts.append(f"[Kaynak {i}: {source}]\n{r['text']}")
            sources.append({
                "index": i,
                "source": source,
                "ticker": r["ticker"],
                "section": r["section"]
            })

        return {
            "context": "\n\n".join(context_parts),
            "sources": sources,
            "num_results": len(results)
        }
