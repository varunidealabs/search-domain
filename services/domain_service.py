"""
Service for checking domain availability.
"""
import requests
import time
import random
from config.settings import WHOIS_API_KEY, GODADDY_API_KEY, GODADDY_API_SECRET, DEMO_MODE, GODADDY_API_URL

def check_domain_availability(domain_name, tlds):
    """
    Check if a domain is available across multiple TLDs
    
    Args:
        domain_name (str): The domain name without TLD
        tlds (list): List of TLDs to check
        
    Returns:
        list: List of dictionaries with availability information
    """
    results = []
    
    for tld in tlds:
        # Create full domain name
        full_domain = f"{domain_name}.{tld}"
        
        # Check availability
        available, price = _check_availability(domain_name, tld)
        
        # Add to results
        results.append({
            "name": domain_name,
            "tld": tld,
            "full_domain": full_domain,
            "available": available,
            "price": price
        })
        
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    return results

def _check_availability(domain_name, tld):
    """
    Check if a specific domain is available using one of multiple methods
    
    Returns:
        tuple: (available, price)
    """
    # If DEMO_MODE is enabled, always use mock data
    if DEMO_MODE:
        return _check_with_mock(domain_name, tld)
    
    # Only try real APIs if not in demo mode
    methods = []
    
    # Only add GoDaddy if credentials are provided
    if GODADDY_API_KEY and GODADDY_API_SECRET:
        methods.append(_check_with_godaddy)
    
    # Only add WHOIS if credentials are provided
    if WHOIS_API_KEY:
        methods.append(_check_with_whois_api)
    
    # Always include mock as fallback
    methods.append(_check_with_mock)
    
    # Try each method in order
    for method in methods:
        try:
            return method(domain_name, tld)
        except Exception as e:
            print(f"Error checking domain with {method.__name__}: {str(e)}")
            continue
    
    # If all methods fail, return as unavailable
    return False, 0

def _check_with_godaddy(domain_name, tld):
    """Check domain availability using GoDaddy API"""
    if not GODADDY_API_KEY or not GODADDY_API_SECRET:
        raise ValueError("GoDaddy API credentials not configured")
    
    # Use configured endpoint based on environment (OTE or PROD)
    url = f"{GODADDY_API_URL}/v1/domains/available"
    params = {
        "domain": f"{domain_name}.{tld}",
        "checkType": "FULL",
        "forTransfer": "false"
    }
    headers = {
        "Authorization": f"sso-key {GODADDY_API_KEY}:{GODADDY_API_SECRET}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        available = data.get("available", False)
        price = data.get("price", 0) / 1000000 if data.get("price") else 9.99  # Convert from microseconds to dollars
        return available, price
    else:
        raise Exception(f"GoDaddy API error: {response.status_code} - {response.text}")

def _check_with_whois_api(domain_name, tld):
    """Check domain availability using WHOIS API"""
    if not WHOIS_API_KEY:
        raise ValueError("WHOIS API key not configured")
    
    url = "https://www.whoisxmlapi.com/whoisserver/WhoisService"
    params = {
        "apiKey": WHOIS_API_KEY,
        "domainName": f"{domain_name}.{tld}",
        "outputFormat": "JSON"
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        
        # Check if domain is registered
        if "WhoisRecord" in data and "registryData" in data["WhoisRecord"]:
            registry_data = data["WhoisRecord"]["registryData"]
            
            # If domainAvailability field exists and equals "AVAILABLE"
            if "domainAvailability" in registry_data and registry_data["domainAvailability"] == "AVAILABLE":
                return True, 9.99
            else:
                return False, 0
        else:
            # If no registry data, assume it's available
            return True, 9.99
    else:
        raise Exception(f"WHOIS API error: {response.status_code} - {response.text}")

def _check_with_mock(domain_name, tld):
    """
    Mock domain availability check for demo purposes
    Uses a deterministic algorithm to simulate availability
    """
    # Seed random with domain name for consistent results
    random.seed(f"{domain_name}.{tld}")
    
    # Common domains are less likely to be available
    common_words = [
        "blog", "tech", "cloud", "digital", "web", "online", "app", 
        "smart", "easy", "best", "top", "pro", "expert", "my", "the",
        "one", "first", "prime", "elite", "global", "world", "market",
        "shop", "store", "buy", "sell", "trade", "exchange", "service",
        "solution", "system", "platform", "network", "connect", "link",
        "data", "info", "media", "social", "creative", "design", "art",
        "health", "fitness", "wellness", "food", "diet", "travel", "trip",
        "vacation", "holiday", "learn", "edu", "study", "course", "class",
        "finance", "money", "invest", "wealth", "rich", "cash", "crypto",
        "game", "play", "fun", "mobile", "phone", "tablet", "computer"
    ]
    
    # Length is also a factor (shorter domains are less likely to be available)
    length_factor = max(0.1, min(0.9, (len(domain_name) - 3) / 10))
    
    # Check if domain contains common words
    word_factor = 0.5
    for word in common_words:
        if word in domain_name:
            word_factor = 0.2
            break
    
    # Availability varies by TLD popularity
    tld_availability_rates = {
        "com": 0.05,  # Only 5% of .com domains are available
        "net": 0.20,
        "org": 0.25,
        "io": 0.30,
        "co": 0.35,
        "app": 0.60,
        "dev": 0.65,
        "ai": 0.40,
        # Add other TLDs as needed
    }
    
    # Get availability rate for this TLD, default to 30%
    base_availability_rate = tld_availability_rates.get(tld, 0.30)
    
    # Calculate final availability rate
    availability_rate = base_availability_rate * length_factor * word_factor
    
    # Special case for exact search: make most common domains unavailable
    if len(domain_name) <= 5 and tld == "com":
        availability_rate = 0.01  # 1% chance for short .com domains
    
    # Generate a random number and compare to availability rate
    is_available = random.random() < availability_rate
    
    # Set pricing based on TLD (realistic pricing)
    tld_pricing = {
        "com": 11.99,
        "net": 12.99,
        "org": 12.99,
        "io": 49.99,
        "co": 29.99,
        "app": 17.99,
        "dev": 15.99,
        "ai": 69.99,
        # Add other TLDs as needed
    }
    
    price = tld_pricing.get(tld, 14.99)
    
    # Add some price variation
    price_variation = random.uniform(0.9, 1.1)
    price = round(price * price_variation, 2)
    
    return is_available, price