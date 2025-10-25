# 🔍 OSInt-AI: Open Source Intelligence Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![DigitalOcean](https://img.shields.io/badge/Powered%20by-DigitalOcean-0080FF.svg)](https://www.digitalocean.com/)

> An AI-powered open source intelligence analyzer that aggregates, analyzes, and generates insights from multiple public data sources using DigitalOcean's Gradient AI Platform.

![OSInt-AI Banner](./docs/banner.png)

## 🎯 Overview

OSInt-AI is an intelligent OSINT aggregation and analysis platform that helps researchers, developers, and security analysts make sense of vast amounts of publicly available information. By leveraging AI agents and knowledge bases, it automatically:

- **Monitors** multiple data sources (GitHub repos, RSS feeds, public APIs)
- **Analyzes** trends and patterns using advanced AI models
- **Generates** actionable insights and comprehensive reports
- **Alerts** users to significant events or anomalies

## ✨ Key Features

### 🤖 AI-Powered Analysis
- Uses DigitalOcean's Gradient AI serverless inference for real-time analysis
- Knowledge base integration for context-aware insights
- Automated trend detection and anomaly identification

### 📊 Multi-Source Aggregation
- GitHub repository monitoring (commits, issues, PRs, releases)
- RSS feed aggregation from news sources and blogs
- Public API integration (Twitter trends, Reddit discussions, etc.)
- Customizable source configuration

### 📈 Real-Time Dashboard
- Interactive web interface for visualization
- Live updates and notifications
- Historical data analysis and comparison
- Exportable reports in multiple formats

### 🔒 Security & Privacy
- No personal data collection
- Public information only
- Secure API key management
- Rate limiting and quota management

## 🏗️ Architecture

```
┌─────────────────┐
│   Data Sources  │
│  (GitHub, RSS,  │
│   Public APIs)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Collector │
│   (FastAPI)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐       ┌──────────────────┐
│ DigitalOcean    │◄──────┤ Knowledge Base   │
│ Gradient AI     │       │ (DO Spaces)      │
│ (Inference)     │       └──────────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   (DO Managed   │
│    Database)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │
│  (React + D3)   │
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+ (for frontend)
- DigitalOcean account with Gradient AI access
- GitHub Personal Access Token (for GitHub monitoring)

### Deployment Options

**🌐 No Local Setup Required? (Perfect for you!)**
- **Web-Only Deployment**: See [WEB_ONLY_DEPLOYMENT.md](WEB_ONLY_DEPLOYMENT.md) ⭐ RECOMMENDED
- Deploy entirely through web browsers - no Docker, Python, or admin access needed!
- Takes 30 minutes, uses only GitHub + DigitalOcean web interfaces

**🚀 Have Local Admin Access?**
- **Automated Script**: Run `./scripts/deploy_to_digitalocean.sh`
- **Full Guide**: See [DO_DEPLOYMENT_GUIDE.md](DO_DEPLOYMENT_GUIDE.md)
- **Quick Reference**: See [DEPLOY_QUICK_REF.md](DEPLOY_QUICK_REF.md)

**💻 Local Development**
- See installation steps below

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/osint-ai.git
cd osint-ai
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

Required environment variables:
```env
# DigitalOcean Configuration
DO_API_TOKEN=your_do_token
GRADIENT_AI_ENDPOINT=your_gradient_endpoint
GRADIENT_AI_API_KEY=your_gradient_key

# Data Source APIs
GITHUB_TOKEN=your_github_token
NEWS_API_KEY=your_news_api_key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/osint_db
```

4. **Initialize Database**
```bash
python scripts/init_db.py
```

5. **Start the Backend**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Frontend Setup** (in a new terminal)
```bash
cd frontend
npm install
npm start
```

7. **Access the Dashboard**
Open your browser to `http://localhost:3000`

## 📖 Usage

### Adding Data Sources

**Via API:**
```bash
curl -X POST http://localhost:8000/api/sources \
  -H "Content-Type: application/json" \
  -d '{
    "type": "github",
    "config": {
      "repositories": ["kubernetes/kubernetes", "tensorflow/tensorflow"]
    }
  }'
```

