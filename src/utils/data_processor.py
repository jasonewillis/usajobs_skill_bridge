"""Data processing utilities for handling large datasets."""
import json
import os
import pandas as pd
from typing import Dict, List, Any
import streamlit as st

def process_large_data(input_file: str, output_dir: str, chunk_size: int = 1000) -> List[str]:
    """Process large data files into smaller chunks."""
    if input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    elif input_file.endswith('.json'):
        with open(input_file, 'r') as f:
            data = json.load(f)
            df = pd.DataFrame(data)
    else:
        raise ValueError(f"Unsupported file format: {input_file}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Split data into chunks
    chunk_files = []
    for i, chunk in enumerate(range(0, len(df), chunk_size)):
        chunk_data = df[chunk:chunk + chunk_size]
        output_file = os.path.join(output_dir, f'data_chunk_{i}.json')
        chunk_data.to_json(output_file, orient='records')
        chunk_files.append(output_file)
        
    return chunk_files

def merge_processed_data(chunk_files: List[str], output_file: str) -> None:
    """Merge processed data chunks back into a single file."""
    merged_data = []
    for file in chunk_files:
        with open(file, 'r') as f:
            chunk_data = json.load(f)
            merged_data.extend(chunk_data)

    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=2)

def create_data_summary(input_file: str, output_file: str) -> None:
    """Create a summary of the data for version control."""
    if input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    elif input_file.endswith('.json'):
        with open(input_file, 'r') as f:
            data = json.load(f)
            df = pd.DataFrame(data)

    summary = {
        'row_count': len(df),
        'columns': list(df.columns),
        'sample_size': min(5, len(df)),
        'sample_data': df.head(5).to_dict(orient='records')
    }

    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == '__main__':
    # Process ComparisonToolData
    data_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    input_file = os.path.join(data_dir, 'data', 'raw', 'ComparisonToolData.xlsx')
    output_dir = os.path.join(data_dir, 'data', 'processed', 'chunks')
    
    # Create data chunks
    chunk_files = process_large_data(input_file, output_dir)
    
    # Create data summary
    summary_file = os.path.join(data_dir, 'data', 'processed', 'data_summary.json')
    create_data_summary(input_file, summary_file)
