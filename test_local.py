#!/usr/bin/env python3
"""
Test script for local development
"""
import sys
import time

def test_bot_import():
    """Test if bot can be imported without errors"""
    try:
        import app
        print("✅ Bot imports successfully")
        return True
    except Exception as e:
        print(f"❌ Bot import error: {e}")
        return False

def test_environment_variables():
    """Test if required environment variables are set"""
    import os
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "GROQ_API_KEY", 
        "YCLIENTS_PARTNER_TOKEN",
        "YCLIENTS_USER_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Create a .env file with these variables")
        return False
    else:
        print("✅ All environment variables are set")
        return True

def main():
    """Run all tests"""
    print("🧪 Testing Telegram Bot locally...")
    
    # Test environment variables
    if not test_environment_variables():
        sys.exit(1)
    
    # Test imports
    if not test_bot_import():
        sys.exit(1)
    
    print("🎉 All tests passed! Bot is ready for Railway deployment.")
    print("🚀 To run locally: python app.py")
    print("🚀 To deploy to Railway: ./deploy_railway.sh")

if __name__ == "__main__":
    main()
