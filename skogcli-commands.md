# SkogCLI Commands

**Usage**:

```console
$ SkogCLI [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `memory`: Knowledge management for SkogAI agents and...
* `config`: Manage SkogCLI configuration
* `script`: Script management commands
* `agent`: Interact with SkogAI agents

## `SkogCLI memory`

Knowledge management for SkogAI agents and their shared memories

**Usage**:

```console
$ SkogCLI memory [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `new`: Create or update a note in your knowledge...
* `add`: Create or update a note in your knowledge...
* `write`: Create or update a note in your knowledge...
* `create`: Create or update a note
* `show`: Read a note from your knowledge base.
* `read`: Read a note by its identifier
* `find`: Search across your knowledge base for...
* `search`: Search notes by content or metadata
* `ls`: List recent activity across your knowledge...
* `list`: List recent notes and activity
* `sync`: Sync notes with the database
* `info`: Show project information and sync status.
* `status`: Show project status and statistics
* `recent-activity`: Alias for &#x27;list&#x27; command

### `SkogCLI memory new`

Create or update a note in your knowledge base.

    Examples:

    Create from argument:
      skogcli memory create &quot;My Idea&quot; notes --content &quot;# My Idea

This is a great idea.&quot;

    Create from stdin:
      echo &quot;# My Idea

This is a great idea.&quot; | skogcli memory create &quot;My Idea&quot; notes

    Create with tags:
      skogcli memory create &quot;Meeting Notes&quot; meetings --tags &quot;work,important,2025&quot;

**Usage**:

```console
$ SkogCLI memory new [OPTIONS] TITLE FOLDER
```

**Arguments**:

* `TITLE`: Title of the note  [required]
* `FOLDER`: Folder to create the note in  [required]

**Options**:

* `-c, --content TEXT`: Note content (if not provided, read from stdin)
* `-t, --tag TEXT`: Tags to apply to the note (comma-separated)
* `-p, --project TEXT`: Specific project to use
* `--help`: Show this message and exit.

### `SkogCLI memory add`

Create or update a note in your knowledge base.

    Examples:

    Create from argument:
      skogcli memory create &quot;My Idea&quot; notes --content &quot;# My Idea

This is a great idea.&quot;

    Create from stdin:
      echo &quot;# My Idea

This is a great idea.&quot; | skogcli memory create &quot;My Idea&quot; notes

    Create with tags:
      skogcli memory create &quot;Meeting Notes&quot; meetings --tags &quot;work,important,2025&quot;

**Usage**:

```console
$ SkogCLI memory add [OPTIONS] TITLE FOLDER
```

**Arguments**:

* `TITLE`: Title of the note  [required]
* `FOLDER`: Folder to create the note in  [required]

**Options**:

* `-c, --content TEXT`: Note content (if not provided, read from stdin)
* `-t, --tag TEXT`: Tags to apply to the note (comma-separated)
* `-p, --project TEXT`: Specific project to use
* `--help`: Show this message and exit.

### `SkogCLI memory write`

Create or update a note in your knowledge base.

**Usage**:

```console
$ SkogCLI memory write [OPTIONS] TITLE FOLDER
```

**Arguments**:

* `TITLE`: Title of the note  [required]
* `FOLDER`: Folder to create the note in  [required]

**Options**:

* `-c, --content TEXT`: Note content (if not provided, read from stdin)
* `-t, --tags TEXT`: Tags to apply to the note (comma-separated)
* `-p, --project TEXT`: Specific project to use
* `--help`: Show this message and exit.

### `SkogCLI memory create`

Create or update a note in your knowledge base.

**Usage**:

```console
$ SkogCLI memory create [OPTIONS] TITLE FOLDER
```

**Arguments**:

* `TITLE`: Title of the note  [required]
* `FOLDER`: Folder to create the note in  [required]

**Options**:

* `-c, --content TEXT`: Note content (if not provided, read from stdin)
* `-t, --tag TEXT`: Tags to apply to the note (comma-separated)
* `-p, --project TEXT`: Specific project to use
* `--help`: Show this message and exit.

### `SkogCLI memory show`

Read a note from your knowledge base.

Examples:

Read a note by identifier:
  skogcli memory read &quot;My Note&quot;

Read a note from a specific project:
  skogcli memory read &quot;My Note&quot; --project my-project

Display raw markdown:
  skogcli memory read &quot;My Note&quot; --raw

Save note content to a file:
  skogcli memory read &quot;My Note&quot; --output note.md

**Usage**:

```console
$ SkogCLI memory show [OPTIONS] IDENTIFIER
```

**Arguments**:

* `IDENTIFIER`: Note identifier in format &#x27;folder/title&#x27; or just &#x27;title&#x27; to search in all folders  [required]

**Options**:

* `-p, --page INTEGER RANGE`: Page number for pagination  [default: 1; x&gt;=1]
* `-s, --page-size INTEGER RANGE`: Number of items per page  [default: 10; 1&lt;=x&lt;=100]
* `-P, --project TEXT`: Specific project to use
* `-r, --raw`: Display raw markdown without rich formatting
* `-o, --output PATH`: Save note content to a file instead of displaying it
* `--help`: Show this message and exit.

### `SkogCLI memory read`

Read a note from your knowledge base.

**Usage**:

```console
$ SkogCLI memory read [OPTIONS] IDENTIFIER
```

**Arguments**:

* `IDENTIFIER`: Note identifier in format &#x27;folder/title&#x27; or just &#x27;title&#x27; to search in all folders  [required]

**Options**:

* `-p, --page INTEGER RANGE`: Page number for pagination  [default: 1; x&gt;=1]
* `-s, --page-size INTEGER RANGE`: Number of items per page  [default: 10; 1&lt;=x&lt;=100]
* `-P, --project TEXT`: Specific project to use
* `-r, --raw`: Display raw markdown without rich formatting
* `-o, --output PATH`: Save note content to a file instead of displaying it
* `--help`: Show this message and exit.

### `SkogCLI memory find`

Search across your knowledge base for specific content.

Examples:

Basic search:
  skogcli memory search &quot;project ideas&quot;

Search only titles:
  skogcli memory search &quot;meeting&quot; --title

Search with date filter:
  skogcli memory search &quot;important&quot; --after-date &quot;1 week&quot;

Search with regex:
  skogcli memory search &quot;regex:project.*ideas&quot;

Display results in JSON:
  skogcli memory search &quot;project ideas&quot; --format json

**Usage**:

```console
$ SkogCLI memory find [OPTIONS] QUERY
```

**Arguments**:

* `QUERY`: Search query (supports simple text or regex with --regex flag)  [required]

**Options**:

* `--permalink / --no-permalink`: Search only in permalink values  [default: no-permalink]
* `--title / --no-title`: Search only in title values  [default: no-title]
* `-a, --after-date TEXT`: Filter results after this date (e.g., &#x27;2d&#x27;, &#x27;1 week&#x27;, &#x27;2023-01-01&#x27;)
* `-b, --before-date TEXT`: Filter results before this date
* `-p, --page INTEGER RANGE`: Page number for pagination  [default: 1; x&gt;=1]
* `-s, --page-size INTEGER RANGE`: Number of items per page  [default: 10; 1&lt;=x&lt;=100]
* `-P, --project TEXT`: Specific project to search in
* `-f, --format TEXT`: Output format (table, json, markdown)  [default: table]
* `--help`: Show this message and exit.

### `SkogCLI memory search`

Search across your knowledge base for specific content.

**Usage**:

```console
$ SkogCLI memory search [OPTIONS] QUERY
```

**Arguments**:

* `QUERY`: Search query (supports simple text or regex with --regex flag)  [required]

**Options**:

* `--permalink / --no-permalink`: Search only in permalink values  [default: no-permalink]
* `--title / --no-title`: Search only in title values  [default: no-title]
* `-a, --after-date TEXT`: Filter results after this date (e.g., &#x27;2d&#x27;, &#x27;1 week&#x27;, &#x27;2023-01-01&#x27;)
* `-b, --before-date TEXT`: Filter results before this date
* `-p, --page INTEGER RANGE`: Page number for pagination  [default: 1; x&gt;=1]
* `-s, --page-size INTEGER RANGE`: Number of items per page  [default: 10; 1&lt;=x&lt;=100]
* `-P, --project TEXT`: Specific project to search in
* `-f, --format TEXT`: Output format (table, json, markdown)  [default: table]
* `--help`: Show this message and exit.

### `SkogCLI memory ls`

List recent activity across your knowledge base.

Examples:

List recent activity (default 7 days):
  skogcli memory list

List specific type:
  skogcli memory list --type entity

Custom timeframe:
  skogcli memory list --timeframe 30d

Display results in JSON:
  skogcli memory list --format json

**Usage**:

```console
$ SkogCLI memory ls [OPTIONS]
```

**Options**:

* `-t, --type TEXT`: Filter by activity type
* `-f, --folder TEXT`: Filter by folder
* `-d, --depth INTEGER RANGE`: Depth of related entities to show  [default: 1; 0&lt;=x&lt;=5]
* `-T, --timeframe TEXT`: Time range to show (e.g., &#x27;7d&#x27;, &#x27;2w&#x27;, &#x27;1m&#x27;)  [default: 7d]
* `-p, --page INTEGER RANGE`: Page number for pagination  [default: 1; x&gt;=1]
* `-s, --page-size INTEGER RANGE`: Number of items per page  [default: 10; 1&lt;=x&lt;=100]
* `-m, --max-related INTEGER RANGE`: Maximum number of related items to show per result  [default: 5; x&gt;=0]
* `-P, --project TEXT`: Specific project to list from
* `-f, --format TEXT`: Output format (table, json, csv, markdown)  [default: table]
* `--help`: Show this message and exit.

### `SkogCLI memory list`

List recent activity across your knowledge base.

**Usage**:

```console
$ SkogCLI memory list [OPTIONS]
```

**Options**:

* `-t, --type TEXT`: Filter by activity type
* `-f, --folder TEXT`: Filter by folder
* `-d, --depth INTEGER RANGE`: Depth of related entities to show  [default: 1; 0&lt;=x&lt;=5]
* `-T, --timeframe TEXT`: Time range to show (e.g., &#x27;7d&#x27;, &#x27;2w&#x27;, &#x27;1m&#x27;)  [default: 7d]
* `-p, --page INTEGER RANGE`: Page number for pagination  [default: 1; x&gt;=1]
* `-s, --page-size INTEGER RANGE`: Number of items per page  [default: 10; 1&lt;=x&lt;=100]
* `-m, --max-related INTEGER RANGE`: Maximum number of related items to show per result  [default: 5; x&gt;=0]
* `-P, --project TEXT`: Specific project to list from
* `-f, --format TEXT`: Output format (table, json, csv, markdown)  [default: table]
* `--help`: Show this message and exit.

### `SkogCLI memory sync`

Synchronize your knowledge files with the database.

**Usage**:

```console
$ SkogCLI memory sync [OPTIONS]
```

**Options**:

* `-p, --project TEXT`: Specific project to sync
* `-f, --force`: Force sync even if no changes detected
* `-n, --dry-run`: Show what would be synced without making changes
* `-v, --verbose`: Show detailed output
* `--help`: Show this message and exit.

### `SkogCLI memory info`

Show project information and sync status.

Examples:

Show status for all projects:
  skogcli memory status

Show status for a specific project:
  skogcli memory status --project my-project

Display results in JSON:
  skogcli memory status --format json
Displays information about the current project, including:
- Project name and location
- Number of notes and entities
- Last sync time
- Files that need to be synchronized

**Usage**:

```console
$ SkogCLI memory info [OPTIONS]
```

**Options**:

* `-p, --project TEXT`: Show status for specific project
* `-f, --format TEXT`: Output format (table, json, yaml)  [default: table]
* `-a, --all`: Show all projects status (if no project specified)
* `-c, --check`: Only show status code (0: success, 1: warning, 2: error)
* `--help`: Show this message and exit.

### `SkogCLI memory status`

Show project information and sync status.

**Usage**:

```console
$ SkogCLI memory status [OPTIONS]
```

**Options**:

* `-p, --project TEXT`: Show status for specific project
* `-f, --format TEXT`: Output format (table, json, yaml)  [default: table]
* `-a, --all`: Show all projects status (if no project specified)
* `-c, --check`: Only show status code (0: success, 1: warning, 2: error)
* `--help`: Show this message and exit.

### `SkogCLI memory recent-activity`

List recent activity across your knowledge base (alias for &#x27;list&#x27;).

**Usage**:

```console
$ SkogCLI memory recent-activity [OPTIONS]
```

**Options**:

* `-t, --type TEXT`: Filter by activity type
* `-d, --depth INTEGER RANGE`: Depth of related entities to show  [default: 1; 0&lt;=x&lt;=5]
* `-T, --timeframe TEXT`: Time range to show (e.g., &#x27;7d&#x27;, &#x27;2w&#x27;, &#x27;1m&#x27;)  [default: 7d]
* `-p, --page INTEGER RANGE`: Page number for pagination  [default: 1; x&gt;=1]
* `-s, --page-size INTEGER RANGE`: Number of items per page  [default: 10; 1&lt;=x&lt;=100]
* `-m, --max-related INTEGER RANGE`: Maximum number of related items to show per result  [default: 5; x&gt;=0]
* `-P, --project TEXT`: Specific project to list from
* `-f, --format TEXT`: Output format (table, json, csv, markdown)  [default: table]
* `-a, --all`: Show all items (ignores pagination)
* `--help`: Show this message and exit.

## `SkogCLI config`

Manage SkogCLI configuration

**Usage**:

```console
$ SkogCLI config [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `show`: Display the current configuration.
* `list`: List all available configuration keys.
* `get`: Get the value of a specific configuration...
* `set`: Set the value of a specific configuration...
* `reset`: Reset configuration to default values.
* `show-defaults`: Display the default configuration.
* `edit-defaults`: Edit the default configuration.
* `edit`: Open the configuration file in your...
* `backup`: Create a backup of the configuration files.
* `restore`: Restore configuration from a backup.
* `list-backups`: List available configuration backups.
* `factory-reset`: Reset configuration to factory default...
* `chat-history`: Manage chat history.

### `SkogCLI config show`

Display the current configuration.

Display the current configuration.

**Usage**:

```console
$ SkogCLI config show [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `SkogCLI config list`

List all available configuration keys.

List all available configuration keys.

**Usage**:

```console
$ SkogCLI config list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `SkogCLI config get`

Get the value of a specific configuration key.

Get the value of a specific configuration key.

**Usage**:

```console
$ SkogCLI config get [OPTIONS] KEY
```

**Arguments**:

* `KEY`: Configuration key (e.g., &#x27;memory.page_size&#x27;)  [required]

**Options**:

* `-r, --raw`: Output raw value without formatting  [default: True]
* `-j, --json`: Output as formatted JSON
* `--help`: Show this message and exit.

### `SkogCLI config set`

Set the value of a specific configuration key.

Set the value of a specific configuration key.

**Usage**:

```console
$ SkogCLI config set [OPTIONS] KEY VALUE
```

**Arguments**:

* `KEY`: Configuration key (e.g., &#x27;memory.page_size&#x27;)  [required]
* `VALUE`: Value to set  [required]

**Options**:

* `--help`: Show this message and exit.

### `SkogCLI config reset`

Reset configuration to default values.

Reset configuration to default values.

**Usage**:

```console
$ SkogCLI config reset [OPTIONS]
```

**Options**:

* `-y, --yes`: Confirm reset without prompting
* `--help`: Show this message and exit.

### `SkogCLI config show-defaults`

Display the default configuration.

Display the default configuration.

**Usage**:

```console
$ SkogCLI config show-defaults [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `SkogCLI config edit-defaults`

Edit the default configuration.

Edit the default configuration.

**Usage**:

```console
$ SkogCLI config edit-defaults [OPTIONS] [KEY] [VALUE]
```

**Arguments**:

* `[KEY]`: Configuration key to edit (if not specified, opens the entire file)
* `[VALUE]`: Value to set (if not specified with key, opens the file in editor)

**Options**:

* `--help`: Show this message and exit.

### `SkogCLI config edit`

Open the configuration file in your default editor.

Open the configuration file in your default editor.

**Usage**:

```console
$ SkogCLI config edit [OPTIONS]
```

**Options**:

* `-s, --sensitive`: Edit sensitive configuration
* `--help`: Show this message and exit.

### `SkogCLI config backup`

Create a backup of the configuration files.

Create a backup of the configuration files.

**Usage**:

```console
$ SkogCLI config backup [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `SkogCLI config restore`

Restore configuration from a backup.

Restore configuration from a backup.

**Usage**:

```console
$ SkogCLI config restore [OPTIONS] [BACKUP_FILE]
```

**Arguments**:

* `[BACKUP_FILE]`: Path to the backup file (if not specified, uses the most recent backup)

**Options**:

* `-y, --yes`: Confirm restore without prompting
* `--help`: Show this message and exit.

### `SkogCLI config list-backups`

List available configuration backups.

List available configuration backups.

**Usage**:

```console
$ SkogCLI config list-backups [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `SkogCLI config factory-reset`

Reset configuration to factory default values.

Reset configuration to factory default values (ignoring custom defaults).

**Usage**:

```console
$ SkogCLI config factory-reset [OPTIONS]
```

**Options**:

* `-y, --yes`: Confirm reset without prompting
* `--help`: Show this message and exit.

### `SkogCLI config chat-history`

Manage chat history.

Manage chat history.

**Usage**:

```console
$ SkogCLI config chat-history [OPTIONS]
```

**Options**:

* `--clear`: Clear chat history
* `-n, --limit INTEGER`: Number of history items to show  [default: 10]
* `-j, --json`: Output in JSON format
* `--help`: Show this message and exit.

## `SkogCLI script`

Script management commands

**Usage**:

```console
$ SkogCLI script [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List all available custom scripts.
* `run`: Run a custom script.
* `create`: Create a new custom script.
* `edit`: Edit an existing custom script.
* `remove`: Remove a custom script.
* `info`: Show detailed information about a script.
* `code`: View or update script code without using...
* `batch`: Process multiple scripts with a single...
* `update-metadata`: Update metadata for a script.
* `templates`: List available script templates.
* `export`: Export a script to a JSON file that can be...
* `transform`: Transform script content using regular...
* `search`: Search for text in scripts.
* `generate`: Generate a script from a description using...
* `import`: Import a script from a JSON export file...
* `import-file`: Import an existing script file into the...
* `copy`: Copy a script to create a new one.

### `SkogCLI script list`

List all available custom scripts.

List all available custom scripts.

**Usage**:

```console
$ SkogCLI script list [OPTIONS]
```

**Options**:

* `--global / --no-global`: Include global scripts  [default: global]
* `-m, --metadata`: Show script metadata
* `--help`: Show this message and exit.

### `SkogCLI script run`

Run a custom script.

Run a custom script.

**Usage**:

```console
$ SkogCLI script run [OPTIONS] NAME [ARGS]...
```

**Arguments**:

* `NAME`: Name of the script to run  [required]
* `[ARGS]...`: Arguments to pass to the script

**Options**:

* `--global / --no-global`: Include global scripts  [default: global]
* `--help`: Show this message and exit.

### `SkogCLI script create`

Create a new custom script.

Create a new custom script.

**Usage**:

```console
$ SkogCLI script create [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name for the new script  [required]

**Options**:

* `-t, --type TEXT`: Script type (python or shell)  [default: python]
* `--template TEXT`: Script template to use  [default: basic]
* `-g, --global`: Install as a global script
* `-d, --description TEXT`: Description of the script
* `--edit / --no-edit`: Open the script in an editor after creation  [default: edit]
* `-e, --editor TEXT`: Specify which editor to use (defaults to $EDITOR)
* `--help`: Show this message and exit.

### `SkogCLI script edit`

Edit an existing custom script.

Edit an existing custom script.

**Usage**:

```console
$ SkogCLI script edit [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the script to edit  [required]

**Options**:

* `--global / --no-global`: Include global scripts  [default: global]
* `-e, --editor TEXT`: Specify which editor to use (defaults to $EDITOR)
* `--help`: Show this message and exit.

### `SkogCLI script remove`

Remove a custom script.

Remove a custom script.

**Usage**:

```console
$ SkogCLI script remove [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the script to remove  [required]

**Options**:

* `--global / --no-global`: Include global scripts  [default: global]
* `-f, --force`: Force removal without confirmation
* `--help`: Show this message and exit.

### `SkogCLI script info`

Show detailed information about a script.

Show detailed information about a script.

**Usage**:

```console
$ SkogCLI script info [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the script  [required]

**Options**:

* `--global / --no-global`: Include global scripts  [default: global]
* `--help`: Show this message and exit.

### `SkogCLI script code`

View or update script code without using an editor.

View or update script code without using an editor.

**Usage**:

```console
$ SkogCLI script code [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the script  [required]

**Options**:

* `-c, --content TEXT`: New content for the script (if not provided, displays current content)
* `-f, --file PATH`: Read new content from this file
* `-o, --output PATH`: Write content to this file instead of updating the script
* `--global / --no-global`: Include global scripts  [default: global]
* `--help`: Show this message and exit.

### `SkogCLI script batch`

Process multiple scripts with a single command.

Process multiple scripts with a single command.

**Usage**:

```console
$ SkogCLI script batch [OPTIONS] SCRIPT_LIST
```

**Arguments**:

* `SCRIPT_LIST`: Path to a file containing a list of scripts to process, one per line  [required]

**Options**:

* `-c, --command TEXT`: Command to run on each script (code, run, info, etc.)  [default: code]
* `--global / --no-global`: Include global scripts  [default: global]
* `-o, --output-dir PATH`: Directory to write output files to
* `--continue-on-error`: Continue processing even if errors occur
* `-p, --pattern TEXT`: Pattern to search for (when using &#x27;search&#x27; command)
* `-r, --replacement TEXT`: Replacement string (when using &#x27;transform&#x27; command)
* `--help`: Show this message and exit.

### `SkogCLI script update-metadata`

Update metadata for a script.

Update metadata for a script.

**Usage**:

```console
$ SkogCLI script update-metadata [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the script  [required]

**Options**:

* `-d, --description TEXT`: Description of the script
* `--global / --no-global`: Include global scripts  [default: global]
* `--help`: Show this message and exit.

### `SkogCLI script templates`

List available script templates.

List available script templates.

**Usage**:

```console
$ SkogCLI script templates [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `SkogCLI script export`

Export a script to a JSON file that can be shared and imported by others.
    
    The export file contains the script&#x27;s code, metadata, and other information.
    

Export a script to a JSON file to share with others.

**Usage**:

```console
$ SkogCLI script export [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the script to export  [required]

**Options**:

* `-o, --output PATH`: Output JSON file path
* `--metadata / --no-metadata`: Include metadata in export  [default: metadata]
* `--global / --no-global`: Include global scripts  [default: global]
* `--help`: Show this message and exit.

### `SkogCLI script transform`

Transform script content using regular expressions.

Transform script content using regular expressions.

**Usage**:

```console
$ SkogCLI script transform [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the script to transform  [required]

**Options**:

* `-p, --pattern TEXT`: Regular expression pattern to search for  [required]
* `-r, --replacement TEXT`: Replacement string  [required]
* `-o, --output PATH`: Write transformed content to this file instead of updating the script
* `--global / --no-global`: Include global scripts  [default: global]
* `--backup / --no-backup`: Create a backup before transforming  [default: backup]
* `--help`: Show this message and exit.

### `SkogCLI script search`

Search for text in scripts.

Search for text in scripts.

**Usage**:

```console
$ SkogCLI script search [OPTIONS] PATTERN
```

**Arguments**:

* `PATTERN`: Text or regular expression to search for  [required]

**Options**:

* `-r, --regex`: Treat pattern as a regular expression
* `-c, --case-sensitive`: Make search case-sensitive
* `--global / --no-global`: Include global scripts  [default: global]
* `-o, --output PATH`: Write results to this file
* `--ignore-errors`: Continue searching even if errors occur
* `--help`: Show this message and exit.

### `SkogCLI script generate`

Generate a script from a description using AI or templates.

Generate a script from a description using AI or templates.

**Usage**:

```console
$ SkogCLI script generate [OPTIONS] NAME DESCRIPTION
```

**Arguments**:

* `NAME`: Name for the new script  [required]
* `DESCRIPTION`: Description of what the script should do  [required]

**Options**:

* `-t, --type TEXT`: Script type (python or shell)  [default: python]
* `-g, --global`: Install as a global script
* `--edit / --no-edit`: Open the script in an editor after creation  [default: edit]
* `-e, --editor TEXT`: Specify which editor to use (defaults to $EDITOR)
* `-m, --model TEXT`: AI model to use for generation  [default: gpt-3.5-turbo]
* `-k, --api-key TEXT`: API key for the AI service
* `-l, --local`: Use local templates instead of AI
* `--help`: Show this message and exit.

### `SkogCLI script import`

Import a script from a JSON export file created by the &#x27;script export&#x27; command.
    
    The export file contains the script&#x27;s code, metadata, and other information.
    

Import a script from an export file.

**Usage**:

```console
$ SkogCLI script import [OPTIONS] FILE
```

**Arguments**:

* `FILE`: Path to the JSON export file created by &#x27;script export&#x27;  [required]

**Options**:

* `-g, --global`: Install as a global script
* `--overwrite`: Overwrite existing script
* `--help`: Show this message and exit.

### `SkogCLI script import-file`

Import an existing script file into the scripts directory.
    
    This command copies a script file from anywhere on your filesystem into the SkogCLI
    scripts directory, making it available as a SkogCLI script.
    

Import an existing script file into the scripts directory.

**Usage**:

```console
$ SkogCLI script import-file [OPTIONS] FILE
```

**Arguments**:

* `FILE`: Path to the existing script file to add  [required]

**Options**:

* `-n, --name TEXT`: Name for the script (defaults to original filename)
* `-g, --global`: Install as a global script
* `--overwrite`: Overwrite existing script
* `-e, --edit`: Open the script in an editor after adding
* `--editor TEXT`: Specify which editor to use (defaults to $EDITOR)
* `--help`: Show this message and exit.

### `SkogCLI script copy`

Copy a script to create a new one.

Copy a script to create a new one.

**Usage**:

```console
$ SkogCLI script copy [OPTIONS] SOURCE DESTINATION
```

**Arguments**:

* `SOURCE`: Name of the source script  [required]
* `DESTINATION`: Name for the new script  [required]

**Options**:

* `--global-source / --no-global-source`: Include global scripts as source  [default: global-source]
* `-g, --global-dest`: Create as a global script
* `--edit / --no-edit`: Open the new script in an editor  [default: edit]
* `-e, --editor TEXT`: Specify which editor to use (defaults to $EDITOR)
* `--help`: Show this message and exit.

## `SkogCLI agent`

Interact with SkogAI agents

**Usage**:

```console
$ SkogCLI agent [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `migrate-scripts`: Create script files for all existing agents.
* `send`: Send a message to an agent and display the...
* `list`: List all available agents and their...
* `create`: Create a new agent with the specified...
* `set`: Set a configuration value for an agent.
* `get`: Get a configuration value for an agent.
* `read`: Read information about an agent.
* `edit-script`: Open the agent&#x27;s script in your default...
* `delete`: Delete an agent and its configuration.

### `SkogCLI agent migrate-scripts`

Create script files for all existing agents.

    This command will create script files in the ./scripts directory for all
    configured agents, based on their current command templates.
    

Migrate all agents to use script files.

**Usage**:

```console
$ SkogCLI agent migrate-scripts [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `SkogCLI agent send`

Send a message to an agent and display the response.

    Examples:

    Send a simple message:
      skogcli agent send &quot;What is the capital of France?&quot;

    Specify an agent:
      skogcli agent send &quot;Write a Python function to calculate Fibonacci numbers&quot; --agent coder

    Use a specific model:
      skogcli agent send &quot;Summarize this article&quot; --model gpt-4
    

Send a message to an agent.

**Usage**:

```console
$ SkogCLI agent send [OPTIONS] MESSAGE
```

**Arguments**:

* `MESSAGE`: Message to send to the agent  [required]

**Options**:

* `-a, --agent TEXT`: Name of the agent to send the message to  [default: default]
* `-m, --model TEXT`: Model to use for this interaction
* `-s, --system TEXT`: System prompt to use for this interaction
* `-r, --raw`: Display raw response without formatting
* `-j, --json`: Output response in JSON format
* `--help`: Show this message and exit.

### `SkogCLI agent list`

List all available agents and their configurations.

List available agents.

**Usage**:

```console
$ SkogCLI agent list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `SkogCLI agent create`

Create a new agent with the specified configuration.

    Examples:

    Create a basic agent:
      skogcli agent create researcher

    Create an agent with a specific model:
      skogcli agent create coder --model gpt-4

    Create an agent with a system prompt:
      skogcli agent create assistant --system &quot;You are a helpful assistant.&quot;
    

Create a new agent.

**Usage**:

```console
$ SkogCLI agent create [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name for the new agent  [required]

**Options**:

* `-m, --model TEXT`: Model to use for this agent
* `-s, --system TEXT`: System prompt for this agent
* `-d, --description TEXT`: Description of this agent
* `-c, --command TEXT`: Command template to use for this agent (e.g., &#x27;python -m goose run --text {message}&#x27;)
* `--help`: Show this message and exit.

### `SkogCLI agent set`

Set a configuration value for an agent.

    If the agent name is not included in the key, it must be provided with --agent.

    Examples:

    Set a model for an agent:
      skogcli agent set model gpt-4 --agent researcher

    Set a system prompt:
      skogcli agent set system_prompt &quot;You are a helpful assistant.&quot; --agent assistant

    Set a configuration directly:
      skogcli agent set agent.coder.model gpt-4
    

Set a configuration value for an agent.

**Usage**:

```console
$ SkogCLI agent set [OPTIONS] KEY VALUE
```

**Arguments**:

* `KEY`: Configuration key  [required]
* `VALUE`: Value to set  [required]

**Options**:

* `-a, --agent TEXT`: Agent name (if not included in the key)
* `--help`: Show this message and exit.

### `SkogCLI agent get`

Get a configuration value for an agent.

    If the agent name is not included in the key, it must be provided with --agent.

    Examples:

    Get a model for an agent:
      skogcli agent get model --agent researcher

    Get a system prompt:
      skogcli agent get system_prompt --agent assistant

    Get a configuration directly:
      skogcli agent get agent.coder.model
    

Get a configuration value for an agent.

**Usage**:

```console
$ SkogCLI agent get [OPTIONS] KEY
```

**Arguments**:

* `KEY`: Configuration key  [required]

**Options**:

* `-a, --agent TEXT`: Agent name (if not included in the key)
* `-r, --raw`: Output raw value without formatting
* `-j, --json`: Output as formatted JSON
* `--help`: Show this message and exit.

### `SkogCLI agent read`

Read information about an agent.

    Examples:

    Read agent information:
      skogcli agent read default

    Read agent using option:
      skogcli agent read --agent default

    Get raw output:
      skogcli agent read researcher --raw
    

Read information about an agent.

**Usage**:

```console
$ SkogCLI agent read [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Name of the agent to read

**Options**:

* `-a, --agent TEXT`: Name of the agent to read (alternative to NAME argument)
* `-r, --raw`: Display raw response without formatting
* `-j, --json`: Output response in JSON format
* `--help`: Show this message and exit.

### `SkogCLI agent edit-script`

Open the agent&#x27;s script in your default editor.

    Examples:

    Edit an agent script:
      skogcli agent edit-script researcher
    

Edit the script for an agent.

**Usage**:

```console
$ SkogCLI agent edit-script [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the agent whose script to edit  [required]

**Options**:

* `--help`: Show this message and exit.

### `SkogCLI agent delete`

Delete an agent and its configuration.

    Examples:

    Delete an agent with confirmation:
      skogcli agent delete researcher

    Force delete without confirmation:
      skogcli agent delete researcher --force
    

Delete an agent.

**Usage**:

```console
$ SkogCLI agent delete [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the agent to delete  [required]

**Options**:

* `-f, --force`: Delete without confirmation
* `--help`: Show this message and exit.
