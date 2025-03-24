import streamlit as st
from dotenv import load_dotenv
import os

# Try to load from .env file for local development
load_dotenv()

# API Keys (try to get from Streamlit secrets first, then fall back to environment variables)
def get_setting(key, default=""):
    # Check Streamlit secrets first
    if hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    # Fall back to environment variables
    return os.getenv(key, default)

# API Keys
WHOIS_API_KEY = get_setting("WHOIS_API_KEY", "")
GODADDY_API_KEY = get_setting("GODADDY_API_KEY", "")
GODADDY_API_SECRET = get_setting("GODADDY_API_SECRET", "")

# Azure OpenAI settings
AZURE_OPENAI_KEY = get_setting("AZURE_OPENAI_KEY", "")
AZURE_OPENAI_ENDPOINT = get_setting("AZURE_OPENAI_ENDPOINT", "https://access-01.openai.azure.com")
AZURE_OPENAI_DEPLOYMENT = get_setting("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_API_VERSION = get_setting("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

# Application settings
APP_NAME = "Domain Finder"
APP_DESCRIPTION = "Check domain availability and find alternatives"
APP_VERSION = "1.0.0"

# Default domain TLDs to check
DEFAULT_TLDS = ["com", "net", "org", "io"]

# Demo mode (if True, uses mock data instead of real API calls)
DEMO_MODE = get_setting("DEMO_MODE", "true").lower() in ["true", "yes", "1", "t", "y"]

# GoDaddy API endpoints based on environment
GODADDY_API_ENV = get_setting("GODADDY_API_ENV", "OTE").upper()  # OTE or PROD
GODADDY_ENDPOINTS = {
    "OTE": "https://api.ote-godaddy.com",
    "PROD": "https://api.godaddy.com"
}
GODADDY_API_URL = GODADDY_ENDPOINTS.get(GODADDY_API_ENV, GODADDY_ENDPOINTS["OTE"])
