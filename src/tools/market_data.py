"""Stock market data tool using borsapy."""
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool


class StockDataInput(BaseModel):
    ticker: str = Field(description="BIST stock ticker symbol (e.g., THYAO, AKBNK)")
    period: str = Field(default="3ay", description="Data period: 1ay, 3ay, 6ay, 1y")


class StockDataOutput(BaseModel):
    ticker: str
    company_name: Optional[str]
    current_price: Optional[float]
    previous_close: Optional[float]
    change_percent: Optional[float]
    volume: Optional[int]
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    dividend_yield: Optional[float]
    week_52_high: Optional[float]
    week_52_low: Optional[float]
    sector: Optional[str]
    free_float: Optional[float]
    foreign_ratio: Optional[float]
    analyst_target: Optional[float]
    analyst_recommendation: Optional[str]
    error: Optional[str] = None


def get_stock_data(ticker: str, period: str = "3ay") -> dict:
    """
    Fetch comprehensive stock data for a BIST ticker.

    Args:
        ticker: BIST stock symbol (e.g., THYAO)
        period: Historical data period

    Returns:
        Dictionary with stock fundamentals and price data
    """
    try:
        import borsapy as bp
        stock = bp.Ticker(ticker.upper())

        # Get fast info (uses attribute access, not dict)
        fast_info = stock.fast_info

        # Get detailed info (this is a dict)
        info = stock.info

        # Safe attribute access helper
        def safe_attr(obj, attr, default=None):
            try:
                return getattr(obj, attr, default)
            except:
                return default

        # Get analyst data if available
        try:
            analyst_targets = stock.analyst_price_targets
            target_price = analyst_targets.get("mean") if analyst_targets and hasattr(analyst_targets, 'get') else None
        except:
            target_price = None

        try:
            recommendations = stock.recommendations_summary
            if recommendations is not None and len(recommendations) > 0:
                rec_summary = recommendations.iloc[0].to_dict() if hasattr(recommendations, 'iloc') else None
            else:
                rec_summary = None
        except:
            rec_summary = None

        # Extract fast_info using attribute access
        current_price = safe_attr(fast_info, 'last_price')
        previous_close = safe_attr(fast_info, 'previous_close')
        volume = safe_attr(fast_info, 'volume')
        market_cap = safe_attr(fast_info, 'market_cap')
        pe_ratio = safe_attr(fast_info, 'pe_ratio')
        pb_ratio = safe_attr(fast_info, 'pb_ratio')
        free_float = safe_attr(fast_info, 'free_float')
        foreign_ratio = safe_attr(fast_info, 'foreign_ratio')
        year_high = safe_attr(fast_info, 'year_high')
        year_low = safe_attr(fast_info, 'year_low')

        # Calculate change percent
        change_percent = None
        if current_price and previous_close:
            change_percent = ((current_price - previous_close) / previous_close * 100)

        return {
            "ticker": ticker.upper(),
            "company_name": info.get("longName") or info.get("shortName") if info else None,
            "current_price": current_price,
            "previous_close": previous_close,
            "change_percent": change_percent,
            "volume": volume,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio or (info.get("trailingPE") if info else None),
            "pb_ratio": pb_ratio or (info.get("priceToBook") if info else None),
            "dividend_yield": info.get("dividendYield") if info else None,
            "week_52_high": year_high or (info.get("fiftyTwoWeekHigh") if info else None),
            "week_52_low": year_low or (info.get("fiftyTwoWeekLow") if info else None),
            "sector": info.get("sector") if info else None,
            "free_float": free_float,
            "foreign_ratio": foreign_ratio,
            "analyst_target": target_price,
            "analyst_recommendation": rec_summary,
            "error": None
        }

    except Exception as e:
        return {
            "ticker": ticker.upper(),
            "error": f"Could not fetch data for {ticker}: {str(e)}"
        }


@tool(args_schema=StockDataInput)
def StockDataTool(ticker: str, period: str = "3ay") -> str:
    """
    Fetch stock market data for a BIST (Turkish stock exchange) ticker.
    Returns current price, fundamentals (P/E, P/B), analyst targets, and more.
    Use this tool when you need stock prices, valuations, or company fundamentals.
    """
    data = get_stock_data(ticker, period)

    if data.get("error"):
        return f"Error: {data['error']}"

    result = f"""
## {data['ticker']} - {data.get('company_name', 'N/A')}

### Fiyat Bilgileri
- Guncel Fiyat: {data.get('current_price', 'N/A')} TL
- Onceki Kapanis: {data.get('previous_close', 'N/A')} TL
- Degisim: {data.get('change_percent', 'N/A'):.2f}%
- Hacim: {data.get('volume', 'N/A'):,}

### Degerleme Carpanlari
- F/K (P/E): {data.get('pe_ratio', 'N/A')}
- PD/DD (P/B): {data.get('pb_ratio', 'N/A')}
- Temettu Verimi: {data.get('dividend_yield', 'N/A')}

### Piyasa Bilgileri
- Piyasa Degeri: {data.get('market_cap', 'N/A'):,.0f} TL
- 52 Hafta En Yuksek: {data.get('week_52_high', 'N/A')} TL
- 52 Hafta En Dusuk: {data.get('week_52_low', 'N/A')} TL
- Halka Aciklik: {data.get('free_float', 'N/A')}%
- Yabanci Orani: {data.get('foreign_ratio', 'N/A')}%

### Sektor
- {data.get('sector', 'N/A')}

### Analist Hedefi
- Hedef Fiyat: {data.get('analyst_target', 'N/A')} TL
"""
    return result
