"""
Test setup utility to ensure proper imports.
Run this script directly to validate imports work.
"""
import os
import sys
import importlib

def setup_test_env():
    """Set up environment for tests"""
    # Add the project root directory to Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    src_path = os.path.join(project_root, 'src')
    
    print(f"Project root: {project_root}")
    print(f"Src path: {src_path}")
    
    # Add paths if not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Set PYTHONPATH environment variable
    paths = [project_root, src_path]
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    if current_pythonpath:
        os.environ["PYTHONPATH"] = os.pathsep.join(paths + [current_pythonpath])
    else:
        os.environ["PYTHONPATH"] = os.pathsep.join(paths)
    
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    print(f"sys.path: {sys.path}")
    
    # Try importing key modules to validate setup
    modules_to_test = [
        'src.app',
        'app',
        'src.app.extensions',
        'app.extensions',
        'src.app.models.user',
        'app.models.user'
    ]
    
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"✓ Successfully imported {module_name}")
        except ImportError as e:
            print(f"✗ Failed to import {module_name}: {e}")

if __name__ == "__main__":
    setup_test_env()
    print("Test environment setup completed.")
