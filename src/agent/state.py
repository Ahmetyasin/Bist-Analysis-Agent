"""Agent state definition."""
from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import add_messages


class AgentState(TypedDict):
    """State for BIST analysis agent."""

    # Input
    query: str
    extracted_ticker: Optional[str]
    query_type: Optional[str]

    # Planning
    plan: Optional[str]

    # Gathered data
    stock_data: Optional[dict]
    macro_data: Optional[dict]
    technical_data: Optional[dict]
    portfolio_data: Optional[dict]
    rag_context: Optional[str]
    rag_sources: Optional[List[dict]]

    # Conversation
    messages: Annotated[list, add_messages]

    # Output
    final_report: Optional[str]

    # Metadata for evaluation
    tools_called: List[str]
    step_count: int
    errors: List[str]
