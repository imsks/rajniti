#!/bin/bash
# Setup script for Rajniti project
# Usage: ./scripts/setup.sh

echo "🔧 Setting up Rajniti project..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install

echo "✅ Setup complete!"
echo ""
echo "💡 Next steps:"
echo "   - Run './scripts/dev.sh' to start the development server"
echo "   - Run './scripts/format.sh' to format code"
echo "   - Run './scripts/test.sh' to run tests"
