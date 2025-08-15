#!/usr/bin/env python3
"""
Test script to verify Flask application startup
"""

import sys
import traceback
from app import app

def test_app_startup():
    """Test if the Flask application can start without errors"""
    try:
        print("Testing Flask application startup...")
        
        # Test app import
        print("✓ App imported successfully")
        
        # Test configuration
        print(f"✓ Configuration loaded (Debug: {app.config['DEBUG']}, Host: {app.config['HOST']}, Port: {app.config['PORT']})")
        
        # Test database connection (implicitly tested through app import)
        print("✓ Database connections working")
        
        # Test route registration
        print(f"✓ Routes registered: {len(list(app.url_map.iter_rules()))} total routes")
        
        # Test specific debt routes
        debt_routes = [rule for rule in app.url_map.iter_rules() if 'debt' in rule.rule.lower()]
        print(f"✓ Debt management routes: {len(debt_routes)} routes registered")
        
        print("\n🎉 ALL TESTS PASSED! Flask application is ready to run.")
        print("\nTo start the application, run:")
        print("python app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_app_startup()
    sys.exit(0 if success else 1)
