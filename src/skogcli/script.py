"""Script management commands for SkogCLI."""

import os
import sys
import json
import shutil
import subprocess
import importlib.util
import typer
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from .decorators import with_explanation
from .settings import get_setting, set_setting

console = Console()

# Create a Typer app for the script commands
script_app = typer.Typer(
    help="Script management commands",
    no_args_is_help=True
)

# Script templates
TEMPLATES = {
    "basic": {
        "python": """#!/usr/bin/env python3
\"\"\"
Custom script for SkogCLI.
\"\"\"

def main(args=None):
    \"\"\"Main entry point for the script.\"\"\"
    if args is None:
        args = []
    
    print(f"Hello from {__file__}!")
    print(f"Arguments: {args}")

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
""",
        "shell": """#!/bin/bash
# Custom script for SkogCLI

echo "Hello from $(basename $0)!"
echo "Arguments: $@"
"""
    },
    "line_counter": {
        "python": """#!/usr/bin/env python3
\"\"\"
Line counting script for files and directories.
\"\"\"
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

def count_lines_in_file(file_path: Path) -> Tuple[int, int, int]:
    \"\"\"
    Count the number of lines, blank lines, and comment lines in a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple of (total lines, blank lines, comment lines)
    \"\"\"
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist")
        return (0, 0, 0)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if line.strip() == '')
        
        # Count comment lines based on file extension
        comment_lines = 0
        ext = file_path.suffix.lower()
        
        # Define comment markers for different file types
        comment_markers = {
            '.py': '#',
            '.js': '//',
            '.java': '//',
            '.c': '//',
            '.cpp': '//',
            '.h': '//',
            '.sh': '#',
            '.rb': '#',
            '.pl': '#',
            '.php': '//',
            '.html': '<!--',
            '.xml': '<!--',
            '.css': '/*',
        }
        
        if ext in comment_markers:
            marker = comment_markers[ext]
            comment_lines = sum(1 for line in lines if line.strip().startswith(marker))
        
        return (total_lines, blank_lines, comment_lines)
    
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return (0, 0, 0)

def count_lines_in_directory(dir_path: Path, extensions: Optional[List[str]] = None) -> Dict[str, Tuple[int, int, int]]:
    \"\"\"
    Count lines in all files in a directory (recursively).
    
    Args:
        dir_path: Path to the directory
        extensions: List of file extensions to include (e.g., ['.py', '.js'])
                   If None, count all files
    
    Returns:
        Dictionary mapping file paths to line counts
    \"\"\"
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: Directory {dir_path} does not exist or is not a directory")
        return {}
    
    results = {}
    
    try:
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = Path(root) / file
                
                # Skip if we're filtering by extension and this file doesn't match
                if extensions and not any(file.lower().endswith(ext) for ext in extensions):
                    continue
                
                # Skip binary files and very large files
                if file_path.stat().st_size > 1024 * 1024:  # Skip files > 1MB
                    continue
                
                try:
                    # Try to read the first few bytes to check if it's binary
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        f.read(1024)
                    
                    # If we got here, it's probably a text file
                    line_counts = count_lines_in_file(file_path)
                    if line_counts[0] > 0:  # Only include files with lines
                        results[str(file_path)] = line_counts
                
                except UnicodeDecodeError:
                    # Probably a binary file
                    continue
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    
    except Exception as e:
        print(f"Error scanning directory {dir_path}: {str(e)}")
    
    return results

def print_summary(results: Dict[str, Tuple[int, int, int]]) -> None:
    \"\"\"Print a summary of the line counting results.\"\"\"
    if not results:
        print("No files found or processed.")
        return
    
    # Calculate totals
    total_files = len(results)
    total_lines = sum(counts[0] for counts in results.values())
    total_blank = sum(counts[1] for counts in results.values())
    total_comments = sum(counts[2] for counts in results.values())
    total_code = total_lines - total_blank - total_comments
    
    # Print summary
    print(f"\\nSummary:")
    print(f"  Total files: {total_files}")
    print(f"  Total lines: {total_lines}")
    print(f"  Code lines: {total_code}")
    print(f"  Blank lines: {total_blank}")
    print(f"  Comment lines: {total_comments}")
    
    if total_lines > 0:
        print(f"\\nPercentages:")
        print(f"  Code: {total_code / total_lines * 100:.1f}%")
        print(f"  Comments: {total_comments / total_lines * 100:.1f}%")
        print(f"  Blank: {total_blank / total_lines * 100:.1f}%")

def main(args=None):
    \"\"\"Main entry point for the script.\"\"\"
    if args is None or len(args) == 0:
        print("Usage: count_lines [file_or_directory] [extension1,extension2,...]")
        print("Examples:")
        print("  count_lines myfile.py")
        print("  count_lines src/")
        print("  count_lines src/ .py,.js,.html")
        return
    
    path = Path(args[0])
    
    # Parse extensions if provided
    extensions = None
    if len(args) > 1 and args[1]:
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in args[1].split(',')]
        print(f"Filtering by extensions: {', '.join(extensions)}")
    
    if path.is_file():
        # Count lines in a single file
        total, blank, comments = count_lines_in_file(path)
        code = total - blank - comments
        
        print(f"File: {path}")
        print(f"  Total lines: {total}")
        print(f"  Code lines: {code}")
        print(f"  Blank lines: {blank}")
        print(f"  Comment lines: {comments}")
    
    elif path.is_dir():
        # Count lines in a directory
        print(f"Scanning directory: {path}")
        results = count_lines_in_directory(path, extensions)
        
        # Print detailed results for each file
        for file_path, (total, blank, comments) in sorted(results.items()):
            code = total - blank - comments
            rel_path = Path(file_path).relative_to(path)
            print(f"{rel_path}: {total} lines ({code} code, {blank} blank, {comments} comments)")
        
        # Print summary
        print_summary(results)
    
    else:
        print(f"Error: {path} does not exist")

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
""",
        "shell": """#!/bin/bash
# Line counting script for files and directories

# Function to count lines in a file
count_lines_in_file() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        echo "Error: File $file does not exist"
        return 1
    fi
    
    # Count total lines
    local total_lines=$(wc -l < "$file")
    
    # Count blank lines
    local blank_lines=$(grep -c "^[[:space:]]*$" "$file")
    
    # Count comment lines (basic detection)
    local comment_lines=0
    local ext="${file##*.}"
    
    case "$ext" in
        py|sh|bash|rb)
            comment_lines=$(grep -c "^[[:space:]]*#" "$file")
            ;;
        js|java|c|cpp|h|php)
            comment_lines=$(grep -c "^[[:space:]]*//" "$file")
            comment_lines=$((comment_lines + $(grep -c "^[[:space:]]*/\\*" "$file")))
            ;;
        html|xml)
            comment_lines=$(grep -c "^[[:space:]]*<!--" "$file")
            ;;
    esac
    
    # Calculate code lines
    local code_lines=$((total_lines - blank_lines - comment_lines))
    
    echo "File: $file"
    echo "  Total lines: $total_lines"
    echo "  Code lines: $code_lines"
    echo "  Blank lines: $blank_lines"
    echo "  Comment lines: $comment_lines"
}

# Function to count lines in all files in a directory
count_lines_in_directory() {
    local dir="$1"
    local extensions="$2"
    
    if [ ! -d "$dir" ]; then
        echo "Error: Directory $dir does not exist"
        return 1
    fi
    
    echo "Scanning directory: $dir"
    
    local total_files=0
    local total_lines=0
    local total_blank=0
    local total_comments=0
    local total_code=0
    
    # Create a temporary file to store results
    local temp_file=$(mktemp)
    
    # Find files and process them
    if [ -z "$extensions" ]; then
        # Process all text files
        find "$dir" -type f -size -1M | while read -r file; do
            # Skip binary files (simple check)
            if file "$file" | grep -q "text"; then
                process_file "$file" >> "$temp_file"
            fi
        done
    else
        # Process only files with specified extensions
        local ext_pattern=$(echo "$extensions" | sed 's/,/\\|/g')
        find "$dir" -type f -size -1M -name "*.$ext_pattern" | while read -r file; do
            process_file "$file" >> "$temp_file"
        done
    fi
    
    # Display results
    if [ -s "$temp_file" ]; then
        cat "$temp_file"
        
        # Calculate totals
        total_files=$(grep -c "^File:" "$temp_file")
        total_lines=$(grep "Total lines:" "$temp_file" | awk '{sum += $3} END {print sum}')
        total_blank=$(grep "Blank lines:" "$temp_file" | awk '{sum += $3} END {print sum}')
        total_comments=$(grep "Comment lines:" "$temp_file" | awk '{sum += $3} END {print sum}')
        total_code=$(grep "Code lines:" "$temp_file" | awk '{sum += $3} END {print sum}')
        
        # Print summary
        echo -e "\\nSummary:"
        echo "  Total files: $total_files"
        echo "  Total lines: $total_lines"
        echo "  Code lines: $total_code"
        echo "  Blank lines: $total_blank"
        echo "  Comment lines: $total_comments"
        
        if [ "$total_lines" -gt 0 ]; then
            echo -e "\\nPercentages:"
            echo "  Code: $(awk -v code=$total_code -v total=$total_lines 'BEGIN {printf "%.1f", (code/total*100)}')%"
            echo "  Comments: $(awk -v comments=$total_comments -v total=$total_lines 'BEGIN {printf "%.1f", (comments/total*100)}')%"
            echo "  Blank: $(awk -v blank=$total_blank -v total=$total_lines 'BEGIN {printf "%.1f", (blank/total*100)}')%"
        fi
    else
        echo "No files found or processed."
    fi
    
    # Clean up
    rm -f "$temp_file"
}

# Function to process a single file
process_file() {
    local file="$1"
    
    # Count total lines
    local total_lines=$(wc -l < "$file" 2>/dev/null || echo 0)
    
    # Count blank lines
    local blank_lines=$(grep -c "^[[:space:]]*$" "$file" 2>/dev/null || echo 0)
    
    # Count comment lines (basic detection)
    local comment_lines=0
    local ext="${file##*.}"
    
    case "$ext" in
        py|sh|bash|rb)
            comment_lines=$(grep -c "^[[:space:]]*#" "$file" 2>/dev/null || echo 0)
            ;;
        js|java|c|cpp|h|php)
            comment_lines=$(grep -c "^[[:space:]]*//" "$file" 2>/dev/null || echo 0)
            comment_lines=$((comment_lines + $(grep -c "^[[:space:]]*/\\*" "$file" 2>/dev/null || echo 0)))
            ;;
        html|xml)
            comment_lines=$(grep -c "^[[:space:]]*<!--" "$file" 2>/dev/null || echo 0)
            ;;
    esac
    
    # Calculate code lines
    local code_lines=$((total_lines - blank_lines - comment_lines))
    
    # Print results for this file
    echo "File: $file"
    echo "  Total lines: $total_lines"
    echo "  Code lines: $code_lines"
    echo "  Blank lines: $blank_lines"
    echo "  Comment lines: $comment_lines"
    echo ""
}

# Main function
main() {
    if [ $# -eq 0 ]; then
        echo "Usage: count_lines [file_or_directory] [extensions]"
        echo "Examples:"
        echo "  count_lines myfile.py"
        echo "  count_lines src/"
        echo "  count_lines src/ py,js,html"
        return 1
    fi
    
    local path="$1"
    local extensions="$2"
    
    if [ -f "$path" ]; then
        # Count lines in a single file
        count_lines_in_file "$path"
    elif [ -d "$path" ]; then
        # Count lines in a directory
        count_lines_in_directory "$path" "$extensions"
    else
        echo "Error: $path does not exist"
        return 1
    fi
}

# Run the script
main "$@"
"""
    },
    "data_processing": {
        "python": """#!/usr/bin/env python3
\"\"\"
Data processing script for SkogCLI.
\"\"\"
import json
import csv
import sys
from pathlib import Path

def process_json(input_file, output_file=None):
    \"\"\"Process JSON data.\"\"\"
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Process the data here
    processed_data = data
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(processed_data, f, indent=2)
        print(f"Processed data written to {output_file}")
    else:
        print(json.dumps(processed_data, indent=2))

def process_csv(input_file, output_file=None):
    \"\"\"Process CSV data.\"\"\"
    rows = []
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    # Process the data here
    processed_rows = rows
    
    if output_file:
        with open(output_file, 'w') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(processed_rows)
        print(f"Processed data written to {output_file}")
    else:
        for row in processed_rows:
            print(row)

def main(args=None):
    \"\"\"Main entry point for the script.\"\"\"
    if args is None or len(args) < 1:
        print("Usage: script input_file [output_file]")
        return
    
    input_file = args[0]
    output_file = args[1] if len(args) > 1 else None
    
    if not Path(input_file).exists():
        print(f"Error: Input file {input_file} does not exist")
        return
    
    if input_file.endswith('.json'):
        process_json(input_file, output_file)
    elif input_file.endswith('.csv'):
        process_csv(input_file, output_file)
    else:
        print(f"Error: Unsupported file format for {input_file}")

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
"""
    },
    "api_client": {
        "python": """#!/usr/bin/env python3
\"\"\"
API client script for SkogCLI.
\"\"\"
import json
import sys
import requests
from urllib.parse import urljoin

BASE_URL = "https://api.example.com"  # Replace with your API base URL

def make_request(endpoint, method="GET", data=None, params=None):
    \"\"\"Make an API request.\"\"\"
    url = urljoin(BASE_URL, endpoint)
    headers = {
        "Content-Type": "application/json",
        # Add any authentication headers here
    }
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"Error: Unsupported method {method}")
            return None
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def main(args=None):
    \"\"\"Main entry point for the script.\"\"\"
    if args is None or len(args) < 1:
        print("Usage: script endpoint [method] [data]")
        return
    
    endpoint = args[0]
    method = args[1].upper() if len(args) > 1 else "GET"
    data = None
    
    if len(args) > 2 and (method == "POST" or method == "PUT"):
        try:
            data = json.loads(args[2])
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON data: {args[2]}")
            return
    
    result = make_request(endpoint, method, data)
    if result:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
"""
    },
    "system_info": {
        "shell": """#!/bin/bash
# System information script for SkogCLI

echo "=== System Information ==="
echo "Hostname: $(hostname)"
echo "Kernel: $(uname -r)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')"
echo

echo "=== CPU Information ==="
echo "CPU Model: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2 | sed 's/^[ \t]*//')"
echo "CPU Cores: $(grep -c processor /proc/cpuinfo)"
echo

echo "=== Memory Information ==="
free -h
echo

echo "=== Disk Usage ==="
df -h
echo

echo "=== Network Information ==="
ip -br addr show
echo

echo "=== Process Information ==="
echo "Top 5 CPU processes:"
ps aux --sort=-%cpu | head -6
echo
echo "Top 5 Memory processes:"
ps aux --sort=-%mem | head -6
"""
    }
}

