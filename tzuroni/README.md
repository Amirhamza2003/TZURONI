# CrowdWisdomTrading AI Agent – Internship Assessment

This repository contains a Python backend using CrewAI and browser-use that:
- Scrapes products/markets from multiple prediction platforms
- Identifies which markets are the same across sites using AI agents
- Produces a unified CSV with prices per site and confidence scores

## 🚀 Features

- **Agent 1 (X Data Collector)**: Uses browser automation to scrape prediction markets from multiple sites
- **Agent 2 (Product Identifier)**: AI-powered analysis to identify and match similar markets across platforms
- **Agent 3 (Presenter)**: Creates unified CSV reports with confidence scoring
- **Fallback Mode**: Local API scraping when browser automation isn't available
- **RAG Chat System**: Interactive chat interface for querying prediction markets using vector similarity search
- **Advanced Logging**: Structured logging with metrics tracking and error handling
- **Product Embeddings**: Semantic search capabilities for finding related markets

## 🛠️ Tech Stack

- **Python 3.10+** (tested with 3.13.5)
- **CrewAI 0.165+** (agents and task orchestration)
- **browser-use 0.6+** (browser automation for Agent 1)
- **LiteLLM 1.74+** (LLM abstraction layer)
- **RapidFuzz** (fuzzy string matching for product identification)
- **Requests + BeautifulSoup** (fallback scraping)
- **Pandas** (data processing)

## 📋 Requirements

- Python >=3.10 and <3.14
- OpenAI API key (or other LiteLLM-supported provider)
- Internet connection for scraping

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```bash
# Copy the example file
copy .env.example .env
```

Edit `.env` with your API keys:

```env
# Required: Your LLM provider API key
LITELLM_API_KEY=your-openai-api-key-here
LITELLM_MODEL=gpt-4o-mini

# Optional: Proxy settings
HTTP_PROXY=
HTTPS_PROXY=

# Runtime
PYTHONUNBUFFERED=1
```

### 3. Run the Application

#### Quick Start (Recommended)
```bash
# Navigate to project directory
cd tzuroni

# Run with logging and RAG system (50 markets per site)
python -m src.main --mode local --limit 50 --log-level INFO
```

#### Test Mode (When Network Issues Occur)
```bash
# Run with sample data for testing and demonstration
python -m src.main --mode test --log-level INFO
```

#### Full CrewAI Mode (Browser Automation)
```bash
cd tzuroni
python -m src.main --mode crewai --output data/output/unified_products.csv
```

#### Local Scraping Mode (API-based)
```bash
cd tzuroni
python -m src.main --mode local --limit 100 --output data/output/unified_products.csv
```

#### Auto Mode (Tries CrewAI first, falls back to local)
```bash
cd tzuroni
python -m src.main --mode auto --output data/output/unified_products.csv
```

#### Advanced Options
```bash
# Run with debug logging
python -m src.main --mode local --limit 50 --log-level DEBUG

# Run without RAG system
python -m src.main --mode local --limit 50 --no-rag

# Custom output location
python -m src.main --mode local --limit 50 --output ./my_results.csv

# Custom sites
python -m src.main --mode local --limit 50 --sites polymarket.com kalshi.com
```

### 4. Chat with Products (RAG System)

#### Interactive Chat Interface
```bash
cd tzuroni
python -m src.chat_interface
```

#### Demo RAG Queries
```bash
cd tzuroni
python demo_chat.py
```

#### Chat Commands
Once in the chat interface, you can use these commands:
- `help` - Show available commands and example questions
- `stats` - Show system statistics (products, sites, confidence scores)
- `history` - Show conversation history
- `quit` or `exit` - Exit the chat

#### Example Chat Questions
- "What are the current prices for Trump election markets?"
- "Show me crypto prediction markets"
- "What sports markets are available?"
- "Which markets have the highest confidence scores?"
- "Tell me about election prediction markets"
- "What are the latest technology prediction markets?"



## 📊 Output Format

The generated CSV contains:

| Column | Description |
|--------|-------------|
| `unified_title` | Representative title for the product group |
| `site` | Source website (polymarket, manifold, predictit) |
| `site_product_id` | Original market ID from the site |
| `price` | Current price/probability (0-1 scale) |
| `confidence` | Confidence score for the match (0-1) |

## 🔧 Advanced Usage

### Complete Workflow Example
```bash
# 1. Set up environment
cd tzuroni
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt

# 2. Configure API keys (create .env file)
echo "LITELLM_API_KEY=your-api-key-here" > .env

# 3. Run data collection with logging
python -m src.main --mode local --limit 50 --log-level INFO

# 4. Chat with the collected data
python -m src.chat_interface
```

