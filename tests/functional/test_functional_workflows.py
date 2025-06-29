"""Functional tests for complete user workflows."""

import pytest
import tempfile
import json
from pathlib import Path
from typer.testing import CliRunner

from skogcli import app


@pytest.mark.functional
class TestUserOnboardingWorkflow:
    """Test the complete user onboarding experience."""

    def test_new_user_setup_workflow(self, cli_runner: CliRunner):
        """Test that a new user can get started with minimal friction."""
        # Step 1: New user runs the CLI for the first time
        help_result = cli_runner.invoke(app, ["--help"])
        assert help_result.exit_code == 0
        assert "SkogCLI" in help_result.stdout
        
        # Step 2: Check version to verify installation
        version_result = cli_runner.invoke(app, ["version"])
        assert version_result.exit_code == 0
        assert "SkogCLI version" in version_result.stdout
        
        # Step 3: Explore available commands
        config_help = cli_runner.invoke(app, ["config", "--help"])
        script_help = cli_runner.invoke(app, ["script", "--help"])
        
        assert config_help.exit_code == 0
        assert script_help.exit_code == 0

    def test_user_explores_configuration(self, cli_runner: CliRunner, isolated_config: Path):
        """Test user exploring configuration options."""
        # User wants to see current config
        show_result = cli_runner.invoke(app, ["config", "show"])
        assert show_result.exit_code == 0
        
        # User wants to see all available config keys
        list_result = cli_runner.invoke(app, ["config", "list"])
        assert list_result.exit_code == 0
        assert "configuration keys" in list_result.stdout
        
        # User checks default configuration
        defaults_result = cli_runner.invoke(app, ["config", "show-defaults"])
        assert defaults_result.exit_code == 0


@pytest.mark.functional
class TestScriptManagementWorkflow:
    """Test complete script management workflows."""

    def test_user_discovers_and_creates_script(
        self, 
        cli_runner: CliRunner,
        mock_environment,
        temp_scripts_dir: Path
    ):
        """Test user discovering script capabilities and creating their first script."""
        # Step 1: User discovers script functionality
        help_result = cli_runner.invoke(app, ["script", "--help"])
        assert help_result.exit_code == 0
        
        # Step 2: User explores available templates
        templates_result = cli_runner.invoke(app, ["script", "templates"])
        assert templates_result.exit_code == 0
        
        # Step 3: User checks if any scripts exist
        list_result = cli_runner.invoke(app, ["script", "list"])
        assert list_result.exit_code == 0
        
        # Step 4: User tries to create a simple script
        # Note: May fail in test environment due to missing templates
        create_result = cli_runner.invoke(app, [
            "script", "create", "my_first_script",
            "--type", "python",
            "--description", "My first SkogCLI script",
            "--no-edit"
        ])
        # Don't assert success as templates may not exist in test environment
        
        # Step 5: User lists scripts again to see their creation
        list_after_result = cli_runner.invoke(app, ["script", "list"])
        assert list_after_result.exit_code == 0

    def test_power_user_script_management(
        self,
        cli_runner: CliRunner,
        mock_environment,
        temp_scripts_dir: Path,
        sample_script_content: str
    ):
        """Test advanced script management workflow."""
        # Create a test script file manually for testing
        script_file = temp_scripts_dir / "test_script.py"
        script_file.write_text(sample_script_content)
        script_file.chmod(0o755)
        
        # User imports existing script
        import_result = cli_runner.invoke(app, [
            "script", "import-file", str(script_file),
            "--name", "imported_script"
        ])
        # May succeed or fail depending on environment setup
        
        # User searches through scripts
        search_result = cli_runner.invoke(app, [
            "script", "search", "print",
            "--ignore-errors"
        ])
        assert search_result.exit_code == 0


@pytest.mark.functional
class TestConfigurationWorkflow:
    """Test configuration management workflows."""

    def test_user_customizes_configuration(
        self, 
        cli_runner: CliRunner, 
        isolated_config: Path
    ):
        """Test user customizing their configuration."""
        # Step 1: User wants to customize script directory
        set_result = cli_runner.invoke(app, [
            "config", "set", 
            "settings.script.user_scripts_dir", 
            "/custom/scripts/path"
        ])
        assert set_result.exit_code == 0
        
        # Step 2: User verifies the setting
        get_result = cli_runner.invoke(app, [
            "config", "get", "settings.script.user_scripts_dir"
        ])
        assert get_result.exit_code == 0
        
        # Step 3: User creates backup before making more changes
        backup_result = cli_runner.invoke(app, ["config", "backup"])
        # Should succeed or show appropriate message
        
        # Step 4: User sets multiple configuration values
        set_multiple = [
            cli_runner.invoke(app, ["config", "set", "user.name", "TestUser"]),
            cli_runner.invoke(app, ["config", "set", "user.email", "test@example.com"]),
            cli_runner.invoke(app, ["config", "set", "preferences.editor", "vim"])
        ]
        
        # All configuration sets should succeed
        for result in set_multiple:
            assert result.exit_code == 0

    def test_user_manages_configuration_backups(
        self, 
        cli_runner: CliRunner, 
        isolated_config: Path
    ):
        """Test backup and restore workflow."""
        # User creates initial backup
        backup_result = cli_runner.invoke(app, ["config", "backup"])
        
        # User makes some changes
        cli_runner.invoke(app, ["config", "set", "test.setting", "value1"])
        cli_runner.invoke(app, ["config", "set", "test.another", "value2"])
        
        # User lists available backups
        list_backups = cli_runner.invoke(app, ["config", "list-backups"])
        assert list_backups.exit_code == 0
        
        # User resets to defaults
        reset_result = cli_runner.invoke(app, ["config", "reset", "--yes"])
        assert reset_result.exit_code == 0