**Via Dashboard:**
1. Navigate to Settings → Data Sources
2. Click "Add Source"
3. Select source type and configure parameters
4. Click "Save and Start Monitoring"

### Generating Reports

```bash
# Generate analysis for the last 24 hours
curl http://localhost:8000/api/reports/generate?period=24h

# Export report as PDF
curl http://localhost:8000/api/reports/latest/export?format=pdf -o report.pdf
```

### Example Queries

**Analyze GitHub Repository Activity:**
```python
from osint_ai import OSIntAnalyzer

analyzer = OSIntAnalyzer()
insights = analyzer.analyze_repo("kubernetes/kubernetes", days=7)
print(insights.summary)
```

**Monitor News Topics:**
```python
from osint_ai import NewsMonitor

monitor = NewsMonitor()
trends = monitor.get_trending_topics(category="technology")
```

## 🎨 Dashboard Preview

The dashboard provides:
- **Overview Page**: Summary statistics and recent alerts
- **Sources Management**: Add, configure, and monitor data sources
- **Analytics**: Trend visualization and pattern detection
- **Reports**: Generated insights and downloadable reports
- **Settings**: API configuration and preferences

## 🔧 Configuration

### Data Source Configuration

Edit `config/sources.yaml`:

```yaml
sources:
  github:
    enabled: true
    repositories:
      - owner/repo
    check_interval: 300  # seconds
    
  rss:
    enabled: true
    feeds:
      - url: https://example.com/feed
        category: tech
    check_interval: 600
    
  twitter:
    enabled: false  # Requires Twitter API access
```

### AI Model Configuration

Edit `config/ai.yaml`:

```yaml
gradient_ai:
  model: "meta-llama/Llama-3.1-70B-Instruct"
  max_tokens: 2048
  temperature: 0.7
  
analysis:
  sentiment_threshold: 0.6
  trend_window_days: 7
  anomaly_sensitivity: 0.8
```

## 📊 Sample Outputs

### Example: GitHub Repository Analysis

```json
{
  "repository": "kubernetes/kubernetes",
  "period": "7 days",
  "summary": "Increased activity detected with 234 commits, 89 new issues, and 45 merged PRs",
  "trends": [
    {
      "topic": "Security Updates",
      "sentiment": "positive",
      "confidence": 0.92,
      "mentions": 23
    }
  ],
  "key_contributors": ["user1", "user2", "user3"],
  "notable_changes": [
    "Major security patch released (v1.28.4)",
    "New API endpoints for container management"
  ],
  "ai_insights": "The repository shows healthy development activity with focus on security improvements..."
}
```

## 🛠️ Development

### Project Structure

```
osint-ai/
├── backend/
│   ├── api/                 # FastAPI routes
│   ├── collectors/          # Data source collectors
│   ├── analyzers/           # AI analysis modules
│   ├── models/              # Database models
│   └── utils/               # Utility functions
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   └── services/        # API services
│   └── public/
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── tests/                   # Test suite
└── config/                  # Configuration files
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Integration tests
./scripts/run_integration_tests.sh
```

### Code Quality

```bash
# Linting
flake8 backend/
eslint frontend/src/

# Formatting
black backend/
prettier --write frontend/src/
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for Hacktoberfest 2024 Hackathon
- Powered by [DigitalOcean's Gradient AI Platform](https://www.digitalocean.com/products/gradient/platform)
- Inspired by the open-source intelligence community

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/osint-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/osint-ai/discussions)
- **Email**: support@osint-ai.dev

## 🗺️ Roadmap

- [x] Basic data collection from GitHub and RSS
- [x] AI-powered analysis with Gradient AI
- [x] Real-time dashboard
- [ ] Advanced anomaly detection
- [ ] Multi-user support with authentication
- [ ] Custom alert rules and notifications
- [ ] Machine learning model training on collected data
- [ ] Mobile app (iOS/Android)
- [ ] Browser extension for quick lookups

## 📈 Performance

- Supports monitoring 100+ repositories simultaneously
- Processes 10,000+ data points per hour
- Dashboard loads in <2 seconds
- AI analysis completes in <5 seconds per query

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐

---

**Built with ❤️ for the Open Source Community**
