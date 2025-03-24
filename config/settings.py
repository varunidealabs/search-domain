import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys (loaded from environment variables)
WHOIS_API_KEY = os.getenv("WHOIS_API_KEY", "")
GODADDY_API_KEY = os.getenv("GODADDY_API_KEY", "")
GODADDY_API_SECRET = os.getenv("GODADDY_API_SECRET", "")
GODADDY_API_ENV = os.getenv("GODADDY_API_ENV", "OTE").upper()  # OTE or PROD

# Azure OpenAI settings
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://access-01.openai.azure.com")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

# Application settings
APP_NAME = "Domain Finder"
APP_DESCRIPTION = "Check domain availability and find alternatives"
APP_VERSION = "1.0.0"

# Default domain TLDs to check
DEFAULT_TLDS = ["com", "net", "org", "io"]

# Demo mode (if True, uses mock data instead of real API calls)
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in ["true", "yes", "1", "t", "y"]

# GoDaddy API endpoints based on environment
GODADDY_ENDPOINTS = {
    "OTE": "https://api.ote-godaddy.com",
    "PROD": "https://api.godaddy.com"
}
GODADDY_API_URL = GODADDY_ENDPOINTS.get(GODADDY_API_ENV, GODADDY_ENDPOINTS["OTE"])