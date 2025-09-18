# Rajniti - Election Commission Data API

A production-grade Flask application for scraping and managing Election Commission of India (ECI) data.

## 🏗️ Architecture

```
rajniti/
├── app/                    # Main application package
│   ├── __init__.py        # Application factory
│   ├── routes/            # API route handlers
│   ├── services/          # Business logic layer
│   ├── scrapers/          # ECI data scrapers
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic validation schemas
│   ├── core/              # Core utilities and exceptions
│   ├── config/            # Configuration management
│   └── data/              # Data files
├── tests/                  # Unit and integration tests
├── migrations/            # Database migrations
├── requirements.txt       # Dependencies
├── run.py                 # Development server
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

-   Python 3.9+
-   PostgreSQL
-   Virtual environment

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd rajniti
```

2. **Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set environment variables**

```bash
export FLASK_ENV=development
export DATABASE_URL=postgresql://username:password@localhost/rajniti
export SECRET_KEY=your-secret-key
```

5. **Run database migrations**

```bash
flask db upgrade
```

6. **Start the development server**

```bash
python run.py
```

The API will be available at `http://localhost:8080`

## 📚 API Documentation

### Core Endpoints

#### Elections

-   `POST /api/v1/election` - Create election
-   `GET /api/v1/election/{id}` - Get election by ID
-   `GET /api/v1/elections` - List elections with filters

#### Parties

-   `GET /api/v1/parties` - List all parties
-   `GET /api/v1/party/{name}` - Get party by name
-   `GET /api/v1/party/search?name=` - Search parties

#### Candidates

-   `GET /api/v1/candidates` - List all candidates
-   `GET /api/v1/candidate/{id}` - Get candidate by ID
-   `GET /api/v1/candidates/constituency/{id}` - Get candidates by constituency

#### Constituencies

-   `GET /api/v1/constituencies` - List all constituencies
-   `GET /api/v1/constituency/{id}` - Get constituency by ID
-   `GET /api/v1/constituencies/state/{id}` - Get constituencies by state

### Data Import Endpoints

-   `POST /api/v1/election/{id}/party/insert` - Import party data
-   `POST /api/v1/election/{id}/candidate/insert` - Import candidate data
-   `POST /api/v1/election/{id}/constituency/insert` - Import constituency data

### 🆕 Dynamic Data API

Standardized endpoints for accessing organized Election Commission data:

#### Discovery

-   `GET /api/v1/index` - List all available data endpoints

#### Parties

-   `GET /api/v1/parties` - Get parties data
-   `GET /api/v1/parties/schema` - Get parties JSON schema
-   `GET /api/v1/parties/meta` - Get parties metadata

#### Candidates

-   `GET /api/v1/candidates` - Get candidates data with results
-   `GET /api/v1/candidates/schema` - Get candidates JSON schema
-   `GET /api/v1/candidates/meta` - Get candidates metadata

#### Constituencies

-   `GET /api/v1/constituencies` - Get constituencies data
-   `GET /api/v1/constituencies/schema` - Get constituencies JSON schema
-   `GET /api/v1/constituencies/meta` - Get constituencies metadata

#### Elections

-   `GET /api/v1/elections` - Get elections metadata
-   `GET /api/v1/elections/schema` - Get elections JSON schema
-   `GET /api/v1/elections/meta` - Get elections metadata

#### States

-   `GET /api/v1/states` - Get states/UTs data
-   `GET /api/v1/states/schema` - Get states JSON schema
-   `GET /api/v1/states/meta` - Get states metadata

#### 🆕 Lok Sabha 2024 Data

-   `GET /api/v1/lok-sabha-2024` - Complete candidate results (3,802 records)
-   `GET /api/v1/lok-sabha-2024/schema` - Lok Sabha results schema
-   `GET /api/v1/lok-sabha-2024/meta` - Lok Sabha metadata
-   `GET /api/v1/lok-sabha-parties-2024` - Party-wise seat summary (211 parties)
-   `GET /api/v1/lok-sabha-parties-2024/schema` - Party results schema
-   `GET /api/v1/lok-sabha-parties-2024/meta` - Party metadata

#### 🆕 Maharashtra 2024 Data

-   `GET /api/v1/maharashtra-2024` - Assembly candidate results (39,817 records)
-   `GET /api/v1/maharashtra-2024/schema` - Maharashtra results schema
-   `GET /api/v1/maharashtra-2024/meta` - Maharashtra metadata
-   `GET /api/v1/maharashtra-constituencies-2024` - All 288 constituencies
-   `GET /api/v1/maharashtra-constituencies-2024/schema` - Constituencies schema
-   `GET /api/v1/maharashtra-constituencies-2024/meta` - Constituencies metadata
-   `GET /api/v1/maharashtra-parties-2024` - Party results (76 parties)
-   `GET /api/v1/maharashtra-parties-2024/schema` - Party schema
-   `GET /api/v1/maharashtra-parties-2024/meta` - Party metadata

### 🔍 Query Parameters

All data endpoints support filtering and pagination:

```bash
# Filter by field
GET /api/v1/candidates?Status=WON

# Pagination
GET /api/v1/candidates?page=1&limit=50

# Multiple filters
GET /api/v1/constituencies?state_id=DL

# Filter Maharashtra winners
GET /api/v1/maharashtra-2024?Status=Won

# Get Lok Sabha BJP results
GET /api/v1/lok-sabha-parties-2024?party_name=Bharatiya%20Janata%20Party
```

### 📊 Data Coverage

| **Dataset**                     | **Records** | **Description**                       |
| ------------------------------- | ----------- | ------------------------------------- |
| Delhi 2025 Candidates           | 6,922       | Complete candidate results with votes |
| Delhi 2025 Constituencies       | 351         | All 70 constituencies                 |
| Delhi 2025 Parties              | 11          | Party-wise seat summary               |
| Lok Sabha 2024 Results          | 3,802       | National candidate results            |
| Lok Sabha 2024 Parties          | 211         | National party summary                |
| Maharashtra 2024 Results        | 39,817      | Assembly candidate results            |
| Maharashtra 2024 Constituencies | 1,441       | All 288 constituencies                |
| Maharashtra 2024 Parties        | 76          | Assembly party summary                |
| **Total Records**               | **52,670**  | **Complete ECI data coverage**        |

## 🛠️ Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
flake8 .
```

### Database Operations

```bash
# Create migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## 🏭 Production Deployment

### Environment Variables

```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=secure-secret-key
LOG_LEVEL=INFO
```

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8080 "app:create_app()"
```

## 📊 Features

-   **🏭 Production-Ready**: App factory pattern, environment-based config
-   **🔒 Secure**: Input validation, CORS, proper error handling
-   **📝 Documented**: Type hints, docstrings, API documentation
-   **🧪 Testable**: Separated business logic, dependency injection ready
-   **📊 Observable**: Structured logging, error tracking
-   **🚀 Scalable**: Service layer architecture, database connection pooling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.
