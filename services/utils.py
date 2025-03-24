import re
import json
import hashlib
import time
from functools import wraps

# Cache mechanism
_cache = {}

def cached(expiration=3600):
    """
    Decorator for caching function results
    
    Args:
        expiration (int): Cache expiration time in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            key = f"{func.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            # Check if result is in cache and not expired
            if key in _cache:
                result, timestamp = _cache[key]
                if time.time() - timestamp < expiration:
                    return result
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            _cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator

def validate_domain_name(domain_name):
    """
    Validate if a string is a valid domain name
    
    Args:
        domain_name (str): Domain name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Valid domain regex pattern
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    
    # Check if domain matches pattern
    if re.match(pattern, domain_name):
        return True
    return False

def clean_domain_name(domain_name):
    """
    Clean and normalize a domain name
    
    Args:
        domain_name (str): Domain name to clean
        
    Returns:
        str: Cleaned domain name
    """
    # Remove invalid characters
    cleaned = re.sub(r'[^a-zA-Z0-9-]', '', domain_name)
    
    # Remove leading/trailing hyphens
    cleaned = cleaned.strip('-')
    
    # Convert to lowercase
    cleaned = cleaned.lower()
    
    return cleaned

def rate_limit(max_calls, time_frame=60):
    """
    Decorator for rate limiting function calls
    
    Args:
        max_calls (int): Maximum calls allowed in time frame
        time_frame (int): Time frame in seconds
    """
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Remove calls older than time_frame
            while calls and calls[0] < current_time - time_frame:
                calls.pop(0)
            
            # Check if we've reached the limit
            if len(calls) >= max_calls:
                raise Exception(f"Rate limit exceeded: {max_calls} calls per {time_frame} seconds")
            
            # Add current call time
            calls.append(current_time)
            
            # Call the function
            return func(*args, **kwargs)
        return wrapper
    return decorator

def parse_keyword_list(text):
    """
    Parse a comma or space separated list of keywords
    
    Args:
        text (str): Text containing keywords
        
    Returns:
        list: List of keywords
    """
    # First split by comma
    items = text.split(',')
    
    # Process each item
    keywords = []
    for item in items:
        # Split by space and add non-empty words
        words = item.strip().split()
        keywords.extend([word.strip() for word in words if word.strip()])
    
    # Remove duplicates
    return list(set(keywords))

def save_to_json(data, filename):
    """
    Save data to a JSON file
    
    Args:
        data: Data to save
        filename (str): File path
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_from_json(filename):
    """
    Load data from a JSON file
    
    Args:
        filename (str): File path
        
    Returns:
        Data from the file or None if file doesn't exist
    """
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None