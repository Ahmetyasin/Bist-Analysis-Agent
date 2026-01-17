"""RAG search tool for financial documents."""
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

# Will be initialized after vector store is set up
_vector_store = None


class RAGSearchInput(BaseModel):
    query: str = Field(description="Search query for financial documents")
    ticker: Optional[str] = Field(default=None, description="Filter by company ticker")
    top_k: int = Field(default=5, description="Number of results to return")


def init_rag_search(vector_store):
    """Initialize RAG search with vector store."""
    global _vector_store
    _vector_store = vector_store


def search_documents(query: str, ticker: Optional[str] = None, top_k: int = 5) -> dict:
    """
    Search financial documents using RAG.

    Args:
        query: Search query
        ticker: Optional ticker filter
        top_k: Number of results

    Returns:
        Dictionary with search results
    """
    global _vector_store

    if _vector_store is None:
        return {
            "query": query,
            "results": [],
            "error": "Vector store not initialized. Run setup_data.py first."
        }

    try:
        # Build filter
        filter_condition = None
        if ticker:
            filter_condition = f"ticker = '{ticker.upper()}'"

        # Search
        results = _vector_store.search(
            query=query,
            top_k=top_k,
            filter=filter_condition
        )

        formatted_results = []
        for r in results:
            formatted_results.append({
                "text": r.get("text", ""),
                "ticker": r.get("ticker", "N/A"),
                "document_type": r.get("document_type", "N/A"),
                "section": r.get("section", "N/A"),
                "score": r.get("score", 0),
                "source": f"{r.get('ticker', 'N/A')} - {r.get('document_type', 'N/A')}"
            })

        return {
            "query": query,
            "results": formatted_results,
            "total_found": len(formatted_results)
        }

    except Exception as e:
        return {
            "query": query,
            "results": [],
            "error": str(e)
        }


@tool(args_schema=RAGSearchInput)
def RAGSearchTool(query: str, ticker: Optional[str] = None, top_k: int = 5) -> str:
    """
    Search through financial documents and reports.
    Returns relevant passages from annual reports, quarterly filings, and analyses.
    Use this for detailed company information, financial analysis, and sector insights.
    """
    data = search_documents(query, ticker, top_k)

    if data.get("error"):
        return f"* Arama hatasi: {data['error']}"

    if not data["results"]:
        return f"'{query}' icin sonuc bulunamadi."

    result = f"## Dokuman Aramasi: '{query}'\n\n"
    result += f"Bulunan: {data['total_found']} sonuc\n\n"

    for i, r in enumerate(data["results"], 1):
        result += f"### Sonuc {i} ({r['source']})\n"
        result += f"Bolum: {r['section']}\n"
        result += f"```\n{r['text'][:500]}{'...' if len(r['text']) > 500 else ''}\n```\n\n"

    return result
