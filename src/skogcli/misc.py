"""Miscellaneous commands for SkogCLI."""

import os
import sys
import subprocess
import importlib.util
import typer
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich import print as rprint
from .decorators import with_explanation

console = Console()

# Create a Typer app for the misc commands
misc_app = typer.Typer(
    help="Miscellaneous utility commands",
    no_args_is_help=True
)

def get_scripts_dir() -> Path:
    """Get the scripts directory, creating it if it doesn't exist."""
    scripts_dir = Path.home() / ".config" / "skogcli" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    return scripts_dir

def list_available_scripts() -> List[Path]:
    """List all available scripts in the scripts directory."""
    scripts_dir = get_scripts_dir()
    return list(scripts_dir.glob("*.*"))

def is_executable(path: Path) -> bool:
    """Check if a file is executable."""
    return os.access(path, os.X_OK)

@misc_app.callback()
def misc_callback():
    """Miscellaneous utility commands."""
    pass

@misc_app.command("list")
@with_explanation("List all available custom scripts.")
def list_scripts():
    """List all available custom scripts."""
    scripts = list_available_scripts()
    
    if not scripts:
        console.print("[yellow]No custom scripts found.[/]")
        console.print(f"Add scripts to [bold]{get_scripts_dir()}[/] to get started.")
        return
    
    console.print("[bold]Available custom scripts:[/]")
    for script in scripts:
        script_type = "Unknown"
        if script.suffix == ".py":
            script_type = "Python"
        elif script.suffix == ".sh":
            script_type = "Shell"
        elif is_executable(script):
            script_type = "Executable"
            
        console.print(f"  [bold]{script.stem}[/] - {script_type} script")

@misc_app.command("run")
@with_explanation("Run a custom script.")
def run_script(
    name: str = typer.Argument(..., help="Name of the script to run"),
    args: List[str] = typer.Argument(None, help="Arguments to pass to the script")
):
    """Run a custom script."""
    scripts_dir = get_scripts_dir()
    
    # Try to find the script with different extensions
    script_path = None
    for ext in [".py", ".sh", ""]:
        test_path = scripts_dir / f"{name}{ext}"
        if test_path.exists():
            script_path = test_path
            break
    
    if not script_path:
        console.print(f"[bold red]Error:[/] Script '{name}' not found.")
        return
    
    # Run the script based on its type
    if script_path.suffix == ".py":
        # Run Python script
        try:
            # Add script directory to path
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
    type: str = typer.Option("python", "--type", "-t", help="Script type (python or shell)"),
    edit: bool = typer.Option(True, "--edit/--no-edit", help="Open the script in an editor after creation")
):
    """Add a new custom script."""
    scripts_dir = get_scripts_dir()
    
    # Determine file extension based on type
    ext = ".py" if type.lower() == "python" else ".sh"
    script_path = scripts_dir / f"{name}{ext}"
    
    # Check if script already exists
    if script_path.exists():
        overwrite = typer.confirm(f"Script '{name}' already exists. Overwrite?")
        if not overwrite:
            return
    
    # Create script with template content
    with open(script_path, "w") as f:
        if type.lower() == "python":
            f.write("""#!/usr/bin/env python3
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
""")
        else:
            f.write("""#!/bin/bash
# Custom script for SkogCLI

echo "Hello from $(basename $0)!"
echo "Arguments: $@"
""")
    
    # Make the script executable
    script_path.chmod(script_path.stat().st_mode | 0o755)
    
    console.print(f"[green]Created script:[/] {script_path}")
    
    # Open in editor if requested
    if edit:
        editor = os.environ.get("EDITOR", "nano")
        try:
            exit_code = os.system(f"{editor} {script_path}")
            if exit_code == 0:
                console.print("[green]Script edited successfully.[/]")
            else:
                console.print(f"[bold red]Error:[/] Editor exited with code {exit_code}")
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")

@misc_app.command("edit")
@with_explanation("Edit an existing custom script.")
def edit_script(
    name: str = typer.Argument(..., help="Name of the script to edit")
):
    """Edit an existing custom script."""
    scripts_dir = get_scripts_dir()
    
    # Try to find the script with different extensions
    script_path = None
    for ext in [".py", ".sh", ""]:
        test_path = scripts_dir / f"{name}{ext}"
        if test_path.exists():
            script_path = test_path
            break
    
    if not script_path:
        console.print(f"[bold red]Error:[/] Script '{name}' not found.")
        return
    
    # Open in editor
    editor = os.environ.get("EDITOR", "nano")
    try:
        exit_code = os.system(f"{editor} {script_path}")
        if exit_code == 0:
            console.print("[green]Script edited successfully.[/]")
        else:
            console.print(f"[bold red]Error:[/] Editor exited with code {exit_code}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")

@misc_app.command("remove")
@with_explanation("Remove a custom script.")
def remove_script(
    name: str = typer.Argument(..., help="Name of the script to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal without confirmation")
):
    """Remove a custom script."""
    scripts_dir = get_scripts_dir()
    
    # Try to find the script with different extensions
    script_path = None
    for ext in [".py", ".sh", ""]:
        test_path = scripts_dir / f"{name}{ext}"
        if test_path.exists():
            script_path = test_path
            break
    
    if not script_path:
        console.print(f"[bold red]Error:[/] Script '{name}' not found.")
        return
    
    # Confirm removal
    if not force:
        confirm = typer.confirm(f"Are you sure you want to remove script '{name}'?")
        if not confirm:
            return
    
    # Remove the script
    try:
        script_path.unlink()
        console.print(f"[green]Removed script:[/] {name}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
