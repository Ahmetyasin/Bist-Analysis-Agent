"""Generate financial documents from API data for RAG indexing."""
import json
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


def generate_company_document(ticker: str) -> dict:
    """Generate a comprehensive document for a company using borsapy data."""
    try:
        import borsapy as bp
        stock = bp.Ticker(ticker)
        info = stock.info
        fast_info = stock.fast_info

        # Get financial statements
        try:
            balance_sheet = stock.balance_sheet
            income_stmt = stock.income_stmt
            has_financials = balance_sheet is not None and income_stmt is not None
        except:
            has_financials = False
            balance_sheet = None
            income_stmt = None

        # Get analyst data
        try:
            analyst_targets = stock.analyst_price_targets
            recommendations = stock.recommendations_summary
        except:
            analyst_targets = None
            recommendations = None

        # Build document sections
        sections = []

        # Company Overview
        sections.append({
            "section": "Sirket Profili",
            "content": f"""
{ticker} - {info.get('longName', info.get('shortName', ticker))}

Sektor: {info.get('sector', 'N/A')}
Alt Sektor: {info.get('industry', 'N/A')}
Web Sitesi: {info.get('website', 'N/A')}

Faaliyet Alani:
{info.get('longBusinessSummary', 'Bilgi mevcut degil.')}
"""
        })

        # Market Data
        sections.append({
            "section": "Piyasa Verileri",
            "content": f"""
{ticker} Piyasa Bilgileri

Guncel Fiyat: {fast_info.get('last_price', 'N/A')} TL
Piyasa Degeri: {fast_info.get('market_cap', 'N/A'):,.0f} TL
Halka Aciklik Orani: {fast_info.get('free_float', 'N/A')}%
Yabanci Payi: {fast_info.get('foreign_ratio', 'N/A')}%

52 Haftalik En Yuksek: {info.get('fiftyTwoWeekHigh', 'N/A')} TL
52 Haftalik En Dusuk: {info.get('fiftyTwoWeekLow', 'N/A')} TL
"""
        })

        # Valuation Metrics
        sections.append({
            "section": "Degerleme Carpanlari",
            "content": f"""
{ticker} Degerleme Analizi

F/K Orani (P/E): {fast_info.get('pe_ratio', 'N/A')}
PD/DD Orani (P/B): {info.get('priceToBook', 'N/A')}
Temettu Verimi: {info.get('dividendYield', 'N/A')}

Degerleme Yorumu:
- F/K orani sektor ortalamasiyla karsilastirilmalidir
- Dusuk PD/DD orani deger yatirimi firsati olabilir
- Temettu verimi gelir odakli yatirimcilar icin onemlidir
"""
        })

        # Financial Analysis (if available)
        if has_financials:
            try:
                # Extract key metrics from income statement
                revenue = income_stmt.iloc[0].get('Total Revenue', 'N/A') if income_stmt is not None else 'N/A'
                net_income = income_stmt.iloc[0].get('Net Income', 'N/A') if income_stmt is not None else 'N/A'

                sections.append({
                    "section": "Finansal Analiz",
                    "content": f"""
{ticker} Finansal Performans

Son Donem Finansal Veriler:
- Toplam Gelir: {revenue}
- Net Kar: {net_income}

Finansal Saglik Degerlendirmesi:
Sirketin finansal tablolari incelendiginde, gelir ve karlilik trendleri
yatirim kararlari icin onemli gostergeler sunmaktadir.
"""
                })
            except:
                pass

        # Analyst Views
        if analyst_targets:
            sections.append({
                "section": "Analist Gorusleri",
                "content": f"""
{ticker} Analist Degerlendirmeleri

Hedef Fiyat Ortalamasi: {analyst_targets.get('mean', 'N/A')} TL
En Yuksek Hedef: {analyst_targets.get('high', 'N/A')} TL
En Dusuk Hedef: {analyst_targets.get('low', 'N/A')} TL

Analist gorusleri yatirim kararlari icin yol gosterici olabilir ancak
tek basina karar vermek icin yeterli degildir.
"""
            })

        # Model Portfolio Info
        portfolio_info = _get_portfolio_info(ticker)
        if portfolio_info:
            sections.append({
                "section": "Kurumsal Yatirimci Gorusleri",
                "content": portfolio_info
            })

        return {
            "ticker": ticker,
            "company_name": info.get('longName', info.get('shortName', ticker)),
            "sector": info.get('sector', 'N/A'),
            "document_type": "company_analysis",
            "generated_date": datetime.now().isoformat(),
            "sections": sections
        }

    except Exception as e:
        return {
            "ticker": ticker,
            "error": str(e),
            "sections": []
        }


def _get_portfolio_info(ticker: str) -> str:
    """Get model portfolio information for a ticker."""
    from src.tools.model_portfolios import get_model_portfolios
    data = get_model_portfolios(ticker)

    if not data.get("found"):
        return ""

    content = f"{ticker} Kurumsal Gorusler\n\n"
    content += f"Toplam {data['consensus']['coverage_count']} kurum tarafindan takip edilmektedir.\n"
    content += f"AL Onerisi: {data['consensus']['buy_count']} kurum\n"
    content += f"TUT Onerisi: {data['consensus']['hold_count']} kurum\n"
    content += f"Ortalama Hedef Fiyat: {data['consensus']['average_target']:.2f} TL\n\n"

    for rec in data["recommendations"]:
        content += f"- {rec['institution']}: {rec['rating']} (Hedef: {rec['target_price']} TL)\n"

    return content


