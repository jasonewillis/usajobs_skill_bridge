import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from dotenv import load_dotenv
import os
import requests
import time
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from ..utils.config import (
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
def fetch_usajobs_jobs(keyword=None, location=None, pay_grade=None):
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

    params = API_CONFIG['api']['default_params'].copy()
    
    if keyword:
        params["Keyword"] = keyword
    if location:
        params["LocationName"] = location
    if pay_grade:
        params["PayGradeLow"] = pay_grade.replace("GS-", "")

    try:
        response = requests.get(
            API_CONFIG['api']['base_url'],
            headers=headers,
            params=params,
            timeout=API_CONFIG.get('request_timeout', 15)
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching jobs: {str(e)}")
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
@st.cache_data(ttl=3600)
def get_coordinates(address, _geolocator=None):
    """Get coordinates for an address using a cached geocoder."""
    if _geolocator is None:
        _geolocator = Nominatim(user_agent="federal_job_roadmap")
    
    try:
        location = _geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        return None
    except (GeocoderTimedOut, GeocoderUnavailable):
        st.error(f"Error geocoding address: {address}")
        return None

def calculate_distance(user_coords, job_coords):
    return geodesic(user_coords, job_coords).miles

def filter_jobs(jobs, user_coords, max_distance, user_skills=None, user_education=None):
    """Filter jobs based on distance and optional skills/education criteria."""
    if not jobs:
        return []
    
    filtered_jobs = []
    
    for job in jobs:
        job_data = job.get("MatchedObjectDescriptor", {})
        
        # Extract job location
        job_locations = job_data.get("PositionLocation", [])
        if not job_locations:
            continue
        
        # Calculate distance for each job location
        for loc in job_locations:
            loc_name = loc.get("LocationName")
            if not loc_name:
                continue
            
            job_coords = get_coordinates(loc_name)
            if not job_coords:
                continue
            
            distance = calculate_distance(user_coords, job_coords)
            
            # Check if within max distance
            if distance <= max_distance:
                # Add distance to job data
                job["calculatedDistance"] = distance
                
                # Filter by skills if provided
                if user_skills:
                    job_description = job_data.get("QualificationSummary", "").lower()
                    user_skills_list = [s.strip().lower() for s in user_skills.split(",")]
                    if not any(skill in job_description for skill in user_skills_list):
                        continue
                
                # Filter by education if provided
                if user_education:
                    job_quals = job_data.get("QualificationSummary", "").lower()
                    if user_education.lower() not in job_quals:
                        continue
                
                # Add to filtered list and break inner loop
                filtered_jobs.append(job)
                break
    
    # Sort by distance
    filtered_jobs.sort(key=lambda x: x.get("calculatedDistance", float("inf")))
    return filtered_jobs

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
        if not coords:
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
                        if coords and job_coords and not show_all_locations:
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
                            if coords and job_coords:
                                job["DistanceFromUser"] = round(calculate_distance(coords, job_coords), 2)
                                
                            matches.append(job)
                    
                    matches_df = pd.DataFrame(matches)
                else:
                    st.warning("No live jobs found. Falling back to sample data...")
                    # Choose appropriate sample data based on user skills and education
                    if any(tech_term in " ".join(user["skills"]).lower() for tech_term in ["python", "sql", "data"]) or \
                       any(tech_term in user["degree"].lower() for tech_term in ["computer", "data", "information technology"]):
                        sample_data = static_job_categories["tech"]
                    else:
                        sample_data = static_job_categories["medical"]
                        
                    matches_df = pd.DataFrame(filter_jobs(
                        sample_data,
                        coords,
                        max_distance,
                        user_skills=", ".join(user["skills"]),
                        user_education=user["degree"]
                    ))
            else:
                # Use sample data based on user profile
                if any(tech_term in " ".join(user["skills"]).lower() for tech_term in ["python", "sql", "data"]) or \
                   any(tech_term in user["degree"].lower() for tech_term in ["computer", "data", "information technology"]):
                    sample_data = static_job_categories["tech"]
                else:
                    sample_data = static_job_categories["medical"]
                    
                matches_df = pd.DataFrame(sample_data)

            # Display results
            st.success(f"Found {len(matches_df)} matching jobs!")
            st.dataframe(matches_df)

            st.session_state["user_location"] = address

