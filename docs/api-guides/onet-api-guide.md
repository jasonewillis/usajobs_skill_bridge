# O*NET Web Services API Guide

## Overview
O*NET Web Services provides RESTful APIs to access occupational data from the O*NET (Occupational Information Network) database. This guide covers version 2.0 of the API, which uses the O*NET 29.3 Database.

## Authentication
- All requests require an API key via the `X-API-Key` header
- API keys can be generated and managed in the My Account section
- Multiple active keys are allowed per project
- Keys must be provided in HTTP headers (not query string or POST body)
- Only GET requests are supported; POST requests are denied

## Base URL
```
https://services.onetcenter.org/ws/
```

## API Features by Category

### Available Data Categories:
1. O*NET Database
2. O*NET OnLine
3. My Next Move
4. My Next Move for Veterans
5. Mi Próximo Paso
6. O*NET-SOC Taxonomy

## Rate Limits
- No fixed maximum rate limit
- Recommended guidelines provided in Terms of Service
- 429 error code when rate limit exceeded
- Minimum 200ms delay recommended between retries
- Consider caching responses for batch processes
- Data updates: quarterly or annual basis

## Error Handling

### HTTP Status Codes
- 422: Invalid parameters or data not found
- 429: Rate limit exceeded
- 404: Resource not found
- 500: Server error

### Error Response Format
```json
{
    "error": "error message description"
}
```

## Pagination
Responses include:
- start: First result index (starts at 1)
- end: Last result index
- total: Total available results
- prev: Link to previous page (if available)
- next: Link to next page (if available)

Parameters:
- start: Starting index
- end: Ending index (max page size: 2000)

## Sample Code
Official examples available on GitHub for:
- Client-side JavaScript
- C#
- NodeJS
- Perl
- PHP
- Python
- Ruby

## Example Usage (Python)
```python
import requests

headers = {
    'X-API-Key': 'your-api-key'
}

response = requests.get(
    'https://services.onetcenter.org/ws/online/search',
    headers=headers,
    params={
        'keyword': 'software'
    }
)

data = response.json()
```

## Best Practices
1. Implement retry logic with delays
2. Cache responses when possible
3. Handle rate limits gracefully
4. Include error handling for all status codes
5. Use pagination for large result sets
6. Keep API keys secure

## OpenAPI Specification
- API defined using OpenAPI 3.1
- JSON definition available for download
- Compatible with standard OpenAPI tools
- Useful for code generation and documentation

## Data Updates
- Database updates quarterly
- Consider caching strategies based on update frequency
- Check version information endpoint for current database version

## Resources
- [Official Documentation](https://services.onetcenter.org/reference/)
- [API Demo](https://services.onetcenter.org/demo)
- [Developer Sign Up](https://services.onetcenter.org/developer/signup)
- [Terms of Service](https://services.onetcenter.org/terms)
- [Sample Code Repository](https://github.com/onetcenter/web-services-v2-samples)

## Support
For additional assistance:
- Email: onet@onetcenter.org
- Visit: [O*NET Resource Center](https://www.onetcenter.org)
- API Support: [Contact Form](https://services.onetcenter.org/contact)
