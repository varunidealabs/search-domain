"""
AI Domain Advisor - Uses Azure OpenAI to generate domain name suggestions.
"""
import requests
import json
import re
from config.settings import (
    AZURE_OPENAI_KEY, 
    AZURE_OPENAI_ENDPOINT, 
    AZURE_OPENAI_DEPLOYMENT, 
    AZURE_OPENAI_API_VERSION,
    DEMO_MODE
)

def get_domain_suggestions(business_description, max_suggestions=5):
    """
    Generate domain name suggestions based on a business description.
    
    Args:
        business_description (str): Description of the business
        max_suggestions (int): Maximum number of suggestions to return
    
    Returns:
        list: List of domain name suggestions (without TLDs)
    """
    # If in demo mode, return sample suggestions
    if DEMO_MODE:
        return _mock_domain_suggestions(business_description)
    
    try:
        # Prepare the AI prompt
        prompt = _prepare_prompt(business_description)
        
        # Call Azure OpenAI API
        suggestions = _call_azure_openai(prompt)
        
        # Process and clean suggestions
        cleaned_suggestions = _process_suggestions(suggestions, max_suggestions)
        
        return cleaned_suggestions
    
    except Exception as e:
        print(f"Error generating domain suggestions: {str(e)}")
        return _mock_domain_suggestions(business_description)  # Fallback to mock suggestions

def _prepare_prompt(business_description):
    """Prepare the prompt for the Azure OpenAI API"""
    
    # Extract business name if present
    business_name_match = re.search(r"called\s+['\"]([^'\"]+)['\"]", business_description, re.IGNORECASE)
    business_name_context = f"The business is called '{business_name_match.group(1)}'." if business_name_match else ""
    
    return f"""
    You are a domain name expert who helps businesses find the perfect domain name.
    Based on the following business description, suggest {5} creative, memorable, and practical domain names.

    Business Description: {business_description}
    {business_name_context}

    Guidelines for domain names:
    1. Keep names short (3-15 characters) and memorable
    2. Avoid hyphens and numbers unless they make sense for the brand
    3. Be creative but relevant to the business
    4. Consider SEO value and brandability
    5. Names should be unique but easy to spell and remember
    6. If a business name is provided, prioritize variations of that name
    
    Provide ONLY the domain names without TLDs (.com, .org, etc.), one per line.
    Do not include explanations, numbering, or any other text.
    
    Domain name suggestions:
    """

def _call_azure_openai(prompt):
    """Call Azure OpenAI API to generate domain suggestions"""
    
    # Prepare the request
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are a domain name expert who helps businesses find the perfect domain name."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 150,
        "top_p": 1,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.6
    }
    
    # Construct the API URL
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
    
    # Make the API request
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    
    # Extract suggestions from response
    if 'choices' in response_data and len(response_data['choices']) > 0:
        suggestions_text = response_data['choices'][0]['message']['content'].strip()
        return suggestions_text
    else:
        raise Exception(f"Azure OpenAI API error: {response_data}")

def _process_suggestions(suggestions_text, max_suggestions):
    """Process and clean domain suggestions"""
    
    # Split by newline and clean up
    raw_suggestions = suggestions_text.strip().split('\n')
    
    # Clean up each suggestion
    cleaned_suggestions = []
    for suggestion in raw_suggestions:
        # Remove any numbering or bullet points
        cleaned = re.sub(r'^\d+[\.\)\-\s]+', '', suggestion)
        
        # Remove quotes and extra spaces
        cleaned = cleaned.strip('\'"').strip()
        
        # Remove any TLD if included
        if '.' in cleaned:
            cleaned = cleaned.split('.')[0]
        
        # Only add if not empty and not a duplicate
        if cleaned and cleaned not in cleaned_suggestions:
            cleaned_suggestions.append(cleaned)
    
    # Limit to max_suggestions
    return cleaned_suggestions[:max_suggestions]

def _mock_domain_suggestions(business_description):
    """Generate mock domain suggestions for demo mode"""
    
    # Try to extract business name
    business_name_match = re.search(r"called\s+['\"]([^'\"]+)['\"]", business_description, re.IGNORECASE)
    
    # Basic set of suggestions
    suggestions = []
    
    if business_name_match:
        business_name = business_name_match.group(1)
        
        # Clean the business name
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', business_name).lower()
        
        # Generate variations based on the business name
        suggestions = [
            clean_name,
            f"the{clean_name}",
            f"{clean_name}online",
            f"get{clean_name}",
            f"{clean_name}hub"
        ]
    else:
        # Extract key terms from description
        words = business_description.lower().split()
        key_terms = [word for word in words if len(word) > 3 and word not in ['with', 'that', 'this', 'from', 'have', 'what', 'about', 'they', 'will']]
        
        # Use the first few key terms if available
        if key_terms:
            base_term = key_terms[0]
            suggestions = [
                base_term,
                f"the{base_term}",
                f"{base_term}hub",
                f"{base_term}pro",
                f"my{base_term}"
            ]
            
            # Try to combine terms if there are multiple
            if len(key_terms) > 1:
                suggestions[2] = f"{key_terms[0]}{key_terms[1]}"
        else:
            # Fallback generic suggestions
            suggestions = [
                "yourbrand",
                "brandname",
                "mybusiness",
                "thebusiness",
                "brandhub"
            ]
    
    return suggestions
