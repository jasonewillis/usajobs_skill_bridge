#!/usr/bin/env python3
"""Setup script for the Federal Job Roadmap project."""
from setuptools import setup, find_packages
import os
import sys
import subprocess

setup(
    name="federal_job_roadmap",
    version="0.1.0",
    packages=find_packages(),
    package_data={
        'src': ['config/*.json'],
    },
    include_package_data=True,
    install_requires=[
        'streamlit>=1.0.0',
        'geopy>=2.3.0',
        'pandas>=1.3.0',
        'requests>=2.26.0',
        'python-dotenv>=0.19.0',
        'numpy>=1.21.0',
        'openpyxl>=3.0.7',
    ],
    python_requires='>=3.9,<3.14',
    entry_points={
        'console_scripts': [
            'federal_job_roadmap=src.usajobs_skill_bridge.streamlit_federal_job_app:main',
        ],
    },
)

def setup_project():
    """Set up the project structure and process data."""
    # Create necessary directories
    directories = [
        'src/api',
        'src/models',
        'tests/unit',
        'data/raw',
        'data/processed/chunks',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, '.gitkeep'), 'w') as f:
            pass

    # Process data if it exists
    raw_data = os.path.join('data', 'raw', 'ComparisonToolData.xlsx')
    if os.path.exists(raw_data):
        print("Processing large data file...")
        chunks_dir = os.path.join('data', 'processed', 'chunks')
        chunk_files = process_large_data(raw_data, chunks_dir)
        print(f"Created {len(chunk_files)} data chunks")

        summary_file = os.path.join('data', 'processed', 'data_summary.json')
        create_data_summary(raw_data, summary_file)
        print("Created data summary")
    else:
        print("No raw data file found. Please add data to data/raw/ directory.")

    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write('USAJOBS_API_KEY=your_api_key_here\n')
        print("Created .env file - please add your USAJOBS API key")

    # Install requirements
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Installed requirements")
    except Exception as e:
        print(f"Error installing requirements: {str(e)}")

if __name__ == '__main__':
    setup_project()
