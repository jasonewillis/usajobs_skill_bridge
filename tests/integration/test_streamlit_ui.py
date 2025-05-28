"""Integration tests for Streamlit UI components."""
import pytest
from src.ui.streamlit_federal_job_app import (
    format_job_listing,
    generate_job_filters,
    validate_location
)

@pytest.fixture
def sample_job_listing():
    return {
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
            "PositionURI": "https://www.usajobs.gov/job/123456",
            "QualificationSummary": "Bachelor's degree in Computer Science...",
            "JobGrade": [{"Code": "GS-13"}]
        }
    }

def test_format_job_listing(sample_job_listing):
    """Test job listing formatting for display."""
    formatted = format_job_listing(sample_job_listing)
    assert "Software Engineer" in formatted
    assert "Department of Defense" in formatted
    assert "Washington, DC" in formatted
    assert "$80,000" in formatted
    assert "$120,000" in formatted

def test_generate_job_filters():
    """Test job filter generation."""
    filters = generate_job_filters()
    assert "pay_grade" in filters
    assert "location" in filters
    assert "job_series" in filters
    
    # Verify filter options
    assert "GS-" in filters["pay_grade"]["options"]
    assert "Washington, DC" in filters["location"]["options"]

def test_validate_location():
    """Test location validation."""
    # Valid locations
    assert validate_location("Washington, DC") is True
    assert validate_location("San Francisco, CA") is True
    
    # Invalid locations
    assert validate_location("Invalid, XX") is False
    assert validate_location("") is False
