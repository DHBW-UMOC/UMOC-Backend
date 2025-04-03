"""
Allows running tests as a module: python -m test
"""
import os
import sys
import pytest

# Add the project root and src directories to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Set PYTHONPATH environment variable
os.environ["PYTHONPATH"] = os.pathsep.join([project_root, src_path, os.environ.get("PYTHONPATH", "")])

if __name__ == "__main__":
    pytest.main()
