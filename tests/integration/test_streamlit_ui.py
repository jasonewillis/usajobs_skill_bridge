"""Integration tests for Streamlit UI components."""
import pytest
import json
import streamlit as st
from unittest.mock import patch, MagicMock
from pathlib import Path

# Mock the configuration first
UI_CONFIG = {
    "debug_mode": False,
    "layout": "wide",
    "page_title": "Federal Job Roadmap",
    "page_icon": "🏛️",
    "tech_search_terms": [
        "python developer",
        "software engineer",
        "data scientist",
        "IT specialist",
        "systems administrator",
        "database administrator",
        "computer scientist",
        "information technology"
    ],
    "veteran_status_options": [
        "Not a Veteran",
        "Veteran",
        "≥ 30% Disabled Veteran",
        "Retired Military",
        "Active Duty (Transitioning)"
    ],
    "form_defaults": {
        "location": "Washington, DC",
        "radius": 25,
        "keywords": [],
        "pay_grade": "all",
        "job_series": "all",
        "name": "John Doe",
        "email": "johndoe@example.com",
        "address": "6900 N Pecos Rd, North Las Vegas, NV 89086",
        "skills": "Python, SQL, data science, data analytics",
        "degree": "BA in Computer Science",
        "max_distance": 50
    }
}

# Initialize Streamlit's session state and functions
if not hasattr(st, 'session_state'):
    setattr(st, 'session_state', {})

st.session_state.update({
    'debug_mode': UI_CONFIG["debug_mode"],
    'form_submitted': False,
    'job_data': None,
    'selected_jobs': [],
    'search_performed': False,
    'form_values': UI_CONFIG["form_defaults"].copy()
})

# Mock all the Streamlit functions we use
st.text = MagicMock()
st.write = MagicMock()
st.error = MagicMock()
st.warning = MagicMock()
st.success = MagicMock()
st.set_page_config = MagicMock()
st.text_input = MagicMock(side_effect=lambda label, value="", **kwargs: value)
st.number_input = MagicMock(side_effect=lambda label, value=0, **kwargs: value)
st.selectbox = MagicMock(side_effect=lambda label, options, **kwargs: options[0])
st.multiselect = MagicMock(return_value=[])
st.form = MagicMock()
st.form_submit_button = MagicMock(return_value=False)
st.spinner = MagicMock()
st.container = MagicMock()
st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])

class MockForm:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
st.form = MagicMock(return_value=MockForm())

# Apply configuration mocks
MOCK_API_CONFIG = {
    "api": {
        "host": "data.usajobs.gov",
        "base_url": "https://data.usajobs.gov/api/Search",
        "default_params": {
            "ResultsPerPage": 50,
            "PayGradeLow": "5",
            "SortField": "Relevance",
            "SortDirection": "Desc",
            "Page": 1,
            "WhoMayApply": "all"
        }
    },
    "job_categories": {
        "it_management": "2210",
        "statistics": "1530",
        "computer_science": "1550",
        "engineering": "0800",
        "medical": "0600"
    },
    "default_location": "Las Vegas, NV",
    "cache_ttl": 3600,
    "max_retries": 3,
    "retry_delay": 1,
    "request_timeout": 15
}

with patch('src.utils.config.get_ui_config', return_value=UI_CONFIG), \
     patch('src.utils.config.get_api_config', return_value=MOCK_API_CONFIG), \
     patch('src.utils.config.get_job_categories', return_value={}), \
     patch.object(st, 'session_state', st.session_state):
    
    # Now import the app code
    from src.ui.streamlit_federal_job_app import (
        fetch_usajobs_jobs,
        get_coordinates,
        calculate_distance,
        filter_jobs,
        verify_usajobs_connection
    )

@pytest.fixture
def mock_job_data():
    """Mock job listing data for tests."""
    return {
        "MatchedObjectDescriptor": {
            "PositionTitle": "Test Job",
            "OrganizationName": "Test Org",
            "PositionLocationDisplay": "Washington, DC",
            "QualificationSummary": "Test qualifications",
            "JobGrade": [{"Code": "GS"}],
            "PositionRemuneration": [{"MinRange": "50000", "MaxRange": "100000"}],
            "PositionLocation": [{"LocationName": "Washington, DC"}]
        }
    }

@pytest.fixture
def mock_coordinates():
    """Mock coordinates for location-based tests."""
    return (38.8977, -77.0365)  # Washington, DC coordinates

def test_verify_usajobs_connection(monkeypatch):
    """Test API connection verification."""
    monkeypatch.setenv("USAJOBS_API_KEY", "test-key")
    with patch('requests.get') as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        assert verify_usajobs_connection() == True

def test_fetch_usajobs_jobs():
    """Test job fetching functionality."""
    result = fetch_usajobs_jobs("data scientist", "Washington, DC")
    assert isinstance(result, dict)
    assert "SearchResult" in result

def test_get_coordinates():
    """Test coordinate lookup functionality."""
    with patch('geopy.geocoders.Nominatim.geocode') as mock_geocode:
        mock_geocode.return_value = MagicMock(
            latitude=38.8977,
            longitude=-77.0365
        )
        coords = get_coordinates("Washington, DC")
        assert coords is not None
        assert len(coords) == 2
        assert coords[0] == pytest.approx(38.8977)
        assert coords[1] == pytest.approx(-77.0365)

def test_calculate_distance():
    """Test distance calculation between two points."""
    dc_coords = (38.8977, -77.0365)  # Washington, DC
    nyc_coords = (40.7128, -74.0060)  # New York City
    distance = calculate_distance(dc_coords, nyc_coords)
    assert isinstance(distance, float)
    assert distance > 0
    assert distance == pytest.approx(225.0, rel=0.1)  # ~225 miles between DC and NYC

@patch('src.ui.streamlit_federal_job_app.get_coordinates')
def test_filter_jobs(mock_get_coords, mock_job_data, mock_coordinates):
    """Test job filtering functionality."""
    mock_get_coords.return_value = (38.8977, -77.0365)  # Washington, DC
    
    jobs = [mock_job_data]
    user_coords = mock_coordinates
    max_distance = 50
    user_skills = "Python, SQL"
    user_education = "Bachelor's"

    filtered_jobs = filter_jobs(jobs, user_coords, max_distance, user_skills, user_education)
    assert isinstance(filtered_jobs, list)
    
    # Test empty case
    filtered_empty = filter_jobs([], user_coords, max_distance)
    assert isinstance(filtered_empty, list)
    assert len(filtered_empty) == 0

def test_fetch_usajobs_with_filters():
    """Test job search with filters"""
    with patch('requests.get') as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "SearchResult": {
                "SearchResultItems": [
                    {
                        "MatchedObjectDescriptor": {
                            "PositionTitle": "Software Engineer",
                            "JobGrade": [{"Code": "GS-13"}],
                            "PositionLocation": [
                                {"LocationName": "San Francisco, CA"}
                            ]
                        }
                    }
                ]
            }
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        result = fetch_usajobs_jobs(
            keyword="software engineer",
            location="San Francisco, CA",
            pay_grade="GS-13"
        )
        
        assert result is not None
        assert "SearchResult" in result
        
        items = result["SearchResult"]["SearchResultItems"]
        if items:
            job = items[0]["MatchedObjectDescriptor"]
            assert any(
                grade["Code"].startswith("GS-13")
                for grade in job.get("JobGrade", [])
            )
