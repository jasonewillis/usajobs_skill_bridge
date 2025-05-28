"""Shared pytest fixtures for the test suite."""
import os
import json
import pytest
import pandas as pd
from typing import Dict, Any

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create a temporary directory for test data that persists across the test session."""
    return tmp_path_factory.mktemp("test_data")

@pytest.fixture
def sample_job_data() -> Dict[str, Any]:
    """Sample job data fixture."""
    return {
        "SearchResult": {
            "SearchResultCount": 2,
            "SearchResultItems": [
                {
                    "MatchedObjectDescriptor": {
                        "PositionTitle": "Software Engineer",
                        "OrganizationName": "Department of Defense",
                        "PositionLocationDisplay": "Washington, DC",
                        "PositionRemuneration": [
                            {
                                "MinimumRange": "80000",
                                "MaximumRange": "120000",
                                "RateIntervalCode": "Per Year"
                            }
                        ],
                        "JobGrade": [{"Code": "GS-13"}]
                    }
                },
                {
                    "MatchedObjectDescriptor": {
                        "PositionTitle": "Data Scientist",
                        "OrganizationName": "NASA",
                        "PositionLocationDisplay": "Houston, TX",
                        "PositionRemuneration": [
                            {
                                "MinimumRange": "90000",
                                "MaximumRange": "130000",
                                "RateIntervalCode": "Per Year"
                            }
                        ],
                        "JobGrade": [{"Code": "GS-14"}]
                    }
                }
            ]
        }
    }

@pytest.fixture
def mock_config():
    """Sample configuration fixture."""
    return {
        "api_config": {
            "api": {
                "base_url": "https://data.usajobs.gov/api/Search",
                "headers": {
                    "User-Agent": "test@example.com",
                    "Authorization-Key": "test_key"
                }
            },
            "cache_ttl": 3600
        },
        "job_categories": {
            "education_job_mapping": {
                "bachelor": {
                    "keywords": ["Bachelor", "BS", "BA"]
                },
                "master": {
                    "keywords": ["Master", "MS", "MA", "MBA"]
                }
            }
        }
    }