### Custom Sites
```bash
python -m src.main --sites polymarket.com kalshi.com prediction-market.com
```

### Limit Markets Per Site
```bash
python -m src.main --limit 50 --output data/output/small_sample.csv
```

### Different Output Location
```bash
python -m src.main --output ./my_results.csv
```

### Logging Options
```bash
# View logs in real-time
tail -f logs/pipeline.log

# Run with debug logging
python -m src.main --mode local --limit 50 --log-level DEBUG --log-file logs/debug.log
```

## 🏗️ Architecture

### Agent Design

1. **Agent 1: X Data Collector**
   - Uses `browser-use` tools for dynamic scraping
   - Navigates to prediction market sites
   - Extracts market data in JSON format
   - Handles multiple sites: Polymarket, Manifold, PredictIt, Kalshi

2. **Agent 2: Product Identifier**
   - Analyzes collected market data
   - Uses semantic similarity to match markets
   - Groups similar products with confidence scores
   - Chooses representative titles for each group

3. **Agent 3: Presenter**
   - Creates unified CSV reports
   - Formats data for easy analysis
   - Includes confidence scores and cross-site pricing

### Pipeline Flow

```
[Agent 1: Data Collection] → [Agent 2: Product Matching] → [Agent 3: CSV Generation]
         ↓                           ↓                           ↓
   Browser scraping           AI-powered analysis         Unified CSV output
   JSON market data          Confidence scoring          Cross-site pricing
```

## 🔍 Supported Sites

- **Polymarket** (polymarket.com) - API-based scraping
- **Manifold** (prediction-market.com) - API-based scraping  
- **PredictIt** (predictit.org) - API-based scraping
- **Kalshi** (kalshi.com) - Browser automation ready

## 🛠️ Development

### Project Structure
```
tzuroni/
├── src/
│   ├── agents.py          # CrewAI agent definitions
│   ├── config.py          # Configuration helpers
│   ├── main.py            # Main entry point
│   ├── matching.py        # Product matching logic
│   ├── types.py           # Data models
│   ├── logging_config.py  # Logging and metrics
│   ├── rag_system.py      # RAG chat system
│   ├── chat_interface.py  # Interactive chat
│   └── scrapers/          # Site-specific scrapers
│       ├── polymarket.py
│       ├── manifold.py
│       └── predictit.py
├── data/
│   └── output/            # Generated CSV files
├── logs/                  # Log files
├── requirements.txt       # Python dependencies
├── demo_chat.py          # RAG demo script
├── README.md             # This file
└── .env.example          # Environment template
```

### Adding New Sites

1. Create a new scraper in `src/scrapers/`
2. Implement the `fetch_sitename()` function
3. Register it in `src/main.py` in the `collect_all()` function
4. Add the site to the default sites list

### Customizing Agents

Edit `src/agents.py` to modify:
- Agent roles and goals
- Task descriptions
- Expected output formats
- LLM model selection

## 🐛 Troubleshooting

### Common Issues

**"LITELLM_API_KEY not set"**
- Ensure your `.env` file exists and contains the API key
- Check that the key is valid and has sufficient credits

**"Browser automation failed"**
- Install Playwright browsers: `python -m playwright install`
- Try local mode: `--mode local`

**"No markets collected"**
- Check internet connection
- Verify site APIs are accessible
- Try with `--limit 10` for testing

**"Import errors"**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Debug Mode

For detailed logging, set environment variables:
```bash
export PYTHONUNBUFFERED=1
export CREWAI_VERBOSE=1
```

## 📈 Performance

- **CrewAI Mode**: ~2-5 minutes for 150 markets per site
- **Local Mode**: ~30-60 seconds for 150 markets per site
- **RAG System**: ~2-3 seconds for query processing
- **Memory Usage**: ~200-500MB depending on data size
- **Logging**: Minimal overhead, detailed performance tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is created for the CrowdWisdomTrading AI Agent internship assessment.

## 🆘 Support

For issues related to:
- **CrewAI**: Check [CrewAI documentation](https://docs.crewai.com/)
- **LiteLLM**: Check [LiteLLM documentation](https://docs.litellm.ai/)
- **browser-use**: Check [browser-use documentation](https://github.com/browser-use/browser-use)

---

**Note**: This implementation provides both AI-powered browser automation and reliable API-based fallback scraping to ensure robust data collection across prediction market platforms.
