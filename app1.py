import streamlit as st
from services.domain_service import check_domain_availability
from services.similar_domain_service import find_similar_domains
import time
from config.settings import DEMO_MODE

# Run configuration check
try:
    from services.config_checker import check_config
    config_ok = check_config()
except ImportError:
    print("Configuration checker not available - skipping configuration validation")
    config_ok = True

# Page configuration
st.set_page_config(
    page_title="Domain Finder - Find Your Perfect Domain",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clear query params on page load to prevent auto-loading previous search
if "q" in st.query_params:
    st.query_params.clear()

# Simple CSS 
st.markdown("""
<style>
    .main-title {
        font-size: 52px;
        font-weight: 700;
        line-height: 1.1;
        color: #111;
        margin-bottom: 20px;
    }
    .search-container {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .stButton button {
        background-color: #ff5a5f !important;
        color: white !important;
        font-weight: bold !important;
    }
    div[data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 2rem !important;
    }
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .tld-badge {
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 50px;
        padding: 5px 10px;
        margin: 0 5px;
        font-size: 14px;
    }
    .tld-badge.active {
        background-color: #ff5a5f;
        color: white;
        border-color: #ff5a5f;
    }
</style>
""", unsafe_allow_html=True)

# Set available TLDs
all_tlds = [".ai", ".com", ".net", ".org", ".io", ".co", ".in", ".co.in"]
default_tlds = [".com", ".net", ".org", ".in"]  # Popular TLDs for fallback

# Currency conversion rate
usd_to_inr_rate = 80

# Initialize session state for search
if 'search_triggered' not in st.session_state:
    st.session_state.search_triggered = False

# Function to run when search is triggered
def trigger_search():
    st.session_state.search_triggered = True

# Main header
st.markdown('<h1 class="main-title">SEARCH DOMAIN.<br>Build your business.</h1>', unsafe_allow_html=True)

# Search row with columns
col1, col2, col3 = st.columns([5, 1, 2])

with col1:
    # Text input that triggers search on Enter key
    domain_query = st.text_input(
        "Domain Search", 
        placeholder="Search domain names", 
        label_visibility="collapsed",
        on_change=trigger_search
    )

with col2:
    search_clicked = st.button("Check Availability", type="primary", use_container_width=True, on_click=trigger_search)

with col3:
    # TLD selection
    tld_options = st.multiselect(
        "Select TLDs to search",
        all_tlds,
        default=[]  # No default selection
    )

# Check if search should be triggered (button click or Enter key)
search_triggered = search_clicked or st.session_state.search_triggered

# Process search when triggered
if search_triggered and domain_query:
    # Reset the trigger for next time
    st.session_state.search_triggered = False
    
    domain_query = domain_query.strip().lower()
    
    # Remove any TLD if the user included one
    if "." in domain_query:
        parts = domain_query.split(".")
        domain_query = parts[0]
    
    # Make sure domain is valid
    if len(domain_query) < 3:
        st.error("Please enter a valid domain name (at least 3 characters)")
    else:
        # If no TLDs selected, use defaults
        if not tld_options:
            tld_list = [tld.replace(".", "") for tld in default_tlds]
        else:
            tld_list = [tld.replace(".", "") for tld in tld_options]
        
        # Show progress
        with st.spinner(f"Checking availability for {domain_query}..."):
            # Check domain availability
            results = check_domain_availability(domain_query, tld_list)
            
            # Group results by availability
            available_domains = [r for r in results if r["available"]]
            unavailable_domains = [r for r in results if not r["available"]]
        
        # Display results
        st.subheader("Search Results")
        
        # Create a clean container for results
        results_container = st.container()
        
        with results_container:
            # Display exact domain results
            for domain in results:
                # Format price in Indian Rupees
                price = f"₹{int(domain['price'] * usd_to_inr_rate)}"
                
                # Create columns for domain row
                col1, col2, col3 = st.columns([5, 2, 2])
                
                with col1:
                    # Domain name with optional badge
                    if domain["available"]:
                        st.write(f"**{domain['name']}.{domain['tld']}** 🟢")
                        st.markdown("---")
                    
                with col2:
                    # Price
                    if domain["available"]:
                        st.write(f"**{price}**")
                        st.markdown("---")
                
                with col3:
                    # Action button
                    if domain["available"]:
                        domain_url = f"https://in.godaddy.com/domainsearch/find?domainToCheck={domain['name']}.{domain['tld']}"
                        st.markdown(f'<a href="{domain_url}" target="_blank"><button style="background-color: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">visit</button></a>', unsafe_allow_html=True)
                        # Add separator
                        st.markdown("---")
            
            try:
                # Use a lower similarity threshold to get more results
                similarity_threshold = 70
                
                # Find similar domain suggestions
                with st.spinner("Finding similar available domains..."):
                    similar_results = find_similar_domains(
                        domain_query, 
                        tld_list, 
                        max_count=15,
                        similarity_threshold=similarity_threshold
                    )
                
                # Display similar domain results
                if similar_results and len(similar_results) > 0:
                    for domain in similar_results:
                        # Format price in Indian Rupees
                        price = f"₹{int(domain['price'] * usd_to_inr_rate)}"
                        similarity = domain.get('similarity', 0)
                        
                        # Create columns for domain row
                        col1, col2, col3 = st.columns([5, 2, 2])
                        
                        with col1:
                            # Domain name with similarity
                            st.write(f"**{domain['name']}.{domain['tld']}** ✓ ({similarity}% match)")
                        
                        with col2:
                            # Price
                            st.write(f"**{price}**")
                        
                        with col3:
                            # Action button
                            domain_url = f"https://in.godaddy.com/domainsearch/find?domainToCheck={domain['name']}.{domain['tld']}"
                            st.markdown(f'<a href="{domain_url}" target="_blank"><button style="background-color: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">visit</button></a>', unsafe_allow_html=True)
                        
                        # Add separator
                        st.markdown("---")
                else:
                    st.info("No similar available domains found. Try a different search term.")
            except Exception as e:
                st.error(f"Error finding similar domains: {str(e)}")
