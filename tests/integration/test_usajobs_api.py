"""Integration tests for USA Jobs API integration."""
import os
import pytest
from dotenv import load_dotenv
from src.api.usajobs_client import fetch_usajobs_jobs

# Load environment variables
load_dotenv()

@pytest.fixture
def api_key():
    """Get API key from environment."""
    return os.getenv("USAJOBS_API_KEY")

def test_fetch_usajobs_jobs(api_key):
    """Test basic job search functionality."""
    # Skip if no API key is available
    if not api_key:
        pytest.skip("No USAJOBS_API_KEY environment variable set")
    
    # Test with basic search parameters
    result = fetch_usajobs_jobs("data scientist", "Washington, DC")
    assert result is not None
    assert "SearchResult" in result
    
    # Verify response structure
    search_result = result["SearchResult"]
    assert "SearchResultItems" in search_result
    assert isinstance(search_result["SearchResultItems"], list)
    
    # Check job listing fields
    if search_result["SearchResultItems"]:
        job = search_result["SearchResultItems"][0]["MatchedObjectDescriptor"]
        assert "PositionTitle" in job
        assert "OrganizationName" in job
        assert "PositionLocationDisplay" in job

def test_fetch_usajobs_with_filters(api_key):
    """Test job search with additional filters."""
    if not api_key:
        pytest.skip("No USAJOBS_API_KEY environment variable set")
    
    # Test with more specific search parameters
    result = fetch_usajobs_jobs(
        keyword="software engineer",
        location="San Francisco, CA",
        pay_grade="GS-13"  # Assuming this parameter exists
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
    """Test job search with specific location."""
    if not api_key:
        pytest.skip("No USAJOBS_API_KEY environment variable set")
    
    result = fetch_usajobs_jobs("police", "Las Vegas, NV")
    assert result is not None
    assert "SearchResult" in result
    
    # Verify location filtering
    items = result["SearchResult"]["SearchResultItems"]
    if items:
        job = items[0]["MatchedObjectDescriptor"]
        assert "Las Vegas" in job["PositionLocationDisplay"]

def test_job_listing_fields(api_key):
    """Test that job listings contain all required fields."""
    if not api_key:
        pytest.skip("No USAJOBS_API_KEY environment variable set")
    
    result = fetch_usajobs_jobs("police", "Las Vegas, NV")
    
    if result["SearchResult"]["SearchResultItems"]:
        job = result["SearchResult"]["SearchResultItems"][0]["MatchedObjectDescriptor"]
        # Check essential fields from the notebook example
        assert "PositionTitle" in job
        assert "OrganizationName" in job
        assert "PositionLocationDisplay" in job
        assert "PositionRemuneration" in job
        
        # Verify remuneration structure
        remuneration = job["PositionRemuneration"][0]
        assert "MinimumRange" in remuneration
        assert "MaximumRange" in remuneration
