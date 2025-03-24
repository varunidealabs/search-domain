"""
Domain Finder Services Package

This package contains all service modules for the domain finder application:
- domain_service: Domain availability checking
- similar_domain_service: Finding similar domain names
- config_checker: Configuration validation
- utils: Helper functions and utilities
"""

from services.domain_service import check_domain_availability
from services.similar_domain_service import find_similar_domains
try:
    from services.config_checker import check_config
except ImportError:
    # Define a dummy function if the module is missing
    def check_config():
        return True

from services.utils import (
    validate_domain_name,
    clean_domain_name,
    cached,
    rate_limit
)

# Version
__version__ = '1.0.0'