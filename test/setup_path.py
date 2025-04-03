"""
Helper module to ensure the test modules can import from the src directory.
"""
import os
import sys

# Add the parent directory (project root) to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')

if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added project root to sys.path: {project_root}")

if src_path not in sys.path:
    sys.path.insert(0, src_path)
    print(f"Added src directory to sys.path: {src_path}")

print(f"Current sys.path: {sys.path}")
