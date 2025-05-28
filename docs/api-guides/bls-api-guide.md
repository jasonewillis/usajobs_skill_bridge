# BLS (Bureau of Labor Statistics) API Guide

## Overview
This guide provides information on integrating BLS occupational outlook data, employment statistics, and wage information, along with crosswalks between different classification systems (CIP, SOC, O*NET) for comprehensive career pathway analysis.

## API Integration Points

### 1. BLS Public Data API
- **Base URL**: `https://api.bls.gov/publicAPI/v2`
- **Authentication**: Requires registration for v2.0 access
- **Rate Limits**: Higher limits with registered API key
- **Response Format**: JSON or XLSX

### 2. CIP Data Integration
Base URL: `https://nces.ed.gov/ipeds/cipcode`

#### CIP Code Structure
```
XX.XXXX
|  |
|  +--- Detailed Program Level
+------ Broad Field Category
```

## Data Crosswalks

### 1. CIP to SOC Crosswalk
Links educational programs to occupational outcomes:

Example for Data Science:
```json
{
    "cip_code": "11.0701",
    "cip_title": "Computer Science",
    "soc_codes": [
        {
            "code": "15-2051",
            "title": "Data Scientists",
            "match_percent": 85
        },
        {
            "code": "15-1252",
            "title": "Software Developers",
            "match_percent": 70
        }
    ]
}
```

### 2. SOC to O*NET Crosswalk
Links occupational codes to detailed job characteristics:

```json
{
    "soc_code": "15-2051",
    "onet_codes": [
        "15-2051.00",
        "15-2051.01",
        "15-2051.02"
    ]
}
```

## Occupational Data Integration

### Sample Career Path: Data Scientist

#### 1. Educational Requirements
- **Typical Entry Level Education**: Bachelor's degree
- **Common Fields**:
  - Mathematics (CIP: 27.0101)
  - Statistics (CIP: 27.0501)
  - Computer Science (CIP: 11.0701)
  - Data Science (CIP: 30.7001)

#### 2. Labor Market Information
```json
{
    "occupation": "Data Scientists",
    "soc_code": "15-2051",
    "employment": {
        "current": 202900,
        "projected_2033": 276000,
        "growth_rate": 36,
        "annual_openings": 20800
    },
    "wages": {
        "median_annual": 112590,
        "range": {
            "low": 63650,
            "high": 194410
        }
    }
}
```

#### 3. Skills and Competencies
Mapped from O*NET:
```json
{
    "technical_skills": [
        "Statistical Analysis",
        "Machine Learning",
        "Programming Languages",
        "Data Visualization"
    ],
    "soft_skills": [
        "Analytical Thinking",
        "Problem Solving",
        "Communication",
        "Logical Thinking"
    ]
}
```

## API Endpoints

### 1. BLS Endpoints

#### Employment Projections
```
GET /timeseries/data/{series-id}
```

Parameters:
- series-id: Unique identifier for occupation data
- startyear: Starting year for projection
- endyear: Ending year for projection

#### Wage Data
```
GET /occupation/wage/{soc-code}
```

### 2. Education Program Data
```
GET /programs/{cip-code}
```

Returns:
- Program description
- Required coursework
- Common career paths
- Related programs

## Integration with Existing Guides

### 1. USAJOBS API Integration
- Use SOC codes to map federal job titles
- Link salary information between BLS and USAJOBS data
- Map veteran preferences to career paths

### 2. O*NET API Integration
- Detailed skill requirements
- Job characteristics and work environment
- Career advancement paths

## Examples

### 1. Complete Career Path Query
```python
import requests

def get_career_path(cip_code):
    # Get educational program info
    program = get_program_details(cip_code)
    
    # Get related occupations
    soc_codes = get_soc_crosswalk(cip_code)
    
    # Get employment outlook
    outlook = get_bls_outlook(soc_codes)
    
    # Get detailed occupation info
    onet_info = get_onet_details(soc_codes)
    
    return {
        "education": program,
        "occupations": outlook,
        "skills": onet_info
    }
```

### 2. Salary Comparison
```python
def compare_salaries(soc_code):
    # Get BLS wage data
    bls_wages = get_bls_wages(soc_code)
    
    # Get USAJOBS salary data
    usajobs_salaries = get_usajobs_salaries(soc_code)
    
    return {
        "national_data": bls_wages,
        "federal_data": usajobs_salaries
    }
```

## Best Practices

1. Data Freshness
   - BLS data updated annually
   - CIP codes updated every 10 years
   - O*NET data updated quarterly

2. Error Handling
   - Implement retry logic
   - Cache responses when appropriate
   - Handle missing data gracefully

3. Data Integration
   - Use standardized codes (SOC, CIP, O*NET)
   - Validate crosswalk accuracy
   - Consider regional variations

## Resources

- [BLS Developer Resources](https://www.bls.gov/developers/)
- [CIP Code Database](https://nces.ed.gov/ipeds/cipcode)
- [O*NET Resource Center](https://www.onetcenter.org/)
- [SOC Classification Manual](https://www.bls.gov/soc/)

## Support
For additional assistance:
- BLS API Support: stats.bls.gov/help/
- CIP Code Help: nces.ed.gov/ipeds/cipcode/help
- Technical Support: Contact repository maintainers

Last Updated: May 28, 2025
