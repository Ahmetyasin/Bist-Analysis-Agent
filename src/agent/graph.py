"""LangGraph agent definition."""
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    parse_query,
    create_plan,
    gather_stock_data,
    gather_macro_data,
    gather_technical_data,
    gather_portfolio_data,
    retrieve_documents,
    synthesize_report
)


def create_agent_graph() -> StateGraph:
    """Create the BIST analysis agent graph."""

    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("parse_query", parse_query)
    workflow.add_node("create_plan", create_plan)
    workflow.add_node("gather_stock_data", gather_stock_data)
    workflow.add_node("gather_macro_data", gather_macro_data)
    workflow.add_node("gather_technical_data", gather_technical_data)
    workflow.add_node("gather_portfolio_data", gather_portfolio_data)
    workflow.add_node("retrieve_documents", retrieve_documents)
    workflow.add_node("synthesize_report", synthesize_report)

    # Define edges
    workflow.set_entry_point("parse_query")
    workflow.add_edge("parse_query", "create_plan")

    # After planning, gather all data (can be parallelized in future)
    workflow.add_edge("create_plan", "gather_stock_data")
    workflow.add_edge("gather_stock_data", "gather_macro_data")
    workflow.add_edge("gather_macro_data", "gather_technical_data")
    workflow.add_edge("gather_technical_data", "gather_portfolio_data")
    workflow.add_edge("gather_portfolio_data", "retrieve_documents")
    workflow.add_edge("retrieve_documents", "synthesize_report")
    workflow.add_edge("synthesize_report", END)

    return workflow.compile()


def run_agent(query: str, verbose: bool = False) -> dict:
    """
    Run the BIST analysis agent.

    Args:
        query: User query
        verbose: Print progress

    Returns:
        Final state with analysis report
    """
    agent = create_agent_graph()

    # Initial state
    initial_state = {
        "query": query,
        "extracted_ticker": None,
        "query_type": None,
        "plan": None,
        "stock_data": None,
        "macro_data": None,
        "technical_data": None,
        "portfolio_data": None,
        "rag_context": None,
        "rag_sources": [],
        "messages": [],
        "final_report": None,
        "tools_called": [],
        "step_count": 0,
        "errors": []
    }

    if verbose:
        print(f"Starting analysis for: {query}")

    # Run agent
    final_state = agent.invoke(initial_state)

    if verbose:
        print(f"Completed in {final_state['step_count']} steps")
        print(f"Tools used: {final_state['tools_called']}")

    return final_state
