# Federal Job Roadmap

A Streamlit application that helps match skills to federal jobs using the USAJOBS API.

## Project Structure

```
project_root/
├── src/                    # Source code
│   ├── api/               # API integration code
│   ├── models/            # Data models
│   ├── utils/            # Utility functions
│   └── ui/               # UI-related code
├── tests/                 # Test files
├── config/               # Configuration files
├── docs/                # Documentation
├── data/                # Data files
└── samples/             # Sample files
```

## Setup

1. Create a virtual environment:
```bash
python -m venv usajobs_env
source usajobs_env/bin/activate  # On Windows: usajobs_env\Scripts\activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your USAJOBS API key
```

## Data Processing

The project uses large datasets that are processed into smaller chunks for efficiency:

1. Raw data is stored in `data/raw/`
2. Processed data chunks are in `data/processed/chunks/`
3. Data summaries are in `data/processed/data_summary.json`

To process large data files:

```bash
python -m src.utils.data_processor
```

## Running the Application

```bash
streamlit run src/ui/streamlit_federal_job_app.py
```

## Development

- Code style follows PEP 8
- Configuration is managed through JSON files in `config/`
- Large files are processed into chunks for better performance
- Use Git LFS for files under 100MB, larger files are processed locally

## Documentation

See the `docs/` directory for:
- API guides
- Capability documentation
- Project context

## Testing

The project includes both unit tests and integration tests. Tests are written using pytest.

### Running Tests

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Run all tests:
```bash
python -m pytest
```

3. Run with coverage report:
```bash
python -m pytest --cov=src tests/
```

4. Run specific test categories:
```bash
# Run only unit tests
python -m pytest tests/unit/

# Run only integration tests
python -m pytest tests/integration/
```

### Test Structure

- `tests/unit/`: Unit tests for individual components
  - `test_data_processor.py`: Tests for data processing utilities
  - `test_config.py`: Tests for configuration management
  
- `tests/integration/`: Integration tests
  - `test_usajobs_api.py`: Tests for USA Jobs API integration
  - `test_streamlit_ui.py`: Tests for UI components
  - `usajobs_api_test_notebook.ipynb`: Interactive API testing notebook

Note: Some integration tests require a valid USAJOBS_API_KEY in your .env file.
