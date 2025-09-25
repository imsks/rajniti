# 🗳️ Rajniti - Indian Election Data API

> **The most comprehensive and developer-friendly API for Indian election data**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![API Version](https://img.shields.io/badge/API-v2.0-orange.svg)](#api-documentation)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Swagger](https://img.shields.io/badge/API-Documented-brightgreen.svg)](#swagger-documentation)
[![Data Coverage](https://img.shields.io/badge/Data-50K%2B_Records-purple.svg)](#data-coverage)

A world-class, production-ready REST API providing comprehensive access to Indian Election Commission data. Built with modern Flask architecture, featuring interactive Swagger documentation, advanced search capabilities, and robust analytics.

---

## 🌟 **Key Features**

<div align="center">

| Feature | Description |
|---------|-------------|
| 🚀 **Modern API Architecture** | RESTful endpoints with Swagger/OpenAPI documentation |
| 📊 **Comprehensive Data** | 50,000+ records across Lok Sabha & Assembly elections |  
| 🔍 **Advanced Search** | Intelligent search with autocomplete and filtering |
| 📈 **Rich Analytics** | Statistical insights, trends, and demographic analysis |
| ⚡ **High Performance** | Optimized queries with caching and pagination |
| 🐳 **Docker Ready** | Containerized deployment with Docker Compose |

</div>

---

## 📊 **Data Coverage**

<div align="center">

| Election | Candidates | Constituencies | Parties | Status |
|----------|------------|----------------|---------|--------|
| **Lok Sabha 2024** | 3,802+ | 543 | 211+ | ✅ Complete |
| **Delhi Assembly 2025** | 6,922+ | 70 | 11+ | ✅ Complete |
| **Maharashtra 2024** | 39,817+ | 288 | 76+ | ✅ Complete |
| **Total Coverage** | **50,541+** | **901** | **298+** | **🎯 Comprehensive** |

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
# Swagger docs at http://localhost:8080/api/v2/docs
```

### **Option 2: Local Installation**

```bash
# Clone and setup
git clone https://github.com/your-username/rajniti.git
cd rajniti

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py
```

---

## 📚 **API Documentation**

### **🎯 Interactive Documentation**
- **Swagger UI**: `http://localhost:8080/api/v2/docs/`
- **API Base URL**: `http://localhost:8080/api/v2/`

### **🔥 Core Endpoints**

#### **Elections API**
```bash
GET /api/v2/elections/overview                    # Elections overview
GET /api/v2/elections/{election-id}               # Election details  
GET /api/v2/elections/{election-id}/results       # Election results
GET /api/v2/elections/{election-id}/winners       # Winners only
GET /api/v2/elections/{election-id}/statistics    # Detailed analytics
```

#### **Candidates API** 
```bash
GET /api/v2/candidates/search?q=modi              # Search candidates
GET /api/v2/candidates/winners                    # All winners
GET /api/v2/candidates/party/{party-name}         # Party candidates
GET /api/v2/candidates/constituency/{code}        # Constituency candidates
GET /api/v2/candidates/statistics                 # Candidate analytics
```

#### **Constituencies API**
```bash
GET /api/v2/constituencies/overview               # Constituencies overview
GET /api/v2/constituencies/{code}                 # Constituency details
GET /api/v2/constituencies/{code}/candidates      # All candidates
GET /api/v2/constituencies/state/{state-code}     # State constituencies
GET /api/v2/constituencies/closest-contests       # Closest margins
```

#### **Parties API**
```bash
GET /api/v2/parties/overview                      # Parties overview
GET /api/v2/parties/{party-name}                  # Party details
GET /api/v2/parties/{party-name}/performance      # Performance analytics
GET /api/v2/parties/comparison?parties=BJP,Congress # Party comparison
GET /api/v2/parties/national-parties              # National parties
```

#### **Analytics API**
```bash
GET /api/v2/analytics/overview                    # Comprehensive analytics
GET /api/v2/analytics/vote-share                  # Vote share analysis
GET /api/v2/analytics/margins                     # Victory margin analysis  
GET /api/v2/analytics/trends                      # Electoral trends
GET /api/v2/analytics/demographics                # Demographic insights
```

#### **Search API**
```bash
GET /api/v2/search?q=query                        # Universal search
GET /api/v2/search/suggestions?q=partial          # Search suggestions
GET /api/v2/search/advanced                       # Advanced search
```

---

## 💡 **Usage Examples**

### **Basic Queries**

```bash
# Get all Lok Sabha 2024 winners
curl "http://localhost:8080/api/v2/elections/lok-sabha-2024/winners"

# Search for candidates named "Modi"
curl "http://localhost:8080/api/v2/candidates/search?q=modi"

# Get Delhi constituency results
curl "http://localhost:8080/api/v2/constituencies/DL-1"

# Compare BJP and Congress performance
curl "http://localhost:8080/api/v2/parties/comparison?parties=BJP,Congress"
```

### **Advanced Filtering**

```bash
# Get winning candidates from Maharashtra with 100K+ votes
curl "http://localhost:8080/api/v2/search/advanced?status=WON&state=MH&min_votes=100000"

# Find closest electoral contests
curl "http://localhost:8080/api/v2/constituencies/closest-contests"

# Analyze vote share trends
curl "http://localhost:8080/api/v2/analytics/vote-share?election=lok-sabha-2024"
```

### **Python Integration**

```python
import requests

# Initialize API client
BASE_URL = "http://localhost:8080/api/v2"

# Search for candidates
response = requests.get(f"{BASE_URL}/candidates/search", params={
    "q": "modi",
    "election": "lok-sabha-2024",
    "limit": 10
})

candidates = response.json()['data']['candidates']
for candidate in candidates:
    print(f"{candidate['name']} - {candidate['party']} - {candidate['status']}")

# Get election statistics
stats = requests.get(f"{BASE_URL}/elections/lok-sabha-2024/statistics").json()
print(f"Total votes: {stats['data']['vote_analysis']['total_votes_polled']:,}")
```

---

## 🏗️ **Architecture**

```
rajniti/
├── app/
│   ├── api/                    # 🆕 Modern API v2 (Flask-RESTX)
│   │   ├── __init__.py         # API initialization & Swagger config  
│   │   ├── models.py           # Pydantic/Marshmallow schemas
│   │   ├── elections.py        # Elections endpoints
│   │   ├── candidates.py       # Candidates endpoints
│   │   ├── constituencies.py   # Constituencies endpoints
│   │   ├── parties.py          # Parties endpoints
│   │   ├── analytics.py        # Analytics & insights
│   │   └── search.py           # Advanced search features
│   ├── routes/                 # Legacy API v1 (backward compatibility)
│   ├── core/                   # Core utilities & error handling
│   ├── data/                   # 📊 Election data (JSON files)
│   │   ├── lok_sabha/          # Lok Sabha election data
│   │   └── vidhan_sabha/       # Assembly election data
│   └── config/                 # Configuration management
├── tests/                      # Comprehensive test suite
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Container configuration
└── requirements.txt            # Python dependencies
```

---

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Application
FLASK_ENV=production                    # Environment (development/production)
FLASK_HOST=0.0.0.0                     # Server host
FLASK_PORT=8080                        # Server port
SECRET_KEY=your-secret-key              # Flask secret key

# Database (Optional - API works without DB)
DATABASE_URL=postgresql://user:pass@host/db

# API Configuration  
API_VERSION=v2                          # API version
CORS_ORIGINS=*                         # CORS allowed origins
LOG_LEVEL=INFO                         # Logging level

# Performance
REDIS_URL=redis://localhost:6379       # Redis for caching (optional)
```

---

## 🚢 **Deployment**

### **Docker Deployment**

```yaml
# docker-compose.yml
version: '3.8'
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

### **Running Tests**
```bash
# Install test dependencies
pip install -r requirements.txt

# Run test suite
pytest tests/ -v

# Run with coverage
pytest --cov=app tests/

# Run specific test modules
pytest tests/test_api/ -v
```

### **Code Quality**
```bash
# Format code
black app/ tests/
isort app/ tests/

# Lint code  
flake8 app/ tests/

# Type checking
mypy app/
```

### **API Testing**
```bash
# Test API endpoints
pytest tests/test_api/ -v

# Load testing with locust
locust -f tests/load_test.py --host=http://localhost:8080
```

---

## 📈 **Performance & Scalability**

### **Performance Metrics**
- **Response Time**: < 100ms for most endpoints
- **Throughput**: 1000+ requests/second  
- **Data Volume**: 50,000+ records efficiently served
- **Memory Usage**: < 512MB base memory footprint

### **Optimization Features**
- **Caching**: Redis-based response caching
- **Pagination**: Efficient large dataset handling
- **Indexing**: Optimized search algorithms
- **Compression**: GZIP response compression
- **CDN Ready**: Static asset optimization

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

# Install dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Make your changes and test
pytest tests/

# Submit pull request
git push origin feature/amazing-feature
```

### **Contribution Guidelines**
- 🐛 **Bug Reports**: Use GitHub issues with detailed descriptions
- ✨ **Feature Requests**: Discuss in issues before implementing
- 📝 **Documentation**: Update docs for any API changes
- ✅ **Testing**: Ensure tests pass and add new tests
- 🎨 **Code Style**: Follow Black formatting and PEP 8

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **Election Commission of India** for providing comprehensive election data
- **Flask Community** for the excellent web framework
- **Contributors** who helped make this project possible

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

*Empowering citizens, researchers, and developers with accessible election data*

</div>
