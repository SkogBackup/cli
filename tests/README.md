# SkogCLI Tests

This directory contains tests for the SkogCLI application. The tests verify that the CLI commands work as expected and that the application's features function correctly.

## Running Tests

Tests can be run using the provided `run_tests.sh` script:

```bash
./tests/run_tests.sh
```

To run tests with verbose output:

```bash
./tests/run_tests.sh -v
```

To run a specific test file:

```bash
./tests/run_tests.sh tests/test_examples.py
```

To run a specific test function:

```bash
./tests/run_tests.sh tests/test_examples.py::test_examples_basic
```

## Test Files

### test_examples.py

Tests the example commands and the `with_explanation` decorator functionality.

#### test_examples_basic
- **Input**: Various combinations of arguments and options for the `examples basic` command
- **Expected Output**: Appropriate greetings based on the provided parameters
- **Purpose**: Verify that arguments and options work correctly

#### test_examples_choices
- **Input**: Different format options and items for the `examples choices` command
- **Expected Output**: Items displayed in the specified format (TEXT or JSON)
- **Purpose**: Verify that enum choices work correctly

#### test_examples_callback
- **Input**: Files with and without the verbose flag for the `examples callback` command
- **Expected Output**: List of files being processed, with additional debug info when verbose is enabled
- **Purpose**: Verify that callback functions work correctly

#### test_with_explanation_decorator
- **Input**: A command with the `with_explanation` decorator
- **Expected Output**: The explanation text followed by help text when invoked without arguments
- **Purpose**: Verify that the `with_explanation` decorator works correctly
- **Note**: This test is currently failing because the explanation text is not being displayed

#### test_app_commands_with_explanation
- **Input**: Various commands with and without arguments
- **Expected Output**: Command execution or help text with explanations
- **Purpose**: Verify that the main app commands with explanations work correctly

### test_config.py

Tests the configuration management functionality.

#### test_config_show
- **Input**: `config --show` command
- **Expected Output**: Current configuration settings
- **Purpose**: Verify that configuration can be displayed

#### test_config_set
- **Input**: `config --set api_url --value https://new-api.example.com` command
- **Expected Output**: Confirmation message that the setting was updated
- **Purpose**: Verify that configuration can be modified

#### test_config_reset
- **Input**: `config --reset` command
- **Expected Output**: Confirmation that configuration was reset to defaults
- **Purpose**: Verify that configuration can be reset

#### test_config_no_args
- **Input**: `config` command with no arguments
- **Expected Output**: Help message about available options
- **Purpose**: Verify that the command provides helpful information when no arguments are provided

## Known Issues

1. **test_with_explanation_decorator**: This test is failing because the explanation text is not being displayed when the command is invoked without arguments. The test expects to see "This is a test explanation for the command." in the output, but only sees "Command executed".

   Possible causes:
   - The `with_explanation` decorator might not be properly attaching the explanation to the command
   - The test might not be correctly simulating a command invocation without arguments
   - The callback function might not be correctly checking for the presence of the explanation
