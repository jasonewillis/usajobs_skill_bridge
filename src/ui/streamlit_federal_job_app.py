import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from dotenv import load_dotenv
import os
import requests
import time
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from src.utils.config import (
    get_api_config,
    get_job_categories,
    get_ui_config,
    get_coordinates as cached_get_coordinates
)

# Load configurations with error handling
try:
    API_CONFIG = get_api_config()
    JOB_CATEGORIES = get_job_categories()
    UI_CONFIG = get_ui_config()
except Exception as e:
    st.error(f"Failed to load configuration: {str(e)}")
    st.stop()

# Initialize session state for settings
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = UI_CONFIG.get('debug_mode', False)

# Page Configuration
st.set_page_config(
    layout=UI_CONFIG.get('layout', "wide"),
    page_title=UI_CONFIG.get('page_title', "Federal Job Roadmap"),
    page_icon=UI_CONFIG.get('page_icon', "🏛️")
)

# Load environment variables with validation
load_dotenv()
USAJOBS_API_KEY = os.getenv("USAJOBS_API_KEY")
if not USAJOBS_API_KEY:
    st.error("❌ USAJOBS_API_KEY not found in environment variables!")
    st.info("Please set up your .env file with your USAJOBS API key.")
    st.stop()

# --- Helper Functions ---
def verify_usajobs_connection():
    with st.sidebar.expander("🔧 API Configuration"):
        st.write("Testing API connection...")
        api_status = False
        
        if not USAJOBS_API_KEY:
            st.error("❌ API Key missing! Check your .env file")
        else:
            headers = {
                "Host": "data.usajobs.gov",
                "User-Agent": "jasonewillis@gmail.com",
                "Authorization-Key": USAJOBS_API_KEY
            }
            
            try:
                response = requests.get(
                    "https://data.usajobs.gov/api/Search",
                    headers=headers,
                    params={"ResultsPerPage": 1}
                )
                
                if response.status_code == 200:
                    st.success("✅ API Connection Successful!")
                    api_status = True
                else:
                    st.error(f"❌ API Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection Error: {str(e)}")
        
        return api_status

