# BIST Stock Market Analysis Agent

A Turkish stock market (BIST) decision support system demonstrating advanced AI techniques: RAG, Agentic Workflows, and comprehensive evaluation metrics.

**Technologies**: LangGraph, Gemini, LanceDB, RAGAS, W&B

---

## Features

### 1. Multi-Tool Agentic Workflow
- **Market Data Tool**: Real-time BIST stock fundamentals (P/E, P/B, price data)
- **Macro Data Tool**: Turkish macroeconomic indicators (interest rates, inflation, FX)
- **Technical Analysis Tool**: RSI, MACD, Bollinger Bands, support/resistance
- **Model Portfolios Tool**: Institutional investor recommendations and target prices
- **RAG Search Tool**: Semantic search through financial documents

### 2. RAG Pipeline
- Automated document generation from live API data
- Smart chunking with overlap
- Gemini embeddings (text-embedding-004)
- LanceDB vector store with hybrid search
- Contextual retrieval for enhanced responses

### 3. Comprehensive Evaluation
- **RAGAS Metrics**: Faithfulness, Answer Relevancy, Context Precision/Recall
- **LLM-as-Judge**: 5-dimension quality scoring (accuracy, depth, reasoning, usefulness, presentation)
- **Tool Metrics**: Precision, Recall, F1 for tool selection
- **Ablation Studies**: 7 configurations to measure component impact
- **W&B Integration**: Experiment tracking and visualization

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- API Keys (create a `.env` file):
  - `GEMINI_API_KEY`: For LLM and embeddings (required)
  - `TCMB_EVDS_API_KEY`: For Turkish economic data (optional)
  - `WANDB_API_KEY`: For experiment tracking (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/Ahmetyasin/Bist-Analysis-Agent.git
cd Bist-Analysis-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Setup Data (First Time Only)

Before using the agent, you need to generate and index documents:

```bash
python main.py --setup
```

This will:
- Fetch live data from BIST API for 10 target stocks
- Generate financial analysis documents
- Create sector reports
- Chunk documents and generate embeddings
- Index in LanceDB vector database

---

## Usage

### Option 1: Web UI (Recommended)

Launch the Streamlit web interface:

```bash
# Option 1: Use the quick start script
./run_ui.sh

# Option 2: Run streamlit directly
streamlit run app.py
```

The UI will open at `http://localhost:8501`

**Note**: A UI flow demonstration video (`UI_flow.mov`) is available in the repository root showing the complete workflow.

**Features:**
- Pre-defined query categories with examples
- Interactive query builder
- Real-time analysis results
- Execution metrics and tool usage display
- Download analysis reports

**Supported Query Types:**
1. **Fundamental Analysis**: Company financials and valuation metrics
2. **Technical Analysis**: Price trends and momentum indicators
3. **Macroeconomic Analysis**: Economic impact on stocks
4. **Institutional Portfolio**: Analyst recommendations
5. **Comprehensive Analysis**: Full multi-dimensional analysis
6. **Sector Analysis**: Industry-level insights
7. **Comparison**: Side-by-side stock comparison
8. **Risk Analysis**: Investment risks and volatility

**Example Queries:**
```
THYAO hissesi icin temel analiz yap
AKBNK ve GARAN'i karsilastir
Bankacilik sektoru gorunumu nasil?
SISE yatirim yapilabilir mi?
```

**Supported Tickers:** THYAO, AKBNK, GARAN, SISE, TUPRS, EREGL, KCHOL, SAHOL, TCELL, BIMAS

### Option 2: Command Line Interface

#### Run Single Query
```bash
python main.py --query "THYAO hissesi icin kapsamli analiz yap"
```

#### Interactive Mode
```bash
python main.py --interactive
```

Chat with the agent in real-time. Type `exit` to quit.

#### Run Evaluation
```bash
python main.py --evaluate
```

Runs 25 test queries across 7 configurations with RAGAS and LLM-Judge metrics.

---

## Project Structure

```
bist-analysis-agent/
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore file
├── requirements.txt          # Python dependencies
├── config.py                 # Central configuration
├── main.py                   # CLI entry point
├── app.py                    # Streamlit web UI
├── run_ui.sh                 # UI launch script
│
├── data/
│   ├── documents/            # Generated financial docs
│   ├── embeddings/           # LanceDB vector store
│   └── evaluation/           # Test queries and results
│
├── src/
│   ├── agent/                # LangGraph Agent
│   │   ├── graph.py         # Agent workflow
│   │   ├── state.py         # Agent state
│   │   ├── nodes.py         # Processing nodes
│   │   └── prompts.py       # System prompts
│   │
│   ├── tools/                # Analysis Tools
│   │   ├── market_data.py   # Stock fundamentals
│   │   ├── macro_data.py    # Macroeconomics
│   │   ├── technicals.py    # Technical indicators
│   │   ├── model_portfolios.py # Recommendations
│   │   └── rag_search.py    # RAG retrieval
│   │
│   ├── rag/                  # RAG Pipeline
│   │   ├── document_generator.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── retrieval.py
│   │
│   ├── evaluation/           # Evaluation Suite
│   │   ├── ragas_metrics.py
│   │   ├── llm_judge.py
│   │   ├── tool_metrics.py
│   │   └── ablation_runner.py
│   │
│   └── utils/
│       └── helpers.py
│
├── scripts/
│   ├── setup_data.py
│   └── run_full_eval_simple.py
│
└── results/                  # Evaluation results
```

---

## Agent Workflow

```
User Query
    ↓
[Parse Query Node]
    - Extract ticker (THYAO, AKBNK, etc.)
    - Determine query type (fundamental, technical, macro, etc.)
    ↓
[Create Plan Node]
    - Select relevant tools based on query type
    - Build execution plan
    ↓
[Gather Data Nodes] (Parallel execution)
    - get_stock_data → Market fundamentals
    - get_macro_data → Economic indicators
    - calculate_technicals → Technical indicators
    - get_model_portfolios → Institutional views
    - search_documents → RAG retrieval
    ↓
[Synthesize Report Node]
    - LLM combines all data sources
    - Generates structured analysis
    - Includes risks, sources, and caveats
    ↓
Final Report
```

---

## Evaluation Metrics

### RAGAS (Retrieval)
- **Faithfulness**: Are claims grounded in retrieved context?
- **Answer Relevancy**: Does answer address the question?
- **Context Precision**: Are retrieved docs relevant?
- **Context Recall**: Was all needed info retrieved?

### LLM-as-Judge (Quality)
- **Data Accuracy** (1-5): Correctness of financial data
- **Analysis Depth** (1-5): Multi-dimensional coverage
- **Reasoning Quality** (1-5): Logic chain from data to conclusions
- **Investor Usefulness** (1-5): Actionable insights
- **Presentation Quality** (1-5): Clarity and structure
- **Overall Score**: Average of 5 dimensions

### Tool Metrics
- **Precision**: % of called tools that were necessary
- **Recall**: % of necessary tools that were called
- **F1 Score**: Harmonic mean of precision/recall
- **Output Validity**: % of tools returning valid data

---

## Configuration

### Target Stocks
10 major BIST companies across sectors:
- **Airlines**: THYAO
- **Banking**: AKBNK, GARAN
- **Industrials**: SISE, TUPRS, EREGL
- **Holdings**: KCHOL, SAHOL
- **Telecom**: TCELL
- **Retail**: BIMAS

### Model Portfolios
Pre-configured recommendations from 4 major Turkish brokerages:
- Is Yatirim
- Oyak Yatirim
- Gedik Yatirim
- Yapi Kredi Yatirim

### Test Queries (25 total)
- 5 Fundamental Analysis
- 3 Technical Analysis
- 3 Macroeconomic
- 3 Model Portfolio
- 4 Comprehensive
- 2 Sector Analysis
- 2 Comparison
- 2 Risk-focused
- 2 Edge cases

---

## Expected Results

Based on similar systems, expected metrics:

### Full System (Baseline)
- RAGAS Faithfulness: 0.80-0.90
- RAGAS Answer Relevancy: 0.85-0.95
- Judge Overall Score: 3.8-4.5 / 5.0
- Tool F1: 0.85-0.95

### Ablation Insights
- **No RAG**: -10-15% faithfulness (loses document grounding)
- **No Tools**: -20-30% overall quality (no real-time data)
- **Zero-shot**: -5-10% vs few-shot (prompting matters)

---

## Viewing Results

### W&B Dashboard
```bash
# After running evaluation, view at:
https://wandb.ai/<your-username>/bist-analysis-agent
```

Compare:
- Metric distributions across configurations
- Individual query performance
- Configuration rankings

### Local JSON
```bash
ls -lh results/
cat results/ablation_results_*.json | jq '.full_system'
```

---

## Troubleshooting

### API Quota Exceeded
**Error**: `429 RESOURCE_EXHAUSTED`

**Solution**:
- Wait for quota reset (daily)
- Check quota: https://ai.dev/rate-limit
- Upgrade to paid tier if needed

### Insufficient Historical Data (Technicals)
**Warning**: Some stocks may have limited data

**Solution**:
- Tool gracefully handles with adjusted parameters
- Returns partial indicators when full calculation impossible

### LanceDB Not Found
**Error**: `Vector store not initialized`

**Solution**:
```bash
python main.py --setup
```

### Slow Embeddings
Embedding 100+ chunks can take 5-10 minutes

**Solution**:
- Normal behavior (Gemini API rate limits)
- Progress shown in console
- One-time cost (embeddings cached)

---

## Next Steps

### 1. Run Your First Analysis
```bash
source venv/bin/activate
python main.py --query "THYAO icin yatirim tavsiyesi"
```

### 2. Explore Interactive Mode
```bash
python main.py --interactive
# Try different queries
# Compare fundamental vs technical analysis
```

### 3. Run Evaluation
```bash
# This will take 30-60 minutes
python main.py --evaluate

# Monitor progress in W&B
```

### 4. Analyze Results
- Check `results/` folder for JSON output
- Visit W&B dashboard for visualizations
- Compare configuration performance

### 5. Extend the System
**Add New Tools**:
- News sentiment analysis
- Earnings calendar
- Peer comparison

**Improve RAG**:
- Add more document types (quarterly reports, news)
- Implement reranking
- Try different chunking strategies

**Enhance Evaluation**:
- Add domain-specific metrics
- Create custom test suites
- Implement A/B testing

---

## Key Design Decisions

### Why LangGraph?
- Explicit control flow for multi-step reasoning
- Easy to debug and visualize workflow
- State persistence across nodes

### Why Gemini?
- Excellent Turkish language support
- Fast inference (gemini-2.0-flash)
- Good quality embeddings (text-embedding-004)
- Free tier generous for development

### Why LanceDB?
- Fast vector search
- Supports hybrid (vector + keyword) search
- No separate server needed
- Easy Python integration

### Why Ablation Studies?
- Proves each component's value
- Identifies failure modes
- Guides future improvements
- Academic rigor for final project

---

## Academic Context

### Course Requirements Met

✅ **RAG Implementation**
- Document generation, chunking, embedding, retrieval
- Semantic search with context injection
- Source attribution

✅ **Agentic Workflows / Tool Use**
- 5 specialized tools
- LangGraph orchestration
- Multi-step reasoning with planning

✅ **Evaluation & Benchmarking**
- RAGAS metrics (industry standard)
- LLM-as-Judge (qualitative assessment)
- Tool usage metrics
- Ablation studies (7 configurations × 3 runs)

✅ **Prompting & Optimization**
- Few-shot examples
- Zero-shot vs one-shot vs three-shot comparison
- System prompts with role definition
- Chain-of-thought in synthesis

---

## Citations & References

### Libraries
- **LangGraph**: Agent orchestration
- **LangChain**: Tool abstractions
- **Gemini API**: LLM and embeddings
- **borsapy**: BIST market data
- **evdspy**: TCMB economic data
- **LanceDB**: Vector database
- **RAGAS**: RAG evaluation metrics
- **W&B**: Experiment tracking

### Methodologies
- RAG: Retrieval-Augmented Generation
- ReAct: Reasoning + Acting paradigm
- Chain-of-Thought prompting
- Few-shot learning
- Ablation testing

---

## License & Disclaimer

**Educational Project**: DSAI 585 Final Project

**Disclaimer**: This system is for educational purposes only. It is NOT financial advice. Always consult a qualified financial advisor before making investment decisions.

---

## Troubleshooting

### "RAG Index Not Found" Warning
Run setup first:
```bash
python main.py --setup
```

### API Quota Exceeded
**Error**: `429 RESOURCE_EXHAUSTED`

**Solution**:
- Wait for quota reset (daily)
- Upgrade to paid tier if needed

### LanceDB Not Found
```bash
python main.py --setup
```

---

## License

This project is for educational purposes.

**Disclaimer**: This system is NOT financial advice. Always consult a qualified financial advisor before making investment decisions.

---

## Technologies

- **LangGraph**: Agent orchestration
- **Gemini**: LLM and embeddings
- **LanceDB**: Vector database
- **RAGAS**: RAG evaluation
- **Streamlit**: Web UI
- **borsapy**: BIST market data
- **evdspy**: Turkish economic data
