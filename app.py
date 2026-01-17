"""Streamlit UI for BIST Analysis Agent."""
import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check for API key before importing agent
import config

# Check if API key is configured
if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_gemini_api_key_here":
    st.error("❌ **GEMINI_API_KEY not configured!**")
    st.info("""
    Please set your Gemini API key in the `.env` file:

    1. Open `.env` file in the project root
    2. Replace `your_gemini_api_key_here` with your actual API key
    3. Restart the app

    Get your API key from: https://makersuite.google.com/app/apikey
    """)
    st.stop()

from src.agent.graph import run_agent

# Page config
st.set_page_config(
    page_title="BIST Analysis Agent",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .ticker-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem;
        background-color: #e8f4f8;
        border-radius: 4px;
        font-family: monospace;
        font-weight: bold;
    }
    .query-example {
        padding: 0.5rem;
        margin: 0.25rem 0;
        background-color: #f8f9fa;
        border-left: 3px solid #1f77b4;
        border-radius: 4px;
        cursor: pointer;
    }
    .query-example:hover {
        background-color: #e9ecef;
    }
    .tool-badge {
        display: inline-block;
        padding: 0.2rem 0.4rem;
        margin: 0.2rem;
        background-color: #d4edda;
        color: #155724;
        border-radius: 3px;
        font-size: 0.85rem;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📈 BIST Stock Analysis Agent</h1>', unsafe_allow_html=True)
st.markdown("**Analyze Turkish stocks using AI-powered multi-tool agent**")
st.markdown("---")

# Sidebar - Info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.info("""
    This agent analyzes Turkish stocks (BIST) using:
    - Real-time market data (borsapy)
    - Technical indicators
    - Macro indicators (TCMB)
    - Institutional portfolios
    - RAG document retrieval
    """)

    st.markdown("### 🎯 Supported Tickers (10 Companies)")
    st.markdown("**Banking:**")
    for ticker in ["AKBNK", "GARAN"]:
        st.markdown(f'<span class="ticker-badge">{ticker}</span>', unsafe_allow_html=True)

    st.markdown("**Aviation:**")
    for ticker in ["THYAO"]:
        st.markdown(f'<span class="ticker-badge">{ticker}</span>', unsafe_allow_html=True)

    st.markdown("**Industrial:**")
    for ticker in ["SISE", "EREGL"]:
        st.markdown(f'<span class="ticker-badge">{ticker}</span>', unsafe_allow_html=True)

    st.markdown("**Energy:**")
    for ticker in ["TUPRS"]:
        st.markdown(f'<span class="ticker-badge">{ticker}</span>', unsafe_allow_html=True)

    st.markdown("**Holding:**")
    for ticker in ["KCHOL", "SAHOL"]:
        st.markdown(f'<span class="ticker-badge">{ticker}</span>', unsafe_allow_html=True)

    st.markdown("**Telecom:**")
    for ticker in ["TCELL"]:
        st.markdown(f'<span class="ticker-badge">{ticker}</span>', unsafe_allow_html=True)

    st.markdown("**Retail:**")
    for ticker in ["BIMAS"]:
        st.markdown(f'<span class="ticker-badge">{ticker}</span>', unsafe_allow_html=True)

    st.markdown("### 🔧 System Status")
    # Check if RAG is initialized
    embeddings_path = config.EMBEDDINGS_DIR / "financial_documents.lance"
    if embeddings_path.exists():
        st.success("✅ RAG Index Ready")
    else:
        st.warning("⚠️ RAG Index Not Found")
        st.caption("Run: `python main.py --setup`")

    st.markdown("---")
    st.markdown("**Model:** " + config.GEMINI_MODEL)
    st.markdown("**Temperature:** " + str(config.TEMPERATURE))

# Main content - Two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<h2 class="section-header">🔍 Query Input</h2>', unsafe_allow_html=True)

    # Query type selector
    query_type = st.selectbox(
        "Select Query Type:",
        [
            "Fundamental Analysis",
            "Technical Analysis",
            "Macroeconomic Analysis",
            "Institutional Portfolio",
            "Comprehensive Analysis",
            "Sector Analysis",
            "Comparison",
            "Risk Analysis",
            "Custom Query"
        ]
    )

    # Sample queries based on type
    sample_queries = {
        "Fundamental Analysis": [
            "THYAO hissesi icin temel analiz yap",
            "AKBNK'nin finansal durumunu degerlendir",
            "GARAN hissesinin temel gostergelerini analiz et",
            "SISE sirketinin mali tablolarini incele",
            "TUPRS'un karlilik durumu nasil?"
        ],
        "Technical Analysis": [
            "THYAO icin teknik analiz yap",
            "EREGL hissesinin teknik gorunumu nasil?",
            "KCHOL'un fiyat trendi hakkinda bilgi ver",
            "GARAN destek direnc seviyeleri nedir?"
        ],
        "Macroeconomic Analysis": [
            "Bankacilik sektoru icin makroekonomik gorunum nasil?",
            "Turkiye ekonomisi hisse senetlerini nasil etkiler?",
            "Enflasyonun BIST uzerindeki etkisini degerlendir",
            "Faiz politikasi hisseleri nasil etkiler?"
        ],
        "Institutional Portfolio": [
            "THYAO icin kurumsal yatirimcilar ne dusunuyor?",
            "Hangi araci kurumlar AKBNK'yi oneriyor?",
            "Model portfoylerde en cok onerilen bankacilik hisseleri hangileri?",
            "GARAN'in hedef fiyatlari nedir?"
        ],
        "Comprehensive Analysis": [
            "THYAO hakkinda kapsamli yatirim arastirmasi yap",
            "GARAN icin detayli analiz raporu hazirla",
            "SISE hissesi yatirim yapilabilir mi? Tum acilardan degerlendir",
            "AKBNK kapsamli degerlendirme"
        ],
        "Sector Analysis": [
            "Havacilik sektorunun gorunumu nasil?",
            "Enerji sektorundeki firsatlari degerlendir",
            "Bankacilik sektorunu analiz et",
            "Holding sektorunde durum nasil?"
        ],
        "Comparison": [
            "AKBNK ve GARAN'i karsilastir",
            "Holding hisseleri arasinda hangisi daha cazip?",
            "THYAO ve PGSUS havacilik hisselerini karsilastir",
            "KCHOL ve SAHOL karsilastirmasi"
        ],
        "Risk Analysis": [
            "TUPRS yatiriminin riskleri nelerdir?",
            "TCELL icin risk-getiri analizi yap",
            "EREGL yatirim riskleri",
            "SAHOL volatilite analizi"
        ],
        "Custom Query": []
    }

    # Show sample queries
    if query_type != "Custom Query" and sample_queries[query_type]:
        selected_sample = st.selectbox(
            "Or select a sample query:",
            [""] + sample_queries[query_type]
        )
        query_input = st.text_area(
            "Enter your query (Turkish):",
            value=selected_sample if selected_sample else "",
            height=100,
            placeholder="Ornek: THYAO hissesi icin temel analiz yap",
            key="query_text"
        )
    else:
        query_input = st.text_area(
            "Enter your query (Turkish):",
            height=100,
            placeholder="Ornek: THYAO hissesi icin temel analiz yap",
            key="query_text_custom"
        )

    # Analyze button
    analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True)

    # Show expected tools for each query type
    expected_tools = {
        "Fundamental Analysis": ["get_stock_data", "search_documents"],
        "Technical Analysis": ["get_stock_data", "calculate_technicals"],
        "Macroeconomic Analysis": ["get_macro_data", "search_documents"],
        "Institutional Portfolio": ["get_model_portfolios", "get_stock_data"],
        "Comprehensive Analysis": ["get_stock_data", "calculate_technicals", "get_macro_data", "get_model_portfolios", "search_documents"],
        "Sector Analysis": ["get_macro_data", "search_documents", "get_stock_data"],
        "Comparison": ["get_stock_data", "get_model_portfolios"],
        "Risk Analysis": ["get_stock_data", "search_documents", "get_macro_data"]
    }

    if query_type in expected_tools:
        st.markdown("**Expected Tools:**")
        for tool in expected_tools[query_type]:
            st.markdown(f'<span class="tool-badge">{tool}</span>', unsafe_allow_html=True)

with col2:
    st.markdown('<h2 class="section-header">📊 Analysis Results</h2>', unsafe_allow_html=True)

    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None

    if analyze_button:
        if not query_input.strip():
            st.error("❌ Please enter a query!")
        else:
            with st.spinner("🔄 Analyzing... This may take 10-30 seconds..."):
                try:
                    # Run agent
                    result = run_agent(query_input, verbose=False)
                    st.session_state.result = result
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)
                    st.session_state.result = None

    # Display results
    if st.session_state.result:
        result = st.session_state.result

        # Metrics row
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Steps", result.get('step_count', 0))
        with col_b:
            st.metric("Tools Used", len(result.get('tools_called', [])))
        with col_c:
            ticker = result.get('extracted_ticker', 'None')
            st.metric("Ticker", ticker if ticker else "General")

        # Execution details in expander
        with st.expander("🔍 Execution Details"):
            st.markdown("**Query Type:** " + result.get('query_type', 'Unknown'))
            st.markdown("**Tools Called:**")
            for tool in result.get('tools_called', []):
                st.markdown(f"- {tool}")

            if result.get('rag_sources'):
                st.markdown(f"**RAG Documents Retrieved:** {len(result['rag_sources'])}")
                for i, src in enumerate(result['rag_sources'][:5], 1):
                    st.markdown(f"{i}. {src.get('source', 'Unknown')} (score: {src.get('score', 0):.3f})")

            if result.get('errors'):
                st.markdown("**⚠️ Errors:**")
                for err in result['errors']:
                    st.error(err)

        # Final report
        st.markdown("### 📄 Analysis Report")
        report = result.get('final_report', 'No report generated.')
        st.markdown(report)

        # Download button
        st.download_button(
            label="💾 Download Report",
            data=report,
            file_name=f"bist_analysis_{result.get('extracted_ticker', 'general')}.txt",
            mime="text/plain"
        )

# Footer - Query Examples
st.markdown("---")
st.markdown('<h2 class="section-header">💡 Quick Query Examples</h2>', unsafe_allow_html=True)

example_cols = st.columns(3)

with example_cols[0]:
    st.markdown("**📊 Fundamental**")
    st.markdown('<div class="query-example">THYAO hissesi icin temel analiz yap</div>', unsafe_allow_html=True)
    st.markdown('<div class="query-example">AKBNK finansal durumu nasil?</div>', unsafe_allow_html=True)

    st.markdown("**📈 Technical**")
    st.markdown('<div class="query-example">EREGL teknik gorunum</div>', unsafe_allow_html=True)
    st.markdown('<div class="query-example">KCHOL fiyat trendi</div>', unsafe_allow_html=True)

with example_cols[1]:
    st.markdown("**🌍 Macroeconomic**")
    st.markdown('<div class="query-example">Bankacilik makroekonomik gorunum</div>', unsafe_allow_html=True)
    st.markdown('<div class="query-example">Enflasyon etkisi</div>', unsafe_allow_html=True)

    st.markdown("**🏦 Portfolio**")
    st.markdown('<div class="query-example">THYAO kurumsal gorusler</div>', unsafe_allow_html=True)
    st.markdown('<div class="query-example">AKBNK model portfoy</div>', unsafe_allow_html=True)

with example_cols[2]:
    st.markdown("**🔬 Comprehensive**")
    st.markdown('<div class="query-example">GARAN kapsamli analiz</div>', unsafe_allow_html=True)
    st.markdown('<div class="query-example">SISE yatirim yapilabilir mi?</div>', unsafe_allow_html=True)

    st.markdown("**⚖️ Comparison**")
    st.markdown('<div class="query-example">AKBNK ve GARAN karsilastir</div>', unsafe_allow_html=True)
    st.markdown('<div class="query-example">Holding hisseleri</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #7f8c8d; padding: 1rem;">'
    'BIST Analysis Agent | Powered by Gemini 2.0 Flash & LangGraph | '
    f'{len(config.TARGET_TICKERS)} companies supported'
    '</div>',
    unsafe_allow_html=True
)
