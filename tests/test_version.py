"""Tests for the skogcli version command."""

import subprocess


def test_version_command():
    """Test that the version command returns the expected output."""
    # Run the version command
    result = subprocess.run(
        ["uv", "run", "skogcli", "version"],
        capture_output=True,
        text=True,
    )

    # Check that the command succeeded
    assert result.returncode == 0

    # Check that the output contains the expected version string
    assert "SkogCLI v" in result.stdout

    # The version should match the expected format (v0.0.3 or similar)
    assert "v0.0.3" in result.stdout
