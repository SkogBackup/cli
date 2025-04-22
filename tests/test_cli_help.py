"""Tests for skogcli help functionality."""

import subprocess
import pytest
from typing import List, Tuple


def run_command(command: List[str]) -> Tuple[str, str, int]:
    """Run a command and return stdout, stderr, and return code."""
    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    return process.stdout, process.stderr, process.returncode


def assert_command_equals_help(base_command: List[str]):
    """Assert that running a command without args is the same as with --help."""
    # Run both commands
    no_args_stdout, no_args_stderr, no_args_code = run_command(base_command)
    help_command = base_command + ["--help"]
    help_stdout, help_stderr, help_code = run_command(help_command)
    
    command_str = " ".join(base_command)
    
    # Both commands should exit with the same status code
    assert no_args_code == help_code, f"Return codes differ for {command_str}"
    
    # Both commands should produce the same stdout
    assert no_args_stdout == help_stdout, f"Stdout output differs for {command_str}"
    
    # Both commands should produce the same stderr
    assert no_args_stderr == help_stderr, f"Stderr output differs for {command_str}"


def test_no_args_equals_help():
    """Test that running skogcli without args is the same as skogcli --help."""
    assert_command_equals_help(["uv", "run", "skogcli"])


def test_memory_subcommand_no_args_equals_help():
    """Test that 'skogcli memory' without args is the same as 'skogcli memory --help'."""
    assert_command_equals_help(["uv", "run", "skogcli", "memory"])


def test_config_subcommand_no_args_equals_help():
    """Test that 'skogcli config' without args is the same as 'skogcli config --help'."""
    assert_command_equals_help(["uv", "run", "skogcli", "config"])


def test_misc_subcommand_no_args_equals_help():
    """Test that 'skogcli misc' without args is the same as 'skogcli misc --help'."""
    assert_command_equals_help(["uv", "run", "skogcli", "misc"])