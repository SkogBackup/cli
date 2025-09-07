# SkogCLI Script Management

The `skogcli script` command provides comprehensive script management capabilities for custom automation scripts. This module enables users to create, manage, and execute custom scripts within the SkogAI ecosystem.

## Subcommands

### list
Lists all available custom scripts in the user's scripts directory. This command provides an overview of all scripts currently available for execution, showing their names and basic metadata. Useful for discovering existing scripts and getting a quick inventory of your automation toolkit.

**Options:**
- `--global` / `--no-global`: Include global scripts (default: global)
- `--metadata` / `-m`: Show script metadata
- `--help`: Show help message

### run
Executes a custom script by name. This is the primary command for running your automation scripts, with support for passing arguments and environment variables. The command handles script execution with proper error handling and output capture, making it safe to run scripts in automated workflows.

**Arguments:**
- `name` (required): Name of the script to run
- `args...` (optional): Arguments to pass to the script

**Options:**
- `--global` / `--no-global`: Include global scripts (default: global)
- `--help`: Show help message

### create
Creates a new custom script interactively. This command guides users through script creation with templates and metadata collection. It sets up proper file structure, permissions, and initial metadata tracking. The creation process includes template selection and initial configuration to ensure scripts follow best practices.

**Arguments:**
- `name` (required): Name for the new script

**Options:**
- `--type` / `-t`: Script type (python or shell, default: python)
- `--template`: Script template to use (default: basic)
- `--global` / `-g`: Install as a global script
- `--description` / `-d`: Description of the script
- `--edit` / `--no-edit`: Open the script in an editor after creation (default: edit)
- `--editor` / `-e`: Specify which editor to use (default: vi)
- `--help`: Show help message

### edit
Opens an existing custom script in the user's preferred editor for modification. This command respects the user's EDITOR environment variable and provides a seamless editing experience. It handles file locking and metadata updates to track script modifications and maintain version history.

**Arguments:**
- `name` (required): Name of the script to edit

**Options:**
- `--global` / `--no-global`: Include global scripts (default: global)
- `--editor` / `-e`: Specify which editor to use (default: vi)
- `--help`: Show help message

### remove
Safely removes a custom script from the scripts directory. This command includes confirmation prompts and metadata cleanup to prevent accidental deletions. It ensures that all associated files and metadata are properly cleaned up when a script is no longer needed.

**Arguments:**
- `name` (required): Name of the script to remove

**Options:**
- `--global` / `--no-global`: Include global scripts (default: global)
- `--force` / `-f`: Force removal without confirmation
- `--help`: Show help message

### info
Displays detailed information about a specific script, including metadata, execution history, and file details. This command provides comprehensive insights into script usage patterns, creation date, modification history, and execution statistics. Essential for script maintenance and troubleshooting.

**Arguments:**
- `name` (required): Name of the script

**Options:**
- `--global` / `--no-global`: Include global scripts (default: global)
- `--help`: Show help message

### code
Views or updates script code directly from the command line without launching an external editor. This command is useful for quick edits, code inspection, and automated script modifications. It supports both viewing and updating script content with proper syntax validation.

**Arguments:**
- `name` (required): Name of the script

**Options:**
- `--content` / `-c`: New content for the script (if not provided, displays current content)
- `--file` / `-f`: Read new content from this file
- `--output` / `-o`: Write content to this file instead of updating the script
- `--global` / `--no-global`: Include global scripts (default: global)
- `--help`: Show help message

### batch
Processes multiple scripts with a single command, enabling bulk operations on script collections. This powerful command supports operations like running multiple scripts in sequence, updating metadata across script sets, and performing maintenance tasks on script groups.

**Arguments:**
- `script_list` (required): Path to a file containing a list of scripts to process, one per line

**Options:**
- `--command` / `-c`: Command to run on each script (code, run, info, etc., default: code)
- `--global` / `--no-global`: Include global scripts (default: global)
- `--output-dir` / `-o`: Directory to write output files to
- `--continue-on-error`: Continue processing even if errors occur
- `--pattern` / `-p`: Pattern to search for (when using 'search' command)
- `--replacement` / `-r`: Replacement string (when using 'transform' command)
- `--help`: Show help message

### update-metadata
Updates metadata information for a script, including description, tags, and execution tracking. This command allows users to maintain accurate script documentation and improve script discoverability. It supports both manual metadata updates and automated metadata extraction.

**Arguments:**
- `name` (required): Name of the script

