"""Integration tests for USA Jobs API integration."""
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from src.api.usajobs_client import fetch_usajobs_jobs

# Load environment variables
load_dotenv()

@pytest.fixture
def api_key():
    """Get API key from environment."""
    return os.getenv("USAJOBS_API_KEY")

@pytest.fixture
def mock_api_response():
    """Mock successful API response."""
    return {
        "SearchResult": {
            "SearchResultCount": 1,
            "SearchResultItems": [
                {
                    "MatchedObjectDescriptor": {
                        "PositionTitle": "Software Engineer",
                        "OrganizationName": "Department of Defense",
                        "DepartmentName": "Department of Defense",
                        "JobCategory": [{"Name": "Information Technology"}],
                        "JobGrade": [{"Code": "GS-13"}],
                        "PositionLocation": [{"LocationName": "San Francisco, CA"}],
                        "PositionURI": "https://www.usajobs.gov/job/123",
                        "QualificationSummary": "Experience with Python, Java",
                        "PositionRemuneration": [{"MinRange": "90000", "MaxRange": "120000"}]
                    }
                }
            ]
        }
    }

def test_fetch_usajobs_jobs(api_key):
    """Test basic job search functionality."""
    if not api_key:
        pytest.skip("No USAJOBS_API_KEY environment variable set")
    
    # Mock the API response
    with patch('requests.get') as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "SearchResult": {
                "SearchResultItems": [
                    {
                        "MatchedObjectDescriptor": {
                            "PositionTitle": "Software Engineer",
                            "OrganizationName": "Department of Defense",
                            "JobGrade": [{"Code": "GS"}]
                        }
                    }
                ]
            }
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        result = fetch_usajobs_jobs("data scientist", "Washington, DC")
        assert result is not None
        assert "SearchResult" in result

def test_fetch_usajobs_with_filters(mock_api_response):
    """Test job search with additional filters."""
    with patch('requests.get') as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Test with more specific search parameters
        result = fetch_usajobs_jobs(
            keyword="software engineer",
            location="San Francisco, CA",
            pay_grade="GS-13"
        )

        assert result is not None
        assert "SearchResult" in result

        # If we got results, verify they match our filters
        items = result["SearchResult"]["SearchResultItems"]
        if items:
            job = items[0]["MatchedObjectDescriptor"]
            assert any(
                grade["Code"].startswith("GS-13")
                for grade in job.get("JobGrade", [])
            )

def test_fetch_usajobs_jobs_with_location(api_key):
    """Test job search with location filtering."""
    if not api_key:
        pytest.skip("No USAJOBS_API_KEY environment variable set")

    # Test with location parameter
    with patch('requests.get') as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "SearchResult": {
                "SearchResultItems": [
                    {
                        "MatchedObjectDescriptor": {
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
        
        result = fetch_usajobs_jobs(location="San Francisco, CA")
        assert result is not None
        if result.get("SearchResult", {}).get("SearchResultItems"):
            item = result["SearchResult"]["SearchResultItems"][0]
            assert item["MatchedObjectDescriptor"]["PositionLocation"][0]["LocationName"] == "San Francisco, CA"

def test_job_listing_fields(api_key):
    """Test that job listings contain all required fields."""
    if not api_key:
        pytest.skip("No USAJOBS_API_KEY environment variable set")
    
    with patch('requests.get') as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "SearchResult": {
                "SearchResultItems": [
                    {
                        "MatchedObjectDescriptor": {
                            "PositionTitle": "Software Engineer",
                            "OrganizationName": "Department of Defense",
                            "DepartmentName": "Department of Defense",
                            "JobCategory": [{"Name": "Information Technology"}],
                            "JobGrade": [{"Code": "GS"}],
                            "PositionLocation": [{"LocationName": "Washington, DC"}],
                            "PositionURI": "https://www.usajobs.gov/job/123",
                            "QualificationSummary": "Experience with Python, Java",
                            "PositionRemuneration": [{"MinRange": "90000", "MaxRange": "120000"}]
                        }
                    }
                ]
            }
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        result = fetch_usajobs_jobs("software engineer", "Washington, DC")
        if result.get("SearchResult", {}).get("SearchResultItems"):
            job = result["SearchResult"]["SearchResultItems"][0]["MatchedObjectDescriptor"]
            required_fields = [
                "PositionTitle",
                "OrganizationName",
                "PositionLocation",
                "QualificationSummary"
            ]
            for field in required_fields:
                assert field in job
