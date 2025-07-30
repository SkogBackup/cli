#!/bin/bash
# Run integration tests with test environment variables

# Export test environment variables that should override JSON config
export SKOGAI_TEST_SCRIPT_USER_SCRIPTS_DIR="/tmp/skogcli_test_env_scripts"
export SKOGAI_TEST_SCRIPT_METADATA_DIR="/tmp/skogcli_test_env_metadata"

# Run integration tests only
uv run pytest tests/integration/ "$@"