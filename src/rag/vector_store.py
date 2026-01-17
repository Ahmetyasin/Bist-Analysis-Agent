"""Vector store using LanceDB."""
from typing import List, Optional
import lancedb
from pathlib import Path
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


class VectorStore:
    """LanceDB vector store for financial documents."""

    def __init__(self, db_path: str = None):
        """Initialize vector store."""
        if db_path is None:
            db_path = str(config.EMBEDDINGS_DIR)

        self.db = lancedb.connect(db_path)
        self.table_name = "financial_documents"
        self.table = None

    def create_index(self, chunks: List[dict], embeddings: List[List[float]]):
        """
        Create index from chunks and embeddings.

        Args:
            chunks: List of chunk dictionaries with metadata
            embeddings: List of embedding vectors
        """
        # Prepare data
        data = []
        for chunk, embedding in zip(chunks, embeddings):
            data.append({
                "id": chunk["id"],
                "text": chunk["text"],
                "ticker": chunk.get("ticker", "N/A"),
                "document_type": chunk.get("document_type", "unknown"),
                "section": chunk.get("section", "N/A"),
                "sector": chunk.get("sector", "N/A"),
                "vector": embedding
            })

        # Create or overwrite table
        if self.table_name in self.db.table_names():
            self.db.drop_table(self.table_name)

        self.table = self.db.create_table(self.table_name, data)

        # Create FTS index for hybrid search
        try:
            self.table.create_fts_index("text")
        except:
            pass  # FTS might already exist

        print(f"Indexed {len(data)} chunks in LanceDB")

    def search(self, query: str, top_k: int = 5, filter: str = None) -> List[dict]:
        """
        Search for similar documents.

        Args:
            query: Search query
            top_k: Number of results
            filter: Optional SQL filter (e.g., "ticker = 'THYAO'")

        Returns:
            List of results with text and metadata
        """
        if self.table is None:
            try:
                self.table = self.db.open_table(self.table_name)
            except:
                return []

        from .embeddings import embed_texts

        # Get query embedding
        query_embedding = embed_texts([query], is_query=True)[0]

        # Build search query
        search_query = self.table.search(query_embedding).limit(top_k)

        if filter:
            search_query = search_query.where(filter)

        # Execute search
        results = search_query.to_list()

        # Format results
        formatted = []
        for r in results:
            formatted.append({
                "text": r.get("text", ""),
                "ticker": r.get("ticker", "N/A"),
                "document_type": r.get("document_type", "unknown"),
                "section": r.get("section", "N/A"),
                "sector": r.get("sector", "N/A"),
                "score": r.get("_distance", 0)
            })

        return formatted

    def hybrid_search(self, query: str, top_k: int = 5, filter: str = None) -> List[dict]:
        """
        Hybrid search combining vector and FTS.

        Args:
            query: Search query
            top_k: Number of results
            filter: Optional SQL filter

        Returns:
            List of results
        """
        if self.table is None:
            try:
                self.table = self.db.open_table(self.table_name)
            except:
                return []

        from .embeddings import embed_texts

        query_embedding = embed_texts([query], is_query=True)[0]

        try:
            # Try hybrid search
            search_query = self.table.search(
                query_embedding,
                query_type="hybrid"
            ).limit(top_k)

            if filter:
                search_query = search_query.where(filter)

            results = search_query.to_list()
        except:
            # Fallback to vector-only search
            results = self.search(query, top_k, filter)
            return results

        formatted = []
        for r in results:
            formatted.append({
                "text": r.get("text", ""),
                "ticker": r.get("ticker", "N/A"),
                "document_type": r.get("document_type", "unknown"),
                "section": r.get("section", "N/A"),
                "sector": r.get("sector", "N/A"),
                "score": r.get("_distance", 0)
            })

        return formatted
