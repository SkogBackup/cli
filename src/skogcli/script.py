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

def get_templates_dir() -> Path:
    """Get the directory containing script templates."""
    # First check if there's a SKOGAI templates directory
    skogai_templates_dir = os.getenv("SKOGAI_TEMPLATES_DIR")
    if skogai_templates_dir:
        templates_path = Path(skogai_templates_dir)
        if templates_path.exists() and templates_path.is_dir():
            return templates_path
    
    # Import get_config_dir to use proper config directory logic
    from .settings import get_config_dir
    
    # Fallback to user templates directory using proper config dir
    user_templates_dir = get_config_dir() / "templates"
    if user_templates_dir.exists() and user_templates_dir.is_dir():
        return user_templates_dir
    
    # Otherwise use the package templates directory
    return Path(__file__).parent / "data" / "templates"

def get_template_content(template_name: str, script_type: str) -> str:
    """Get the content of a template file."""
    templates_dir = get_templates_dir()
    
    # Map script type to directory name
    type_dir = script_type.lower()
    
    # Determine file extension
    extension = ".py" if script_type.lower() == "python" else ".sh"
    
    # Check for the template file
    template_path = templates_dir / type_dir / f"{template_name}{extension}"
    
    if not template_path.exists():
        # Check in the package templates directory as fallback
        package_templates_dir = Path(__file__).parent / "data" / "templates"
        template_path = package_templates_dir / type_dir / f"{template_name}{extension}"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template {template_name} for {script_type} not found")
    
    with open(template_path, "r") as f:
        return f.read()

def list_available_templates() -> Dict[str, List[str]]:
    """List all available templates by type."""
    templates_dir = get_templates_dir()
    package_templates_dir = Path(__file__).parent / "data" / "templates"
    
    templates = {}
    
    # Function to scan a templates directory
    def scan_templates_dir(dir_path):
        if not dir_path.exists() or not dir_path.is_dir():
            return
            
        for type_dir in dir_path.iterdir():
            if type_dir.is_dir():
                type_name = type_dir.name
                if type_name not in templates:
                    templates[type_name] = []
                
                for template_file in type_dir.iterdir():
                    if template_file.is_file():
                        template_name = template_file.stem
                        if template_name not in templates[type_name]:
                            templates[type_name].append(template_name)
    
    # Scan both user and package template directories
    scan_templates_dir(package_templates_dir)
    scan_templates_dir(templates_dir)  # User templates can override package templates
    
    return templates

def get_global_scripts_dir() -> Path:
    """Get the global scripts directory, creating it if it doesn't exist."""
    # Check for SKOGAI global scripts directory first
    skogai_global_scripts_dir = os.getenv("SKOGAI_SCRIPTS_GLOBAL_DIR")
    if skogai_global_scripts_dir:
        return Path(skogai_global_scripts_dir)
    
    # Fallback to /usr/local/share for global scripts
    scripts_dir = Path("/usr/local/share/skogcli/scripts")
    return scripts_dir

def get_user_scripts_dir() -> Path:
    """Get the user scripts directory, creating it if it doesn't exist."""
    # Check for SKOGAI scripts directory first
    skogai_scripts_dir = os.getenv("SKOGAI_SCRIPTS_DIR")
    if skogai_scripts_dir:
        scripts_dir = Path(skogai_scripts_dir)
        scripts_dir.mkdir(parents=True, exist_ok=True)
        return scripts_dir
    
    # Import get_config_dir to use proper config directory logic
    from .settings import get_config_dir
    
    # Fallback to user scripts directory using proper config dir
    scripts_dir = get_config_dir() / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    return scripts_dir

def get_metadata_file() -> Path:
    """Get the path to the script metadata file."""
    # Check for SKOGAI metadata directory first
    skogai_metadata_dir = os.getenv("SKOGAI_SCRIPT_METADATA_DIR")
    if skogai_metadata_dir:
        metadata_dir = Path(skogai_metadata_dir)
        metadata_dir.mkdir(parents=True, exist_ok=True)
        return metadata_dir / "script_metadata.json"
    
    # Import get_config_dir to use proper config directory logic
    from .settings import get_config_dir
    
    # Fallback to metadata file in proper config directory
    metadata_dir = get_config_dir()
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
    templates = list_available_templates()
    # Flatten the dictionary to get a unique list of template names
    template_names = set()
    for type_templates in templates.values():
        template_names.update(type_templates)
    return sorted(list(template_names))

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

@script_app.command("create")
@with_explanation("Create a new custom script.")
def create_script(
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
    """Create a new custom script."""
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
    try:
        template_content = get_template_content(template, type.lower())
    except FileNotFoundError:
        # List available templates
        templates = list_available_templates()
        available_templates = []
        for t_type, t_names in templates.items():
            if t_type == type.lower():
                available_templates = t_names
                break
        
        console.print(f"[yellow]Warning:[/] Template '{template}' not found for {type}.")
        if available_templates:
            console.print(f"Available {type} templates: {', '.join(available_templates)}")
            # Try to use basic template
            if "basic" in available_templates:
                template = "basic"
                console.print(f"[yellow]Using 'basic' template instead.[/]")
                template_content = get_template_content("basic", type.lower())
            else:
                console.print("[bold red]Error:[/] No suitable template found.")
                return
        else:
            console.print(f"[bold red]Error:[/] No templates available for {type}.")
            return
    
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
    
    templates = list_available_templates()
    if not templates:
        console.print("[yellow]No templates found.[/]")
        console.print(f"Templates should be placed in {get_templates_dir()}/[type]/[template].[ext]")
        return
    
    for script_type, template_names in templates.items():
        console.print(f"[bold]{script_type.upper()}[/] templates:")
        for template_name in sorted(template_names):
            console.print(f"  • {template_name}")

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
    if name == "count_lines":
        try:
            generated_code = get_template_content("line_counter", type.lower())
            use_local_template = True
            template_name = "line_counter"
            console.print(f"[green]Using '{template_name}' template for line counting script.[/]")
        except FileNotFoundError:
            # Continue with normal flow if template not found
            pass
    
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
    if use_local_template and generated_code is None:
        # Choose the most appropriate template based on the description
        template_name = "basic"
        
        # Simple keyword matching to find the best template
        keywords = {
            "data_processing": ["data", "csv", "json", "process", "file", "read", "write", "parse"],
            "api_client": ["api", "http", "request", "rest", "endpoint", "server", "client"],
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
            try:
                generated_code = get_template_content(best_match[0], type.lower())
                template_name = best_match[0]
            except FileNotFoundError:
                # Fall back to basic template
                try:
                    generated_code = get_template_content("basic", type.lower())
                    template_name = "basic"
                except FileNotFoundError:
                    console.print(f"[bold red]Error:[/] No templates found for {type.lower()}.")
                    return
        else:
            # Use basic template
            try:
                generated_code = get_template_content("basic", type.lower())
                template_name = "basic"
            except FileNotFoundError:
                console.print(f"[bold red]Error:[/] No templates found for {type.lower()}.")
                return
        
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

@script_app.command("import-file")
@with_explanation("Import an existing script file into the scripts directory.")
def import_file(
    file: Path = typer.Argument(..., help="Path to the existing script file to add"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Name for the script (defaults to original filename)"),
    global_script: bool = typer.Option(False, "--global", "-g", help="Install as a global script"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing script"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Open the script in an editor after adding"),
    editor: Optional[str] = typer.Option(None, "--editor", help="Specify which editor to use (defaults to $EDITOR)")
):
    """Import an existing script file into the scripts directory.
    
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
