"""Unit tests for pure functions in script module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from skogcli.script import (
    get_script_names, 
    get_script_types,
    get_script_templates,
    is_executable,
    list_available_templates
)


class TestGetScriptNames:
    """Test the get_script_names function."""

    @patch('skogcli.script.list_available_scripts')
    def test_should_return_script_names_without_extensions(self, mock_list):
        """Test that script names are returned without file extensions."""
        # Arrange
        mock_scripts = [
            Path("/path/script1.py"),
            Path("/path/script2.sh"),
            Path("/path/script3")
        ]
        mock_list.return_value = mock_scripts
        
        # Act
        result = get_script_names()
        
        # Assert
        expected = ["script1", "script2", "script3"]
        assert result == expected

    @patch('skogcli.script.list_available_scripts')
    def test_should_handle_empty_script_list(self, mock_list):
        """Test handling of empty script list."""
        # Arrange
        mock_list.return_value = []
        
        # Act
        result = get_script_names()
        
        # Assert
        assert result == []


class TestGetScriptTypes:
    """Test the get_script_types function."""

    def test_should_return_supported_script_types(self):
        """Test that supported script types are returned."""
        # Act
        result = get_script_types()
        
        # Assert
        assert "python" in result
        assert "shell" in result
        assert len(result) >= 2


class TestIsExecutable:
    """Test the is_executable function."""

    @patch('os.access')
    def test_should_return_true_for_executable_file(self, mock_access):
        """Test that executable files return True."""
        # Arrange
        mock_access.return_value = True
        test_path = Path("/path/to/script.py")
        
        # Act
        result = is_executable(test_path)
        
        # Assert
        assert result is True
        mock_access.assert_called_once()

    @patch('os.access')
    def test_should_return_false_for_non_executable_file(self, mock_access):
        """Test that non-executable files return False."""
        # Arrange
        mock_access.return_value = False
        test_path = Path("/path/to/script.py")
        
        # Act
        result = is_executable(test_path)
        
        # Assert
        assert result is False


class TestListAvailableTemplates:
    """Test the list_available_templates function."""

    @patch('skogcli.script.get_templates_dir')
    def test_should_scan_templates_directory(self, mock_get_templates_dir):
        """Test that templates directory is scanned correctly."""
        # Arrange
        mock_templates_dir = Mock()
        mock_get_templates_dir.return_value = mock_templates_dir
        
        # Create mock directory structure
        python_dir = Mock()
        python_dir.name = "python"
        python_dir.is_dir.return_value = True
        
        shell_dir = Mock()
        shell_dir.name = "shell"
        shell_dir.is_dir.return_value = True
        
        mock_templates_dir.exists.return_value = True
        mock_templates_dir.is_dir.return_value = True
        mock_templates_dir.iterdir.return_value = [python_dir, shell_dir]
        
        # Mock template files
        basic_py = Mock()
        basic_py.is_file.return_value = True
        basic_py.stem = "basic"
        
        api_py = Mock()
        api_py.is_file.return_value = True
        api_py.stem = "api_client"
        
        basic_sh = Mock()
        basic_sh.is_file.return_value = True
        basic_sh.stem = "basic"
        
        python_dir.iterdir.return_value = [basic_py, api_py]
        shell_dir.iterdir.return_value = [basic_sh]
        
        # Act
        result = list_available_templates()
        
        # Assert
        assert "python" in result
        assert "shell" in result
        assert "basic" in result["python"]
        assert "api_client" in result["python"] 
        assert "basic" in result["shell"]

    @patch('skogcli.script.get_templates_dir')  
    def test_should_handle_missing_templates_directory(self, mock_get_templates_dir):
        """Test handling when templates directory doesn't exist."""
        # Arrange
        mock_templates_dir = Mock()
        mock_templates_dir.exists.return_value = False
        mock_get_templates_dir.return_value = mock_templates_dir
        
        # Act
        result = list_available_templates()
        
        # Assert
        assert isinstance(result, dict)
        # Should still try package templates directory

    @patch('skogcli.script.get_templates_dir')
    def test_should_deduplicate_templates_from_multiple_sources(self, mock_get_templates_dir):
        """Test that templates from user and package dirs are deduplicated."""
        # Arrange
        mock_templates_dir = Mock()
        mock_get_templates_dir.return_value = mock_templates_dir
        
        # Setup mock that returns same template names from both sources
        python_dir = Mock()
        python_dir.name = "python"
        python_dir.is_dir.return_value = True
        
        mock_templates_dir.exists.return_value = True
        mock_templates_dir.is_dir.return_value = True
        mock_templates_dir.iterdir.return_value = [python_dir]
        
        # Mock template file that appears in both locations
        basic_py = Mock()
        basic_py.is_file.return_value = True
        basic_py.stem = "basic"
        
        python_dir.iterdir.return_value = [basic_py]
        
        # Act
        result = list_available_templates()
        
        # Assert
        assert "python" in result
        # Should only have one "basic" template even if it exists in multiple places
        assert result["python"].count("basic") == 1


class TestGetScriptTemplates:
    """Test the get_script_templates function."""

    @patch('skogcli.script.list_available_templates')
    def test_should_flatten_template_names(self, mock_list_templates):
        """Test that template names are flattened from all types."""
        # Arrange
        mock_templates = {
            "python": ["basic", "api_client", "data_processing"],
            "shell": ["basic", "system_info"],
        }
        mock_list_templates.return_value = mock_templates
        
        # Act
        result = get_script_templates()
        
        # Assert
        assert "basic" in result
        assert "api_client" in result
        assert "data_processing" in result
        assert "system_info" in result
        # Should be sorted and deduplicated
        assert result == sorted(result)
        assert len(set(result)) == len(result)  # No duplicates

    @patch('skogcli.script.list_available_templates')
    def test_should_handle_empty_templates(self, mock_list_templates):
        """Test handling when no templates are available."""
        # Arrange
        mock_list_templates.return_value = {}
        
        # Act
        result = get_script_templates()
        
        # Assert
        assert result == []

    @patch('skogcli.script.list_available_templates')
    def test_should_deduplicate_template_names_across_types(self, mock_list_templates):
        """Test that duplicate template names across types are deduplicated."""
        # Arrange
        mock_templates = {
            "python": ["basic", "advanced"],
            "shell": ["basic", "network"],
        }
        mock_list_templates.return_value = mock_templates
        
        # Act
        result = get_script_templates()
        
        # Assert
        assert result.count("basic") == 1  # Only one "basic" despite being in both types
        assert "advanced" in result
        assert "network" in result