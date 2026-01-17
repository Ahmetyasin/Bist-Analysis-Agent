"""Technical analysis tool."""
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import pandas as pd
import numpy as np


class TechnicalsInput(BaseModel):
    ticker: str = Field(description="BIST stock ticker symbol")
    period: str = Field(default="6ay", description="Analysis period: 1ay, 3ay, 6ay, 1y")


def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """Calculate RSI indicator."""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if len(rsi) > 0 else None


def calculate_macd(prices: pd.Series) -> dict:
    """Calculate MACD indicator."""
    exp1 = prices.ewm(span=12, adjust=False).mean()
    exp2 = prices.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    return {
        "macd": macd.iloc[-1],
        "signal": signal.iloc[-1],
        "histogram": histogram.iloc[-1]
    }


def calculate_technicals(ticker: str, period: str = "6ay") -> dict:
    """
    Calculate technical indicators for a BIST stock.

    Args:
        ticker: Stock symbol
        period: Analysis period

    Returns:
        Dictionary with technical indicators
    """
    try:
        import borsapy as bp
        stock = bp.Ticker(ticker.upper())
        df = stock.history(period=period)

        # Accept smaller datasets (at least 10 rows)
        if df is None or len(df) < 10:
            return {"ticker": ticker, "error": "Insufficient historical data"}

        close = df['Close']
        data_len = len(close)

        # Moving Averages - adjusted for available data
        sma_window = min(20, data_len - 1)
        sma_20 = close.rolling(window=sma_window).mean().iloc[-1] if sma_window > 0 else close.iloc[-1]
        sma_50 = close.rolling(window=50).mean().iloc[-1] if data_len >= 50 else None
        sma_200 = close.rolling(window=200).mean().iloc[-1] if data_len >= 200 else None

        # RSI - adjusted for available data
        rsi_period = min(14, data_len - 1)
        rsi = calculate_rsi(close, period=rsi_period) if rsi_period >= 2 else None

        # MACD - need at least 26 periods for proper calculation
        if data_len >= 26:
            macd_data = calculate_macd(close)
        else:
            macd_data = {"macd": 0, "signal": 0, "histogram": 0}

        # Bollinger Bands - adjusted for available data
        bb_window = min(20, data_len - 1)
        if bb_window > 1:
            sma_20_bb = close.rolling(window=bb_window).mean()
            std_20 = close.rolling(window=bb_window).std()
            upper_band = (sma_20_bb + (std_20 * 2)).iloc[-1]
            lower_band = (sma_20_bb - (std_20 * 2)).iloc[-1]
        else:
            upper_band = close.iloc[-1]
            lower_band = close.iloc[-1]

        # Current price position
        current_price = close.iloc[-1]

        # Trend determination
        if sma_50:
            if current_price > sma_20 > sma_50:
                trend = "Guclu Yukselis"
            elif current_price > sma_20:
                trend = "Yukselis"
            elif current_price < sma_20 < sma_50:
                trend = "Guclu Dusus"
            elif current_price < sma_20:
                trend = "Dusus"
            else:
                trend = "Yatay"
        else:
            trend = "Yukselis" if current_price > sma_20 else "Dusus"

        # RSI interpretation
        if rsi:
            if rsi > 70:
                rsi_signal = "Asiri Alim"
            elif rsi < 30:
                rsi_signal = "Asiri Satim"
            else:
                rsi_signal = "Notr"
        else:
            rsi_signal = "N/A"

        # Support/Resistance (simple: recent low/high)
        sr_window = min(20, data_len)
        support = close.rolling(window=sr_window).min().iloc[-1]
        resistance = close.rolling(window=sr_window).max().iloc[-1]

        # Volume trend
        if 'Volume' in df.columns:
            vol_window = min(20, data_len)
            vol_sma = df['Volume'].rolling(window=vol_window).mean().iloc[-1]
            current_vol = df['Volume'].iloc[-1]
            volume_trend = "Artan" if current_vol > vol_sma else "Azalan"
        else:
            volume_trend = "N/A"

        return {
            "ticker": ticker.upper(),
            "current_price": current_price,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "rsi_14": rsi,
            "rsi_signal": rsi_signal,
            "macd": macd_data["macd"],
            "macd_signal": macd_data["signal"],
            "macd_histogram": macd_data["histogram"],
            "bollinger_upper": upper_band,
            "bollinger_lower": lower_band,
            "support": support,
            "resistance": resistance,
            "trend": trend,
            "volume_trend": volume_trend,
            "error": None
        }

    except Exception as e:
        return {"ticker": ticker, "error": f"Technical analysis failed: {str(e)}"}


@tool(args_schema=TechnicalsInput)
def TechnicalsTool(ticker: str, period: str = "6ay") -> str:
    """
    Calculate technical analysis indicators for a BIST stock.
    Returns RSI, MACD, moving averages, Bollinger Bands, support/resistance levels.
    Use this tool for price trend analysis and timing signals.
    """
    data = calculate_technicals(ticker, period)

    if data.get("error"):
        return f"Error: {data['error']}"

    result = f"""
## {data['ticker']} Teknik Analiz

### Fiyat ve Trend
- Guncel Fiyat: {data['current_price']:.2f} TL
- Trend: **{data['trend']}**
- Hacim Trendi: {data['volume_trend']}

### Hareketli Ortalamalar
- SMA 20: {data['sma_20']:.2f} TL
- SMA 50: {data['sma_50']:.2f if data['sma_50'] else 'N/A'} TL
- SMA 200: {data['sma_200']:.2f if data['sma_200'] else 'N/A'} TL

### Momentum Gostergeleri
- RSI (14): {data['rsi_14']:.1f} - **{data['rsi_signal']}**
- MACD: {data['macd']:.3f}
- MACD Sinyal: {data['macd_signal']:.3f}
- MACD Histogram: {data['macd_histogram']:.3f}

### Bollinger Bantlari
- Ust Bant: {data['bollinger_upper']:.2f} TL
- Alt Bant: {data['bollinger_lower']:.2f} TL

### Destek / Direnc
- Destek: {data['support']:.2f} TL
- Direnc: {data['resistance']:.2f} TL
"""
    return result