def generate_sector_document(sector_name: str, tickers: list) -> dict:
    """Generate a sector analysis document."""
    sections = []

    # Collect data for all tickers in sector
    sector_data = []
    for ticker in tickers:
        try:
            import borsapy as bp
            stock = bp.Ticker(ticker)
            info = stock.info
            fast_info = stock.fast_info
            sector_data.append({
                "ticker": ticker,
                "name": info.get('shortName', ticker),
                "price": fast_info.get('last_price'),
                "pe": fast_info.get('pe_ratio'),
                "market_cap": fast_info.get('market_cap'),
            })
        except:
            pass

    # Sector overview
    sections.append({
        "section": "Sektor Ozeti",
        "content": f"""
{sector_name} Sektor Analizi

Takip Edilen Sirket Sayisi: {len(sector_data)}
Sirketler: {', '.join([d['ticker'] for d in sector_data])}

Sektor, Turkiye ekonomisinin onemli bir bilesenidir ve yatirimcilar
icin cesitli firsatlar sunmaktadir.
"""
    })

    # Company comparison
    if sector_data:
        comparison = f"{sector_name} Sirket Karsilastirmasi\n\n"
        for d in sector_data:
            comparison += f"**{d['ticker']}** - {d.get('name', 'N/A')}\n"
            comparison += f"  Fiyat: {d.get('price', 'N/A')} TL\n"
            comparison += f"  F/K: {d.get('pe', 'N/A')}\n"
            comparison += f"  Piyasa Degeri: {d.get('market_cap', 'N/A'):,.0f} TL\n\n"

        sections.append({
            "section": "Sirket Karsilastirmasi",
            "content": comparison
        })

    return {
        "sector": sector_name,
        "document_type": "sector_analysis",
        "generated_date": datetime.now().isoformat(),
        "sections": sections
    }


def generate_macro_document() -> dict:
    """Generate macroeconomic analysis document."""
    from src.tools.macro_data import get_macro_data

    macro_data = get_macro_data()
    indicators = macro_data.get("indicators", {})

    sections = []

    # Macro overview
    policy_rate = indicators.get("policy_rate", {}).get("value", "N/A")
    cpi = indicators.get("cpi_annual", {}).get("value", "N/A")
    usd_try = indicators.get("usd_try", {}).get("value", "N/A")

    sections.append({
        "section": "Makroekonomik Gorunum",
        "content": f"""
Turkiye Makroekonomik Analiz

Para Politikasi:
TCMB Politika Faizi: %{policy_rate}
Merkez Bankasi siki para politikasi uygulamaya devam etmektedir.

Enflasyon:
TUFE Yillik: %{cpi}
Enflasyon hala yuksek seviyelerde seyretmektedir.

Doviz Kurlari:
USD/TRY: {usd_try} TL
Kur volatilitesi yatirim kararlarinda dikkate alinmalidir.

Piyasa Uzerindeki Etkiler:
- Yuksek faiz ortami banka hisselerini destekleyebilir
- Enflasyon sirket maliyetlerini etkilemektedir
- Kur hareketleri ihracatci sirketler icin onemlidir
"""
    })

    # Interest rate analysis
    sections.append({
        "section": "Faiz Analizi",
        "content": f"""
Faiz Oranlari ve Piyasa Etkisi

Mevcut Politika Faizi: %{policy_rate}

Sektorel Etkiler:
- Bankacilik: Yuksek faizler net faiz marjini destekler
- Gayrimenkul: Yuksek faizler sektoru olumsuz etkiler
- Sanayi: Finansman maliyetleri artmaktadir
- Perakende: Tuketici harcamalari baski altinda

Yatirimci Stratejisi:
Yuksek faiz ortaminda temettu veren ve dusuk kaldiracli sirketler
one cikabilir.
"""
    })

    return {
        "document_type": "macro_analysis",
        "generated_date": datetime.now().isoformat(),
        "sections": sections
    }


def generate_financial_documents() -> list:
    """Generate all financial documents for RAG indexing."""
    documents = []

    print("Generating financial documents from API data...")

    # Generate company documents
    for ticker in config.TARGET_TICKERS:
        print(f"  Processing {ticker}...")
        doc = generate_company_document(ticker)
        if doc.get("sections"):
            documents.append(doc)

    # Generate sector documents
    sectors = {
        "Bankacilik": ["AKBNK", "GARAN", "YKBNK"],
        "Havacilik": ["THYAO", "PGSUS"],
        "Holding": ["KCHOL", "SAHOL"],
        "Enerji": ["TUPRS"],
        "Sanayi": ["EREGL", "SISE"],
        "Perakende": ["BIMAS"],
        "Telekomunikasyon": ["TCELL"],
    }

    for sector_name, tickers in sectors.items():
        print(f"  Processing {sector_name} sector...")
        doc = generate_sector_document(sector_name, tickers)
        documents.append(doc)

    # Generate macro document
    print("  Processing macro data...")
    macro_doc = generate_macro_document()
    documents.append(macro_doc)

    print(f"Generated {len(documents)} documents")
    return documents
