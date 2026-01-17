"""Configuration for BIST Analysis Agent."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# === API Keys ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TCMB_API_KEY = os.getenv("TCMB_EVDS_API_KEY")
WANDB_API_KEY = os.getenv("WANDB_API_KEY")
WANDB_PROJECT = os.getenv("WANDB_PROJECT", "bist-analysis-agent")

# === Model Configuration ===
GEMINI_MODEL = "gemini-2.0-flash"  # Use the latest model as user requested
EMBEDDING_MODEL = "models/text-embedding-004"
EMBEDDING_DIMENSION = 768

# === Paths ===
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
EVALUATION_DIR = DATA_DIR / "evaluation"
RESULTS_DIR = BASE_DIR / "results"

# Create directories
for dir_path in [DOCUMENTS_DIR, EMBEDDINGS_DIR, EVALUATION_DIR, RESULTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# === RAG Configuration ===
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 5
RERANK_TOP_K = 3

# === Agent Configuration ===
MAX_AGENT_STEPS = 10
TEMPERATURE = 0.1

# === Evaluation Configuration ===
NUM_ABLATION_RUNS = 3
TEST_QUERIES_COUNT = 25

# === Target Companies for Analysis ===
TARGET_TICKERS = ["THYAO", "AKBNK", "GARAN", "SISE", "TUPRS", "EREGL", "KCHOL", "SAHOL", "TCELL", "BIMAS"]

# === Model Portfolio Data (Pre-collected) ===
MODEL_PORTFOLIOS = {
    "is_yatirim": {
        "name": "Is Yatirim",
        "last_updated": "2025-01",
        "stocks": [
            {"ticker": "THYAO", "rating": "AL", "target_price": 295.0, "current_weight": 0.12},
            {"ticker": "AKBNK", "rating": "AL", "target_price": 58.0, "current_weight": 0.10},
            {"ticker": "GARAN", "rating": "TUT", "target_price": 125.0, "current_weight": 0.08},
            {"ticker": "SISE", "rating": "AL", "target_price": 72.0, "current_weight": 0.07},
            {"ticker": "TUPRS", "rating": "AL", "target_price": 185.0, "current_weight": 0.09},
            {"ticker": "EREGL", "rating": "TUT", "target_price": 52.0, "current_weight": 0.06},
            {"ticker": "KCHOL", "rating": "AL", "target_price": 215.0, "current_weight": 0.08},
            {"ticker": "TCELL", "rating": "AL", "target_price": 98.0, "current_weight": 0.07},
        ]
    },
    "oyak_yatirim": {
        "name": "Oyak Yatirim",
        "last_updated": "2025-01",
        "stocks": [
            {"ticker": "AKBNK", "rating": "AL", "target_price": 55.0, "current_weight": 0.11},
            {"ticker": "YKBNK", "rating": "AL", "target_price": 38.0, "current_weight": 0.10},
            {"ticker": "THYAO", "rating": "AL", "target_price": 290.0, "current_weight": 0.12},
            {"ticker": "TOASO", "rating": "AL", "target_price": 320.0, "current_weight": 0.09},
            {"ticker": "KCHOL", "rating": "AL", "target_price": 210.0, "current_weight": 0.08},
            {"ticker": "BIMAS", "rating": "TUT", "target_price": 620.0, "current_weight": 0.07},
            {"ticker": "PGSUS", "rating": "AL", "target_price": 980.0, "current_weight": 0.08},
        ]
    },
    "gedik_yatirim": {
        "name": "Gedik Yatirim",
        "last_updated": "2025-01",
        "stocks": [
            {"ticker": "GARAN", "rating": "AL", "target_price": 130.0, "current_weight": 0.10},
            {"ticker": "THYAO", "rating": "AL", "target_price": 285.0, "current_weight": 0.11},
            {"ticker": "SISE", "rating": "AL", "target_price": 75.0, "current_weight": 0.08},
            {"ticker": "EREGL", "rating": "AL", "target_price": 55.0, "current_weight": 0.07},
            {"ticker": "SAHOL", "rating": "TUT", "target_price": 85.0, "current_weight": 0.09},
            {"ticker": "TUPRS", "rating": "AL", "target_price": 190.0, "current_weight": 0.10},
        ]
    },
    "yapi_kredi_yatirim": {
        "name": "Yapi Kredi Yatirim",
        "last_updated": "2025-01",
        "stocks": [
            {"ticker": "AKBNK", "rating": "AL", "target_price": 56.0, "current_weight": 0.12},
            {"ticker": "THYAO", "rating": "AL", "target_price": 300.0, "current_weight": 0.10},
            {"ticker": "TCELL", "rating": "AL", "target_price": 95.0, "current_weight": 0.08},
            {"ticker": "BIMAS", "rating": "AL", "target_price": 640.0, "current_weight": 0.09},
            {"ticker": "KCHOL", "rating": "AL", "target_price": 220.0, "current_weight": 0.08},
        ]
    }
}

# === Test Queries for Evaluation ===
TEST_QUERIES = [
    # Fundamental Analysis Queries
    {"id": 1, "query": "THYAO hissesi icin temel analiz yap", "ticker": "THYAO", "type": "fundamental",
     "expected_tools": ["get_stock_data", "search_documents"], "expected_elements": ["F/K", "gelir", "kar marji"]},
    {"id": 2, "query": "AKBNK'nin finansal durumunu degerlendir", "ticker": "AKBNK", "type": "fundamental",
     "expected_tools": ["get_stock_data", "search_documents"], "expected_elements": ["ozkaynak karlilik", "aktif kalitesi"]},
    {"id": 3, "query": "GARAN hissesinin temel gostergelerini analiz et", "ticker": "GARAN", "type": "fundamental",
     "expected_tools": ["get_stock_data", "search_documents"], "expected_elements": ["F/K", "PD/DD"]},
    {"id": 4, "query": "SISE sirketinin mali tablolarini incele", "ticker": "SISE", "type": "fundamental",
     "expected_tools": ["get_stock_data", "search_documents"], "expected_elements": ["gelir tablosu", "bilanco"]},
    {"id": 5, "query": "TUPRS'un karlilik durumu nasil?", "ticker": "TUPRS", "type": "fundamental",
     "expected_tools": ["get_stock_data", "search_documents"], "expected_elements": ["net kar", "FAVOK"]},

    # Technical Analysis Queries
    {"id": 6, "query": "THYAO icin teknik analiz yap", "ticker": "THYAO", "type": "technical",
     "expected_tools": ["get_stock_data", "calculate_technicals"], "expected_elements": ["RSI", "hareketli ortalama", "trend"]},
    {"id": 7, "query": "EREGL hissesinin teknik gorunumu nasil?", "ticker": "EREGL", "type": "technical",
     "expected_tools": ["get_stock_data", "calculate_technicals"], "expected_elements": ["destek", "direnc", "momentum"]},
    {"id": 8, "query": "KCHOL'un fiyat trendi hakkinda bilgi ver", "ticker": "KCHOL", "type": "technical",
     "expected_tools": ["get_stock_data", "calculate_technicals"], "expected_elements": ["trend", "SMA"]},

    # Macroeconomic Queries
    {"id": 9, "query": "Bankacilik sektoru icin makroekonomik gorunum nasil?", "ticker": None, "type": "macro",
     "expected_tools": ["get_macro_data", "search_documents"], "expected_elements": ["faiz", "enflasyon", "kredi buyumesi"]},
    {"id": 10, "query": "Turkiye ekonomisi hisse senetlerini nasil etkiler?", "ticker": None, "type": "macro",
     "expected_tools": ["get_macro_data"], "expected_elements": ["TCMB", "politika faizi", "doviz kuru"]},
    {"id": 11, "query": "Enflasyonun BIST uzerindeki etkisini degerlendir", "ticker": None, "type": "macro",
     "expected_tools": ["get_macro_data", "search_documents"], "expected_elements": ["TUFE", "reel getiri"]},

    # Model Portfolio Queries
    {"id": 12, "query": "THYAO icin kurumsal yatirimcilar ne dusunuyor?", "ticker": "THYAO", "type": "portfolio",
     "expected_tools": ["get_model_portfolios", "get_stock_data"], "expected_elements": ["model portfoy", "hedef fiyat", "AL/TUT"]},
    {"id": 13, "query": "Hangi araci kurumlar AKBNK'yi oneriyor?", "ticker": "AKBNK", "type": "portfolio",
     "expected_tools": ["get_model_portfolios"], "expected_elements": ["Is Yatirim", "hedef fiyat", "tavsiye"]},
    {"id": 14, "query": "Model portfoylerde en cok onerilen bankacilik hisseleri hangileri?", "ticker": None, "type": "portfolio",
     "expected_tools": ["get_model_portfolios"], "expected_elements": ["banka", "agirlik", "oneri"]},

    # Comprehensive Analysis Queries
    {"id": 15, "query": "THYAO hakkinda kapsamli yatirim arastirmasi yap", "ticker": "THYAO", "type": "comprehensive",
     "expected_tools": ["get_stock_data", "calculate_technicals", "get_macro_data", "get_model_portfolios", "search_documents"],
     "expected_elements": ["temel", "teknik", "makro", "kurumsal gorus"]},
    {"id": 16, "query": "GARAN icin detayli analiz raporu hazirla", "ticker": "GARAN", "type": "comprehensive",
     "expected_tools": ["get_stock_data", "calculate_technicals", "get_model_portfolios", "search_documents"],
     "expected_elements": ["F/K", "RSI", "hedef fiyat"]},
    {"id": 17, "query": "SISE hissesi yatirim yapilabilir mi? Tum acilardan degerlendir", "ticker": "SISE", "type": "comprehensive",
     "expected_tools": ["get_stock_data", "calculate_technicals", "get_macro_data", "get_model_portfolios", "search_documents"],
     "expected_elements": ["temel analiz", "teknik analiz", "sektor", "kurumsal"]},

    # Sector Analysis Queries
    {"id": 18, "query": "Havacilik sektorunun gorunumu nasil?", "ticker": None, "type": "sector",
     "expected_tools": ["get_macro_data", "search_documents", "get_stock_data"], "expected_elements": ["sektor", "buyume", "risk"]},
    {"id": 19, "query": "Enerji sektorundeki firsatlari degerlendir", "ticker": None, "type": "sector",
     "expected_tools": ["search_documents", "get_macro_data"], "expected_elements": ["enerji", "petrol", "dogalgaz"]},

    # Comparison Queries
    {"id": 20, "query": "AKBNK ve GARAN'i karsilastir", "ticker": "AKBNK,GARAN", "type": "comparison",
     "expected_tools": ["get_stock_data", "search_documents"], "expected_elements": ["karsilastirma", "F/K", "ozkaynak"]},
    {"id": 21, "query": "Holding hisseleri arasinda hangisi daha cazip?", "ticker": None, "type": "comparison",
     "expected_tools": ["get_stock_data", "get_model_portfolios"], "expected_elements": ["KCHOL", "SAHOL", "degerleme"]},

    # Risk-focused Queries
    {"id": 22, "query": "TUPRS yatiriminin riskleri nelerdir?", "ticker": "TUPRS", "type": "risk",
     "expected_tools": ["get_stock_data", "search_documents", "get_macro_data"], "expected_elements": ["risk", "volatilite", "sektor riski"]},
    {"id": 23, "query": "TCELL icin risk-getiri analizi yap", "ticker": "TCELL", "type": "risk",
     "expected_tools": ["get_stock_data", "calculate_technicals"], "expected_elements": ["risk", "getiri", "volatilite"]},

    # Edge Cases / Robustness
    {"id": 24, "query": "XYZABC hissesini analiz et", "ticker": "XYZABC", "type": "edge_invalid",
     "expected_tools": [], "expected_elements": ["bulunamadi", "gecersiz"]},
    {"id": 25, "query": "Borsa", "ticker": None, "type": "edge_vague",
     "expected_tools": [], "expected_elements": ["detay", "aciklama"]},
]
