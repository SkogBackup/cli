"""Miscellaneous commands for SkogCLI."""

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

# Create a Typer app for the misc commands
misc_app = typer.Typer(
    help="Miscellaneous utility commands",
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

@misc_app.callback()
def misc_callback():
    """Miscellaneous utility commands."""
    pass

@misc_app.command("list")
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

@misc_app.command("run")
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

@misc_app.command("add")
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

@misc_app.command("edit")
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

@misc_app.command("remove")
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
@misc_app.command("info")
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

@misc_app.command("code")
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

@misc_app.command("batch")
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
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Directory to write output files to")
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
                        console.print(f"[bold red]Error:[/] Failed to write to output file: {str(e)}")
                else:
                    # Otherwise display the content
                    console.print(f"[bold]Content of script '{script_name}':[/]\n")
                    console.print(content)
            except Exception as e:
                console.print(f"[bold red]Error:[/] Failed to read script: {str(e)}")
        
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
        
        else:
            console.print(f"[bold red]Error:[/] Unknown command '{command}'. Skipping.")
    
    console.print("\n[green]Batch processing complete.[/]")

@misc_app.command("update-metadata")
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

@misc_app.command("templates")
@with_explanation("List available script templates.")
def list_templates():
    """List available script templates."""
    console.print("[bold]Available script templates:[/]")
    
    for template_name, template_data in TEMPLATES.items():
        available_types = ", ".join(template_data.keys())
        console.print(f"  [bold]{template_name}[/] (Types: {available_types})")

@misc_app.command("export")
@with_explanation("Export a script to share with others.")
def export_script(
    name: str = typer.Argument(
        ..., 
        help="Name of the script to export",
        autocompletion=lambda: get_script_names()
    ),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    include_metadata: bool = typer.Option(True, "--metadata/--no-metadata", help="Include metadata in export"),
    global_script: bool = typer.Option(True, "--global/--no-global", help="Include global scripts")
):
    """Export a script to share with others."""
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

@misc_app.command("transform")
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

@misc_app.command("import")
@with_explanation("Import a script from an export file.")
def import_script(
    file: Path = typer.Argument(..., help="Path to the export file"),
    global_script: bool = typer.Option(False, "--global", "-g", help="Install as a global script"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing script")
):
    """Import a script from an export file."""
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

@misc_app.command("copy")
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
