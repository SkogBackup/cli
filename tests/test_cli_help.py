"""Tests for skogcli help functionality."""

from typer.testing import CliRunner
from skogcli import app

runner = CliRunner()


def assert_command_equals_help(base_command: list[str]):
    """Assert that running a command without args is the same as with --help."""
    no_args_result = runner.invoke(app, base_command)
    help_result = runner.invoke(app, base_command + ["--help"])

    command_str = f"skogcli {' '.join(base_command)}"

    assert (
        no_args_result.exit_code == help_result.exit_code
    ), f"Return codes differ for {command_str}"
    assert (
        no_args_result.output == help_result.output
    ), f"Output differs for {command_str}"


def test_no_args_equals_help():
    """Test that running skogcli without args is the same as skogcli --help."""
    assert_command_equals_help([])


def test_memory_subcommand_no_args_equals_help():
    """Test that 'skogcli memory' without args is the same as 'skogcli memory --help'."""
    assert_command_equals_help(["memory"])


def test_config_subcommand_no_args_equals_help():
    """Test that 'skogcli config' without args is the same as 'skogcli config --help'."""
    assert_command_equals_help(["config"])


def test_misc_subcommand_no_args_equals_help():
    """Test that 'skogcli misc' without args is the same as 'skogcli misc --help'."""
    assert_command_equals_help(["misc"])
