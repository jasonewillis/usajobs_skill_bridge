"""Unit tests for configuration management."""
import os
import json
import pytest
from src.utils.config import ConfigManager

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory with test files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create sample config files
    api_config = {
        "api": {
            "host": "data.usajobs.gov",
            "base_url": "https://data.usajobs.gov/api/Search",
            "default_params": {
                "ResultsPerPage": 50,
                "PayGradeLow": "5",
                "SortField": "Relevance",
                "SortDirection": "Desc"
            }
        },
        "cache_ttl": 3600,
        "request_timeout": 15
    }
    with open(config_dir / "api_config.json", "w") as f:
        json.dump(api_config, f)
        
    job_config = {
        "job_categories": {
            "it_management": "2210",
            "statistics": "1530",
            "computer_science": "1550"
        }
    }
    with open(config_dir / "job_categories.json", "w") as f:
        json.dump(job_config, f)
        
    ui_config = {
        "form_defaults": {
            "location": "Washington, DC",
            "radius": 25,
            "keywords": []
        },
        "tech_search_terms": [
            "python developer",
            "software engineer"
        ]
    }
    with open(config_dir / "ui_config.json", "w") as f:
        json.dump(ui_config, f)
        
    return config_dir

@pytest.fixture
def config_manager(temp_config_dir):
    """Create a ConfigManager instance for testing."""
    ConfigManager._instance = None  # Reset singleton for testing
    manager = ConfigManager()
    manager.config_dir = str(temp_config_dir)
    return manager

def test_validate_api_config(config_manager):
    test_config = {
        "api": {
            "host": "data.usajobs.gov",
            "base_url": "https://test.api.com",
            "default_params": {
                "ResultsPerPage": 50,
                "PayGradeLow": "5"
            }
        }
    }
    assert config_manager.validate_config("api_config", test_config) is True

def test_validate_invalid_api_config(config_manager):
    test_config = {
        "base_url": "https://test.api.com"  # Missing required 'api' field
    }
    assert config_manager.validate_config("api_config", test_config) is False

def test_validate_job_categories_config(config_manager):
    test_config = {
        "job_categories": {
            "it_management": "2210",
            "statistics": "1530"
        }
    }
    assert config_manager.validate_config("job_categories", test_config) is True

def test_load_all_configs(config_manager):
    config_manager.load_all_configs()

    # Verify API config was loaded
    assert "api_config" in config_manager._configs
    assert "base_url" in config_manager._configs["api_config"]["api"]
    
    # Verify job categories config was loaded
    assert "job_categories" in config_manager._configs
    assert isinstance(config_manager._configs["job_categories"]["job_categories"], dict)
    assert "it_management" in config_manager._configs["job_categories"]["job_categories"]
    
    # Verify UI config was loaded
    assert "ui_config" in config_manager._configs
    assert isinstance(config_manager._configs["ui_config"]["form_defaults"], dict)
    assert isinstance(config_manager._configs["ui_config"]["tech_search_terms"], list)
