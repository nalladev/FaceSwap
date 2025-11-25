#!/usr/bin/env python3
"""
Unified Test Runner for FaceSwap Application

This script provides a single entry point for running all tests with proper
configuration and reporting.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --quick            # Run only quick tests
    python run_tests.py --installation     # Run only installation tests
    python run_tests.py --coverage         # Run with coverage
    python run_tests.py --help             # Show help
"""

import sys
import subprocess
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_command(cmd, description=""):
    """Run a command and return success status."""
    if description:
        logger.info(f"{description}")
    
    logger.info(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr and result.returncode != 0:
            print("STDERR:", result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    
    except Exception as e:
        logger.error(f"Failed to run command: {e}")
        return False

def check_pytest_available():
    """Check if pytest is available."""
    try:
        import pytest
        return True
    except ImportError:
        logger.error("pytest not found. Install with: pip install pytest")
        return False

def run_installation_tests():
    """Run installation verification tests."""
    cmd = [sys.executable, "-m", "pytest", "tests/test_installation.py", "-v"]
    return run_command(cmd, "Running installation tests")

def run_quick_tests():
    """Run quick tests (excludes slow tests)."""
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", "-v", 
        "-m", "not slow"
    ]
    return run_command(cmd, "Running quick tests")

def run_all_tests():
    """Run all tests."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    return run_command(cmd, "Running all tests")

def run_with_coverage():
    """Run tests with coverage reporting."""
    try:
        import pytest_cov
    except ImportError:
        logger.warning("pytest-cov not found. Install with: pip install pytest-cov")
        logger.info("Running tests without coverage...")
        return run_all_tests()
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", "-v",
        "--cov=.", 
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov"
    ]
    return run_command(cmd, "Running tests with coverage")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="FaceSwap Test Runner")
    parser.add_argument("--quick", action="store_true", 
                       help="Run only quick tests (excludes slow tests)")
    parser.add_argument("--installation", action="store_true",
                       help="Run only installation verification tests") 
    parser.add_argument("--coverage", action="store_true",
                       help="Run tests with coverage reporting")
    parser.add_argument("--list-tests", action="store_true",
                       help="List available tests without running")
    
    args = parser.parse_args()
    
    # Check prerequisites
    if not check_pytest_available():
        return 1
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)
    
    logger.info(f"FaceSwap Test Runner")
    logger.info(f"Project root: {project_root}")
    logger.info("=" * 50)
    
    success = False
    
    if args.list_tests:
        cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q"]
        success = run_command(cmd, "Listing available tests")
    
    elif args.installation:
        success = run_installation_tests()
    
    elif args.quick:
        success = run_quick_tests()
    
    elif args.coverage:
        success = run_with_coverage()
    
    else:
        success = run_all_tests()
    
    logger.info("=" * 50)
    if success:
        logger.info("✅ Tests completed successfully!")
        return 0
    else:
        logger.error("❌ Some tests failed. Check output above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
