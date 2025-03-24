import os
import random
import requests
import json
from config.settings import AZURE_OPENAI_KEY

def generate_domain_suggestions(query, filters=None):
    """
    Generate domain name suggestions based on user input.
    
    This function can use different methods based on configuration:
    1. OpenAI API for AI-generated suggestions
    2. Algorithmic combinations if API is not available
    3. Fallback to basic word combinations
    
    Args:
        query (str): User description of their business/project
        filters (dict): Optional filters to apply to suggestions
        
    Returns:
        list: List of domain name suggestions
    """
    if not filters:
        filters = {}
    
    # Try using Azure OpenAI API first
    try:
        if AZURE_OPENAI_KEY:
            suggestions = _generate_with_openai(query, filters)
            if suggestions:
                return suggestions
    except Exception as e:
        print(f"Azure OpenAI API error: {str(e)}")
    
    # Fallback to algorithmic generation
    suggestions = _generate_algorithmic(query, filters)
    
    # Apply filters
    suggestions = _apply_filters(suggestions, filters)
    
    return suggestions[:20]  # Limit to 20 suggestions

def _generate_with_openai(query, filters):
    """Generate domain suggestions using Azure OpenAI API"""
    import requests
    import json
    from config.settings import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION
    
    # Construct prompt based on query and filters
    prompt = _build_openai_prompt(query, filters)
    
    # Prepare the API request for Azure OpenAI
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }
    
    # Using the chat completions endpoint with GPT-4o
    payload = {
        "messages": [
            {"role": "system", "content": "You are a domain name generator. Generate creative and relevant domain names based on the user's description."},
            {"role": "user", "content": prompt}
        ],
        "temperature": filters.get("creativity_level", 7) / 10,  # Convert 1-10 scale to 0-1
        "max_tokens": 150,
        "top_p": 1,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    }
    
    # Construct the full URL
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
    
    # Make the API request
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    
    # Parse response from Azure OpenAI
    if 'choices' in response_data and len(response_data['choices']) > 0:
        text_response = response_data['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"Azure OpenAI API error: {response_data}")
    
    # Extract domain names from response
    suggestions = []
    for line in text_response.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('Note:'):
            # Remove any numbering or bullet points
            cleaned = line.split('.', 1)[-1].strip() if '.' in line[:3] else line
            cleaned = cleaned.strip('-').strip()
            
            # Extract just the domain name part (without TLD)
            domain_name = cleaned.split('.')[0].strip() if '.' in cleaned else cleaned
            
            if domain_name and len(domain_name) <= filters.get("max_length", 30):
                suggestions.append(domain_name)
    
    return suggestions

def _build_openai_prompt(query, filters):
    """Build a prompt for the OpenAI API based on user query and filters"""
    prompt = f"""
    Generate unique and creative domain name suggestions for the following business or project:
    
    Description: {query}
    
    Requirements:
    - Domain names should be memorable, unique, and relevant to the description
    - Maximum length: {filters.get('max_length', 15)} characters (excluding TLD)
    """
    
    if filters.get("no_hyphens"):
        prompt += "\n- Do not include hyphens"
    
    if filters.get("no_numbers"):
        prompt += "\n- Do not include numbers"
    
    if filters.get("alliteration"):
        prompt += "\n- Prefer alliteration when possible"
    
    creativity = filters.get("creativity_level", 7)
    if creativity >= 8:
        prompt += "\n- Be very creative, novel and unexpected with suggestions"
    elif creativity <= 3:
        prompt += "\n- Focus on straightforward, simple, and direct domain names"
    
    prompt += """
    
    Format: Return only the domain names without TLDs (e.g., 'brandname' not 'brandname.com')
    Generate 15 suggestions.
    """
    
    return prompt

def _generate_algorithmic(query, filters):
    """Generate domain suggestions algorithmically using keyword extraction and combinations"""
    # Extract keywords from query
    keywords = _extract_keywords(query)
    
    # Generate combinations
    suggestions = []
    
    # 1. Use keywords directly
    suggestions.extend(keywords)
    
    # 2. Add common prefixes and suffixes
    prefixes = ["get", "try", "use", "my", "the", "go", "best"]
    suffixes = ["app", "hub", "pro", "now", "hq", "io", "lab", "tech"]
    
    for keyword in keywords:
        # Add prefixes
        for prefix in prefixes:
            if len(prefix + keyword) <= filters.get("max_length", 15):
                suggestions.append(prefix + keyword)
        
        # Add suffixes
        for suffix in suffixes:
            if len(keyword + suffix) <= filters.get("max_length", 15):
                suggestions.append(keyword + suffix)
    
    # 3. Combine keywords
    if len(keywords) >= 2:
        for i in range(len(keywords)):
            for j in range(len(keywords)):
                if i != j:
                    combined = keywords[i] + keywords[j]
                    if len(combined) <= filters.get("max_length", 15):
                        suggestions.append(combined)
    
    # 4. Create portmanteaus
    if len(keywords) >= 2:
        for i in range(len(keywords)):
            for j in range(len(keywords)):
                if i != j and len(keywords[i]) > 3 and len(keywords[j]) > 3:
                    # Take first part of first word and last part of second word
                    portmanteau = keywords[i][:len(keywords[i])//2] + keywords[j][len(keywords[j])//2:]
                    if len(portmanteau) <= filters.get("max_length", 15):
                        suggestions.append(portmanteau)
    
    # Remove duplicates and return
    return list(set(suggestions))

def _extract_keywords(query):
    """Extract relevant keywords from the user query"""
    # Remove common words and keep only significant terms
    common_words = {"a", "an", "the", "and", "or", "but", "for", "in", "on", "with", 
                   "about", "to", "from", "by", "of", "is", "are", "was", "were", 
                   "will", "would", "should", "could", "can", "may", "might", "must",
                   "that", "this", "these", "those", "it", "they", "them", "their"}
    
    # Split and clean keywords
    words = query.lower().replace(',', ' ').replace('.', ' ').split()
    keywords = [word for word in words if word not in common_words and len(word) > 2]
    
    return list(set(keywords))

def _apply_filters(suggestions, filters):
    """Apply user-defined filters to domain suggestions"""
    filtered = []
    
    for domain in suggestions:
        # Check length
        if len(domain) > filters.get("max_length", 30):
            continue
        
        # Check for hyphens
        if filters.get("no_hyphens") and "-" in domain:
            continue
        
        # Check for numbers
        if filters.get("no_numbers") and any(c.isdigit() for c in domain):
            continue
        
        filtered.append(domain)
    
    # Sort by relevance/quality (basic implementation)
    filtered.sort(key=lambda x: (
        # Prioritize shorter names
        len(x),
        # Then prioritize all alphabetic names
        0 if x.isalpha() else 1,
        # Random factor for some variety
        random.random()
    ))
    
    return filtered