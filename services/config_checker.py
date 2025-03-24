"""
Configuration checker to validate application settings on startup
"""
import os
import requests

def check_azure_openai_config():
    """Check if Azure OpenAI configuration is valid"""
    from config.settings import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION
    
    # Check if key is present
    if not AZURE_OPENAI_KEY:
        print("\n❌ ERROR: Azure OpenAI API key is missing")
        print("   Please add your key to the .env file as AZURE_OPENAI_KEY=your_key_here")
        return False
    
    # Check if key is correct format (basic validation)
    if len(AZURE_OPENAI_KEY) < 10:
        print("\n❌ ERROR: Azure OpenAI API key appears to be invalid (too short)")
        print("   Please check your key in the .env file")
        return False
    
    # Check if endpoint is present
    if not AZURE_OPENAI_ENDPOINT:
        print("\n❌ ERROR: Azure OpenAI endpoint is missing")
        print("   Please add your endpoint to the .env file")
        return False
    
    # We'll skip the actual API test to avoid making unnecessary API calls
    print("✅ Azure OpenAI configuration found (skipping connection test)")
    return True

def check_godaddy_config():
    """Check GoDaddy API configuration"""
    from config.settings import GODADDY_API_KEY, GODADDY_API_SECRET, GODADDY_API_ENV
    
    if GODADDY_API_KEY and GODADDY_API_SECRET:
        print(f"✅ GoDaddy API configuration found (Environment: {GODADDY_API_ENV})")
        return True
    else:
        print("ℹ️ GoDaddy API credentials not found")
        return False

def check_config():
    """Run all configuration checks"""
    from config.settings import DEMO_MODE
    
    print("\n=== Domain Finder Configuration Check ===\n")
    
    if DEMO_MODE:
        print("🔍 Running in DEMO MODE - domain availability will be simulated")
    else:
        print("🔍 Running in PRODUCTION MODE - will attempt to check real domain availability")
    
    # Check API configurations
    azure_ok = check_azure_openai_config()
    godaddy_ok = check_godaddy_config()
    
    print("\n======================================\n")
    
    # In demo mode, we only need Azure to work
    if DEMO_MODE:
        return azure_ok
    else:
        # In production mode, we need either Azure + GoDaddy or Azure + WHOIS
        return azure_ok and godaddy_ok

if __name__ == "__main__":
    check_config()