def get_global_scripts_dir() -> Path:
    """Get the global scripts directory, creating it if it doesn't exist."""
    # Use /usr/local/share for global scripts
    scripts_dir = Path("/usr/local/share/skogcli/scripts")
    return scripts_dir

def get_user_scripts_dir() -> Path:
    """Get the user scripts directory, creating it if it doesn't exist."""
    scripts_dir = Path.home() / ".config" / "skogcli" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    return scripts_dir

def get_metadata_file() -> Path:
    """Get the path to the script metadata file."""
    metadata_dir = Path.home() / ".config" / "skogcli"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    return metadata_dir / "script_metadata.json"

def load_metadata() -> Dict[str, Any]:
    """Load script metadata from the metadata file."""
    metadata_file = get_metadata_file()
    
    if not metadata_file.exists():
        return {}
    
    try:
        with open(metadata_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/] Metadata file is corrupted.")
        return {}

def save_metadata(metadata: Dict[str, Any]) -> None:
    """Save script metadata to the metadata file."""
    metadata_file = get_metadata_file()
    
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

def update_script_metadata(script_path: Path, metadata: Dict[str, Any]) -> None:
    """Update metadata for a script."""
    all_metadata = load_metadata()
    script_key = str(script_path)
    
    if script_key not in all_metadata:
        all_metadata[script_key] = {}
    
    # Update with new metadata
    all_metadata[script_key].update(metadata)
    
    # Add/update timestamp
    all_metadata[script_key]["last_updated"] = datetime.now().isoformat()
    
    save_metadata(all_metadata)

def get_script_metadata(script_path: Path) -> Dict[str, Any]:
    """Get metadata for a script."""
    all_metadata = load_metadata()
    script_key = str(script_path)
    
    return all_metadata.get(script_key, {})

