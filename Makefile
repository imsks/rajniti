# Makefile for Rajniti project
# Usage: make <command>

.PHONY: help setup dev test format lint clean install pre-commit

help: ## Show this help message
	@echo "Rajniti Project Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Set up the development environment
	./scripts/setup.sh

dev: ## Start the development server
	./scripts/dev.sh

test: ## Run tests
	./scripts/test.sh

format: ## Format code with autoflake, black, isort, and flake8
	./scripts/format.sh

lint: ## Run linting checks
	@echo "🔍 Running linting checks..."
	@source venv/bin/activate && flake8 app/
	@source venv/bin/activate && black --check app/
	@source venv/bin/activate && isort --check-only app/

install: ## Install dependencies
	@echo "📥 Installing dependencies..."
	@source venv/bin/activate && pip install -r requirements.txt

pre-commit: ## Install pre-commit hooks
	@echo "🔗 Installing pre-commit hooks..."
	@source venv/bin/activate && pre-commit install

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type f -name ".coverage" -delete

docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t rajniti .

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run -p 8080:8080 rajniti