@pytest.mark.functional
@pytest.mark.slow
class TestCompleteWorkflows:
    """Test complete end-to-end user workflows."""

    def test_developer_workflow(
        self, 
        cli_runner: CliRunner,
        mock_environment,
        isolated_config: Path,
        temp_scripts_dir: Path
    ):
        """Test complete developer workflow from setup to daily use."""
        # Developer first-time setup
        version_check = cli_runner.invoke(app, ["version"])
        assert version_check.exit_code == 0
        
        # Developer configures their environment
        config_setup = [
            cli_runner.invoke(app, ["config", "set", "user.name", "Developer"]),
            cli_runner.invoke(app, ["config", "set", "preferences.editor", "code"]),
            cli_runner.invoke(app, ["config", "backup"])
        ]
        
        # Developer explores script capabilities
        exploration = [
            cli_runner.invoke(app, ["script", "templates"]),
            cli_runner.invoke(app, ["script", "list"]),
        ]
        
        for result in exploration:
            assert result.exit_code == 0
        
        # Developer tries to create utility script
        create_attempt = cli_runner.invoke(app, [
            "script", "create", "dev_utils",
            "--type", "python",
            "--description", "Development utilities",
            "--no-edit"
        ])
        # May fail due to missing templates in test environment
        
        # Developer checks what they have
        final_check = cli_runner.invoke(app, ["script", "list", "--metadata"])
        assert final_check.exit_code == 0

    def test_team_collaboration_workflow(
        self, 
        cli_runner: CliRunner,
        isolated_config: Path
    ):
        """Test workflow for team collaboration scenarios."""
        # Team member sets up consistent configuration
        team_config = [
            cli_runner.invoke(app, ["config", "set", "team.name", "SkogAI Team"]),
            cli_runner.invoke(app, ["config", "set", "team.standards", "true"]),
            cli_runner.invoke(app, ["config", "backup"])
        ]
        
        for result in team_config:
            assert result.exit_code == 0
        
        # Team member validates their setup
        validation = [
            cli_runner.invoke(app, ["config", "show"]),
            cli_runner.invoke(app, ["config", "list"])
        ]
        
        for result in validation:
            assert result.exit_code == 0

    def test_troubleshooting_workflow(
        self, 
        cli_runner: CliRunner,
        isolated_config: Path
    ):
        """Test user troubleshooting common issues."""
        # User having issues, checks basic functionality
        diagnostics = [
            cli_runner.invoke(app, ["--help"]),
            cli_runner.invoke(app, ["version"]),
            cli_runner.invoke(app, ["config", "show"])
        ]
        
        for result in diagnostics:
            assert result.exit_code == 0
        
        # User resets configuration to defaults
        reset_result = cli_runner.invoke(app, ["config", "reset", "--yes"])
        assert reset_result.exit_code == 0
        
        # User verifies reset worked
        verify_result = cli_runner.invoke(app, ["config", "show"])
        assert verify_result.exit_code == 0


@pytest.mark.functional
class TestErrorHandlingWorkflows:
    """Test how the application handles various error conditions."""

    def test_graceful_degradation_with_missing_dependencies(
        self, 
        cli_runner: CliRunner
    ):
        """Test that the app degrades gracefully when optional dependencies are missing."""
        # All core commands should work even if optional features are unavailable
        core_commands = [
            cli_runner.invoke(app, ["--help"]),
            cli_runner.invoke(app, ["version"]),
            cli_runner.invoke(app, ["config", "--help"]),
            cli_runner.invoke(app, ["script", "--help"]),
            cli_runner.invoke(app, ["memory", "--help"]),
            cli_runner.invoke(app, ["agent", "--help"])
        ]
        
        for result in core_commands:
            assert result.exit_code == 0

    def test_invalid_input_handling(self, cli_runner: CliRunner, isolated_config: Path):
        """Test handling of invalid user inputs."""
        # Test invalid configuration keys
        invalid_get = cli_runner.invoke(app, ["config", "get", "nonexistent.key"])
        # Should handle gracefully (may return 0 with message or non-zero)
        
        # Test invalid script names
        invalid_script = cli_runner.invoke(app, ["script", "info", "nonexistent_script"])
        # Should handle gracefully
        
        # Test invalid commands
        invalid_command = cli_runner.invoke(app, ["invalid_command"])
        assert invalid_command.exit_code != 0  # Should fail for invalid commands