def list_available_scripts(global_scripts: bool = False) -> List[Path]:
    """List all available scripts in the scripts directory."""
    scripts = []
    
    # User scripts
    user_scripts_dir = get_user_scripts_dir()
    scripts.extend(list(user_scripts_dir.glob("*.*")))
    
    # Global scripts if requested
    if global_scripts:
        global_scripts_dir = get_global_scripts_dir()
        if global_scripts_dir.exists():
            scripts.extend(list(global_scripts_dir.glob("*.*")))
    
    # Filter out directories that might have been included due to having extensions
    scripts = [script for script in scripts if not script.is_dir()]
    
    return scripts

def get_script_names() -> List[str]:
    """Get a list of all available script names for completion."""
    scripts = list_available_scripts(global_scripts=True)
    return [script.stem for script in scripts]

def get_script_templates() -> List[str]:
    """Get a list of available script templates for completion."""
    return list(TEMPLATES.keys())

def get_script_types() -> List[str]:
    """Get a list of available script types for completion."""
    return ["python", "shell"]

def find_script(name: str, global_scripts: bool = True) -> Optional[Path]:
    """Find a script by name, checking both user and global directories."""
    # Check user scripts first
    user_scripts_dir = get_user_scripts_dir()
    for ext in [".py", ".sh", ""]:
        test_path = user_scripts_dir / f"{name}{ext}"
        if test_path.exists():
            return test_path
    
    # Check global scripts if enabled
    if global_scripts:
        global_scripts_dir = get_global_scripts_dir()
        if global_scripts_dir.exists():
            for ext in [".py", ".sh", ""]:
                test_path = global_scripts_dir / f"{name}{ext}"
                if test_path.exists():
                    return test_path
    
    return None

def is_executable(path: Path) -> bool:
    """Check if a file is executable."""
    return os.access(path, os.X_OK)

@script_app.callback()
def script_callback():
    """Script management commands."""
    pass

@script_app.command("list")
@with_explanation("List all available custom scripts.")
def list_scripts(
    global_scripts: bool = typer.Option(True, "--global/--no-global", help="Include global scripts"),
    show_metadata: bool = typer.Option(False, "--metadata", "-m", help="Show script metadata")
):
    """List all available custom scripts."""
    scripts = list_available_scripts(global_scripts)
    
    if not scripts:
        console.print("[yellow]No custom scripts found.[/]")
        console.print(f"Add scripts to [bold]{get_user_scripts_dir()}[/] to get started.")
        return
    
    if show_metadata:
        # Create a table with metadata
        table = Table(title="Available Scripts")
        table.add_column("Name", style="bold")
        table.add_column("Type")
        table.add_column("Location")
        table.add_column("Last Updated")
        table.add_column("Description")
        
        for script in scripts:
            script_type = "Unknown"
            if script.suffix == ".py":
                script_type = "Python"
            elif script.suffix == ".sh":
                script_type = "Shell"
            elif is_executable(script):
                script_type = "Executable"
            
            # Get metadata
            metadata = get_script_metadata(script)
            last_updated = metadata.get("last_updated", "Never")
            description = metadata.get("description", "")
            
            # Determine location (user or global)
            location = "User" if str(get_user_scripts_dir()) in str(script) else "Global"
            
            table.add_row(
                script.stem,
                script_type,
                location,
                last_updated,
                description
            )
        
        console.print(table)
    else:
        console.print("[bold]Available custom scripts:[/]")
        for script in scripts:
            script_type = "Unknown"
            if script.suffix == ".py":
                script_type = "Python"
            elif script.suffix == ".sh":
                script_type = "Shell"
            elif is_executable(script):
                script_type = "Executable"
            
            # Determine location (user or global)
            location = "[cyan]user[/]" if str(get_user_scripts_dir()) in str(script) else "[magenta]global[/]"
            
            console.print(f"  [bold]{script.stem}[/] - {script_type} script ({location})")

@script_app.command("run")
@with_explanation("Run a custom script.")
def run_script(
    name: str = typer.Argument(
        ..., 
        help="Name of the script to run",
        autocompletion=lambda: get_script_names()
    ),
    args: List[str] = typer.Argument(None, help="Arguments to pass to the script"),
    global_scripts: bool = typer.Option(True, "--global/--no-global", help="Include global scripts")
):
    """Run a custom script."""
    # Find the script
    script_path = find_script(name, global_scripts)
    
    if not script_path:
        console.print(f"[bold red]Error:[/] Script '{name}' not found.")
        return
    
    # Update metadata to track usage
    metadata = get_script_metadata(script_path)
    run_count = metadata.get("run_count", 0) + 1
    update_script_metadata(script_path, {"run_count": run_count, "last_run": datetime.now().isoformat()})
    
    # Run the script based on its type
    if script_path.suffix == ".py":
        # Run Python script
        try:
            # Add script directory to path
            scripts_dir = script_path.parent
            sys.path.insert(0, str(scripts_dir))
            
            # Load the module
            spec = importlib.util.spec_from_file_location(name, script_path)
            if spec is None or spec.loader is None:
                console.print(f"[bold red]Error:[/] Failed to load Python script '{name}'.")
                return
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if the module has a main function
            if hasattr(module, "main"):
                # Call the main function with arguments
                module.main(args)
            else:
                console.print("[yellow]Warning:[/] Python script has no 'main' function.")
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
    else:
        # Run shell script or executable
        try:
            # Make sure the script is executable
            if not is_executable(script_path):
                script_path.chmod(script_path.stat().st_mode | 0o755)
            
            # Run the script with arguments
            cmd = [str(script_path)] + (args or [])
            result = subprocess.run(cmd, check=True)
            
            if result.returncode != 0:
                console.print(f"[bold red]Error:[/] Script exited with code {result.returncode}")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")

@script_app.command("add")
@with_explanation("Add a new custom script.")
def add_script(
    name: str = typer.Argument(..., help="Name for the new script"),
    type: str = typer.Option(
        "python", 
        "--type", "-t", 
        help="Script type (python or shell)",
        autocompletion=lambda: get_script_types()
    ),
    template: str = typer.Option(
        "basic", 
        "--template", 
        help="Script template to use",
        autocompletion=lambda: get_script_templates()
    ),
    global_script: bool = typer.Option(False, "--global", "-g", help="Install as a global script"),
    description: str = typer.Option("", "--description", "-d", help="Description of the script"),
    edit: bool = typer.Option(True, "--edit/--no-edit", help="Open the script in an editor after creation"),
    editor: Optional[str] = typer.Option(None, "--editor", "-e", help="Specify which editor to use (defaults to $EDITOR)")
):
    """Add a new custom script."""
    # Determine the scripts directory
    if global_script:
        # Check if user has permission to write to global directory
        global_dir = get_global_scripts_dir()
        if not os.access(global_dir.parent, os.W_OK):
            console.print("[bold red]Error:[/] You don't have permission to create global scripts.")
            console.print("Try running with sudo or use --no-global for a user script.")
            return
        scripts_dir = global_dir
        scripts_dir.mkdir(parents=True, exist_ok=True)
    else:
        scripts_dir = get_user_scripts_dir()
    
    # Determine file extension based on type
    ext = ".py" if type.lower() == "python" else ".sh"
    script_path = scripts_dir / f"{name}{ext}"
    
    # Check if script already exists
    if script_path.exists():
        overwrite = typer.confirm(f"Script '{name}' already exists. Overwrite?")
        if not overwrite:
            return
    
    # Get template content
    template_content = ""
    if template in TEMPLATES and type.lower() in TEMPLATES[template]:
        template_content = TEMPLATES[template][type.lower()]
    else:
        # Fall back to basic template if the requested one doesn't exist
        available_templates = list(TEMPLATES.keys())
        console.print(f"[yellow]Warning:[/] Template '{template}' not found. Using 'basic' template.")
        console.print(f"Available templates: {', '.join(available_templates)}")
        template_content = TEMPLATES["basic"][type.lower()]
    
    # Create script with template content
    with open(script_path, "w") as f:
        f.write(template_content)
    
    # Make the script executable
    script_path.chmod(script_path.stat().st_mode | 0o755)
    
    # Save metadata
    metadata = {
        "description": description,
        "template": template,
        "type": type.lower(),
        "created": datetime.now().isoformat(),
        "run_count": 0
    }
    update_script_metadata(script_path, metadata)
    
    location = "global" if global_script else "user"
    console.print(f"[green]Created {location} script:[/] {script_path}")
    
    # Open in editor if requested
    if edit:
        # Get the editor from the environment or use the provided one
        editor_cmd = editor or os.environ.get("EDITOR", "nano")
        try:
            exit_code = subprocess.call([editor_cmd, str(script_path)])
            if exit_code == 0:
                console.print("[green]Script edited successfully.[/]")
            else:
                console.print(f"[bold red]Error:[/] Editor exited with code {exit_code}")
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/] Editor '{editor_cmd}' not found. Set the EDITOR environment variable or use --editor.")
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")

