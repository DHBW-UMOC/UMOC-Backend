"""
This file is used by VS Code to bootstrap pytest.
It ensures the paths are set up correctly.
"""
import os
import sys
import pytest  # Ensure pytest is imported

# Ensure the proper directories are in the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')

# Force the paths to be at the beginning
if src_path in sys.path:
    sys.path.remove(src_path)
sys.path.insert(0, src_path)

if project_root in sys.path:
    sys.path.remove(project_root)
sys.path.insert(0, project_root)

# Set environment variables
os.environ['PYTHONPATH'] = os.pathsep.join([project_root, src_path])

print("VS Code Pytest Bootstrap:")
print(f"Project root: {project_root}")
print(f"Src path: {src_path}")
print(f"sys.path: {sys.path}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
print(f"pytest version: {pytest.__version__}")

# Try importing as a test
try:
    import app
    print("Successfully imported app module")
except ImportError as e:
    print(f"Failed to import app module: {e}")
    try:
        import src.app
        print("Successfully imported src.app module")
    except ImportError as e:
        print(f"Failed to import src.app module: {e}")
