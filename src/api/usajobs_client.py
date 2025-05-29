"""USAJOBS API client module."""
import os
from typing import Dict, Any, Optional
import requests

def fetch_usajobs_jobs(
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    pay_grade: Optional[str] = None
) -> Dict[str, Any]:
    """Fetch job listings from USAJOBS API."""
    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": os.getenv("USAJOBS_EMAIL", "example@email.com"),
        "Authorization-Key": os.getenv("USAJOBS_API_KEY")
    }

    params = {
        "ResultsPerPage": 10
    }

    if keyword:
        params["Keyword"] = keyword
    if location:
        params["LocationName"] = location
    if pay_grade:
        params["PayGrade"] = pay_grade

    response = requests.get(
        "https://data.usajobs.gov/api/Search",
        headers=headers,
        params=params
    )
    
    response.raise_for_status()
    return response.json()
