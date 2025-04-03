"""
Script to fix dependency issues with Flask and pytest-flask
"""
import subprocess
import sys
import os

def main():
    print("Fixing Flask and pytest-flask compatibility...")
    try:
        # Uninstall current Flask and dependencies to avoid conflicts
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "flask", "werkzeug"])
        
        # Clean install of compatible versions
        subprocess.check_call([sys.executable, "-m", "pip", "install", "werkzeug==2.2.3"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask==2.2.5"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest-flask==1.2.0"])
        
        # Also ensure other required packages are installed
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("\nDependencies updated successfully!")
        print("You may need to restart your IDE or terminal for changes to take effect.")
        
        # Special note about the conftest.py workaround
        if os.path.exists("conftest.py"):
            print("\nNote: You also have a conftest.py file with a workaround.")
            print("If you're still experiencing issues after downgrading Flask,")
            print("this workaround might be causing conflicts.")
    except subprocess.CalledProcessError as e:
        print(f"Error fixing dependencies: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
