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
            "base_url": "https://data.usajobs.gov/api/Search",
            "headers": {"User-Agent": "test@example.com"}
        },
        "cache_ttl": 3600
    }
    with open(config_dir / "api_config.json", "w") as f:
        json.dump(api_config, f)
        
    job_config = {
        "education_job_mapping": {
            "bachelor": {
                "keywords": ["Bachelor", "BS", "BA"]
            }
        }
    }
    with open(config_dir / "job_categories.json", "w") as f:
        json.dump(job_config, f)
        
    return config_dir

@pytest.fixture
def config_manager(temp_config_dir):
    """Create a ConfigManager instance with test configs."""
    return ConfigManager(config_dir=str(temp_config_dir))

def test_validate_api_config(config_manager):
    test_config = {
        "api": {
            "base_url": "https://test.api.com",
            "headers": {"User-Agent": "test@example.com"}
        },
        "cache_ttl": 3600
    }
    assert config_manager.validate_config("api_config", test_config) is True

def test_validate_invalid_api_config(config_manager):
    test_config = {
        "api": "not_a_dict",  # Should be a dict
        "cache_ttl": "not_a_number"  # Should be a number
    }
    assert config_manager.validate_config("api_config", test_config) is False

def test_validate_job_categories_config(config_manager):
    test_config = {
        "education_job_mapping": {
            "master": {
                "keywords": ["Master", "MS", "MA"]
            }
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
    assert "education_job_mapping" in config_manager._configs["job_categories"]