# --- Fetching Jobs from USAJOBS API ---
@st.cache_data(ttl=API_CONFIG.get('cache_ttl', 3600))
def fetch_usajobs_jobs(keyword="police", location="Las Vegas, NV"):
    """
    Fetch jobs from USAJOBS API with enhanced search capabilities and debugging.
    Uses cached configuration and implements retry logic.
    """
    # Debug: Show API configuration
    st.write("🔧 API Configuration:")
    st.write("- API Key:", "✅ Present" if USAJOBS_API_KEY else "❌ Missing")
    
    headers = {
        "Host": API_CONFIG['api']['host'],
        "User-Agent": "jasonewillis@gmail.com",
        "Authorization-Key": USAJOBS_API_KEY
    }
    
    # Use tech keywords from configuration
    tech_keywords = [f'"{kw}"' for kw in UI_CONFIG['tech_search_terms']]
    
    # Properly handle comma-separated keywords
    keywords_list = [k.strip() for k in keyword.split(',') if k.strip()]
    search_parts = [f'"{k}"' for k in keywords_list]
    
    # For tech-related searches, add specialized keywords
    if any(tech_term in keyword.lower() for tech_term in ["python", "sql", "developer", "software", "computer", "it", "data"]):
        tech_query = " OR ".join(tech_keywords)
        if search_parts:
            search_query = f"({' OR '.join(search_parts)}) OR ({tech_query})"
        else:
            search_query = tech_query
    else:
        search_query = " OR ".join(search_parts)
    
    st.write("🔍 Search Configuration:")
    st.write(f"- Base Keywords: {keyword}")
    st.write(f"- Full Query: {search_query}")
    
    # Determine appropriate job categories based on keywords
    job_categories = []
    keyword_lower = keyword.lower()
    
    # Get mappings from configuration
    for field, info in JOB_CATEGORIES.get('education_job_mapping', {}).items():
        if any(kw.lower() in keyword_lower for kw in info.get('keywords', [])):
            # Add specific job series based on field
            if field == 'data_analytics':
                job_categories.extend(['1530', '1550'])  # Statistics and Computer Science
            elif field == 'computer_science':
                job_categories.append('2210')  # IT Management
            elif field == 'information_technology':
                job_categories.extend(['2210', '0391'])  # IT Management and Telecommunications
    
    # Default to IT Management if no specific categories matched
    if not job_categories:
        job_categories = ['2210']

    # Enhanced search parameters
    # Start with default parameters from config
    params = API_CONFIG['api']['default_params'].copy()
    
    # Add request-specific parameters
    params.update({
        "Keyword": search_query,
        "LocationName": location,
        "JobCategoryCode": ",".join(job_categories),
    })
    
    try:
        # Enhanced error handling with retries
        max_retries = 3
        retry_delay = 1  # seconds
        response = None
        
        for attempt in range(max_retries):
            try:
                st.write(f"🔄 API Request Attempt {attempt + 1}/{max_retries}")
                
                response = requests.get(
                    "https://data.usajobs.gov/api/Search", 
                    headers=headers, 
                    params=params,
                    timeout=15  # Increased timeout
                )
                
                # Show detailed response information
                st.write("📊 Response Information:")
                st.write(f"- Status: {response.status_code}")
                st.write(f"- Content Type: {response.headers.get('Content-Type', 'unknown')}")
                st.write(f"- Response Time: {response.elapsed.total_seconds():.2f}s")
                
                if response.status_code == 200:
                    break
                elif response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        wait_time = min(retry_delay * (2 ** attempt), 8)  # Exponential backoff
                        st.warning(f"Rate limit reached. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                st.error(f"API Error {response.status_code}: {response.text}")
                return None
                
            except requests.Timeout:
                if attempt < max_retries - 1:
                    st.warning("Request timed out. Retrying...")
                    continue
                st.error("Maximum retries reached after timeouts.")
                return None
            except requests.ConnectionError:
                st.error("Connection error. Please check your internet connection.")
                return None
            
        if not response or response.status_code != 200:
            st.error("Failed to get a successful response after multiple attempts.")
            return None
            
        # Process response data with enhanced error handling
        try:
            data = response.json()
            
            # Validate response structure
            search_result = data.get("SearchResult", {})
            if not search_result:
                st.error("Invalid API response structure: missing SearchResult")
                return None

            result_count = search_result.get("SearchResultCount", 0)
            items = search_result.get("SearchResultItems", [])
            
            # Log response metrics
            st.write("📝 Response Summary:")
            st.write(f"- Total Results: {result_count}")
            st.write(f"- Results in this page: {len(items)}")
            
            # Show detailed job information with enhanced formatting
            if items:
                st.write("📋 Jobs Found:")
                for item in items[:UI_CONFIG.get('max_preview_jobs', 5)]:
                    desc = item.get("MatchedObjectDescriptor", {})
                    position = desc.get("PositionTitle", "No Title")
                    org = desc.get("OrganizationName", "Unknown Organization")
                    location = desc.get("PositionLocationDisplay", "Unknown Location")
                    pay = desc.get("PositionRemuneration", [{}])[0]
                    grade = desc.get("JobGrade", [{}])[0].get("Code", "Unknown")
                    
                    # Format salary range
                    min_salary = "${:,.2f}".format(float(pay.get('MinimumRange', 0)))
                    max_salary = "${:,.2f}".format(float(pay.get('MaximumRange', 0)))
                    
                    st.write(f"- 💼 {position} (Grade: {grade})")
                    st.write(f"  🏢 Organization: {org}")
                    st.write(f"  📍 Location: {location}")
                    st.write(f"  💰 Salary Range: {min_salary} - {max_salary}")
                    
                    # Show required education if available
                    qualification_summary = desc.get("QualificationSummary", "")
                    if qualification_summary:
                        with st.expander("📚 Qualification Requirements"):
                            st.write(qualification_summary)
            
            # Store raw response in session state for debugging
            if st.session_state.get('debug_mode', False):
                with st.expander("🔍 View Full API Response"):
                    st.json(data)
                    
            return data
            
        except ValueError as e:
            st.error(f"Failed to parse API response: {str(e)}")
            if st.session_state.get('debug_mode', False):
                st.error(f"Raw response: {response.text}")
            return None
        except Exception as e:
            st.error(f"Unexpected error processing response: {str(e)}")
            return None

    except Exception as e:
        st.error(f"Unexpected error during API request: {str(e)}")
        return None
    



# --- Static sample job listings with coordinates ---
static_job_categories = {
    "medical": [
        {
            "PositionTitle": "Registered Nurse",
            "OrganizationName": "Department of Veterans Affairs",
            "LocationName": "Las Vegas, NV",
            "SalaryRange": "$68,000 - $89,000",
            "ClosingDate": "2025-06-15",
            "VeteranPreferred": True,
            "JobCoordinates": (36.1699, -115.1398),
            "Keywords": ["RN", "Nurse", "BSN", "Nursing", "Healthcare"]
        },
        {
            "PositionTitle": "Clinical Nurse",
            "OrganizationName": "Department of Defense",
            "LocationName": "Fort Hood, TX",
            "SalaryRange": "$72,000 - $93,000",
            "ClosingDate": "2025-06-20",
            "VeteranPreferred": True,
            "JobCoordinates": (31.1346, -97.7790),
            "Keywords": ["RN", "Nurse", "BSN", "Nursing", "Clinical"]
        },
        {
            "PositionTitle": "Nurse Practitioner",
            "OrganizationName": "Department of Health and Human Services",
            "LocationName": "Washington, DC",
            "SalaryRange": "$85,000 - $110,000",
            "ClosingDate": "2025-06-25",
            "VeteranPreferred": True,
            "JobCoordinates": (38.8951, -77.0364),
            "Keywords": ["RN", "Nurse", "BSN", "Nursing", "NP"]
        }
    ],
    "tech": [
        {
            "PositionTitle": "Data Scientist",
            "OrganizationName": "Department of Energy",
            "LocationName": "Las Vegas, NV",
            "SalaryRange": "$85,000 - $140,000",
            "ClosingDate": "2025-06-30",
            "VeteranPreferred": True,
            "JobCoordinates": (36.1699, -115.1398),
            "Keywords": ["Python", "SQL", "Data Science", "Machine Learning", "Analytics"]
        },
        {
            "PositionTitle": "Software Engineer",
            "OrganizationName": "Department of Defense",
            "LocationName": "Las Vegas, NV",
            "SalaryRange": "$80,000 - $130,000",
            "ClosingDate": "2025-07-01",
            "VeteranPreferred": True,
            "JobCoordinates": (36.1699, -115.1398),
            "Keywords": ["Python", "SQL", "Software Engineering", "Backend", "DevOps"]
        },
        {
            "PositionTitle": "IT Specialist (Data Management)",
            "OrganizationName": "Department of Homeland Security",
            "LocationName": "Washington, DC",
            "SalaryRange": "$75,000 - $115,000",
            "ClosingDate": "2025-06-28",
            "VeteranPreferred": True,
            "JobCoordinates": (38.8951, -77.0364),
            "Keywords": ["Database", "SQL", "Python", "Data Management", "ETL"]
        }
    ]
}

# Get dynamic location if available from the form
location = st.session_state.get("user_location") or "Las Vegas, NV"

if st.sidebar.button("🔍 Test USAJobs API"):
    st.subheader("🧪 API Test Results")
    
    # Test 1: Check API Key
    st.write("1️⃣ Checking API Key...")
    if not USAJOBS_API_KEY:
        st.error("❌ API Key missing! Check your .env file")
    else:
        st.success("✅ API Key found")
        
    # Test 2: API Connection
    st.write("2️⃣ Testing API Connection...")
    data = fetch_usajobs_jobs("police", location)
    
    if data:
        st.success("✅ Successfully connected to USAJobs API")
        
        # Test 3: Parse Response
        st.write("3️⃣ Analyzing Response...")
        results = data.get("SearchResult", {}).get("SearchResultItems", [])
        
        st.json(data)  # Show full response for debugging
        
        if results:
            st.success(f"✅ Found {len(results)} jobs")
            # Display jobs as before
            for job in results:
                desc = job.get("MatchedObjectDescriptor", {})
                title = desc.get("PositionTitle", "No Title")
                org = desc.get("OrganizationName", "Unknown Org")
                loc = desc.get("PositionLocationDisplay", "Unknown Location")
                pay = desc.get("PositionRemuneration", [{}])[0]
                pay_range = f"${pay.get('MinimumRange', '?')} - ${pay.get('MaximumRange', '?')}"
                st.markdown(f"**{title}** at _{org}_")
                st.caption(f"{loc} | {pay_range}")
                st.markdown("---")
        else:
            st.warning("⚠️ No jobs found in response")
    else:
        st.error("❌ Failed to connect to API")



# --- Helper Functions ---
def get_coordinates(address, max_retries=3, timeout=5):
    """Get coordinates for an address with retry logic and caching."""
    geolocator = Nominatim(
        user_agent="fed-career-map",
        timeout=timeout
    )
    
    # Try to get cached coordinates first
    coords = cached_get_coordinates(address, geolocator)
    if coords[0] is not None:
        return coords
            
    # If not in cache, try with retries
    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
            return (None, None)
            
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            if attempt == max_retries - 1:
                st.error(f"Geocoding service unavailable: {str(e)}")
                return (None, None)
            st.warning(f"Attempt {attempt + 1} failed, retrying in 2 seconds...")
            time.sleep(2)
            
        except Exception as e:
            st.error(f"Unexpected error during geocoding: {str(e)}")
            return (None, None)

def calculate_distance(user_coords, job_coords):
    return geodesic(user_coords, job_coords).miles

def filter_jobs(jobs, user_coords, max_distance, user_skills=None, user_education=None):
    """Filter jobs based on location, skills, and education."""
    results = []
    
    # Debug: Show incoming data
    st.write("🔍 Debug - Filtering Process:")
    st.write(f"- Number of jobs to filter: {len(jobs)}")
    st.write(f"- User coordinates: {user_coords}")
    st.write(f"- Max distance: {max_distance}")
    st.write(f"- User skills: {user_skills}")
    st.write(f"- User education: {user_education}")
    
    # Enhanced education-job mapping with more tech roles
    education_job_mapping = {
        "data analytics": [
            "data", "analyst", "analytics", "statistics", "data science",
            "data engineering", "business intelligence", "quantitative",
            "machine learning", "forecasting", "modeling", "python", "sql"
        ],
        "computer science": [
            "software", "developer", "engineer", "programmer", "analyst",
            "it", "information technology", "systems", "data", "database",
            "computer", "tech", "application", "devops", "cloud", "security"
        ],
        "information technology": [
            "it", "information technology", "systems", "network", "support",
            "security", "administrator", "cloud", "infrastructure"
        ],
        "data science": [
            "data", "analyst", "scientist", "analytics", "machine learning",
            "statistics", "research", "python", "sql", "database"
        ],
        "software engineering": [
            "software", "developer", "engineer", "programmer", "web",
            "full stack", "backend", "frontend", "mobile", "devops"
        ],
        "cybersecurity": [
            "security", "cyber", "information assurance", "network",
            "analyst", "engineer", "administrator", "compliance"
        ],
        # Keep existing mappings
        "nursing": ["nurse", "rn", "lpn", "clinical", "healthcare"],
        "medical": ["health", "medical", "clinical", "healthcare"],
        "criminal justice": ["police", "security", "law enforcement", "criminal"],
        "business": ["manager", "analyst", "administrator", "coordinator"],
        "engineering": ["engineer", "technical", "systems", "mechanical", "electrical"]
    }
    
    for job in jobs:
        # Initialize match flags
        distance_match = True
        skills_match = True
        education_match = True

        # Distance filter
        if not show_all_locations and user_coords and job.get("JobCoordinates"):
            distance = calculate_distance(user_coords, job["JobCoordinates"])
            distance_match = distance <= max_distance
            if distance_match:
                job["DistanceFromUser"] = round(distance, 2)
        
        # Enhanced skills matching with better tech skills handling
        if user_skills:
            user_skills_lower = [skill.lower().strip() for skill in user_skills]
            
            # Get all searchable text
            searchable_text = job.get("PositionTitle", "").lower()
            if job.get("Keywords"):  # For static data
                searchable_text += " " + " ".join(kw.lower() for kw in job["Keywords"])
            if job.get("QualificationSummary"):  # For API data
                searchable_text += " " + job["QualificationSummary"].lower()
            
            # Common tech skill variations
            tech_skill_variations = {
                "python": ["python programming", "python developer", "python script"],
                "sql": ["database", "sql server", "mysql", "postgresql"],
                "javascript": ["js", "node.js", "nodejs", "react", "angular"],
                "java": ["java developer", "java programming", "j2ee"],
                "c#": ["c sharp", "dotnet", ".net", "asp.net"],
                "cloud": ["aws", "azure", "gcp", "cloud computing"],
                "devops": ["ci/cd", "jenkins", "docker", "kubernetes"],
                "data science": ["machine learning", "ai", "deep learning", "analytics"]
            }
            
                    # Default to no match until we find one
            skills_match = False
            
            # Check each user skill against searchable text
            required_skills_found = 0
            for skill in user_skills_lower:
                skill_found = False
                
                # Check exact match first
                if skill in searchable_text:
                    skill_found = True
                # Check variations without spaces/hyphens
                elif (skill.replace(" ", "") in searchable_text or 
                    skill.replace("-", "") in searchable_text):
                    skill_found = True
                # Check tech variations if applicable
                else:
                    for tech_skill, variations in tech_skill_variations.items():
                        if tech_skill in skill.lower():
                            if any(var in searchable_text for var in variations):
                                skill_found = True
                                break
                
                if skill_found:
                    required_skills_found += 1
            
            # Require all skills to match for technical positions
            if any(tech_term in " ".join(user_skills_lower) for tech_term in ["python", "sql", "developer", "software"]):
                skills_match = required_skills_found == len(user_skills_lower)
            else:
                # For non-technical positions, require at least one skill match
                skills_match = required_skills_found > 0
            
            # Debug output for skills matching
            st.write(f"\nSkills matching for {job.get('PositionTitle')}:")
            st.write(f"- User skills: {user_skills_lower}")
            st.write(f"- Searchable text excerpt: {searchable_text[:200]}...")
            st.write(f"- Match found: {skills_match}")
        
        # Enhanced education matching
        if user_education:
            education_lower = user_education.lower()
            searchable_text = job.get("PositionTitle", "").lower()
            if job.get("QualificationSummary"):
                searchable_text += " " + job["QualificationSummary"].lower()
            
                    # First, detect the degree level and field
            degree_level = ""
            if "phd" in education_lower or "doctorate" in education_lower:
                degree_level = "phd"
            elif "master" in education_lower or "ms" in education_lower or "ma" in education_lower:
                degree_level = "master"
            elif "bachelor" in education_lower or "bs" in education_lower or "ba" in education_lower:
                degree_level = "bachelor"
            
            # Extract the field of study
            field_found = False
            for edu_field in education_job_mapping.keys():
                if edu_field in education_lower:
                    field_found = True
                    # Check if job matches the field
                    education_match = any(kw in searchable_text for kw in education_job_mapping[edu_field])
                    if education_match:
                        break
            
            # If no specific field match found, check general degree requirements
            if not field_found:
                education_match = any(edu in searchable_text 
                                   for edu in ["degree", degree_level, "bachelor", "master", "phd", 
                                             "diploma", education_lower])
            
            # Debug output for education matching
            st.write(f"\nEducation matching for {job.get('PositionTitle')}:")
            st.write(f"- Education: {education_lower}")
            st.write(f"- Searchable text excerpt: {searchable_text[:200]}...")
            st.write(f"- Match found: {education_match}")
        
        # Only include job if all applicable filters match
        if all([distance_match, skills_match, education_match]):
            results.append(job)
    
    # Debug: Show final results
    st.write(f"\n✅ Filtering complete - Found {len(results)} matching jobs")
    return pd.DataFrame(results)

# --- Streamlit UI ---
st.title("🇺🇸 Federal Job Roadmap")

# Add toggle for live/sample data
use_live_data = st.sidebar.toggle("Use Live USAJOBS Data", value=False)
api_ready = verify_usajobs_connection() if use_live_data else False

if use_live_data and not api_ready:
    st.warning("⚠️ Live job search is not available. Using sample data instead.")
    use_live_data = False

with st.form("user_profile_form"):
    form_defaults = UI_CONFIG['form_defaults']
    name = st.text_input("Full Name", form_defaults['name'])
    email = st.text_input("Email", form_defaults['email'])
    address = st.text_input("Street Address", form_defaults['address'])
    veteran_status = st.selectbox("Veteran Status", UI_CONFIG['veteran_status_options'])
    skills = st.text_input("Key Skills (comma-separated)", form_defaults['skills'])
    degree = st.text_input("Degree", form_defaults['degree'])
    max_distance = st.slider("Max Distance (miles)", 10, 500, form_defaults['max_distance'])
    show_all_locations = st.checkbox("Show all locations (ignore distance filter)", False)
    submit = st.form_submit_button("Find Jobs")

if submit:
    with st.spinner("Processing your request..."):
        user = {
            "name": name,
            "email": email,
            "address": address,
            "veteran_status": veteran_status,
            "skills": [s.strip() for s in skills.split(",")],
            "degree": degree
        }
        
        # Get coordinates
        coords = get_coordinates(user["address"])
        if not coords[0]:
            st.error("Could not geocode your address. Please check and try again.")
        else:
            # Try live data first if enabled
            if use_live_data:
                st.write("🌐 Using live USAJOBS data...")
                st.write(f"📍 Location: {address}")
                
                # Combine skills into search query
                keywords = " OR ".join(f'"{skill.strip()}"' for skill in user["skills"])
                if "computer science" in user["degree"].lower():
                    keywords += ' OR "python" OR "sql" OR "developer" OR "software" OR "programmer" OR "IT"'
                
                st.write(f"🔍 Search keywords: {keywords}")
                data = fetch_usajobs_jobs(
                    keyword=keywords,
                    location=address
                )
                
                if data and data.get("SearchResult", {}).get("SearchResultItems"):
                    # Process live results
                    st.success("✅ Found live job matches!")
                    
                    # Show raw results for verification
                    with st.expander("🔍 View Raw API Response"):
                        st.json(data)
                    
                    # Process results
                    results = data.get("SearchResult", {}).get("SearchResultItems", [])
                    matches = []
                    
                    for item in results:
                        desc = item.get("MatchedObjectDescriptor", {})
                        pay = desc.get("PositionRemuneration", [{}])[0]
                        location_display = desc.get("PositionLocationDisplay")
                        position_title = desc.get("PositionTitle", "")
                        
                        # Get all searchable text
                        qualification_summary = desc.get("QualificationSummary", "").lower()
                        position_title_lower = position_title.lower()
                        job_text = f"{qualification_summary} {position_title_lower}"
                        
                        # Initialize match flags
                        distance_match = True
                        skills_match = True
                        education_match = True
                        
                        # Try to get coordinates for the job location
                        job_coords = get_coordinates(location_display)
                        
                        # Check distance if coordinates are available
                        if coords[0] and job_coords[0] and not show_all_locations:
                            distance = calculate_distance(coords, job_coords)
                            distance_match = distance <= max_distance
                        
                        # Skills matching
                        if user["skills"]:
                            user_skills_lower = [skill.lower().strip() for skill in user["skills"]]
                            # Get all searchable text for the job
                            job_text = f"{position_title_lower} {qualification_summary}"
                            if desc.get("UserArea", {}).get("Requirements", {}).get("RequiredSkills"):
                                job_text += " " + " ".join(desc["UserArea"]["Requirements"]["RequiredSkills"])
                            
                            # Try different variations of skill names
                            skills_match = any(
                                any(variation in job_text for variation in [
                                    skill,  # exact match
                                    skill.replace(" ", ""),  # no spaces
                                    skill.replace("-", ""),  # no hyphens
                                    skill.replace("_", ""),  # no underscores
                                    # Common variations
                                    "python" if skill == "python programming" else "",
                                    "sql database" if skill == "sql" else "",
                                    "programming" if skill == "python" else ""
                                ] if variation)  # only check non-empty variations
                                for skill in user_skills_lower
                            )
                            
                            st.write(f"Skills matching for {position_title}:")
                            st.write(f"- User skills: {user_skills_lower}")
                            st.write(f"- Job text excerpt: {job_text[:200]}...")
                            st.write(f"- Match found: {skills_match}")
                        
                        # Education matching
                        if user["degree"]:
                            education_lower = user["degree"].lower()
                            education_match = (education_lower in qualification_summary or
                                            any(edu in qualification_summary 
                                                for edu in ["degree", "diploma", education_lower]))
                        
                        # Only process if all conditions match
                        if all([distance_match, skills_match, education_match]):
                            job = {
                                "PositionTitle": position_title,
                                "OrganizationName": desc.get("OrganizationName"),
                                "LocationName": location_display,
                                "SalaryRange": f"${pay.get('MinimumRange', '?')} - ${pay.get('MaximumRange', '?')}",
                                "ClosingDate": desc.get("ApplicationCloseDate", "Not specified"),
                                "VeteranPreferred": True if "Veterans" in desc.get("UserArea", {}).get("VeteransPreference", "") else False
                            }
                            
                            # Add distance if available
                            if coords[0] and job_coords[0]:
                                job["DistanceFromUser"] = round(calculate_distance(coords, job_coords), 2)
                                
                            matches.append(job)
                    
                    matches_df = pd.DataFrame(matches)
                else:
                    st.warning("No live jobs found. Falling back to sample data...")
                    # Choose appropriate sample data based on user skills and education
                    sample_data = []
                    if any(tech_term in " ".join(user["skills"]).lower() for tech_term in ["python", "sql", "data"]) or \
                       any(tech_term in user["degree"].lower() for tech_term in ["computer", "data", "information technology"]):
                        sample_data = static_job_categories["tech"]
                    else:
                        sample_data = static_job_categories["medical"]
                        
                    matches_df = filter_jobs(
                        sample_data,
                        coords,
                        max_distance,
                        user_skills=user["skills"],
                        user_education=user["degree"]
                    )
            else:
                # Use sample data based on user profile
                sample_data = []
                if any(tech_term in " ".join(user["skills"]).lower() for tech_term in ["python", "sql", "data"]) or \
                   any(tech_term in user["degree"].lower() for tech_term in ["computer", "data", "information technology"]):
                    sample_data = static_job_categories["tech"]
                else:
                    sample_data = static_job_categories["medical"]
                    
                matches_df = filter_jobs(
                    sample_data,
                    coords,
                    max_distance,
                    user_skills=user["skills"],
                    user_education=user["degree"]
                )
            
            # Display results
            st.success(f"Found {len(matches_df)} matching jobs!")
            st.dataframe(matches_df)
            
            # PDF functionality temporarily disabled
            # pdf_filename = "job_report.pdf"
            # generate_pdf_report(user, matches_df, pdf_filename)
            
            # with open(pdf_filename, "rb") as f:
            #     pdf_bytes = f.read()
            #     st.download_button(
            #         label="📄 Download Job Report (PDF)",
            #         data=pdf_bytes,
            #         file_name=pdf_filename,
            #         mime="application/pdf"
            #     )

            st.session_state["user_location"] = address

