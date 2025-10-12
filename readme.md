# 🗳️ Rajniti - Simple Election Data API

> **A clean, lightweight Flask API for Indian election data**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![API Version](https://img.shields.io/badge/API-v1.0-orange.svg)](#api-documentation)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Data Coverage](https://img.shields.io/badge/Data-50K%2B_Records-purple.svg)](#data-coverage)

A simple, clean REST API serving Indian Election Commission data from JSON files. Built with minimal Flask setup for easy deployment and scraping capabilities.

---

## 🌟 **Key Features**

<div align="center">

| Feature                     | Description                                               |
| --------------------------- | --------------------------------------------------------- |
| 🚀 **Simple Flask API**     | Clean RESTful endpoints serving JSON data                 |
| 📊 **Election Data**        | 50,000+ records across Lok Sabha & Assembly elections     |
| 🔍 **Search & Filter**      | Basic search and filtering capabilities                   |
| 🕸️ **Intelligent Scraping** | Advanced scraping system with retry logic & rate limiting |
| 📸 **Image Downloads**      | Candidate photos and party symbols extraction             |
| ⚡ **Lightweight**          | Minimal dependencies, fast startup                        |
| 🐳 **Docker Ready**         | Single container deployment                               |

</div>

---

## 📊 **Data Coverage**

<div align="center">

| Election                | Candidates  | Constituencies | Parties  | Status               |
| ----------------------- | ----------- | -------------- | -------- | -------------------- |
| **Lok Sabha 2024**      | 3,802+      | 543            | 211+     | ✅ Complete          |
| **Delhi Assembly 2025** | 6,922+      | 70             | 11+      | ✅ Complete          |
| **Maharashtra 2024**    | 39,817+     | 288            | 76+      | ✅ Complete          |
| **Total Coverage**      | **50,541+** | **901**        | **298+** | **🎯 Comprehensive** |

</div>

---

## 🚀 **Quick Start**

### **Option 1: Docker (Recommended)**

```bash
# Clone the repository
git clone https://github.com/your-username/rajniti.git
cd rajniti

# Start with Docker Compose
docker-compose up -d

# API available at http://localhost:8080
# Health check: http://localhost:8080/api/v1/health
```

### **Option 2: Local Installation (Automated)**

```bash
# Clone and setup
git clone https://github.com/your-username/rajniti.git
cd rajniti

# Automated setup (recommended)
make setup

# Start development server
make dev

# Or run directly
python run.py
```

### **Option 3: Manual Setup**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run development server
python run.py
```

---

## 🕸️ **Data Scraping**

### **🎯 Overview**

Rajniti includes powerful scraping capabilities to collect fresh election data from the Election Commission of India (ECI) website. The scraping system is modular and supports both Lok Sabha and Assembly elections.

### **🚀 Quick Start Scraping**

#### **✨ NEW: Interactive Scraper (Recommended)**

The easiest way to scrape election data - just provide the URL!

```bash
# Activate virtual environment
source venv/bin/activate

# Run interactive scraper (auto-detects everything!)
python scripts/scrape_interactive.py

# You'll be prompted for:
# 1. Election Results URL (e.g., https://results.eci.gov.in/ResultAcGenFeb2025)
# 2. Election Type (LOK_SABHA or VIDHAN_SABHA)
# Everything else is auto-discovered!
```

#### **Legacy Scraping Methods**

```bash
# Direct URL scraping (no hardcoded values!)
python scripts/scrape_lok_sabha.py --url https://results.eci.gov.in/PcResultGen2024
python scripts/scrape_vidhan_sabha.py --url https://results.eci.gov.in/ResultAcGenFeb2025

# Legacy: State/Year based (constructs URLs automatically)
python scripts/scrape_lok_sabha.py --year 2024
python scripts/scrape_vidhan_sabha.py --state DL --year 2025

# Using Make commands
make setup  # Setup environment first
make scrape-help # Show scraping help
```

### **📋 Available Scrapers**

<div align="center">

| Scraper                  | Description                     | Command                            | Data Output                  |
| ------------------------ | ------------------------------- | ---------------------------------- | ---------------------------- |
| **✨ Interactive (NEW)** | URL-based, auto-discovery       | `scrape_interactive.py`            | Complete election data       |
| **🏛️ Lok Sabha**         | Parliamentary elections         | `scrape_lok_sabha.py --url URL`    | Candidates, Parties, Results |
| **🏛️ Vidhan Sabha**      | State assembly elections        | `scrape_vidhan_sabha.py --url URL` | Assembly candidates, Results |
| **🎯 Complete**          | All elections combined (legacy) | `scrape_all.py --year 2024`        | Comprehensive dataset        |

</div>

### **⚙️ Scraping Commands**

#### **✨ Interactive Scraper (Recommended)**

```bash
# Interactive mode - easiest way!
python scripts/scrape_interactive.py

# The script will guide you through:
# 1. Enter the ECI results URL
# 2. Confirm or select election type (auto-detected)
# 3. Review configuration
# 4. Start scraping with full auto-discovery!

# Example URLs you can use:
# - https://results.eci.gov.in/PcResultGen2024         (Lok Sabha 2024)
# - https://results.eci.gov.in/ResultAcGenFeb2025     (Delhi 2025)
# - https://results.eci.gov.in/ResultAcGenOct2024     (Maharashtra 2024)
```

#### **Direct URL Scraping**

```bash
# Lok Sabha Elections (URL-based)
python scripts/scrape_lok_sabha.py --url https://results.eci.gov.in/PcResultGen2024

# Vidhan Sabha Elections (URL-based)
python scripts/scrape_vidhan_sabha.py --url https://results.eci.gov.in/ResultAcGenFeb2025

# Custom output directory
python scripts/scrape_lok_sabha.py --url URL --output-dir data/custom
python scripts/scrape_vidhan_sabha.py --url URL --output-dir data/custom
```

### **🏗️ Scraper Architecture**

```
app/scrapers/
├── base.py                    # 🏗️ Base scraping classes
│   ├── BaseScraper            # Core scraping functionality
│   ├── ECIScraper             # ECI-specific scraper with auto-discovery
│   │   ├── discover_constituency_links()  # Auto-find constituencies
│   │   └── discover_party_links()         # Auto-find parties
│   ├── PartyScraper           # Party data extraction
│   ├── CandidateScraper       # Candidate data extraction
│   └── ConstituencyScraper    # Constituency data extraction
├── lok_sabha.py              # 🏛️ Lok Sabha scrapers (URL-based)
└── vidhan_sabha.py           # 🏛️ Assembly scrapers (URL-based)

scripts/
├── scrape_interactive.py     # ✨ NEW: Interactive URL-based scraper
├── scrape_lok_sabha.py       # 🏛️ Parliamentary elections (URL/legacy)
├── scrape_vidhan_sabha.py    # 🏛️ Assembly elections (URL/legacy)
└── scrape_all.py             # 🎯 Complete scraping script (legacy)
```

### **📊 Data Sources & URLs**

The scrapers automatically fetch data from:

-   **Lok Sabha 2024**: `https://results.eci.gov.in/PcResultGen2024/`
-   **Assembly Elections**: State-specific ECI result pages
-   **Party Results**: Party-wise winner lists
-   **Candidate Data**: Complete candidate profiles with photos
-   **Constituency Info**: Constituency-wise detailed results

### **⚡ Scraping Features**

-   **✨ Auto-Discovery**: Automatically finds constituencies and parties (NEW!)
-   **🌐 URL-Based**: No hardcoded values - works with any ECI URL (NEW!)
-   **🤖 Interactive Mode**: Guided scraping with smart defaults (NEW!)
-   **🔄 Retry Logic**: Automatic retry with exponential backoff
-   **🛡️ Rate Limiting**: Respectful scraping with delays
-   **📸 Image Downloads**: Candidate photos and party symbols
-   **🧹 Data Cleaning**: Automatic data normalization
-   **📁 JSON Output**: Clean, structured data files
-   **🔍 Error Handling**: Comprehensive error reporting
-   **📈 Progress Tracking**: Real-time scraping progress
-   **🎯 Flexible Scraping**: URL-based or legacy state/year modes

### **🛠️ Advanced Usage**

#### **Custom Scraping Configuration**

```python
from app.scrapers.lok_sabha import LokSabhaScraper
from app.scrapers.vidhan_sabha import VidhanSabhaScraper

# URL-based scraping (recommended)
lok_sabha_scraper = LokSabhaScraper(
    base_url="https://results.eci.gov.in/PcResultGen2024",
    output_dir="custom_data/lok_sabha"
)

vidhan_sabha_scraper = VidhanSabhaScraper(
    base_url="https://results.eci.gov.in/ResultAcGenFeb2025",
    output_dir="custom_data/vidhan_sabha",
    state_code="DL"  # Optional, auto-detected if not provided
)

# Run scraping with auto-discovery
lok_sabha_scraper.scrape()
vidhan_sabha_scraper.scrape()

# Auto-discovery also available independently
constituencies = scraper.discover_constituency_links()
parties = scraper.discover_party_links()
```

#### **Environment Variables**

```bash
# Configure scraping behavior
export ECI_BASE_URL="https://results.eci.gov.in"
export SCRAPER_RETRY_ATTEMPTS=3
export SCRAPER_RETRY_DELAY=2
export SCRAPER_TIMEOUT=30
```

### **🎭 Supported Elections**

<div align="center">

| Election Type      | Years Available  | States Supported | Status        |
| ------------------ | ---------------- | ---------------- | ------------- |
| **Lok Sabha**      | 2024, 2019, 2014 | All India        | ✅ Active     |
| **Delhi Assembly** | 2025, 2020, 2015 | Delhi            | ✅ Active     |
| **Maharashtra**    | 2024, 2019       | Maharashtra      | ✅ Active     |
| **Other States**   | Various          | Generic Support  | 🔄 On Request |

</div>

### **📋 Output Data Structure**

#### **Candidates Data**

```json
{
    "name": "Candidate Name",
    "party": "Party Name",
    "constituency": "Constituency Name",
    "status": "WON/LOST",
    "votes": "12345",
    "margin": "1234",
    "image_url": "https://results.eci.gov.in/...",
    "election_type": "LOK_SABHA/VIDHAN_SABHA"
}
```

#### **Party Results**

```json
{
  "party_name": "Party Name",
  "symbol": "Party Symbol",
  "total_seats": 303,
  "winning_candidates": [...]
}
```

### **🚨 Important Notes**

-   **⏰ Respectful Scraping**: Built-in delays to avoid overwhelming ECI servers
-   **🔄 Data Updates**: Re-run scrapers to get latest results
-   **💾 Storage**: Large datasets may require significant disk space
-   **🌐 Internet Required**: Active internet connection needed for scraping
-   **📅 Election Timing**: Best results during and after election declaration

### **🐛 Troubleshooting Scraping**

```bash
# Common issues and solutions

# 1. Connection timeout
python scripts/scrape_all.py --year 2024  # Increase timeout in config

# 2. Missing dependencies
pip install -r requirements.txt

# 3. Permission errors
chmod +x scripts/scrape_all.py

# 4. Rate limiting
# Wait and retry - scrapers include automatic rate limiting

# 5. Incomplete data
# Check network connection and ECI website availability
```

---

## 📚 **API Documentation**

### **🎯 Simple API Documentation**

-   **API Base URL**: `http://localhost:8080/api/v1/`
-   **Health Check**: `http://localhost:8080/api/v1/health`

### **🔥 Core Endpoints**

#### **Elections API**

```bash
GET /api/v1/elections                             # All elections
GET /api/v1/elections/{election-id}               # Election details
GET /api/v1/elections/{election-id}/results       # Election results
GET /api/v1/elections/{election-id}/winners       # Winners only
```

#### **Candidates API**

```bash
GET /api/v1/candidates/search?q=modi              # Search candidates
GET /api/v1/candidates/winners                    # All winners
GET /api/v1/candidates/party/{party-name}         # Party candidates
GET /api/v1/elections/{id}/candidates/{id}        # Candidate details
```

#### **Constituencies API**

```bash
GET /api/v1/elections/{id}/constituencies          # Election constituencies
GET /api/v1/elections/{id}/constituencies/{id}     # Constituency details
GET /api/v1/constituencies/state/{state-code}      # State constituencies
```

#### **Parties API**

```bash
GET /api/v1/elections/{id}/parties                 # Election parties
GET /api/v1/elections/{id}/parties/{name}          # Party details
GET /api/v1/parties                               # All parties
GET /api/v1/parties/{name}/performance            # Party performance
```

---

## 💡 **Usage Examples**

### **Basic Queries**

```bash
# Get all elections
curl "http://localhost:8080/api/v1/elections"

# Search for candidates named "Modi"
curl "http://localhost:8080/api/v1/candidates/search?q=modi"

# Get Lok Sabha 2024 winners
curl "http://localhost:8080/api/v1/elections/lok-sabha-2024/winners"

# Get all parties
curl "http://localhost:8080/api/v1/parties"
```

### **Filtering Examples**

```bash
# Get candidates by party
curl "http://localhost:8080/api/v1/candidates/party/Bharatiya%20Janata%20Party"

# Get constituency candidates
curl "http://localhost:8080/api/v1/elections/delhi-assembly-2025/constituencies/DL-1/candidates"

# Get party performance
curl "http://localhost:8080/api/v1/parties/Bharatiya%20Janata%20Party/performance"
```

### **Python Integration**

```python
import requests

# Simple API client
BASE_URL = "http://localhost:8080/api/v1"

# Search for candidates
response = requests.get(f"{BASE_URL}/candidates/search", params={"q": "modi"})
data = response.json()

if data['success']:
    for candidate in data['data']['candidates']:
        name = candidate.get('Name') or candidate.get('candidate_name', '')
        party = candidate.get('Party', '')
        print(f"{name} - {party}")

# Get election details
response = requests.get(f"{BASE_URL}/elections/lok-sabha-2024")
election = response.json()
print(f"Election: {election['data']['name']}")
print(f"Total candidates: {election['data']['statistics']['total_candidates']}")
```

---

## 🏗️ **Architecture**

```
rajniti/
├── app/
│   ├── controllers/            # 🎯 MVC Controllers (business logic)
│   ├── core/                   # 🔧 Simple utilities & exceptions
│   ├── data/                   # 📊 Election data (JSON files)
│   │   ├── lok_sabha/          # Lok Sabha election data
│   │   └── vidhan_sabha/       # Assembly election data
│   ├── models/                 # 📋 Pydantic models
│   ├── routes/                 # 🌐 Flask API routes
│   ├── services/               # 💾 Data access layer
│   └── __init__.py             # Flask app factory
├── tests/                      # Test files
├── requirements.in             # 📦 Direct dependencies
├── requirements.txt            # 📦 Compiled dependencies (pip-compile)
├── docker-compose.yml          # 🐳 Docker setup
├── dockerfile                  # 🐳 Container config
└── run.py                      # 🚀 Development server
```

---

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Application (minimal configuration)
SECRET_KEY=your-secret-key              # Flask secret key
FLASK_ENV=production                    # Environment (development/production)
```

---

## 🚢 **Deployment**

### **Docker Deployment**

```yaml
# docker-compose.yml
version: "3.8"
services:
    rajniti-api:
        build: .
        ports:
            - "8080:8080"
        environment:
            - FLASK_ENV=production
            - SECRET_KEY=${SECRET_KEY}
        volumes:
            - ./app/data:/app/app/data:ro

    redis:
        image: redis:7-alpine
        ports:
            - "6379:6379"
```

```bash
# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### **Cloud Deployment**

#### **Heroku**

```bash
# Install Heroku CLI and login
heroku create your-rajniti-api
git push heroku main
```

#### **AWS/Digital Ocean**

```bash
# Build and push to container registry
docker build -t rajniti-api .
docker tag rajniti-api your-registry/rajniti-api
docker push your-registry/rajniti-api
```

---

## 🧪 **Testing & Development**

### **Dependency Management (pip-compile)**

```bash
# Install pip-tools
pip install pip-tools

# Add new dependency to requirements.in
echo "new-package==1.0.0" >> requirements.in

# Compile dependencies
pip-compile requirements.in

# Install compiled dependencies
pip-sync requirements.txt

# Or upgrade all
pip-compile --upgrade requirements.in
```

### **Running Tests**

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Format code
black app/
isort app/
flake8 app/
```

## 📈 **Performance & Scalability**

### **Performance Features**

-   **Fast Startup**: Minimal dependencies, quick boot time
-   **JSON Serving**: Direct file-based data serving
-   **Simple Search**: Basic filtering and search capabilities
-   **Memory Efficient**: Low memory footprint
-   **Stateless**: No database dependencies

---

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

### **Development Setup**

```bash
# Fork and clone
git clone https://github.com/your-username/rajniti.git
cd rajniti

# Create feature branch
git checkout -b feature/amazing-feature

# Install dependencies using pip-compile
pip install pip-tools
pip-sync requirements.txt

# Make your changes and test
pytest tests/

# Submit pull request
git push origin feature/amazing-feature
```

### **Contribution Guidelines**

-   🐛 **Bug Reports**: Use GitHub issues with detailed descriptions
-   ✨ **Feature Requests**: Discuss in issues before implementing
-   📝 **Documentation**: Update docs for any API changes
-   ✅ **Testing**: Ensure tests pass and add new tests
-   🎨 **Code Style**: Follow Black formatting and PEP 8

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

-   **Election Commission of India** for providing comprehensive election data
-   **Flask Community** for the excellent web framework
-   **Contributors** who helped make this project possible

---

## 📞 **Support & Community**

<div align="center">

[![GitHub Issues](https://img.shields.io/badge/Issues-GitHub-red.svg)](https://github.com/your-username/rajniti/issues)
[![Discussions](https://img.shields.io/badge/Discussions-GitHub-blue.svg)](https://github.com/your-username/rajniti/discussions)
[![Email](https://img.shields.io/badge/Email-Contact-green.svg)](mailto:rajniti@example.com)

**⭐ Star this repository if you find it helpful!**

</div>

---

<div align="center">

**Built with ❤️ for Indian Democracy**

_Empowering citizens, researchers, and developers with accessible election data_

</div>