@script_app.command("edit")
@with_explanation("Edit an existing custom script.")
def edit_script(
    name: str = typer.Argument(
        ..., 
        help="Name of the script to edit",
        autocompletion=lambda: get_script_names()
    ),
    global_script: bool = typer.Option(True, "--global/--no-global", help="Include global scripts"),
    editor: Optional[str] = typer.Option(None, "--editor", "-e", help="Specify which editor to use (defaults to $EDITOR)")
):
    """Edit an existing custom script."""
    # Find the script
    script_path = find_script(name, global_script)
    
    if not script_path:
        console.print(f"[bold red]Error:[/] Script '{name}' not found.")
        return
    
    # Check if user has permission to edit the script
    if not os.access(script_path, os.W_OK):
        console.print("[bold red]Error:[/] You don't have permission to edit this script.")
        console.print("Try running with sudo if it's a global script.")
        return
    
    # Get the editor from the environment or use the provided one
    editor_cmd = editor or os.environ.get("EDITOR", "nano")
    
    # Open in editor
    try:
        exit_code = subprocess.call([editor_cmd, str(script_path)])
        if exit_code == 0:
            # Update metadata
            update_script_metadata(script_path, {"last_edited": datetime.now().isoformat()})
            console.print("[green]Script edited successfully.[/]")
        else:
            console.print(f"[bold red]Error:[/] Editor exited with code {exit_code}")
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/] Editor '{editor_cmd}' not found. Set the EDITOR environment variable or use --editor.")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")

