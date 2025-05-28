# USAJOBS API Guide

## Overview
This guide provides comprehensive documentation for integrating with the USAJOBS API, which allows access to federal job postings and related data.

## Authentication
The USAJOBS API requires API key authentication for all requests. Headers required for authentication:

- `Authorization-Key`: Your unique API key
- `Host`: data.usajobs.gov
- `User-Agent`: Your application name (email address)

## Base URL
```
https://data.usajobs.gov/api/
```

## Main Endpoints

### 1. Search Jobs
```
GET /api/Search
```
Search for job announcements with various filters and parameters.

Parameters:
- Page: Page number for results
- ResultsPerPage: Number of results per page (default: 25)
- Keyword: Search term
- LocationName: Location to search in
- DatePosted: Number of days since announcement was posted
- JobCategoryCode: Job category codes

### 2. Historic Job Announcements
```
GET /api/HistoricJoa
```
Retrieve historical job announcements.

### 3. Announcement Text
```
GET /api/HistoricJoa/AnnouncementText
```
Get the full text of a specific job announcement.

## Code Lists
The API provides various code list endpoints for reference data:

- Agency Subelements: `/codelist/agencysubelements`
- Occupational Series: `/codelist/occupationalseries`
- Pay Plans: `/codelist/payplans`
- Position Schedule Types: `/codelist/positionscheduletypes`
- Location Codes: `/codelist/geoloccodes`
- Hiring Paths: `/codelist/hiringpaths`

## Rate Limiting
- API requests are rate-limited
- Rate limits are applied per API key
- Consider implementing retry logic with exponential backoff

## Response Format
All API responses are in JSON format and follow this general structure:

```json
{
    "LanguageCode": "EN",
    "SearchResult": {
        "SearchResultCount": 0,
        "SearchResultCountAll": 0,
        "SearchResultItems": [],
        "UserArea": {}
    },
    "ExecutionTime": "0"
}
```

## Error Handling
Common HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 429: Too Many Requests
- 500: Internal Server Error

## Best Practices
1. Always include required headers
2. Implement proper error handling
3. Cache results when appropriate
4. Respect rate limits
5. Use specific search parameters to optimize results
6. Keep API keys secure

## Example Usage
Python example using requests:

```python
import requests

headers = {
    'Authorization-Key': 'your-api-key',
    'User-Agent': 'your-email@example.com',
    'Host': 'data.usajobs.gov'
}

response = requests.get(
    'https://data.usajobs.gov/api/Search',
    headers=headers,
    params={
        'Keyword': 'software',
        'LocationName': 'Washington, DC',
        'ResultsPerPage': '10'
    }
)

data = response.json()
```

## Resources
- [Official Documentation](https://developer.usajobs.gov/)
- [API Reference](https://developer.usajobs.gov/api-reference/)
- [Authentication Guide](https://developer.usajobs.gov/guides/authentication)
- [Terms of Use](https://developer.usajobs.gov/guides/terms-of-use)
