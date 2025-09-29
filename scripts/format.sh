#!/bin/bash
# Format script for Rajniti project
# Usage: ./scripts/format.sh

echo "🎨 Running code formatting tools..."

# Activate virtual environment
source venv/bin/activate

echo "🧹 Running autoflake (remove unused imports)..."
autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive app/

echo "📦 Running Black (code formatter)..."
black app/

echo "📋 Running isort (import organizer)..."
isort app/

echo "🔍 Running flake8 (linter)..."
flake8 app/

echo "✅ Formatting complete!"
echo ""
echo "💡 Tip: Run 'pre-commit install' to set up automatic formatting on git commit"
