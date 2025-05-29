# Federal Job Roadmap Project Context

## Project Overview
The Federal Job Roadmap is a Streamlit-based application designed to help veterans and students find federal job opportunities. It provides personalized job matching based on skills, education, location, and veteran status.

## Key Features
- Live integration with USAJOBS API
- Sample data fallback when API is unavailable
- Geocoding and distance-based job filtering
- Education and skills-based job matching
- Professional PDF report generation
- Veteran preference handling
- Comprehensive test coverage
- Robust configuration management

## Technical Stack
- **Frontend**: Streamlit with mocked components for testing
- **API Integration**: USAJOBS API with optional parameters
- **Data Processing**: Pandas, GeoPy
- **PDF Generation**: ReportLab
- **Environment Management**: Python venv (Python 3.11)
- **Version Control**: Git
- **Geocoding**: Nominatim
- **Documentation**: Markdown
- **Testing Framework**: Pytest with comprehensive coverage

## Project Structure
```
USAJobs_Proj/
├── streamlit_federal_job_app.py  # Main application file
├── requirements.txt              # Project dependencies
├── .env                         # Environment variables (API keys)
├── veteran_status_options.txt   # Veteran status configurations
├── project_context.md            # Project documentation
├── README.md                     # Project overview
├── init_git_push.sh             # Git initialization script
├── SampleReports/              # Generated PDF reports directory
│   ├── _Archive/               # Old report versions
│   └── *.pdf                   # Generated reports
├── US/                         # Geographic data
│   ├── US.txt
│   └── US.zip
└── usajobs_env/               # Python virtual environment
```

## Data Models

### Job Listing Schema
```python
{
    "PositionTitle": str,
    "OrganizationName": str,
    "LocationName": str,
    "SalaryRange": str,
    "ClosingDate": str,
    "VeteranPreferred": bool,
    "JobCoordinates": tuple(float, float),
    "Keywords": list[str]
}
```

### User Profile Schema
```python
{
    "name": str,
    "email": str,
    "address": str,
    "veteran_status": str,
    "skills": list[str],
    "degree": str
}
```

## Key Functions
1. `verify_usajobs_connection()`: API connection verification
2. `fetch_usajobs_jobs()`: Live job data retrieval
3. `filter_jobs()`: Job filtering based on user criteria
4. `get_coordinates()`: Geocoding with retry logic
5. `generate_pdf_report()`: PDF report generation

## Education-Job Mappings
Current mappings for education to job titles:
- Nursing → nurse, rn, lpn, clinical
- Medical → health, medical, clinical
- Criminal Justice → police, security, law enforcement
- Computer Science → it, software, programmer, developer

## Development Notes
- API responses are cached for 1 hour (currently commented out)
- Geocoding includes retry logic for reliability
- PDF reports include page numbers and professional styling
- Job matching uses flexible keyword matching for better results

## Future Enhancements
- [ ] Implement caching for API calls
- [ ] Add more education-job mappings
- [ ] Enhance error handling for PDF cleanup
- [ ] Add salary range filtering
- [ ] Implement agency-specific filtering

## Environment Setup
```bash
# Create and activate virtual environment
python -m venv usajobs_env
source usajobs_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your USAJOBS API key

# Run application
streamlit run streamlit_federal_job_app.py
```

## API Usage
The application uses the USAJOBS API with the following considerations:

### Rate Limits
- API requests are currently not cached (TODO: implement caching)
- Default limit: 1000 requests per hour
- Recommended: Implement rate limiting and caching

### API Response Structure
```python
{
    "LanguageCode": str,
    "SearchResult": {
        "SearchResultCount": int,
        "SearchResultItems": [
            {
                "MatchedObjectDescriptor": {
                    "PositionTitle": str,
                    "OrganizationName": str,
                    "PositionLocationDisplay": str,
                    "PositionRemuneration": [
                        {
                            "MinimumRange": str,
                            "MaximumRange": str
                        }
                    ],
                    "QualificationSummary": str,
                    "ApplicationCloseDate": str,
                    "UserArea": {
                        "VeteransPreference": str
                    }
                }
            }
        ]
    }
}
```

### Error Handling
- Connection timeout: 5 seconds
- Geocoding retries: 3 attempts with 2-second delays
- API fallback: Uses static sample data when API is unavailable

## Test Coverage
- **Integration Tests**:
  - Streamlit UI components (6 tests)
  - USAJOBS API integration (4 tests)
  - Proper caching and state management
- **Unit Tests**:
  - Configuration management (4 tests)
  - Data processing (2 tests)
  - Edge case handling
  - Parameter validation

## Configuration Management
- Path resolution with proper project root detection
- Validated configuration with default fallbacks
- Environment-specific settings support
- Secure API key management

Last Updated: May 28, 2025
