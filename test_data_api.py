#!/usr/bin/env python3
"""
Test script for the dynamic data API endpoints.
"""
import json
import requests
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8080/api/v1"

def test_endpoint(endpoint: str, description: str) -> bool:
    """Test a single API endpoint."""
    try:
        print(f"Testing {description}...")
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ SUCCESS - {len(str(data))} bytes received")
            
            # If it's a data endpoint, show record count
            if endpoint.endswith(('parties', 'candidates', 'constituencies', 'elections', 'states')):
                if 'data' in data and isinstance(data['data'], list):
                    print(f"  📊 Records: {len(data['data'])}")
                    
            return True
        else:
            print(f"  ❌ FAILED - Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ⚠️  CONNECTION ERROR - Server not running on {BASE_URL}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {str(e)}")
        return False

def main():
    """Test all data API endpoints."""
    print("🔍 TESTING RAJNITI DATA API")
    print("=" * 50)
    
    # Test all data endpoints
    endpoints = [
        ("/index", "🔍 Data Index"),
        
        # Delhi Election Data
        ("/candidates", "🗳️  Delhi Candidates"),
        ("/candidates/schema", "📋 Delhi Candidates Schema"),
        ("/candidates/meta", "📊 Delhi Candidates Meta"),
        ("/constituencies", "🏛️  Delhi Constituencies"),
        ("/constituencies/schema", "📋 Delhi Constituencies Schema"),
        ("/constituencies/meta", "📊 Delhi Constituencies Meta"),
        ("/parties", "🎉 Delhi Parties"),
        ("/parties/schema", "📋 Delhi Parties Schema"),
        ("/parties/meta", "📊 Delhi Parties Meta"),
        
        # General Data
        ("/elections", "🗳️  Elections Meta"),
        ("/elections/schema", "📋 Elections Schema"),
        ("/elections/meta", "📊 Elections Meta"),
        ("/states", "🗺️  States Data"),
        ("/states/schema", "📋 States Schema"),
        ("/states/meta", "📊 States Meta"),
        
        # Lok Sabha 2024
        ("/lok-sabha-2024", "🏛️  Lok Sabha 2024 Results"),
        ("/lok-sabha-2024/schema", "📋 Lok Sabha Schema"),
        ("/lok-sabha-2024/meta", "📊 Lok Sabha Meta"),
        ("/lok-sabha-parties-2024", "🎉 Lok Sabha Parties"),
        ("/lok-sabha-parties-2024/schema", "📋 Lok Sabha Parties Schema"),
        ("/lok-sabha-parties-2024/meta", "📊 Lok Sabha Parties Meta"),
        
        # Maharashtra 2024
        ("/maharashtra-2024", "🗳️  Maharashtra 2024 Results"),
        ("/maharashtra-2024/schema", "📋 Maharashtra Schema"),
        ("/maharashtra-2024/meta", "📊 Maharashtra Meta"),
        ("/maharashtra-constituencies-2024", "🏛️  Maharashtra Constituencies"),
        ("/maharashtra-constituencies-2024/schema", "📋 Maharashtra Constituencies Schema"),
        ("/maharashtra-constituencies-2024/meta", "📊 Maharashtra Constituencies Meta"),
        ("/maharashtra-parties-2024", "🎉 Maharashtra Parties"),
        ("/maharashtra-parties-2024/schema", "📋 Maharashtra Parties Schema"),
        ("/maharashtra-parties-2024/meta", "📊 Maharashtra Parties Meta"),
    ]
    
    passed = 0
    total = len(endpoints)
    
    for endpoint, description in endpoints:
        if test_endpoint(endpoint, description):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ Some tests failed. Check server logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

