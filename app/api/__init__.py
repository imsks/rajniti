"""
Rajniti Public API - Indian Election Data API

A comprehensive RESTful API for accessing Indian election data from Election Commission of India.
Provides access to Lok Sabha, Vidhan Sabha election results, candidate information, 
constituency data, and political party statistics.

Version: 2.0.0
Author: Rajniti Team
License: MIT
"""

from flask import Blueprint
from flask_restx import Api
from app.core.responses import APIResponse

# Create blueprint for API v2
api_bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')

# Create API instance with comprehensive documentation
api = Api(
    api_bp,
    version='2.0.0',
    title='Rajniti - Indian Election Data API',
    description="""
# 🗳️ Rajniti - Indian Election Data API

Welcome to the official API for Indian Election Commission data. This API provides comprehensive 
access to election results, candidate information, constituency data, and political analytics 
for Indian elections.

## 📊 Available Data
- **Lok Sabha 2024**: Complete candidate results (3,802+ records)  
- **Delhi Assembly 2025**: Real-time results (6,900+ candidates, 70 constituencies)
- **Maharashtra Assembly 2024**: Complete results (39,800+ candidates, 288 constituencies)

## 🚀 Key Features
- **Real-time Data**: Always up-to-date with latest ECI results
- **Rich Analytics**: Statistical insights and trends
- **Advanced Filtering**: Query data with multiple parameters
- **High Performance**: Cached responses and optimized queries
- **Developer Friendly**: Comprehensive documentation and examples

## 🔧 Usage Examples

### Get all Lok Sabha 2024 winners
```
GET /api/v2/elections/lok-sabha-2024/results?status=WON
```

### Search candidates by name
```  
GET /api/v2/candidates/search?name=modi&election=lok-sabha-2024
```

### Get constituency-wise results
```
GET /api/v2/constituencies/DL-1/results?year=2025
```

## 📈 Rate Limits
- **Free Tier**: 1000 requests/hour
- **Pro Tier**: 10,000 requests/hour  
- **Enterprise**: Unlimited

## 🤝 Support
- Documentation: [https://rajniti-api.com/docs](https://rajniti-api.com/docs)
- GitHub: [https://github.com/username/rajniti](https://github.com/username/rajniti)
- Issues: [https://github.com/username/rajniti/issues](https://github.com/username/rajniti/issues)

---
Built with ❤️ for Democracy
""",
    doc='/docs/',
    contact="rajniti@example.com",
    license="MIT",
    license_url="https://opensource.org/licenses/MIT",
    security='apikey',
    authorizations={
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
            'description': 'API Key for authentication (optional for public endpoints)'
        }
    },
    ordered=True,
    strict_slashes=False
)

# Error handlers for API
@api.errorhandler(Exception)
def handle_exception(error):
    """Global exception handler for API"""
    return APIResponse.internal_error(str(error))

@api.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors"""
    return APIResponse.not_found("Resource")

@api.errorhandler(400)
def handle_bad_request(error):
    """Handle 400 errors"""
    return APIResponse.error("Bad request", "BAD_REQUEST", 400)

# Import and register namespaces
from app.api.elections import elections_ns
from app.api.candidates import candidates_ns  
from app.api.constituencies import constituencies_ns
from app.api.parties import parties_ns
from app.api.analytics import analytics_ns
from app.api.search import search_ns

# Register namespaces with API
api.add_namespace(elections_ns, path='/elections')
api.add_namespace(candidates_ns, path='/candidates') 
api.add_namespace(constituencies_ns, path='/constituencies')
api.add_namespace(parties_ns, path='/parties')
api.add_namespace(analytics_ns, path='/analytics')
api.add_namespace(search_ns, path='/search')

__all__ = ['api_bp', 'api']
