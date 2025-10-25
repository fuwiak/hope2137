#!/usr/bin/env python3
"""
Test script for local development
"""
import requests
import time
import sys

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_bot_import():
    """Test if bot can be imported without errors"""
    try:
        import app
        print("✅ Bot imports successfully")
        return True
    except Exception as e:
        print(f"❌ Bot import error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Telegram Bot locally...")
    
    # Test imports
    if not test_bot_import():
        sys.exit(1)
    
    # Wait a bit for Flask to start
    print("⏳ Waiting for Flask to start...")
    time.sleep(2)
    
    # Test health check
    if not test_health_check():
        print("💡 Make sure to run: python app.py")
        sys.exit(1)
    
    print("🎉 All tests passed! Bot is ready for Railway deployment.")

if __name__ == "__main__":
    main()
