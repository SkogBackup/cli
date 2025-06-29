"""Unit tests for pure functions in settings module."""

import pytest
from typing import Dict, Any

from skogcli.settings import extract_keys, migrate_config


class TestExtractKeys:
    """Test the extract_keys pure function."""

    def test_should_extract_flat_keys(self):
        """Test extracting keys from a flat dictionary."""
        # Arrange
        data = {"key1": "value1", "key2": "value2"}
        
        # Act
        result = extract_keys(data)
        
        # Assert
        assert set(result) == {"key1", "key2"}

    def test_should_extract_nested_keys(self):
        """Test extracting keys from nested dictionary."""
        # Arrange
        data = {
            "level1": {
                "level2": {
                    "level3": "value"
                },
                "key2": "value2"
            },
            "key1": "value1"
        }
        
        # Act
        result = extract_keys(data)
        
        # Assert
        expected = {"level1", "level1.level2", "level1.level2.level3", "level1.key2", "key1"}
        assert set(result) == expected

    def test_should_handle_empty_dictionary(self):
        """Test extracting keys from empty dictionary."""
        # Arrange
        data = {}
        
        # Act
        result = extract_keys(data)
        
        # Assert
        assert result == []

    def test_should_use_prefix_correctly(self):
        """Test extracting keys with custom prefix."""
        # Arrange
        data = {"key1": "value1", "key2": {"nested": "value"}}
        
        # Act
        result = extract_keys(data, "prefix.")
        
        # Assert
        expected = {"prefix.key1", "prefix.key2", "prefix.key2.nested"}
        assert set(result) == expected


class TestMigrateConfig:
    """Test the migrate_config pure function."""

    def test_should_add_settings_section_if_missing(self):
        """Test that settings section is added when missing."""
        # Arrange
        config = {}
        
        # Act
        result = migrate_config(config)
        
        # Assert
        assert "settings" in result
        assert isinstance(result["settings"], dict)

    def test_should_add_meta_section_with_version(self):
        """Test that meta section with version is added."""
        # Arrange
        config = {}
        
        # Act
        result = migrate_config(config)
        
        # Assert
        assert "settings" in result
        assert "meta" in result["settings"]
        assert "version" in result["settings"]["meta"]
        assert "last_updated" in result["settings"]["meta"]

    def test_should_initialize_module_section(self):
        """Test that module section is initialized."""
        # Arrange
        config = {}
        
        # Act
        result = migrate_config(config)
        
        # Assert
        assert "module" in result["settings"]
        assert "history" in result["settings"]["module"]
        assert result["settings"]["module"]["history"] == []

    def test_should_add_credentials_section(self):
        """Test that credentials section is added."""
        # Arrange
        config = {}
        
        # Act
        result = migrate_config(config)
        
        # Assert
        assert "credentials" in result

    def test_should_migrate_chat_history_to_module(self):
        """Test migration of chat history from old location."""
        # Arrange
        old_history = [
            {"message": "test1", "timestamp": 123456},
            {"message": "test2", "timestamp": 123457}
        ]
        config = {
            "chat": {
                "history": old_history
            }
        }
        
        # Act
        result = migrate_config(config)
        
        # Assert
        assert "settings" in result
        assert "module" in result["settings"]
        assert "history" in result["settings"]["module"]
        assert result["settings"]["module"]["history"] == old_history

    def test_should_preserve_existing_settings(self):
        """Test that existing settings are preserved during migration."""
        # Arrange
        config = {
            "settings": {
                "existing_key": "existing_value",
                "meta": {
                    "version": 1,
                    "last_updated": 987654321
                }
            }
        }
        
        # Act
        result = migrate_config(config)
        
        # Assert
        assert result["settings"]["existing_key"] == "existing_value"
        assert result["settings"]["meta"]["version"] == 1

    def test_should_not_mutate_original_config(self):
        """Test that original config is not mutated."""
        # Arrange
        original = {"test": "value"}
        
        # Act
        result = migrate_config(original)
        
        # Assert
        assert original == {"test": "value"}  # Original unchanged
        assert result != original  # Result is different object

    def test_should_handle_partial_settings_structure(self):
        """Test migration with partial existing settings."""
        # Arrange
        config = {
            "settings": {
                "module": {
                    "existing_setting": "value"
                }
            }
        }
        
        # Act
        result = migrate_config(config)
        
        # Assert
        assert result["settings"]["module"]["existing_setting"] == "value"
        assert "history" in result["settings"]["module"]
        assert "meta" in result["settings"]

    @pytest.mark.parametrize("version,expected", [
        (0, True),  # Should migrate
        (1, False), # Current version, no migration needed
        (2, False), # Future version, no migration needed
    ])
    def test_should_handle_version_based_migration(self, version, expected):
        """Test version-based migration logic."""
        # Arrange
        config = {
            "settings": {
                "meta": {
                    "version": version
                }
            }
        }
        
        # Act
        result = migrate_config(config)
        
        # Assert
        assert "meta" in result["settings"]
        # Version should be updated for old configs
        if expected:
            assert result["settings"]["meta"]["version"] >= 1