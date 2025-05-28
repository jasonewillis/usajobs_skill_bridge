"""Unit tests for data processing utilities."""
import os
import json
import pytest
import pandas as pd
from src.utils.data_processor import process_large_data, create_data_summary

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'id': range(1, 11),
        'title': [f'Job {i}' for i in range(1, 11)],
        'salary': [50000 + i*1000 for i in range(1, 11)]
    })

@pytest.fixture
def temp_dir(tmp_path):
    return str(tmp_path)

def test_process_large_data(sample_data, temp_dir):
    # Save sample data to temp Excel file
    input_file = os.path.join(temp_dir, 'test_data.xlsx')
    sample_data.to_excel(input_file, index=False)
    
    # Process data into chunks
    output_dir = os.path.join(temp_dir, 'chunks')
    os.makedirs(output_dir, exist_ok=True)
    chunk_files = process_large_data(input_file, output_dir, chunk_size=3)
    
    # Verify chunks were created
    assert len(chunk_files) == 4  # 10 rows with chunk_size=3 should create 4 chunks
    
    # Verify chunk contents
    chunk_data = []
    for file in chunk_files:
        with open(file, 'r') as f:
            chunk_data.extend(json.load(f))
            
    assert len(chunk_data) == len(sample_data)
    assert all(item['title'].startswith('Job ') for item in chunk_data)

def test_create_data_summary(sample_data, temp_dir):
    # Save sample data
    input_file = os.path.join(temp_dir, 'test_data.xlsx')
    sample_data.to_excel(input_file, index=False)
    
    # Create summary
    summary_file = os.path.join(temp_dir, 'summary.json')
    create_data_summary(input_file, summary_file)
    
    # Verify summary contents
    with open(summary_file, 'r') as f:
        summary = json.load(f)
        
    assert summary['row_count'] == len(sample_data)
    assert 'id' in summary['columns']
    assert 'title' in summary['columns']
    assert 'salary' in summary['columns']
    assert len(summary['sample_data']) == min(5, len(sample_data))
