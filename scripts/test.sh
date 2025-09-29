#!/bin/bash
# Test script for Rajniti project
# Usage: ./scripts/test.sh

echo "🧪 Running tests..."

# Activate virtual environment
source venv/bin/activate

# Run tests
pytest tests/ -v

echo "✅ Tests complete!"
