"""
Service for finding similar domain names that are available.
"""
import random
import time
from difflib import SequenceMatcher
from services.domain_service import check_domain_availability
from config.settings import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION

def find_similar_domains(domain_name, tlds, max_count=15, similarity_threshold=70):
    """
    Find similar domain names that are available.
    
    Args:
        domain_name (str): The original domain name to find alternatives for
        tlds (list): List of TLDs to check
        max_count (int): Maximum number of similar domains to return
        similarity_threshold (int): Minimum similarity score (0-100) for suggestions
        
    Returns:
        list: List of dictionaries with similar domain suggestions
    """
    print(f"Finding similar domains for '{domain_name}' with TLDs: {tlds}")
    
    # First try to generate alternatives using algorithmic method
    suggestions = generate_alternatives_algorithmic(domain_name, max_count * 3)
    print(f"Generated {len(suggestions)} algorithmic suggestions")
    
    # Calculate similarity scores
    scored_suggestions = []
    for suggestion in suggestions:
        # Skip exact matches or too short suggestions
        if suggestion == domain_name or len(suggestion) < 3:
            continue
            
        # Calculate similarity score
        similarity = calculate_similarity(domain_name, suggestion)
        similarity_percent = int(similarity * 100)
        
        # Only include if it meets the threshold
        if similarity_percent >= similarity_threshold:
            scored_suggestions.append({
                "name": suggestion,
                "similarity": similarity_percent
            })
    
    # Sort by similarity score (highest first)
    scored_suggestions.sort(key=lambda x: x["similarity"], reverse=True)
    print(f"Found {len(scored_suggestions)} suggestions that meet the similarity threshold")
    
    # Remove duplicates while preserving order
    unique_suggestions = []
    unique_names = set()
    for suggestion in scored_suggestions:
        if suggestion["name"] not in unique_names:
            unique_suggestions.append(suggestion)
            unique_names.add(suggestion["name"])
    
    # Limit to max_count unique suggestions
    unique_suggestions = unique_suggestions[:max_count * 2]
    print(f"After removing duplicates, have {len(unique_suggestions)} suggestions")
    
    # Check availability for each suggested domain
    available_suggestions = []
    for suggestion in unique_suggestions:
        # First check one TLD at a time to avoid checking all TLDs for each suggestion
        for tld in tlds:
            # Check availability
            try:
                results = check_domain_availability(suggestion["name"], [tld])
                
                # If available, add to available suggestions
                if results and results[0]["available"]:
                    # Add TLD and price to suggestion
                    suggestion["tld"] = results[0]["tld"]
                    suggestion["price"] = results[0]["price"]
                    available_suggestions.append(suggestion.copy())
                    
                    # Stop checking other TLDs once we found an available one
                    break
            except Exception as e:
                print(f"Error checking domain {suggestion['name']}.{tld}: {str(e)}")
        
        # Stop if we have enough suggestions
        if len(available_suggestions) >= max_count:
            break
    
    print(f"Found {len(available_suggestions)} available similar domains")
    return available_suggestions

def generate_alternatives_algorithmic(domain_name, count=50):
    """
    Generate similar domain name alternatives algorithmically.
    
    Args:
        domain_name (str): The original domain name
        count (int): Maximum number of alternatives to generate
        
    Returns:
        list: List of similar domain names
    """
    suggestions = []
    
    # Common prefixes and suffixes for domain names
    prefixes = ["my", "the", "get", "try", "go", "best", "top", "pro", "smart", "easy", "e"]
    suffixes = ["hub", "spot", "zone", "app", "site", "web", "now", "pro", "hq", "online", "center", "tech", "place"]
    
    # 1. Add/change prefix
    for prefix in prefixes:
        if not domain_name.startswith(prefix):
            suggestions.append(f"{prefix}{domain_name}")
    
    # 2. Add/change suffix
    for suffix in suffixes:
        if not domain_name.endswith(suffix):
            suggestions.append(f"{domain_name}{suffix}")
    
    # 3. Remove vowels or replace with similar sounding characters
    vowels = "aeiou"
    vowel_replacements = {"a": ["e"], "e": ["a", "i"], "i": ["y", "e"], "o": ["u", "0"], "u": ["oo"]}
    
    for i in range(len(domain_name)):
        if domain_name[i] in vowels:
            # Try removing the vowel if it wouldn't make the domain too short
            if len(domain_name) > 4:
                new_name = domain_name[:i] + domain_name[i+1:]
                suggestions.append(new_name)
            
            # Try replacing the vowel
            for replacement in vowel_replacements.get(domain_name[i], []):
                new_name = domain_name[:i] + replacement + domain_name[i+1:]
                suggestions.append(new_name)
    
    # 4. Replace similar sounding consonants
    consonant_replacements = {
        "c": ["k", "s"], "k": ["c"], "s": ["z"], "z": ["s"],
        "ph": ["f"], "f": ["ph"], "x": ["ks"], "ck": ["k", "c"],
        "q": ["kw"], "w": ["v"], "v": ["w"], "j": ["g"], "g": ["j"]
    }
    
    for old, replacements in consonant_replacements.items():
        if old in domain_name:
            for new in replacements:
                suggestions.append(domain_name.replace(old, new))
    
    # 5. Add/remove double letters
    for i in range(len(domain_name) - 1):
        # Double a letter
        if domain_name[i] != domain_name[i+1]:
            new_name = domain_name[:i+1] + domain_name[i] + domain_name[i+1:]
            suggestions.append(new_name)
        
        # Remove a double letter
        if domain_name[i] == domain_name[i+1]:
            new_name = domain_name[:i] + domain_name[i+1:]
            suggestions.append(new_name)
    
    # 6. Mixed case alternatives (camelCase, etc.)
    if len(domain_name) > 5:
        for i in range(1, len(domain_name) - 1):
            # Try splitting at this position
            first_part = domain_name[:i]
            second_part = domain_name[i:]
            
            # Combine with common connecting words
            suggestions.append(f"{first_part}and{second_part}")
            suggestions.append(f"{first_part}my{second_part}")
            suggestions.append(f"{first_part}the{second_part}")
    
    # 7. Synonyms for common words (very simplified)
    common_word_synonyms = {
        "big": ["large", "huge", "mega"],
        "small": ["tiny", "mini", "little"],
        "good": ["great", "best", "top"],
        "fast": ["quick", "rapid", "swift"],
        "smart": ["clever", "bright", "wise"]
    }
    
    for word, synonyms in common_word_synonyms.items():
        if word in domain_name:
            for synonym in synonyms:
                suggestions.append(domain_name.replace(word, synonym))
    
    # 8. Add numbers at the end
    for i in range(1, 10):
        suggestions.append(f"{domain_name}{i}")
    
    # Filter and prepare the final list
    cleaned_suggestions = []
    for suggestion in suggestions:
        # Remove any invalid characters
        clean_suggestion = ''.join(c for c in suggestion if c.isalnum() or c == '-')
        
        # Skip if too short or duplicated
        if len(clean_suggestion) >= 3 and clean_suggestion != domain_name and clean_suggestion not in cleaned_suggestions:
            cleaned_suggestions.append(clean_suggestion)
    
    # Randomize and limit to count
    random.shuffle(cleaned_suggestions)
    return cleaned_suggestions[:count]

def calculate_similarity(str1, str2):
    """
    Calculate string similarity between 0 and 1.
    
    Args:
        str1 (str): First string
        str2 (str): Second string
        
    Returns:
        float: Similarity score between 0 and 1
    """
    # Use SequenceMatcher for a good balance of speed and accuracy
    return SequenceMatcher(None, str1, str2).ratio()