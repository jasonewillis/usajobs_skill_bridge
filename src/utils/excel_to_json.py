import pandas as pd
import json
import os
import sys
from datetime import datetime

def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

try:
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output paths
    excel_file = os.path.join(current_dir, 'ComparisonToolData.xlsx')
    output_file = os.path.join(current_dir, 'ComparisonToolData.json')
    
    print(f"Reading Excel file from: {excel_file}")
    
    # Read all sheets into a dictionary
    excel_data = pd.read_excel(excel_file, sheet_name=None)
    
    # Convert each sheet to JSON
    json_data = {}
    for sheet_name, df in excel_data.items():
        print(f"Processing sheet: {sheet_name}")
        # Convert datetime columns to string
        for col in df.select_dtypes(include=['datetime64[ns]']).columns:
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        # Convert DataFrame to dict, handling NaN values
        sheet_data = df.fillna('').to_dict(orient='records')
        json_data[sheet_name] = sheet_data
    
    # Write to JSON file
    print(f"Writing JSON to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False, default=datetime_handler)
    
    print(f"Successfully converted {excel_file} to {output_file}")

except Exception as e:
    print(f"Error: {str(e)}", file=sys.stderr)
    sys.exit(1)
