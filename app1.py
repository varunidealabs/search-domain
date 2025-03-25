import streamlit as st
from services.domain_service import check_domain_availability
from services.similar_domain_service import find_similar_domains
from services.ai_domain_advisor import get_domain_suggestions
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
    .tab-subheader {
        font-size: 16px;
        color: #555;
        margin-bottom: 20px;
    }
    .search-box {
        border-radius: 8px;
        border: 1px solid #ddd;
        padding: 10px;
    }
    .domain-advisor-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
    .domain-suggestion {
        padding: 10px;
        background-color: #fff;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .domain-suggestion button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 4px;
        cursor: pointer;
    }
    .search-tabs {
        margin-bottom: 20px;
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
    
if 'advisor_search_triggered' not in st.session_state:
    st.session_state.advisor_search_triggered = False

if 'domain_suggestions' not in st.session_state:
    st.session_state.domain_suggestions = []
    
if 'selected_suggestion' not in st.session_state:
    st.session_state.selected_suggestion = None
    
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "direct_search"

# Function to run when search is triggered
def trigger_search():
    st.session_state.search_triggered = True

def trigger_advisor_search():
    st.session_state.advisor_search_triggered = True
    
def select_suggestion(suggestion):
    st.session_state.selected_suggestion = suggestion
    st.session_state.active_tab = "direct_search"
    st.experimental_rerun()

def set_active_tab(tab):
    st.session_state.active_tab = tab

# Main header
st.markdown('<h1 class="main-title">SEARCH DOMAIN.<br>Build your business.</h1>', unsafe_allow_html=True)

# Create tabs for different search methods
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("Domain Search", on_click=lambda: set_active_tab("direct_search"), 
                 type="secondary" if st.session_state.active_tab != "direct_search" else "primary"):
        pass

with col2:
    if st.button("Domain Advisor (AI-Powered)", on_click=lambda: set_active_tab("advisor"), 
                 type="secondary" if st.session_state.active_tab != "advisor" else "primary",
                 help="Get AI recommendations for your business name"):
        pass

st.markdown("<hr>", unsafe_allow_html=True)

# Direct Domain Search Tab
if st.session_state.active_tab == "direct_search":
    # If there was a selected suggestion, populate the search field
    domain_query_default = st.session_state.selected_suggestion if st.session_state.selected_suggestion else ""
    
    # Search row with columns
    col1, col2 = st.columns([5, 1])

    with col1:
        # Text input that triggers search on Enter key
        domain_query = st.text_input(
            "Domain Search", 
            value=domain_query_default,
            placeholder="Enter domain name (e.g., yourbrand)", 
            label_visibility="collapsed",
            on_change=trigger_search
        )

    with col2:
        search_clicked = st.button("Check Availability", type="primary", use_container_width=True, on_click=trigger_search)

    # TLD selection row (below search)
    tld_options = st.multiselect(
        "Select TLDs to search",
        all_tlds,
        default=[]  # No default selection
    )

    # Check if search should be triggered (button click or Enter key)
    search_triggered = search_clicked or st.session_state.search_triggered or st.session_state.selected_suggestion

    # Clear selected suggestion after use
    if st.session_state.selected_suggestion:
        st.session_state.selected_suggestion = None

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
                        
                    with col2:
                        # Price
                        if domain["available"]:
                            st.write(f"**{price}**")
                    
                    with col3:
                        # Action button
                        if domain["available"]:
                            domain_url = f"https://in.godaddy.com/domainsearch/find?domainToCheck={domain['name']}.{domain['tld']}"
                            st.markdown(f'<a href="{domain_url}" target="_blank"><button style="background-color: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">Visit</button></a>', unsafe_allow_html=True)
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
                                st.markdown(f'<a href="{domain_url}" target="_blank"><button style="background-color: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">Visit</button></a>', unsafe_allow_html=True)
                            
                            # Add separator
                            st.markdown("---")
                    else:
                        st.info("No similar available domains found. Try a different search term.")
                except Exception as e:
                    st.error(f"Error finding similar domains: {str(e)}")

# Domain Advisor Tab
elif st.session_state.active_tab == "advisor":
    st.markdown("<p class='tab-subheader'>Tell us about your business, and we'll suggest the perfect domain names</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='domain-advisor-container'>", unsafe_allow_html=True)
        
        business_description = st.text_area(
            "Describe your business",
            placeholder="Example: I'm starting a bakery called 'Tom Bakers' that specializes in artisanal bread and pastries in New York City...",
            height=100,
            label_visibility="visible"
        )
        
        col1, col2, col3 = st.columns([3, 1, 3])
        with col2:
            advisor_search_clicked = st.button("Get Domain Suggestions", 
                                    type="primary", 
                                    use_container_width=True, 
                                    on_click=trigger_advisor_search)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    if advisor_search_clicked or st.session_state.advisor_search_triggered:
        st.session_state.advisor_search_triggered = False
        
        if not business_description:
            st.error("Please describe your business to get domain suggestions")
        else:
            with st.spinner("Our AI is thinking of the perfect domain names for your business..."):
                # Get domain suggestions from AI service
                domain_suggestions = get_domain_suggestions(business_description)
                st.session_state.domain_suggestions = domain_suggestions
            
            if domain_suggestions:
                st.subheader("Recommended Domain Names")
                st.write("Select a domain name to check its availability:")
                
                # Display domain suggestions
                for i, suggestion in enumerate(domain_suggestions):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{i+1}. {suggestion}**")
                        
                    with col2:
                        if st.button(f"Check", key=f"btn_{i}", on_click=lambda s=suggestion: select_suggestion(s)):
                            pass
                    
                    st.markdown("<hr>", unsafe_allow_html=True)
                
                st.info("💡 Click 'Check' on any domain to see its availability across different TLDs.")
            else:
                st.error("Sorry, we couldn't generate domain suggestions. Please try a more detailed description.")
