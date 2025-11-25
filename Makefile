.PHONY: help install test clean dev setup models run

help:  ## Show this help
	@echo "FaceSwap Build System"
	@echo "===================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install core dependencies
	@echo "Installing core dependencies..."
	pip install -r requirements.txt

dev-install:  ## Install with development dependencies
	@echo "Installing with development dependencies..."
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8

models:  ## Download required AI models
	@echo "Downloading AI models..."
	python download_models.py

setup: install models test-install  ## Complete setup (install + models + verify)
	@echo ""
	@echo "✅ Setup complete!"
	@echo "Run the application with: make run"

test-install:  ## Test installation only
	python run_tests.py --installation

test-quick:  ## Run quick tests (excludes slow tests)
	python run_tests.py --quick

test-all:  ## Run all tests including slow ones
	python run_tests.py

test-coverage:  ## Run tests with coverage report
	python run_tests.py --coverage

run:  ## Run the FaceSwap application
	python main.py

clean:  ## Clean temporary files and caches
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "htmlcov" -delete
	rm -rf build/ dist/ *.egg-info/
	rm -f .coverage

format:  ## Format code with black
	@echo "Formatting code..."
	black --line-length 100 .

lint:  ## Run code linting
	@echo "Running linting..."
	flake8 --max-line-length=100 --ignore=E203,W503 .

check: lint test-quick  ## Run quality checks (lint + quick tests)
	@echo "Quality checks complete!"

build-dev: clean dev-install setup  ## Complete development build
	@echo "Development environment ready!"

status:  ## Show project status
	@echo "FaceSwap Project Status"
	@echo "======================"
	@echo "Python version: $$(python --version)"
	@echo "Pip version: $$(pip --version)"
	@echo "Project root: $$(pwd)"
	@echo "Dependencies status:"
	@pip list | grep -E "(opencv|numpy|PySide|dlib|pytest)" || echo "  No key dependencies found"
	@echo ""
	@echo "Models status:"
	@ls -la models/ 2>/dev/null || echo "  Models directory not found"

list-files:  ## List current project files
	@echo "Current FaceSwap directory contents:"
	@echo "===================================="
	@ls -la
	@echo ""
	@echo "Redundant files that should be removed:"
	@ls -1 test_app.py test_gpu_acceleration.py test_installation.py quick_test.sh install_test_deps.py install.sh install.bat 2>/dev/null || echo "  (No redundant files found)"

remove-redundant:  ## Remove redundant files (one-time cleanup)
	@echo "Removing redundant files..."
	@rm -f test_app.py test_gpu_acceleration.py test_installation.py
	@rm -f quick_test.sh install_test_deps.py install.sh install.bat
	@rm -f tests/test_automated_stress.py tests/test_automated_integration.py tests/test_automated_face_detection.py
	@echo "✅ Cleanup complete!"
	@echo ""
	@echo "Current directory after cleanup:"
	@ls -1

verify-clean:  ## Verify clean directory structure
	@echo "FaceSwap Directory Structure Verification"
	@echo "========================================"
	@echo ""
	@echo "✅ Essential files:"
	@ls -1 main.py config.py requirements.txt Makefile setup.py 2>/dev/null | sed 's/^/  /'
	@echo ""
	@echo "✅ Core modules:"
	@ls -1 face_*.py download_models.py run_tests.py 2>/dev/null | sed 's/^/  /'
	@echo ""
	@echo "✅ Directories:"
	@ls -1d gui/ utils/ tests/ scripts/ 2>/dev/null | sed 's/^/  /'
	@echo ""
	@echo "Total files in root: $$(ls -1 *.py *.txt *.md Makefile LICENSE 2>/dev/null | wc -l)"