@script_app.command("remove")
@with_explanation("Remove a custom script.")
def remove_script(
    name: str = typer.Argument(
        ..., 
        help="Name of the script to remove",
        autocompletion=lambda: get_script_names()
    ),
    global_script: bool = typer.Option(True, "--global/--no-global", help="Include global scripts"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal without confirmation")
):
    """Remove a custom script."""
    # Find the script
    script_path = find_script(name, global_script)
    
    if not script_path:
        console.print(f"[bold red]Error:[/] Script '{name}' not found.")
        return
    
    # Check if user has permission to remove the script
    if not os.access(script_path, os.W_OK):
        console.print("[bold red]Error:[/] You don't have permission to remove this script.")
        console.print("Try running with sudo if it's a global script.")
        return
    
    # Confirm removal
    if not force:
        location = "global" if str(get_global_scripts_dir()) in str(script_path) else "user"
        confirm = typer.confirm(f"Are you sure you want to remove {location} script '{name}'?")
        if not confirm:
            return
    
    # Remove the script
    try:
        script_path.unlink()
        
        # Remove metadata
        all_metadata = load_metadata()
        script_key = str(script_path)
        if script_key in all_metadata:
            del all_metadata[script_key]
            save_metadata(all_metadata)
        
        location = "global" if str(get_global_scripts_dir()) in str(script_path) else "user"
        console.print(f"[green]Removed {location} script:[/] {name}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
@script_app.command("info")
@with_explanation("Show detailed information about a script.")
def script_info(
    name: str = typer.Argument(
        ..., 
        help="Name of the script",
        autocompletion=lambda: get_script_names()
    ),
    global_script: bool = typer.Option(True, "--global/--no-global", help="Include global scripts")
):
    """Show detailed information about a script."""
    # Find the script
    script_path = find_script(name, global_script)
    
    if not script_path:
        console.print(f"[bold red]Error:[/] Script '{name}' not found.")
        return
    
    # Get metadata
    metadata = get_script_metadata(script_path)
    
    # Determine script type
    script_type = "Unknown"
    if script_path.suffix == ".py":
        script_type = "Python"
    elif script_path.suffix == ".sh":
        script_type = "Shell"
    elif is_executable(script_path):
        script_type = "Executable"
    
    # Determine location
    location = "Global" if str(get_global_scripts_dir()) in str(script_path) else "User"
    
    # Display information
    console.print(f"[bold]Script:[/] {name}")
    console.print(f"[bold]Path:[/] {script_path}")
    console.print(f"[bold]Type:[/] {script_type}")
    console.print(f"[bold]Location:[/] {location}")
    
    if metadata:
        console.print("\n[bold]Metadata:[/]")
        for key, value in metadata.items():
            console.print(f"  [bold]{key}:[/] {value}")
    else:
        console.print("\n[yellow]No metadata available for this script.[/]")

@script_app.command("code")
@with_explanation("View or update script code without using an editor.")
def script_code(
    name: str = typer.Argument(
        ..., 
        help="Name of the script",
        autocompletion=lambda: get_script_names()
    ),
    content: Optional[str] = typer.Option(
        None, "--content", "-c", help="New content for the script (if not provided, displays current content)"
    ),
    input_file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Read new content from this file"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write content to this file instead of updating the script"
    ),
    global_script: bool = typer.Option(True, "--global/--no-global", help="Include global scripts")
):
    """View or update script code without using an editor."""
    # Find the script
    script_path = find_script(name, global_script)
    
    if not script_path:
        console.print(f"[bold red]Error:[/] Script '{name}' not found.")
        return
    
    # If content or input file is provided, update the script
    if content is not None or input_file is not None:
        # Get content from file if specified
        if input_file is not None:
            if not input_file.exists():
                console.print(f"[bold red]Error:[/] Input file '{input_file}' not found.")
                return
            
            try:
                with open(input_file, "r") as f:
                    content = f.read()
            except Exception as e:
                console.print(f"[bold red]Error:[/] Failed to read input file: {str(e)}")
                return
        
        # If output file is specified, write to that instead of updating the script
        if output_file is not None:
            try:
                with open(output_file, "w") as f:
                    f.write(content)
                console.print(f"[green]Content written to:[/] {output_file}")
                return
            except Exception as e:
                console.print(f"[bold red]Error:[/] Failed to write to output file: {str(e)}")
                return
        
        # Otherwise update the script
        # Check if user has permission to edit the script
        if not os.access(script_path, os.W_OK):
            console.print("[bold red]Error:[/] You don't have permission to edit this script.")
            console.print("Try running with sudo if it's a global script.")
            return
        
        # Write the new content
        try:
            with open(script_path, "w") as f:
                f.write(content)
            
            # Make sure the script is executable
            script_path.chmod(script_path.stat().st_mode | 0o755)
            
            # Update metadata
            update_script_metadata(script_path, {"last_edited": datetime.now().isoformat()})
            
            console.print(f"[green]Updated script:[/] {name}")
        except Exception as e:
            console.print(f"[bold red]Error:[/] Failed to update script: {str(e)}")
            return
    else:
        # Display the current content
        try:
            with open(script_path, "r") as f:
                content = f.read()
            
            # If output file is specified, write to that instead of displaying
            if output_file is not None:
                try:
                    with open(output_file, "w") as f:
                        f.write(content)
                    console.print(f"[green]Content written to:[/] {output_file}")
                    return
                except Exception as e:
                    console.print(f"[bold red]Error:[/] Failed to write to output file: {str(e)}")
                    return
            
            # Otherwise display the content
            console.print(f"[bold]Content of script '{name}':[/]\n")
            console.print(content)
        except Exception as e:
            console.print(f"[bold red]Error:[/] Failed to read script: {str(e)}")

@script_app.command("batch")
@with_explanation("Process multiple scripts with a single command.")
def batch_process(
    script_list: Path = typer.Argument(
        ...,
        help="Path to a file containing a list of scripts to process, one per line"
    ),
    command: str = typer.Option(
        "code", "--command", "-c", 
        help="Command to run on each script (code, run, info, etc.)"
    ),
    global_script: bool = typer.Option(True, "--global/--no-global", help="Include global scripts"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Directory to write output files to"),
    continue_on_error: bool = typer.Option(False, "--continue-on-error", help="Continue processing even if errors occur"),
    pattern: Optional[str] = typer.Option(None, "--pattern", "-p", help="Pattern to search for (when using 'search' command)"),
    replacement: Optional[str] = typer.Option(None, "--replacement", "-r", help="Replacement string (when using 'transform' command)")
):
    """Process multiple scripts with a single command."""
    if not script_list.exists():
        console.print(f"[bold red]Error:[/] Script list file '{script_list}' not found.")
        return
    
    try:
        with open(script_list, "r") as f:
            scripts = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to read script list: {str(e)}")
        return
    
    if not scripts:
        console.print("[yellow]No scripts found in the list file.[/]")
        return
    
    console.print(f"[bold]Processing {len(scripts)} scripts with command '{command}':[/]")
    
    for script_name in scripts:
        console.print(f"\n[bold]Processing script:[/] {script_name}")
        
        # Find the script
        script_path = find_script(script_name, global_script)
        
        if not script_path:
            console.print(f"[bold red]Error:[/] Script '{script_name}' not found. Skipping.")
            continue
        
        # Execute the requested command
        if command == "code":
            # Display the script content
            try:
                with open(script_path, "r") as f:
                    content = f.read()
            
                # If output directory is specified, write to a file there
                if output_dir is not None:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_file = output_dir / f"{script_name}{script_path.suffix}"
                    try:
                        with open(output_file, "w") as f:
                            f.write(content)
                        console.print(f"[green]Content written to:[/] {output_file}")
                    except Exception as e:
                        error_msg = f"Failed to write to output file: {str(e)}"
                        console.print(f"[bold red]Error:[/] {error_msg}")
                        if not continue_on_error:
                            return
                else:
                    # Otherwise display the content
                    console.print(f"[bold]Content of script '{script_name}':[/]\n")
                    console.print(content)
            except Exception as e:
                error_msg = f"Failed to read script: {str(e)}"
                console.print(f"[bold red]Error:[/] {error_msg}")
                if not continue_on_error:
                    continue
        
        elif command == "info":
            # Show script info
            script_type = "Unknown"
            if script_path.suffix == ".py":
                script_type = "Python"
            elif script_path.suffix == ".sh":
                script_type = "Shell"
            elif is_executable(script_path):
                script_type = "Executable"
            
            location = "Global" if str(get_global_scripts_dir()) in str(script_path) else "User"
            metadata = get_script_metadata(script_path)
            
            console.print(f"[bold]Script:[/] {script_name}")
            console.print(f"[bold]Path:[/] {script_path}")
            console.print(f"[bold]Type:[/] {script_type}")
            console.print(f"[bold]Location:[/] {location}")
            
            if metadata:
                console.print("[bold]Metadata:[/]")
                for key, value in metadata.items():
                    console.print(f"  [bold]{key}:[/] {value}")
        
        elif command == "run":
            # Run the script
            console.print(f"[bold]Running script:[/] {script_name}")
            
            # Update metadata to track usage
            metadata = get_script_metadata(script_path)
            run_count = metadata.get("run_count", 0) + 1
            update_script_metadata(script_path, {"run_count": run_count, "last_run": datetime.now().isoformat()})
            
            # Run the script based on its type
            if script_path.suffix == ".py":
                try:
                    # Add script directory to path
                    scripts_dir = script_path.parent
                    sys.path.insert(0, str(scripts_dir))
                    
                    # Load the module
                    spec = importlib.util.spec_from_file_location(script_name, script_path)
                    if spec is None or spec.loader is None:
                        console.print(f"[bold red]Error:[/] Failed to load Python script '{script_name}'.")
                        continue
                        
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Check if the module has a main function
                    if hasattr(module, "main"):
                        # Call the main function with no arguments
                        module.main([])
                    else:
                        console.print("[yellow]Warning:[/] Python script has no 'main' function.")
                except Exception as e:
                    console.print(f"[bold red]Error:[/] {str(e)}")
            else:
                # Run shell script or executable
                try:
                    # Make sure the script is executable
                    if not is_executable(script_path):
                        script_path.chmod(script_path.stat().st_mode | 0o755)
                    
                    # Run the script with no arguments
                    result = subprocess.run([str(script_path)], check=True)
                    
                    if result.returncode != 0:
                        console.print(f"[bold red]Error:[/] Script exited with code {result.returncode}")
                except subprocess.CalledProcessError as e:
                    console.print(f"[bold red]Error:[/] {str(e)}")
                except Exception as e:
                    console.print(f"[bold red]Error:[/] {str(e)}")
        
        elif command == "search" and pattern is not None:
            # Search for pattern in the script
            import re
            try:
                with open(script_path, "r") as f:
                    content = f.read()
            
                # Search for matches
                matches = []
                for i, line in enumerate(content.splitlines(), 1):
                    if pattern in line:
                        matches.append((i, line.strip()))
            
                if matches:
                    console.print(f"[bold]Matches in '{script_name}':[/]")
                    for line_num, line in matches:
                        console.print(f"  Line {line_num}: {line}")
                
                    # If output directory is specified, write matches to a file there
                    if output_dir is not None:
                        output_dir.mkdir(parents=True, exist_ok=True)
                        output_file = output_dir / f"{script_name}_matches.txt"
                        try:
                            with open(output_file, "w") as f:
                                f.write(f"Matches in '{script_name}':\n")
                                for line_num, line in matches:
                                    f.write(f"  Line {line_num}: {line}\n")
                            console.print(f"[green]Matches written to:[/] {output_file}")
                        except Exception as e:
                            error_msg = f"Failed to write matches to file: {str(e)}"
                            console.print(f"[bold red]Error:[/] {error_msg}")
                            if not continue_on_error:
                                return
                else:
                    console.print(f"[yellow]No matches found in '{script_name}'[/]")
            except Exception as e:
                error_msg = f"Failed to search script: {str(e)}"
                console.print(f"[bold red]Error:[/] {error_msg}")
                if not continue_on_error:
                    continue
    
        elif command == "transform" and pattern is not None and replacement is not None:
            # Transform script content using regex
            import re
            try:
                with open(script_path, "r") as f:
                    content = f.read()
            
                # Apply the transformation
                try:
                    transformed_content = content.replace(pattern, replacement)
                
                    # Check if any changes were made
                    if transformed_content == content:
                        console.print(f"[yellow]No changes made to '{script_name}'. Pattern did not match any content.[/]")
                        continue
                
                    # If output directory is specified, write to a file there
                    if output_dir is not None:
                        output_dir.mkdir(parents=True, exist_ok=True)
                        output_file = output_dir / f"{script_name}_transformed{script_path.suffix}"
                        try:
                            with open(output_file, "w") as f:
                                f.write(transformed_content)
                            console.print(f"[green]Transformed content written to:[/] {output_file}")
                        except Exception as e:
                            error_msg = f"Failed to write transformed content to file: {str(e)}"
                            console.print(f"[bold red]Error:[/] {error_msg}")
                            if not continue_on_error:
                                return
                    else:
                        # Otherwise update the script
                        # Check if user has permission to edit the script
                        if not os.access(script_path, os.W_OK):
                            console.print(f"[bold red]Error:[/] You don't have permission to edit script '{script_name}'.")
                            if not continue_on_error:
                                continue
                        else:
                            # Write the transformed content
                            with open(script_path, "w") as f:
                                f.write(transformed_content)
                        
                            # Make sure the script is executable
                            script_path.chmod(script_path.stat().st_mode | 0o755)
                        
                            # Update metadata
                            update_script_metadata(script_path, {"last_edited": datetime.now().isoformat()})
                        
                            console.print(f"[green]Transformed script:[/] {script_name}")
                except Exception as e:
                    error_msg = f"Failed to transform script: {str(e)}"
                    console.print(f"[bold red]Error:[/] {error_msg}")
                    if not continue_on_error:
                        continue
            except Exception as e:
                error_msg = f"Failed to read script: {str(e)}"
                console.print(f"[bold red]Error:[/] {error_msg}")
                if not continue_on_error:
                    continue
        else:
            if command not in ["code", "info", "run"] and (command == "search" and pattern is None) or (command == "transform" and (pattern is None or replacement is None)):
                console.print(f"[bold red]Error:[/] Command '{command}' requires additional parameters. Skipping.")
            else:
                console.print(f"[bold red]Error:[/] Unknown command '{command}'. Skipping.")
    
    console.print("\n[green]Batch processing complete.[/]")

@script_app.command("update-metadata")
@with_explanation("Update metadata for a script.")
def update_metadata(
    name: str = typer.Argument(
        ..., 
        help="Name of the script",
        autocompletion=lambda: get_script_names()
    ),
    description: str = typer.Option(None, "--description", "-d", help="Description of the script"),
    global_script: bool = typer.Option(True, "--global/--no-global", help="Include global scripts")
):
    """Update metadata for a script."""
    # Find the script
    script_path = find_script(name, global_script)
    
    if not script_path:
        console.print(f"[bold red]Error:[/] Script '{name}' not found.")
        return
    
    # Update metadata
    new_metadata = {}
    if description is not None:
        new_metadata["description"] = description
    
    if not new_metadata:
        console.print("[yellow]No metadata changes specified.[/]")
        return
    
    update_script_metadata(script_path, new_metadata)
    console.print(f"[green]Updated metadata for script:[/] {name}")

@script_app.command("templates")
@with_explanation("List available script templates.")
def list_templates():
    """List available script templates."""
    console.print("[bold]Available script templates:[/]")
    
    for template_name, template_data in TEMPLATES.items():
        available_types = ", ".join(template_data.keys())
        console.print(f"  [bold]{template_name}[/] (Types: {available_types})")

@script_app.command("export")
@with_explanation("Export a script to a JSON file to share with others.")
def export_script(
    name: str = typer.Argument(
        ..., 
        help="Name of the script to export",
        autocompletion=lambda: get_script_names()
    ),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output JSON file path"),
    include_metadata: bool = typer.Option(True, "--metadata/--no-metadata", help="Include metadata in export"),
    global_script: bool = typer.Option(True, "--global/--no-global", help="Include global scripts")
):
    """Export a script to a JSON file that can be shared and imported by others.
    
    The export file contains the script's code, metadata, and other information.
    """
    # Find the script
    script_path = find_script(name, global_script)
    
    if not script_path:
        console.print(f"[bold red]Error:[/] Script '{name}' not found.")
        return
    
    # Determine output file if not specified
    if output_file is None:
        output_file = Path(f"{name}_export{script_path.suffix}")
    
    # Read script content
    with open(script_path, "r") as f:
        script_content = f.read()
    
    # Get metadata if requested
    metadata = {}
    if include_metadata:
        metadata = get_script_metadata(script_path)
    
    # Create export data
    export_data = {
        "name": name,
        "content": script_content,
        "type": script_path.suffix.lstrip("."),
        "metadata": metadata,
        "exported_at": datetime.now().isoformat(),
        "exported_by": os.environ.get("USER", "unknown")
    }
    
    # Write export file
    with open(output_file, "w") as f:
        json.dump(export_data, f, indent=2)
    
    console.print(f"[green]Exported script to:[/] {output_file}")

@script_app.command("transform")
@with_explanation("Transform script content using regular expressions.")
def transform_script(
    name: str = typer.Argument(
        ..., 
        help="Name of the script to transform",
        autocompletion=lambda: get_script_names()
    ),
    pattern: str = typer.Option(..., "--pattern", "-p", help="Regular expression pattern to search for"),
    replacement: str = typer.Option(..., "--replacement", "-r", help="Replacement string"),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write transformed content to this file instead of updating the script"
    ),
    global_script: bool = typer.Option(True, "--global/--no-global", help="Include global scripts"),
    backup: bool = typer.Option(True, "--backup/--no-backup", help="Create a backup before transforming")
):
    """Transform script content using regular expressions."""
    import re
    
    # Find the script
    script_path = find_script(name, global_script)
    
    if not script_path:
        console.print(f"[bold red]Error:[/] Script '{name}' not found.")
        return
    
    # Read the script content
    try:
        with open(script_path, "r") as f:
            content = f.read()
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to read script: {str(e)}")
        return
    
    # Create a backup if requested
    if backup and output_file is None:
        backup_path = script_path.with_suffix(f"{script_path.suffix}.bak")
        try:
            shutil.copy2(script_path, backup_path)
            console.print(f"[green]Created backup:[/] {backup_path}")
        except Exception as e:
            console.print(f"[bold red]Error:[/] Failed to create backup: {str(e)}")
            if not typer.confirm("Continue without backup?"):
                return
    
    # Apply the transformation
    try:
        transformed_content = re.sub(pattern, replacement, content)
        
        # Check if any changes were made
        if transformed_content == content:
            console.print("[yellow]Warning:[/] No changes made. Pattern did not match any content.")
            return
        
        # If output file is specified, write to that instead of updating the script
        if output_file is not None:
            try:
                with open(output_file, "w") as f:
                    f.write(transformed_content)
                console.print(f"[green]Transformed content written to:[/] {output_file}")
                return
            except Exception as e:
                console.print(f"[bold red]Error:[/] Failed to write to output file: {str(e)}")
                return
        
        # Otherwise update the script
        # Check if user has permission to edit the script
        if not os.access(script_path, os.W_OK):
            console.print("[bold red]Error:[/] You don't have permission to edit this script.")
            console.print("Try running with sudo if it's a global script.")
            return
        
        # Write the transformed content
        with open(script_path, "w") as f:
            f.write(transformed_content)
        
        # Make sure the script is executable
        script_path.chmod(script_path.stat().st_mode | 0o755)
        
        # Update metadata
        update_script_metadata(script_path, {"last_edited": datetime.now().isoformat()})
        
        console.print(f"[green]Transformed script:[/] {name}")
    except re.error as e:
        console.print(f"[bold red]Error:[/] Invalid regular expression: {str(e)}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to transform script: {str(e)}")

@script_app.command("search")
@with_explanation("Search for text in scripts.")
def search_scripts(
    pattern: str = typer.Argument(..., help="Text or regular expression to search for"),
    regex: bool = typer.Option(False, "--regex", "-r", help="Treat pattern as a regular expression"),
    case_sensitive: bool = typer.Option(False, "--case-sensitive", "-c", help="Make search case-sensitive"),
    global_scripts: bool = typer.Option(True, "--global/--no-global", help="Include global scripts"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Write results to this file"),
    ignore_errors: bool = typer.Option(False, "--ignore-errors", help="Continue searching even if errors occur")
):
    """Search for text in scripts."""
    import re
    
    # Get all scripts
    scripts = list_available_scripts(global_scripts)
    
    if not scripts:
        console.print("[yellow]No scripts found to search.[/]")
        return
    
    console.print(f"[bold]Searching {len(scripts)} scripts for:[/] {pattern}")
    
    # Prepare regex pattern
    if regex:
        try:
            if case_sensitive:
                pattern_obj = re.compile(pattern)
            else:
                pattern_obj = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            console.print(f"[bold red]Error:[/] Invalid regular expression: {str(e)}")
            return
    
    # Store results
    results = []
    errors = []
    
    # Search each script
    for script_path in scripts:
        # Skip directories
        if script_path.is_dir():
            if not ignore_errors:
                errors.append(f"Skipped directory: {script_path}")
            continue
            
        try:
            with open(script_path, "r") as f:
                content = f.read()
                
            # Search for matches
            matches = []
            if regex:
                for i, line in enumerate(content.splitlines(), 1):
                    if pattern_obj.search(line):
                        matches.append((i, line.strip()))
            else:
                for i, line in enumerate(content.splitlines(), 1):
                    if (pattern in line) if case_sensitive else (pattern.lower() in line.lower()):
                        matches.append((i, line.strip()))
            
            if matches:
                script_name = script_path.stem
                location = "Global" if str(get_global_scripts_dir()) in str(script_path) else "User"
                results.append((script_name, script_path, location, matches))
        except Exception as e:
            error_msg = f"Failed to search script {script_path}: {str(e)}"
            errors.append(error_msg)
            if not ignore_errors:
                console.print(f"[bold red]Error:[/] {error_msg}")
    
    # Display results
    if not results:
        console.print("[yellow]No matches found.[/]")
        return
    
    # Format results
    formatted_results = []
    for script_name, script_path, location, matches in results:
        formatted_results.append(f"[bold]{script_name}[/] ({location}): {script_path}")
        for line_num, line in matches:
            formatted_results.append(f"  Line {line_num}: {line}")
        formatted_results.append("")
    
    # Add error summary at the end if there were errors
    if errors:
        formatted_results.append("[bold red]Errors encountered during search:[/]")
        for error in errors:
            formatted_results.append(f"  {error}")
        formatted_results.append("")
    
    # Write to output file if specified
    if output_file is not None:
        try:
            with open(output_file, "w") as f:
                for line in formatted_results:
                    # Strip rich formatting for file output
                    clean_line = line.replace("[bold]", "").replace("[/]", "").replace("[bold red]", "").replace("[yellow]", "")
                    f.write(f"{clean_line}\n")
            console.print(f"[green]Search results written to:[/] {output_file}")
        except Exception as e:
            console.print(f"[bold red]Error:[/] Failed to write to output file: {str(e)}")
    else:
        # Display results in console
        for line in formatted_results:
            console.print(line)
        
        console.print(f"[green]Found matches in {len(results)} scripts.[/]")
        if errors and not ignore_errors:
            console.print(f"[yellow]Note: {len(errors)} errors occurred during search. Use --ignore-errors to suppress these messages.[/]")

@script_app.command("generate")
@with_explanation("Generate a script from a description using AI or templates.")
def generate_script(
    name: str = typer.Argument(..., help="Name for the new script"),
    description: str = typer.Argument(..., help="Description of what the script should do"),
    type: str = typer.Option(
        "python", 
        "--type", "-t", 
        help="Script type (python or shell)",
        autocompletion=lambda: get_script_types()
    ),
    global_script: bool = typer.Option(False, "--global", "-g", help="Install as a global script"),
    edit: bool = typer.Option(True, "--edit/--no-edit", help="Open the script in an editor after creation"),
    editor: Optional[str] = typer.Option(None, "--editor", "-e", help="Specify which editor to use (defaults to $EDITOR)"),
    model: str = typer.Option("gpt-3.5-turbo", "--model", "-m", help="AI model to use for generation"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="API key for the AI service"),
    local: bool = typer.Option(False, "--local", "-l", help="Use local templates instead of AI")
):
    """Generate a script from a description using AI or templates."""
    # Determine the scripts directory
    if global_script:
        # Check if user has permission to write to global directory
        global_dir = get_global_scripts_dir()
        if not os.access(global_dir.parent, os.W_OK):
            console.print("[bold red]Error:[/] You don't have permission to create global scripts.")
            console.print("Try running with sudo or use --no-global for a user script.")
            return
        scripts_dir = global_dir
        scripts_dir.mkdir(parents=True, exist_ok=True)
    else:
        scripts_dir = get_user_scripts_dir()
    
    # Determine file extension based on type
    ext = ".py" if type.lower() == "python" else ".sh"
    script_path = scripts_dir / f"{name}{ext}"
    
    # Check if script already exists
    if script_path.exists():
        overwrite = typer.confirm(f"Script '{name}' already exists. Overwrite?")
        if not overwrite:
            return
    
    # Use local template if requested or if API generation fails
    use_local_template = local
    generated_code = None
    generation_method = "template"
    
    # Special case for count_lines - use the line_counter template directly
    if name == "count_lines" and "line_counter" in TEMPLATES and type.lower() in TEMPLATES["line_counter"]:
        use_local_template = True
        template_name = "line_counter"
        console.print(f"[green]Using '{template_name}' template for line counting script.[/]")
    
    if not use_local_template:
        # Try to use AI generation
        try:
            import requests
        except ImportError:
            console.print("[yellow]Warning:[/] The 'requests' package is required for AI generation.")
            console.print("Falling back to local template. Install requests with: pip install requests")
            use_local_template = True
        
        if not use_local_template:
            # Get API key from environment if not provided
            if api_key is None:
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key is None:
                    console.print("[yellow]Warning:[/] No API key provided.")
                    console.print("Falling back to local template. Set the OPENAI_API_KEY environment variable or use --api-key.")
                    use_local_template = True
    
    if not use_local_template:
        # Prepare the prompt
        language = "Python" if type.lower() == "python" else "Bash"
        prompt = f"""Create a {language} script that does the following:
{description}

The script should:
1. Be well-documented with comments
2. Include error handling
3. Have a main function that can be called with arguments
4. Be executable from the command line

Return ONLY the code with no additional text or explanations.
"""
        
        # Show a spinner while waiting for the API response
        with console.status(f"[bold green]Generating {language} script using {model}...[/]"):
            try:
                # Make the API request
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": f"You are an expert {language} programmer."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code != 200:
                    console.print(f"[yellow]Warning:[/] API request failed with status code {response.status_code}")
                    console.print(response.text)
                    console.print("Falling back to local template.")
                    use_local_template = True
                else:
                    # Extract the generated code
                    response_data = response.json()
                    generated_code = response_data["choices"][0]["message"]["content"].strip()
                    generation_method = model
            
            except requests.exceptions.RequestException as e:
                console.print(f"[yellow]Warning:[/] Failed to connect to the API: {str(e)}")
                console.print("Falling back to local template.")
                use_local_template = True
            except Exception as e:
                console.print(f"[yellow]Warning:[/] {str(e)}")
                console.print("Falling back to local template.")
                use_local_template = True
    
    # Use local template if AI generation failed or was not requested
    if use_local_template:
        # Choose the most appropriate template based on the description
        template_name = "basic"
        
        # Simple keyword matching to find the best template
        keywords = {
            "data": ["data", "csv", "json", "process", "file", "read", "write", "parse"],
            "api": ["api", "http", "request", "rest", "endpoint", "server", "client"],
            "system_info": ["system", "info", "hardware", "cpu", "memory", "disk", "network"]
        }
        
        # Count keyword matches for each template
        matches = {template: 0 for template in keywords}
        for template, words in keywords.items():
            for word in words:
                if word.lower() in description.lower():
                    matches[template] += 1
        
        # Find the template with the most matches
        best_match = max(matches.items(), key=lambda x: x[1])
        if best_match[1] > 0:
            if best_match[0] == "data" and "data_processing" in TEMPLATES and type.lower() in TEMPLATES["data_processing"]:
                template_name = "data_processing"
            elif best_match[0] == "api" and "api_client" in TEMPLATES and type.lower() in TEMPLATES["api_client"]:
                template_name = "api_client"
            elif best_match[0] == "system_info" and "system_info" in TEMPLATES and type.lower() in TEMPLATES["system_info"]:
                template_name = "system_info"
        
        # Get template content
        if template_name in TEMPLATES and type.lower() in TEMPLATES[template_name]:
            generated_code = TEMPLATES[template_name][type.lower()]
        else:
            # Fall back to basic template
            generated_code = TEMPLATES["basic"][type.lower()]
        
        # Customize the template with the description
        if type.lower() == "python":
            generated_code = generated_code.replace("Custom script for SkogCLI.", f"Script to {description}")
        elif type.lower() == "shell":
            generated_code = generated_code.replace("# Custom script for SkogCLI", f"# Script to {description}")
        
        console.print(f"[green]Using '{template_name}' template for script generation.[/]")
    
    # Add shebang line if it's not already there
    if type.lower() == "python" and not generated_code.startswith("#!/"):
        generated_code = "#!/usr/bin/env python3\n" + generated_code
    elif type.lower() == "shell" and not generated_code.startswith("#!/"):
        generated_code = "#!/bin/bash\n" + generated_code
    
    # Write the generated code to the file
    with open(script_path, "w") as f:
        f.write(generated_code)
    
    # Make the script executable
    script_path.chmod(script_path.stat().st_mode | 0o755)
    
    # Create a symlink in the current directory for easy access if it's a user script
    if not global_script:
        symlink_path = Path(name + ext)
        try:
            # Remove existing symlink if it exists
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()
            
            # Create the symlink
            os.symlink(script_path, symlink_path)
            console.print(f"[green]Created symlink:[/] {symlink_path} -> {script_path}")
        except Exception as e:
            console.print(f"[yellow]Warning:[/] Could not create symlink: {str(e)}")
    
    # Save metadata
    metadata = {
        "description": description,
        "type": type.lower(),
        "created": datetime.now().isoformat(),
        "generated_by": generation_method,
        "run_count": 0
    }
    update_script_metadata(script_path, metadata)
    
    location = "global" if global_script else "user"
    console.print(f"[green]Generated {location} script:[/] {script_path}")
    
    # Open in editor if requested
    if edit:
        # Get the editor from the environment or use the provided one
        editor_cmd = editor or os.environ.get("EDITOR", "nano")
        try:
            exit_code = subprocess.call([editor_cmd, str(script_path)])
            if exit_code == 0:
                console.print("[green]Script edited successfully.[/]")
            else:
                console.print(f"[bold red]Error:[/] Editor exited with code {exit_code}")
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/] Editor '{editor_cmd}' not found. Set the EDITOR environment variable or use --editor.")
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")

@script_app.command("import")
@with_explanation("Import a script from an export file.")
def import_script(
    file: Path = typer.Argument(..., help="Path to the JSON export file created by 'script export'"),
    global_script: bool = typer.Option(False, "--global", "-g", help="Install as a global script"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing script")
):
    """Import a script from a JSON export file created by the 'script export' command.
    
    The export file contains the script's code, metadata, and other information.
    """
    # Check if file exists
    if not file.exists():
        console.print(f"[bold red]Error:[/] Export file '{file}' not found.")
        return
    
    # Read export data
    try:
        with open(file, "r") as f:
            export_data = json.load(f)
    except json.JSONDecodeError:
        console.print(f"[bold red]Error:[/] Invalid export file format.")
        return
    
    # Validate export data
    required_fields = ["name", "content", "type"]
    for field in required_fields:
        if field not in export_data:
            console.print(f"[bold red]Error:[/] Export file is missing required field: {field}")
            return
    
    # Determine the scripts directory
    if global_script:
        # Check if user has permission to write to global directory
        global_dir = get_global_scripts_dir()
        if not os.access(global_dir.parent, os.W_OK):
            console.print("[bold red]Error:[/] You don't have permission to create global scripts.")
            console.print("Try running with sudo or use --no-global for a user script.")
            return
        scripts_dir = global_dir
        scripts_dir.mkdir(parents=True, exist_ok=True)
    else:
        scripts_dir = get_user_scripts_dir()
    
    # Determine script path
    name = export_data["name"]
    script_type = export_data["type"]
    ext = f".{script_type}" if script_type else ""
    script_path = scripts_dir / f"{name}{ext}"
    
    # Check if script already exists
    if script_path.exists() and not overwrite:
        console.print(f"[bold red]Error:[/] Script '{name}' already exists.")
        console.print("Use --overwrite to replace the existing script.")
        return
    
    # Write script content
    with open(script_path, "w") as f:
        f.write(export_data["content"])
    
    # Make the script executable
    script_path.chmod(script_path.stat().st_mode | 0o755)
    
    # Import metadata if available
    if "metadata" in export_data and export_data["metadata"]:
        metadata = export_data["metadata"]
        # Add import information
        metadata["imported_at"] = datetime.now().isoformat()
        metadata["imported_from"] = str(file)
        update_script_metadata(script_path, metadata)
    
    location = "global" if global_script else "user"
    console.print(f"[green]Imported {location} script:[/] {name}")

@script_app.command("add-file")
@with_explanation("Add an existing script file to the scripts directory.")
def add_file(
    file: Path = typer.Argument(..., help="Path to the existing script file to add"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Name for the script (defaults to original filename)"),
    global_script: bool = typer.Option(False, "--global", "-g", help="Install as a global script"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing script"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Open the script in an editor after adding"),
    editor: Optional[str] = typer.Option(None, "--editor", help="Specify which editor to use (defaults to $EDITOR)")
):
    """Add an existing script file to the scripts directory.
    
    This command copies a script file from anywhere on your filesystem into the SkogCLI
    scripts directory, making it available as a SkogCLI script.
    """
    # Check if file exists
    if not file.exists():
        console.print(f"[bold red]Error:[/] File '{file}' not found.")
        return
    
    if not file.is_file():
        console.print(f"[bold red]Error:[/] '{file}' is not a file.")
        return
    
    # Determine script name
    script_name = name if name else file.stem
    
    # Determine the scripts directory
    if global_script:
        # Check if user has permission to write to global directory
        global_dir = get_global_scripts_dir()
        if not os.access(global_dir.parent, os.W_OK):
            console.print("[bold red]Error:[/] You don't have permission to create global scripts.")
            console.print("Try running with sudo or use --no-global for a user script.")
            return
        scripts_dir = global_dir
        scripts_dir.mkdir(parents=True, exist_ok=True)
    else:
        scripts_dir = get_user_scripts_dir()
    
    # Determine destination path (preserve original extension)
    dest_path = scripts_dir / f"{script_name}{file.suffix}"
    
    # Check if destination already exists
    if dest_path.exists() and not overwrite:
        console.print(f"[bold red]Error:[/] Script '{script_name}' already exists.")
        console.print("Use --overwrite to replace the existing script.")
        return
    
    # Copy the file
    try:
        shutil.copy2(file, dest_path)
        
        # Make the script executable
        dest_path.chmod(dest_path.stat().st_mode | 0o755)
        
        # Determine script type
        script_type = "unknown"
        if file.suffix == ".py":
            script_type = "python"
        elif file.suffix == ".sh":
            script_type = "shell"
        
        # Create metadata
        metadata = {
            "description": f"Added from {file}",
            "type": script_type,
            "created": datetime.now().isoformat(),
            "source_file": str(file),
            "run_count": 0
        }
        update_script_metadata(dest_path, metadata)
        
        location = "global" if global_script else "user"
        console.print(f"[green]Added {location} script:[/] {dest_path}")
        
        # Open in editor if requested
        if edit:
            # Get the editor from the environment or use the provided one
            editor_cmd = editor or os.environ.get("EDITOR", "nano")
            try:
                exit_code = subprocess.call([editor_cmd, str(dest_path)])
                if exit_code == 0:
                    console.print("[green]Script edited successfully.[/]")
                else:
                    console.print(f"[bold red]Error:[/] Editor exited with code {exit_code}")
            except FileNotFoundError:
                console.print(f"[bold red]Error:[/] Editor '{editor_cmd}' not found. Set the EDITOR environment variable or use --editor.")
            except Exception as e:
                console.print(f"[bold red]Error:[/] {str(e)}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")

@script_app.command("copy")
@with_explanation("Copy a script to create a new one.")
def copy_script(
    source: str = typer.Argument(
        ..., 
        help="Name of the source script",
        autocompletion=lambda: get_script_names()
    ),
    destination: str = typer.Argument(..., help="Name for the new script"),
    global_source: bool = typer.Option(True, "--global-source/--no-global-source", help="Include global scripts as source"),
    global_dest: bool = typer.Option(False, "--global-dest", "-g", help="Create as a global script"),
    edit: bool = typer.Option(True, "--edit/--no-edit", help="Open the new script in an editor"),
    editor: Optional[str] = typer.Option(None, "--editor", "-e", help="Specify which editor to use (defaults to $EDITOR)")
):
    """Copy a script to create a new one."""
    # Find the source script
    source_path = find_script(source, global_source)
    
    if not source_path:
        console.print(f"[bold red]Error:[/] Source script '{source}' not found.")
        return
    
    # Determine the destination directory
    if global_dest:
        # Check if user has permission to write to global directory
        global_dir = get_global_scripts_dir()
        if not os.access(global_dir.parent, os.W_OK):
            console.print("[bold red]Error:[/] You don't have permission to create global scripts.")
            console.print("Try running with sudo or use --no-global-dest for a user script.")
            return
        dest_dir = global_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
    else:
        dest_dir = get_user_scripts_dir()
    
    # Determine destination path
    dest_path = dest_dir / f"{destination}{source_path.suffix}"
    
    # Check if destination already exists
    if dest_path.exists():
        overwrite = typer.confirm(f"Script '{destination}' already exists. Overwrite?")
        if not overwrite:
            return
    
    # Copy the script
    try:
        shutil.copy2(source_path, dest_path)
        
        # Make the script executable
        dest_path.chmod(dest_path.stat().st_mode | 0o755)
        
        # Copy and update metadata
        source_metadata = get_script_metadata(source_path)
        if source_metadata:
            metadata = source_metadata.copy()
            # Update metadata for the copy
            metadata["copied_from"] = str(source_path)
            metadata["created"] = datetime.now().isoformat()
            metadata["run_count"] = 0
            if "last_run" in metadata:
                del metadata["last_run"]
            if "last_edited" in metadata:
                del metadata["last_edited"]
            
            update_script_metadata(dest_path, metadata)
        
        location = "global" if global_dest else "user"
        console.print(f"[green]Copied to new {location} script:[/] {dest_path}")
        
        # Open in editor if requested
        if edit:
            # Get the editor from the environment or use the provided one
            editor_cmd = editor or os.environ.get("EDITOR", "nano")
            try:
                exit_code = subprocess.call([editor_cmd, str(dest_path)])
                if exit_code == 0:
                    console.print("[green]Script edited successfully.[/]")
                else:
                    console.print(f"[bold red]Error:[/] Editor exited with code {exit_code}")
            except FileNotFoundError:
                console.print(f"[bold red]Error:[/] Editor '{editor_cmd}' not found. Set the EDITOR environment variable or use --editor.")
            except Exception as e:
                console.print(f"[bold red]Error:[/] {str(e)}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
