"""Agent graph nodes."""
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

from .state import AgentState
from .prompts import SYSTEM_PROMPT, PLANNING_PROMPT, SYNTHESIS_PROMPT


# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=config.GEMINI_MODEL,
    google_api_key=config.GEMINI_API_KEY,
    temperature=config.TEMPERATURE
)


def parse_query(state: AgentState) -> AgentState:
    """Parse user query to extract intent and ticker."""
    query = state["query"]

    # Simple ticker extraction
    ticker = None
    query_upper = query.upper()

    for t in config.TARGET_TICKERS:
        if t in query_upper:
            ticker = t
            break

    # Determine query type
    query_lower = query.lower()
    if any(w in query_lower for w in ["temel", "fundamental", "finansal", "bilanco", "gelir"]):
        query_type = "fundamental"
    elif any(w in query_lower for w in ["teknik", "rsi", "trend", "grafik", "fiyat hareketi"]):
        query_type = "technical"
    elif any(w in query_lower for w in ["makro", "ekonomi", "faiz", "enflasyon", "tcmb"]):
        query_type = "macro"
    elif any(w in query_lower for w in ["model portfoy", "kurumsal", "analist", "hedef fiyat"]):
        query_type = "portfolio"
    elif any(w in query_lower for w in ["kapsamli", "detayli", "tum", "genel"]):
        query_type = "comprehensive"
    elif any(w in query_lower for w in ["karsilastir", "kiyasla", "vs", "ile"]):
        query_type = "comparison"
    elif any(w in query_lower for w in ["sektor", "havacilik", "bankacilik", "enerji"]):
        query_type = "sector"
    else:
        query_type = "comprehensive" if ticker else "general"

    return {
        **state,
        "extracted_ticker": ticker,
        "query_type": query_type,
        "step_count": state.get("step_count", 0) + 1
    }


def create_plan(state: AgentState) -> AgentState:
    """Create analysis plan based on query type."""
    query_type = state.get("query_type", "comprehensive")
    ticker = state.get("extracted_ticker")

    # Determine which tools to use based on query type
    tools_map = {
        "fundamental": ["get_stock_data", "search_documents"],
        "technical": ["get_stock_data", "calculate_technicals"],
        "macro": ["get_macro_data", "search_documents"],
        "portfolio": ["get_model_portfolios", "get_stock_data"],
        "comprehensive": ["get_stock_data", "calculate_technicals", "get_macro_data", "get_model_portfolios", "search_documents"],
        "comparison": ["get_stock_data", "get_model_portfolios"],
        "sector": ["get_macro_data", "search_documents", "get_stock_data"],
        "general": ["get_macro_data", "search_documents"]
    }

    tools_needed = tools_map.get(query_type, ["search_documents"])

    plan = f"""
Analiz Plani:
- Ticker: {ticker or 'Genel'}
- Analiz Turu: {query_type}
- Kullanilacak Araclar: {', '.join(tools_needed)}
"""

    return {
        **state,
        "plan": plan,
        "tools_called": tools_needed,
        "step_count": state.get("step_count", 0) + 1
    }


def gather_stock_data(state: AgentState) -> AgentState:
    """Gather stock data if needed."""
    if "get_stock_data" not in state.get("tools_called", []):
        return state

    ticker = state.get("extracted_ticker")
    if not ticker:
        return {**state, "stock_data": None}

    from src.tools.market_data import get_stock_data
    data = get_stock_data(ticker)

    return {
        **state,
        "stock_data": data,
        "step_count": state.get("step_count", 0) + 1
    }


def gather_macro_data(state: AgentState) -> AgentState:
    """Gather macroeconomic data if needed."""
    if "get_macro_data" not in state.get("tools_called", []):
        return state

    from src.tools.macro_data import get_macro_data
    data = get_macro_data()

    return {
        **state,
        "macro_data": data,
        "step_count": state.get("step_count", 0) + 1
    }


def gather_technical_data(state: AgentState) -> AgentState:
    """Gather technical analysis data if needed."""
    if "calculate_technicals" not in state.get("tools_called", []):
        return state

    ticker = state.get("extracted_ticker")
    if not ticker:
        return {**state, "technical_data": None}

    from src.tools.technicals import calculate_technicals
    data = calculate_technicals(ticker)

    return {
        **state,
        "technical_data": data,
        "step_count": state.get("step_count", 0) + 1
    }


def gather_portfolio_data(state: AgentState) -> AgentState:
    """Gather model portfolio data if needed."""
    if "get_model_portfolios" not in state.get("tools_called", []):
        return state

    ticker = state.get("extracted_ticker")

    from src.tools.model_portfolios import get_model_portfolios
    data = get_model_portfolios(ticker)

    return {
        **state,
        "portfolio_data": data,
        "step_count": state.get("step_count", 0) + 1
    }


def retrieve_documents(state: AgentState) -> AgentState:
    """Retrieve relevant documents via RAG."""
    if "search_documents" not in state.get("tools_called", []):
        return state

    from src.rag.retrieval import RAGRetriever

    try:
        retriever = RAGRetriever()
        result = retriever.retrieve_with_context(
            query=state["query"],
            ticker=state.get("extracted_ticker"),
            top_k=config.TOP_K_RETRIEVAL
        )

        return {
            **state,
            "rag_context": result["context"],
            "rag_sources": result["sources"],
            "step_count": state.get("step_count", 0) + 1
        }
    except Exception as e:
        return {
            **state,
            "rag_context": f"Dokuman aramasi basarisiz: {str(e)}",
            "rag_sources": [],
            "errors": state.get("errors", []) + [str(e)],
            "step_count": state.get("step_count", 0) + 1
        }


def synthesize_report(state: AgentState) -> AgentState:
    """Synthesize final analysis report."""
    # Format data for synthesis
    stock_str = _format_dict(state.get("stock_data")) if state.get("stock_data") else "Veri yok"
    macro_str = _format_dict(state.get("macro_data")) if state.get("macro_data") else "Veri yok"
    tech_str = _format_dict(state.get("technical_data")) if state.get("technical_data") else "Veri yok"
    portfolio_str = _format_dict(state.get("portfolio_data")) if state.get("portfolio_data") else "Veri yok"
    rag_str = state.get("rag_context", "Dokuman bulunamadi")

    # Build synthesis prompt
    synthesis_input = SYNTHESIS_PROMPT.format(
        stock_data=stock_str,
        macro_data=macro_str,
        technical_data=tech_str,
        portfolio_data=portfolio_str,
        rag_context=rag_str,
        query=state["query"]
    )

    # Generate report
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=synthesis_input)
    ]

    response = llm.invoke(messages)

    return {
        **state,
        "final_report": response.content,
        "messages": state.get("messages", []) + [AIMessage(content=response.content)],
        "step_count": state.get("step_count", 0) + 1
    }


def _format_dict(d: dict, indent: int = 0) -> str:
    """Format dictionary as readable string."""
    if d is None:
        return "None"

    lines = []
    prefix = "  " * indent

    for key, value in d.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_format_dict(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}: {value}")
        else:
            lines.append(f"{prefix}{key}: {value}")

    return "\n".join(lines)