**Options:**
- `--description` / `-d`: Description of the script
- `--global` / `--no-global`: Include global scripts (default: global)
- `--help`: Show help message

### templates
Lists available script templates that can be used as starting points for new scripts. This command helps users discover pre-built script patterns and best practices. Templates provide standardized structures for common automation tasks and ensure consistency across script implementations.

**Options:**
- `--help`: Show help message

### export
Exports a script to a JSON file format suitable for sharing with others or backing up script configurations. This command creates portable script packages that include both code and metadata, enabling easy script distribution and collaboration between team members.

**Arguments:**
- `name` (required): Name of the script to export

**Options:**
- `--output` / `-o`: Output JSON file path
- `--metadata` / `--no-metadata`: Include metadata in export (default: metadata)
- `--global` / `--no-global`: Include global scripts (default: global)
- `--help`: Show help message

### transform
Transforms script content using regular expressions and pattern matching. This powerful command enables automated code refactoring, pattern replacement, and bulk modifications across scripts. Useful for maintaining code consistency and applying systematic updates to script collections.

**Arguments:**
- `name` (required): Name of the script to transform

**Options:**
- `--pattern` / `-p` (required): Regular expression pattern to search for
- `--replacement` / `-r` (required): Replacement string
- `--output` / `-o`: Write transformed content to this file instead of updating the script
- `--global` / `--no-global`: Include global scripts (default: global)
- `--backup` / `--no-backup`: Create a backup before transforming (default: backup)
- `--help`: Show help message

### search
Searches for specific text patterns within scripts, supporting both literal text and regular expression matching. This command helps users locate scripts containing specific functionality, find usage examples, and perform code archaeology across their script collection.

**Arguments:**
- `pattern` (required): Text or regular expression to search for

**Options:**
- `--regex` / `-r`: Treat pattern as a regular expression
- `--case-sensitive` / `-c`: Make search case-sensitive
- `--global` / `--no-global`: Include global scripts (default: global)
- `--output` / `-o`: Write results to this file
- `--ignore-errors`: Continue searching even if errors occur
- `--help`: Show help message

### generate
Generates a script from a natural language description using AI assistance or template expansion. This command leverages artificial intelligence to create script scaffolding based on user requirements, significantly accelerating script development and reducing boilerplate code creation.

**Arguments:**
- `name` (required): Name for the new script
- `description` (required): Description of what the script should do

**Options:**
- `--type` / `-t`: Script type (python or shell, default: python)
- `--global` / `-g`: Install as a global script
- `--edit` / `--no-edit`: Open the script in an editor after creation (default: edit)
- `--editor` / `-e`: Specify which editor to use (default: vi)
- `--model` / `-m`: AI model to use for generation (default: gpt-3.5-turbo)
- `--api-key` / `-k`: API key for the AI service
- `--local` / `-l`: Use local templates instead of AI
- `--help`: Show help message

### import
Imports a script from a previously exported JSON file, enabling script sharing and backup restoration. This command reconstructs both script code and metadata from export files, maintaining full script functionality and historical information across different environments.

**Arguments:**
- `file` (required): Path to the JSON export file created by 'script export'

**Options:**
- `--global` / `-g`: Install as a global script
- `--overwrite`: Overwrite existing script
- `--help`: Show help message

### import-file
Imports an existing script file directly into the managed scripts directory. This command brings external scripts under SkogCLI management, adding metadata tracking and integration with other script management features. Useful for migrating existing automation scripts into the SkogAI ecosystem.

**Arguments:**
- `file` (required): Path to the existing script file to add

**Options:**
- `--name` / `-n`: Name for the script (defaults to original filename)
- `--global` / `-g`: Install as a global script
- `--overwrite`: Overwrite existing script
- `--edit` / `-e`: Open the script in an editor after adding
- `--editor`: Specify which editor to use (default: vi)
- `--help`: Show help message

### copy
Creates a copy of an existing script with a new name, useful for creating variations or backups. This command duplicates both script code and metadata while generating unique identifiers for the new script. Essential for script versioning and creating script families with related functionality.

**Arguments:**
- `source` (required): Name of the source script
- `destination` (required): Name for the new script

**Options:**
- `--global-source` / `--no-global-source`: Include global scripts as source (default: global-source)
- `--global-dest` / `-g`: Create as a global script
- `--edit` / `--no-edit`: Open the new script in an editor (default: edit)
- `--editor` / `-e`: Specify which editor to use (default: vi)
- `--help`: Show help message