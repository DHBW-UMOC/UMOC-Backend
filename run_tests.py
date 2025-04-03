#!/usr/bin/env python
"""
Enhanced script to execute tests with proper path setup and more options.
"""
import os
import sys
import argparse
import pytest

def setup_environment():
    """Set up the Python path and environment variables."""
    # Add the project root directory to Python path
    project_root = os.path.abspath(os.path.dirname(__file__))
    src_path = os.path.join(project_root, 'src')
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Set PYTHONPATH environment variable
    paths = [project_root, src_path]
    os.environ["PYTHONPATH"] = os.pathsep.join(paths)
    
    return project_root

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Run UMOC Backend tests')
    parser.add_argument('--path', '-p', default='test/',
                      help='Path to test file or directory (default: test/)')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output')
    parser.add_argument('--markers', '-m', 
                      help='Only run tests with specific markers (e.g., "unit" or "api")')
    parser.add_argument('--failfast', '-f', action='store_true',
                      help='Stop on first failure')
    return parser.parse_args()

def main():
    """Main function to run the tests."""
    project_root = setup_environment()
    print(f"Running tests from: {project_root}")
    
    args = parse_args()
    pytest_args = [args.path]
    
    # Add verbosity flag if requested
    if args.verbose:
        pytest_args.append('-v')
    
    # Add marker filter if specified
    if args.markers:
        pytest_args.extend(['-m', args.markers])
    
    # Add failfast option if requested
    if args.failfast:
        pytest_args.append('--exitfirst')
    
    print(f"Running pytest with arguments: {pytest_args}")
    sys.exit(pytest.main(pytest_args))

if __name__ == "__main__":
    main()
