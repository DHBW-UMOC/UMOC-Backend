"""Package initialization for tests"""
import os
import sys

# Add the project root and src directories to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')

if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added project root to path: {project_root}")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
    print(f"Added src path to path: {src_path}")

# Print paths for debugging
print(f"Current sys.path in test/__init__.py: {sys.path}")

# Try to import app modules as a test
try:
    import src.app
    print("Successfully imported src.app")
except ImportError as e:
    print(f"Failed to import src.app: {e}")

try:
    import app
    print("Successfully imported app")
except ImportError as e:
    print(f"Failed to import app: {e}")
