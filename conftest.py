"""
Pytest configuration file with fixes for Flask compatibility issues
"""
import pytest
import sys
import os
import importlib

# First, check if pytest-flask is installed and disable it if needed
try:
    import pytest_flask
    # We could potentially disable it here if needed
except ImportError:
    pytest_flask = None

# Fix for pytest-flask compatibility with Flask 2.3+
try:
    from flask import _request_ctx_stack
    # We're good, this works with the current Flask version
except ImportError:
    # For Flask 2.3+, request_ctx_stack was moved
    import flask
    try:
        from flask import globals as _flask_globals
        if hasattr(_flask_globals, 'request_context'):
            flask._request_ctx_stack = _flask_globals.request_context
        else:
            # Alternative approach
            from werkzeug.local import LocalStack
            flask._request_ctx_stack = LocalStack()
            print("Applied Flask compatibility workaround in conftest.py")
    except (ImportError, AttributeError):
        # Last resort patch
        from werkzeug.local import LocalStack
        flask._request_ctx_stack = LocalStack()
        print("Applied last-resort Flask compatibility workaround in conftest.py")

# Flask compatibility workaround
import sys
import os

# Flask compatibility fix for pytest-flask
try:
    import flask
    if not hasattr(flask, '_request_ctx_stack'):
        # In newer Flask versions, _request_ctx_stack has been moved
        from werkzeug.local import LocalStack
        flask._request_ctx_stack = LocalStack()
        print("Applied Flask compatibility workaround for pytest-flask")
except ImportError:
    print("Flask import failed, skipping compatibility fix")

# Monkeypatch pytest_flask if it's installed
try:
    import pytest_flask.fixtures
    if hasattr(pytest_flask.fixtures, 'accept_any'):
        # Replace the import with our patched version
        if not hasattr(flask, '_request_ctx_stack'):
            from werkzeug.local import LocalStack
            flask._request_ctx_stack = LocalStack()
        print("Monkeypatched pytest_flask fixtures")
except ImportError:
    print("pytest_flask not found, no monkeypatching needed")

# Fixture to prevent pytest-flask issues by skipping its fixtures if needed
@pytest.fixture(autouse=True)
def _prevent_flask_fixture_issues():
    """Protect against Flask version mismatches with pytest-flask"""
    pass
