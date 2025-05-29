import json
import os
import time
import threading
from typing import Dict, Any, List, Tuple, Optional, ClassVar
import requests
from geopy.geocoders import Nominatim
import streamlit as st

class ConfigManager:
    _instance: Optional['ConfigManager'] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()
    _configs: Dict[str, Dict[str, Any]] = {}
    _required_fields: ClassVar[Dict[str, List[str]]] = {
        'api_config': ['api'],
        'job_categories': ['job_categories'],
        'ui_config': ['form_defaults', 'tech_search_terms']
    }
    _default_values: ClassVar[Dict[str, Dict[str, Any]]] = {
        'api_config': {
            'api': {
                'host': 'data.usajobs.gov',
                'base_url': 'https://data.usajobs.gov/api/Search',
                'default_params': {
                    'ResultsPerPage': 50,
                    'PayGradeLow': '5',
                    'SortField': 'Relevance',
                    'SortDirection': 'Desc',
                    'Page': 1,
                    'WhoMayApply': 'all'
                }
            },
            'cache_ttl': 3600,
            'max_retries': 3,
            'retry_delay': 1,
            'request_timeout': 15
        },
        'ui_config': {
            'layout': 'wide',
            'page_title': 'Federal Job Roadmap',
            'page_icon': '🏛️',
            'debug_mode': False,
            'form_defaults': {
                'location': 'Washington, DC',
                'radius': 25,
                'keywords': [],
                'pay_grade': 'all',
                'job_series': 'all'
            }
        }
    }

    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-check pattern
                    cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        with self._lock:
            if not self._configs:
                self.load_all_configs()

    def _apply_defaults(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to configuration."""
        if name in self._default_values:
            defaults = self._default_values[name].copy()
            if config:
                for key, value in config.items():
                    if isinstance(value, dict) and key in defaults and isinstance(defaults[key], dict):
                        defaults[key].update(value)
                    else:
                        defaults[key] = value
            return defaults
        return config

    def validate_config(self, name: str, config: Dict[str, Any]) -> bool:
        """Validate that a configuration has all required fields."""
        if name not in self._required_fields:
            return True
        
        for field in self._required_fields[name]:
            if field not in config:
                return False
            
            # For API config, validate deeper structure
            if name == 'api_config' and field == 'api':
                api_config = config['api']
                required_api_fields = ['host', 'base_url', 'default_params']
                if not all(f in api_config for f in required_api_fields):
                    return False
        
        return True

    def load_all_configs(self):
        """Load all configuration files from the config directory."""
        # Start from the current file's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to src directory
        src_dir = os.path.dirname(current_dir)
        # Go up to project root
        project_root = os.path.dirname(src_dir)
        # Config directory is at project root
        config_dir = os.path.join(project_root, 'config')
        
        # Override config directory if set manually (for testing)
        if hasattr(self, 'config_dir'):
            config_dir = self.config_dir
        
        if not os.path.exists(config_dir):
            raise FileNotFoundError(f"Config directory not found: {config_dir}")
        
        for filename in os.listdir(config_dir):
            if filename.endswith('.json'):
                name = os.path.splitext(filename)[0]
                with open(os.path.join(config_dir, filename), 'r') as f:
                    try:
                        config = json.load(f)
                        config = self._apply_defaults(name, config)
                        if self.validate_config(name, config):
                            self._configs[name] = config
                    except json.JSONDecodeError:
                        continue
    
        # Add required keys if missing
        # Handle job categories specially
        if "job_categories" in self._configs:
            if "job_categories" not in self._configs["job_categories"]:
                self._configs["job_categories"] = {
                    "job_categories": self._configs["job_categories"].get("education_job_mapping", {})
                }

    def get_config(self, name: str) -> Dict[str, Any]:
        """Get a specific configuration with validation."""
        with self._lock:
            config = self._configs.get(name, {})
            if not config:
                if name in self._required_fields:
                    st.error(f"Configuration '{name}' is missing or invalid")
                return self._default_values.get(name, {})
            return config

    def update_config(self, name: str, updates: Dict[str, Any]) -> bool:
        """Update configuration values."""
        with self._lock:
            if name not in self._configs:
                st.error(f"Configuration '{name}' not found")
                return False

            current_config = self._configs[name].copy()
            current_config.update(updates)

            if self.validate_config(name, current_config):
                self._configs[name] = current_config
                if st.session_state.get('debug_mode', False):
                    st.write(f"✅ Updated {name} configuration")
                return True
            return False

    def get_sample_jobs(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get sample jobs with optional category filtering."""
        with self._lock:
            jobs = self._configs.get('sample_jobs', {}).get('sample_jobs', {})
            if category:
                return jobs.get(category, [])
            return [job for jobs_list in jobs.values() for job in jobs_list]

    def get_job_categories_for_keyword(self, keyword: str) -> List[str]:
        """Get relevant job categories based on keyword."""
        with self._lock:
            categories = []
            keyword_lower = keyword.lower()
            job_mappings = self.get_config('job_categories').get('education_job_mapping', {})
            
            for field, info in job_mappings.items():
                if any(kw.lower() in keyword_lower for kw in info.get('keywords', [])):
                    if field == 'data_analytics':
                        categories.extend(['1530', '1550'])
                    elif field == 'computer_science':
                        categories.append('2210')
                    elif field == 'information_technology':
                        categories.extend(['2210', '0391'])
            
            return list(set(categories)) or ['2210']  # Default to IT Management if no matches

# Initialize the configuration manager
config_manager = ConfigManager()

@st.cache_data(ttl=3600)
def get_api_config() -> Dict[str, Any]:
    """Get API configuration with caching."""
    return config_manager.get_config('api_config')

@st.cache_data(ttl=3600)
def get_job_categories() -> Dict[str, Any]:
    """Get job categories configuration with caching."""
    return config_manager.get_config('job_categories')

@st.cache_data(ttl=3600)
def get_ui_config() -> Dict[str, Any]:
    """Get UI configuration with caching."""
    return config_manager.get_config('ui_config')

@st.cache_data(ttl=3600)
def get_sample_jobs(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get sample jobs with caching."""
    return config_manager.get_sample_jobs(category)

@st.cache_data(ttl=3600)
def get_coordinates(address: str) -> Tuple[Optional[float], Optional[float]]:
    """Cache geocoding results for addresses with retry logic."""
    if not address:
        return (None, None)

    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            geolocator = Nominatim(user_agent="fed-career-map", timeout=5)
            location = geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
            elif attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                continue
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Geocoding attempt {attempt + 1} failed: {str(e)}. Retrying...")
                time.sleep(retry_delay * (2 ** attempt))
                continue
            st.error(f"Geocoding failed after {max_retries} attempts: {str(e)}")
    
    return (None, None)

@st.cache_data(ttl=3600)
def fetch_usajobs_data(
    keyword: str,
    location: str,
    headers: Dict[str, str],
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Cache USAJOBS API responses with enhanced error handling and retry logic."""
    api_config = get_api_config()
    max_retries = api_config.get('max_retries', 3)
    base_delay = api_config.get('retry_delay', 1)
    timeout = api_config.get('request_timeout', 15)

    for attempt in range(max_retries):
        try:
            response = requests.get(
                api_config['api']['base_url'],
                headers=headers,
                params=params,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                # Validate response structure
                if 'SearchResult' not in data:
                    st.error("Invalid API response: missing SearchResult")
                    return {}
                return data
            
            elif response.status_code == 429:  # Rate limit
                if attempt < max_retries - 1:
                    wait_time = min(base_delay * (2 ** attempt), 8)
                    st.warning(f"Rate limit reached. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
            
            elif response.status_code in [500, 502, 503, 504]:  # Server errors
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    st.warning(f"Server error {response.status_code}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
            
            st.error(f"API Error {response.status_code}: {response.text}")
            
        except requests.Timeout:
            if attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)
                st.warning(f"Request timed out. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            st.error(f"API request timed out after {max_retries} attempts")
            
        except requests.ConnectionError:
            if attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)
                st.warning(f"Connection error. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            st.error("Failed to connect to the API. Please check your internet connection.")
            
        except Exception as e:
            st.error(f"Unexpected error during API request: {str(e)}")
            if st.session_state.get('debug_mode', False):
                st.exception(e)
    
    return {}
