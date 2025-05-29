# Federal Job Roadmap Capabilities Guide

This guide helps answer common questions about what the Federal Job Roadmap application can and cannot do.

## Job Search Capabilities

### Location-Based Search
[+] **Available Features:**
- Search jobs within a specific radius (10-500 miles) of your location
- Filter jobs by city and state
- View distance to each job opportunity
- Show all locations regardless of distance (optional)

[-] **Limitations:**
- Requires valid US address for geocoding
- Some remote positions may not have coordinates
- International locations not supported

### Veteran-Specific Features
[+] **Available Features:**
- Filter jobs with veteran preference
- Support for different veteran statuses:
  - Not a Veteran
  - Veteran
  - >= 30% Disabled Veteran
  - Retired Military
  - Active Duty (Transitioning)
- Highlight veteran-preferred positions

### Education & Skills Matching
[+] **Available Features:**
- Match jobs based on education level
- Support for multiple degree types
- Skill-based job matching
- Flexible keyword matching
- Education-to-job title mappings for:
  - Nursing
  - Medical
  - Criminal Justice
  - Computer Science

[-] **Limitations:**
- Limited to predefined education-job mappings
- Keyword matching may miss some relevant positions
- Cannot currently filter by specific certification requirements

### Salary Information
[+] **Available Features:**
- Display salary ranges for positions
- Show minimum and maximum pay
- Include locality pay information when available

[-] **Limitations:**
- Cannot currently filter by salary range
- Pay grade filtering not implemented
- Cannot calculate take-home pay

### Application Features
[+] **Available Features:**
- Generate professional PDF reports
- Include application deadlines
- Show qualification summaries
- List organization details

[-] **Limitations:**
- Cannot submit applications directly
- Cannot save application drafts
- No resume builder functionality

### Data Reliability
[+] **Available Features:**
- Live USAJOBS API integration with flexible parameters
- Fallback to sample data when API is unavailable
- Automatic retry for failed requests
- Improved caching support with proper validation
- Optional location and keyword parameters
- Configurable request timeout handling

[-] **Limitations:**
- API limited to 1000 requests per hour
- Some cached data may be slightly outdated
- Network connectivity required for live data

### Configuration Management
[+] **Available Features:**
- Automatic project root detection
- Environment-specific configuration support
- Validated configuration with default fallbacks
- Secure API key management
- Flexible configuration overrides
- Test-friendly configuration setup

[-] **Limitations:**
- Manual configuration backup not implemented
- Limited to predefined configuration options

### Labor Market Information (BLS Integration)
[+] **Available Features:**
- Access real-time employment statistics
- View occupation growth projections
- Compare salary data across regions
- Access detailed industry statistics
- Track employment trends

[-] **Limitations:**
- Data updates follow BLS release schedule
- Historical data may have gaps
- Some industry-specific data may be aggregated

### Career Exploration (O*NET Integration)
[+] **Available Features:**
- Detailed skill requirements mapping
- Career advancement pathways
- Related occupation suggestions
- Work environment details
- Education and experience requirements

[-] **Limitations:**
- Skill assessments not available
- Cannot customize career paths
- Limited to O*NET-listed occupations

### Cross-System Integration
[+] **Available Features:**
- Map education programs to occupations
- Link federal jobs to industry statistics
- Compare federal vs private sector salaries
- Track occupation demand trends
- View similar job recommendations

[-] **Limitations:**
- Some crosswalk mappings may be incomplete
- Real-time integration depends on all APIs
- Data freshness varies by source

## Technical Capabilities

### API Integration
- USAJOBS API for live job data
- Real-time data verification
- Error handling with fallback options
- Rate limit monitoring

### Geocoding Features
- Address validation
- Coordinate calculation
- Distance computation
- Multiple retry attempts

### Report Generation
- Professional PDF formatting
- Customized for each user
- Includes:
  - Personal profile
  - Matched opportunities
  - Distance information
  - Salary details
  - Application instructions

### Data Processing
- Real-time job filtering
- Education-skills correlation
- Distance calculations
- Veteran status validation

### BLS Data Processing
- Employment statistics analysis
- Wage data computation
- Industry trend analysis
- Regional market comparisons
- Time series data handling

### O*NET Integration Features
- Skill matrix mapping
- Career pathway tracking
- Competency analysis
- Work activity profiling
- Job zone classification

## Future Capabilities
The following features are planned but not yet implemented:
- [ ] Salary range filtering
- [ ] Agency-specific filtering
- [ ] Enhanced caching system
- [ ] Additional education-job mappings
- [ ] Improved PDF error handling
- [ ] Resume analysis and matching
- [ ] Job alert notifications
- [ ] Application tracking

## Support and Limitations
- Application requires internet connection
- USAJOBS API key required for live data
- Python 3.11 or higher required
- Some features require Streamlit server access
- Limited to US federal positions only

Last Updated: May 28, 2025
