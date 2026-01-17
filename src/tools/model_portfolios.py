"""Model portfolio lookup tool."""
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


class ModelPortfoliosInput(BaseModel):
    ticker: Optional[str] = Field(default=None, description="Stock ticker to lookup, or None for all portfolios")


def get_model_portfolios(ticker: Optional[str] = None) -> dict:
    """
    Get model portfolio recommendations for a ticker.

    Args:
        ticker: Stock symbol or None for overview

    Returns:
        Dictionary with model portfolio data
    """
    portfolios = config.MODEL_PORTFOLIOS

    if ticker is None:
        # Return overview of all portfolios
        overview = []
        for key, portfolio in portfolios.items():
            overview.append({
                "institution": portfolio["name"],
                "stock_count": len(portfolio["stocks"]),
                "last_updated": portfolio["last_updated"],
                "top_picks": [s["ticker"] for s in portfolio["stocks"][:3]]
            })
        return {"type": "overview", "portfolios": overview}

    # Find ticker in all portfolios
    ticker = ticker.upper()
    results = []

    for key, portfolio in portfolios.items():
        for stock in portfolio["stocks"]:
            if stock["ticker"] == ticker:
                results.append({
                    "institution": portfolio["name"],
                    "rating": stock["rating"],
                    "target_price": stock["target_price"],
                    "weight": stock["current_weight"],
                    "last_updated": portfolio["last_updated"]
                })
                break

    if not results:
        return {
            "type": "ticker_search",
            "ticker": ticker,
            "found": False,
            "message": f"{ticker} model portfoylerde bulunamadi"
        }

    # Calculate consensus
    buy_count = sum(1 for r in results if r["rating"] == "AL")
    hold_count = sum(1 for r in results if r["rating"] == "TUT")
    sell_count = sum(1 for r in results if r["rating"] == "SAT")
    avg_target = sum(r["target_price"] for r in results) / len(results)

    return {
        "type": "ticker_search",
        "ticker": ticker,
        "found": True,
        "recommendations": results,
        "consensus": {
            "buy_count": buy_count,
            "hold_count": hold_count,
            "sell_count": sell_count,
            "average_target": avg_target,
            "coverage_count": len(results)
        }
    }


@tool(args_schema=ModelPortfoliosInput)
def ModelPortfoliosTool(ticker: Optional[str] = None) -> str:
    """
    Lookup model portfolio recommendations from Turkish brokerage firms.
    Shows which institutions recommend the stock and their target prices.
    Use this to understand institutional sentiment and consensus views.
    """
    data = get_model_portfolios(ticker)

    if data["type"] == "overview":
        result = "## Model Portfoy Ozeti\n\n"
        for p in data["portfolios"]:
            result += f"### {p['institution']}\n"
            result += f"- Hisse Sayisi: {p['stock_count']}\n"
            result += f"- Son Guncelleme: {p['last_updated']}\n"
            result += f"- One Cikanlar: {', '.join(p['top_picks'])}\n\n"
        return result

    if not data.get("found"):
        return f"* {data['message']}"

    result = f"""
## {data['ticker']} - Kurumsal Gorusler

### Konsensus
- AL Sayisi: {data['consensus']['buy_count']}
- TUT Sayisi: {data['consensus']['hold_count']}
- SAT Sayisi: {data['consensus']['sell_count']}
- Ortalama Hedef Fiyat: {data['consensus']['average_target']:.2f} TL
- Kapsama: {data['consensus']['coverage_count']} kurum

### Kurum Detaylari
"""

    for rec in data["recommendations"]:
        result += f"\n**{rec['institution']}**\n"
        result += f"- Tavsiye: {rec['rating']}\n"
        result += f"- Hedef Fiyat: {rec['target_price']:.2f} TL\n"
        result += f"- Portfoy Agirligi: {rec['weight']*100:.1f}%\n"

    return result
