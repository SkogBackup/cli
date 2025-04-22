"""Tests for skogcli misc functionality."""

import pytest
import subprocess
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
from skogcli.misc import (
    get_user_scripts_dir,
    get_metadata_file,
    load_metadata,
    save_metadata,
    get_script_names,
    get_script_templates
)


def test_misc_help():
    """Test that running misc without args shows help."""
    # Run the command
    no_args_result = subprocess.run(
        ["uv", "run", "skogcli", "misc"],
        capture_output=True,
        text=True,
    )
    
    help_result = subprocess.run(
        ["uv", "run", "skogcli", "misc", "--help"],
        capture_output=True,
        text=True,
    )
    
    # Both commands should exit with the same status code
    assert no_args_result.returncode == help_result.returncode
    
    # Both commands should produce the same stdout
    assert no_args_result.stdout == help_result.stdout


class TestMiscFunctions:
    """Tests for misc module functions."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.original_home = os.environ.get("HOME")
        self.test_home = Path("/tmp/skogcli_misc_test_home")
        self.test_home.mkdir(parents=True, exist_ok=True)
        os.environ["HOME"] = str(self.test_home)
        
        # Create a test scripts directory
        self.test_scripts_dir = self.test_home / ".config" / "skogcli" / "scripts"
        self.test_scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a test script
        self.test_script = self.test_scripts_dir / "test_script.py"
        with open(self.test_script, "w") as f:
            f.write("#!/usr/bin/env python3\nprint('Hello from test script')\n")
        self.test_script.chmod(0o755)
        
        # Create test metadata
        self.test_metadata_file = self.test_home / ".config" / "skogcli" / "script_metadata.json"
        test_metadata = {
            str(self.test_script): {
                "description": "Test script description",
                "created": datetime.now().isoformat(),
                "run_count": 0
            }
        }
        with open(self.test_metadata_file, "w") as f:
            json.dump(test_metadata, f, indent=2)

    def teardown_method(self):
        """Clean up after each test."""
        if self.original_home:
            os.environ["HOME"] = self.original_home
        shutil.rmtree(self.test_home, ignore_errors=True)

    def test_get_user_scripts_dir(self):
        """Test get_user_scripts_dir returns the correct path."""
        scripts_dir = get_user_scripts_dir()
        expected_dir = self.test_home / ".config" / "skogcli" / "scripts"
        assert scripts_dir == expected_dir
        assert scripts_dir.exists()

    def test_get_metadata_file(self):
        """Test get_metadata_file returns the correct path."""
        metadata_file = get_metadata_file()
        expected_file = self.test_home / ".config" / "skogcli" / "script_metadata.json"
        assert metadata_file == expected_file
    
    def test_load_metadata(self):
        """Test load_metadata loads the metadata."""
        metadata = load_metadata()
        assert str(self.test_script) in metadata
        assert metadata[str(self.test_script)]["description"] == "Test script description"
    
    def test_save_metadata(self):
        """Test save_metadata saves the metadata."""
        new_metadata = {"test": "data"}
        save_metadata(new_metadata)
        
        # Read the file directly to verify
        with open(self.test_metadata_file, "r") as f:
            saved_data = json.load(f)
        
        assert saved_data == new_metadata
    
    def test_get_script_names(self):
        """Test get_script_names returns script names."""
        names = get_script_names()
        assert "test_script" in names
    
    def test_get_script_templates(self):
        """Test get_script_templates returns template names."""
        templates = get_script_templates()
        assert "basic" in templates
        assert "line_counter" in templates
        assert "data_processing" in templates


class TestMiscCommands:
    """Tests for misc module commands."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.original_home = os.environ.get("HOME")
        self.test_home = Path("/tmp/skogcli_misc_cmd_test_home")
        self.test_home.mkdir(parents=True, exist_ok=True)
        os.environ["HOME"] = str(self.test_home)

    def teardown_method(self):
        """Clean up after each test."""
        if self.original_home:
            os.environ["HOME"] = self.original_home
        shutil.rmtree(self.test_home, ignore_errors=True)
    
    def test_misc_list_no_scripts(self):
        """Test misc list when no scripts exist."""
        result = subprocess.run(
            ["uv", "run", "skogcli", "misc", "list"],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert "No custom scripts found" in result.stdout
    
    def test_misc_add_and_list(self):
        """Test adding a script and then listing it."""
        # Add a script
        add_result = subprocess.run(
            ["uv", "run", "skogcli", "misc", "add", "hello", "--type", "python", "--no-edit"],
            capture_output=True,
            text=True,
        )
        
        assert add_result.returncode == 0
        assert "Created user script" in add_result.stdout
        
        # List scripts
        list_result = subprocess.run(
            ["uv", "run", "skogcli", "misc", "list"],
            capture_output=True,
            text=True,
        )
        
        assert list_result.returncode == 0
        assert "hello" in list_result.stdout
        
        # Verify script exists
        scripts_dir = self.test_home / ".config" / "skogcli" / "scripts"
        script_path = scripts_dir / "hello.py"
        assert script_path.exists()
        
        # Verify script is executable
        assert os.access(script_path, os.X_OK)
    
    def test_misc_templates(self):
        """Test listing templates."""
        result = subprocess.run(
            ["uv", "run", "skogcli", "misc", "templates"],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        assert "Available script templates" in result.stdout
        assert "basic" in result.stdout
        assert "line_counter" in result.stdout