#!/usr/bin/env python3
"""
Startup script for Ozark Finances Flask Application
This script initializes the database and starts the Flask app
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is supported"""
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or later is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install requirements: {e}")
        return False

def init_database():
    """Initialize the database"""
    print("Initializing database...")
    try:
        subprocess.check_call([sys.executable, 'init_db.py'])
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Database initialization failed: {e}")
        return False

def start_app():
    """Start the Flask application"""
    print("\n" + "="*50)
    print("Starting Ozark Finances Flask Application")
    print("="*50)
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    try:
        subprocess.check_call([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to start application: {e}")

def main():
    """Main startup routine"""
    print("Ozark Finances Flask Port - Startup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Check if database exists
    db_path = Path('../data/FinanceData.sqlite')
    if not db_path.exists():
        print(f"Database not found at: {db_path.absolute()}")
        response = input("Would you like to initialize a new database? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            if not init_database():
                input("Press Enter to exit...")
                return
        else:
            print("Cannot start without database. Exiting...")
            input("Press Enter to exit...")
            return
    
    # Check if requirements are installed
    try:
        import flask
        import openpyxl
        print("✓ Requirements already satisfied")
    except ImportError:
        if not install_requirements():
            input("Press Enter to exit...")
            return
    
    # Start the application
    start_app()

if __name__ == "__main__":
    main()
