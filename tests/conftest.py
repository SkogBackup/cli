"""Pytest configuration and shared fixtures."""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, patch

# Add the src directory to the path so pytest can find the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer.testing


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Get the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def temp_config_dir(temp_dir: Path) -> Path:
    """Create a temporary config directory."""
    config_dir = temp_dir / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def temp_scripts_dir(temp_dir: Path) -> Path:
    """Create a temporary scripts directory."""
    scripts_dir = temp_dir / "scripts"
    scripts_dir.mkdir()
    return scripts_dir


@pytest.fixture
def cli_runner() -> typer.testing.CliRunner:
    """Get a CLI test runner."""
    return typer.testing.CliRunner()


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Mock configuration data."""
    return {
        "settings": {
            "meta": {
                "version": 1,
                "last_updated": 1234567890.0
            },
            "module": {
                "history": [],
                "max_history_items": 100
            },
            "script": {
                "user_scripts_dir": "/tmp/test_scripts",
                "templates_dir": "/tmp/test_templates",
                "metadata_dir": "/tmp/test_metadata"
            }
        },
        "credentials": {}
    }


@pytest.fixture
def mock_environment(temp_dir: Path):
    """Mock environment variables for testing."""
    env_vars = {
        "SKOGAI_CONFIG_DIR": str(temp_dir / "config"),
        "SKOGAI_SCRIPTS_DIR": str(temp_dir / "scripts"),
        "SKOGAI_TEMPLATES_DIR": str(temp_dir / "templates"),
        "EDITOR": "nano"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_script_content() -> str:
    """Sample Python script content for testing."""
    return '''#!/usr/bin/env python3
"""Sample test script."""

def main(args=None):
    """Main function for the script."""
    print("Hello from test script!")
    if args:
        print(f"Args: {args}")

if __name__ == "__main__":
    main()
'''


@pytest.fixture
def sample_shell_script() -> str:
    """Sample shell script content for testing."""
    return '''#!/bin/bash
# Sample shell script for testing

echo "Hello from shell script!"
if [ $# -gt 0 ]; then
    echo "Args: $@"
fi
'''


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        yield mock_run


@pytest.fixture
def isolated_config(temp_config_dir: Path, mock_config: Dict[str, Any]):
    """Provide isolated configuration for tests."""
    config_file = temp_config_dir / "config.json"
    
    # Create the config file with mock data
    import json
    with open(config_file, 'w') as f:
        json.dump(mock_config, f, indent=2)
    
    # Patch the config directory getter
    with patch('skogcli.settings.get_config_dir', return_value=temp_config_dir):
        yield config_file


@pytest.fixture
def mock_typer_confirm():
    """Mock typer.confirm to always return True."""
    with patch('typer.confirm', return_value=True) as mock_confirm:
        yield mock_confirm


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, json_data: Dict[str, Any], status_code: int = 200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = str(json_data)
    
    def json(self):
        return self.json_data


@pytest.fixture
def mock_http_requests():
    """Mock HTTP requests."""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        
        # Default successful responses
        mock_post.return_value = MockResponse({
            "choices": [{"message": {"content": "Generated code here"}}]
        })
        mock_get.return_value = MockResponse({"status": "ok"})
        
        yield {
            'post': mock_post,
            'get': mock_get
        }


# Pytest markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"  
    )
    config.addinivalue_line(
        "markers", "functional: mark test as functional test"
    )
    config.addinivalue_line(
        "markers", "benchmark: mark test as benchmark"
    )


# Test collection customization
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to tests in unit/ directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to tests in integration/ directory
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        # Add functional marker to tests in functional/ directory
        elif "functional" in str(item.fspath):
            item.add_marker(pytest.mark.functional)


@pytest.fixture
def benchmark_config():
    """Configuration for benchmark tests."""
    return {
        'min_rounds': 5,
        'max_time': 1.0,
        'disable_gc': True,
        'timer': 'time.perf_counter'
    }
